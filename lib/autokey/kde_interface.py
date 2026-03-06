#  Copyright (C) 2026 David King
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################

#  For standalone testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/home/dlk/src/autokey-wayland/lib')

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import json
import os
import subprocess
import tempfile
import threading
import time

from autokey.sys_interface.abstract_interface import AbstractSysInterface, AbstractMouseInterface, AbstractWindowInterface, WindowInfo

try:
    logger = __import__("autokey.logger").logger.get_logger(__name__)
except Exception:
    #  For standalone testing
    import logging
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

#  The name we use for our KWin listener dbus service.
DBUS_SERVICE_NAME='com.autokey.KwinListener'

class KWinListener(dbus.service.Object):
    """
    Create a DBus service that listens for one message, returns the
    content of that message, and then quits.

    :keyword timeout_seconds: how long, in seconds, the service should
    wait to receive a message before it quits, returning nothing.
    Default is 5 seconds.
   :type timeout_seconds: integer
    """
    def __init__(self, timeout_seconds=5):
        self._result = ''
        self._timeout_seconds = timeout_seconds
        self._service_name = DBUS_SERVICE_NAME
        self._service_path = '/' + self._service_name.replace('.', '/')

    def run(self):
        """
        Start the dbus service, wait for a message, and return the
        content.

        :return: the contents of the dbus message that was received, if
        any.
        :rtype: string
        """
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(self._service_name, dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, self._service_path)
        GLib.timeout_add_seconds(self._timeout_seconds, self._timeout)
        self._loop = GLib.MainLoop()
        logger.debug('KWinListener dbus service is ready to receive messages')
        self._loop.run()
        return self._result

    def _timeout(self):
        """
        This method is called to terminate the service when it times out,
        """
        logger.debug('KWinListener timed out waiting for a message')
        self._loop.quit()

    @dbus.service.method(dbus_interface=DBUS_SERVICE_NAME, in_signature='s', out_signature='')
    def Response(self, result):
        """
        This is the dbus service's sole method.

        :param result: The contents of the message that was received from
        the client, if any.
        :type result: string
        """
        self._loop.quit()
        self._result = result

class KWinInterface():

    @staticmethod
    def __send_kwin_script(script, service_name, response_expected=False):
        """
        Loads a KWin script and executes it.  If a response is expected
        to come back from the script via a bdus, a KWinListener dbus
        service is used to collect that response.

        :param script: The KWin script's code
        :type script: string
        :param service_name: The name of the KwinListener dbus service
        :type service_name: string
        :keyword response_expected: Flag indicating whether or not a
        KWinListener service needs to be set up to collect data from the
        KWin script when it runs.
        :type response_expected: boolean
        """
        #  Write the script into a temporary file
        (f, fn) = tempfile.mkstemp(prefix='autokey.kwin.script', suffix='.js')
        with open(fn, 'w') as script_file:
            script_file.write(script)
        logger.debug(f'KWin script filename: {fn}')

        #  Load the script in KWin
        try:
            proc = subprocess.run(['dbus-send', '--print-reply', '--dest=org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.loadScript', f'string:{fn}'], capture_output=True, check=True)
            logger.debug(proc)
        except subprocess.CalledProcessError:
            logger.exception('Unexpected exception loading a KWin script')
            return
        script_id = proc.stdout.decode('utf-8').split('\n')[1].strip().split(' ')[1]
        if not script_id:
            try:
                script_id = print(proc.stdout.split('\n')[1].strip().split(' ')[1])
            except TypeError:
                pass
            if not script_id:
                logger.error('KWin script loaded, but I could not get the script_id')
                try:
                    proc = subprocess.run(['dbus-send', '--print-reply', '--dest=org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.unloadScript', f'string:{fn}'], capture_output=True, check=True)
                    logger.debug(proc)
                except subprocess.CalledProcessError:
                    logger.exception('Unexpected exception loading a KWin script')
                return

        logger.debug(f'KWin script id number: {script_id}')

        #  Wait for the listener to come up, but only if we're expecting a response
        if response_expected:
            #  Wait for KWinListener service to appear
            found = False
            while not found:
                proc = subprocess.run(['dbus-send', '--session', '--print-reply', '--dest=' + service_name, '/' + service_name.replace('.', '/'), 'org.freedesktop.DBus.Introspectable.Introspect'], capture_output=True, check=True)
                if proc.returncode == 0:
                    found=True
                time.sleep(0.1)

        #  Execute the KWin script
        try:
            proc = subprocess.run(['dbus-send', '--print-reply', '--dest=org.kde.KWin', f'/Scripting/Script{script_id}', 'org.kde.kwin.Script.run'], capture_output=True, check=True)
            logger.debug(proc)
        except subprocess.CalledProcessError:
            logger.exception('Unexpected exception running a KWin script')
            return

        #  Unload the script from KWin and erase the temporary file
        try:
            proc = subprocess.run(['dbus-send', '--print-reply', '--dest=org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.unloadScript', f'string:{fn}'], capture_output=True, check=True)
            logger.debug(proc)
            os.unlink(fn)
        except subprocess.CalledProcessError:
            logger.exception('Unexpected exception running a KWin script')
            return

    def run_kwin_script(script, response_expected=False):
        """
        This the entrypoint into the KWin interface.  Call this method
        to execute a KWin script and retrieve the results, if any.

        :param script: The KWin script's code
        :type script: string
        :keyword response_expected: Flag indicating whether or not data
        is expected to be returned.
        :type response_expected: boolean
        """
        if response_expected:
            #  Append the callDBus to the end of the script.  Make sure script
            #  has put the data it wants to send into the "result" variable.
            script = script + f'\ncallDBus("{DBUS_SERVICE_NAME}", "{'/' + DBUS_SERVICE_NAME.replace('.', '/')}", "{DBUS_SERVICE_NAME}", "Response", result)'
            #  Send the script to Kwin using a separate thread
            t = threading.Thread(target=KWinInterface.__send_kwin_script, args=(script, DBUS_SERVICE_NAME,), kwargs={'response_expected': response_expected})
            t.start()
            #  Start our dbus listener
            result = KWinListener().run()
            t.join()
            return result
        else:
            #  Send the script without waiting for anything back
            KWinInterface.__send_kwin_script(script, DBUS_SERVICE_NAME)

class KdeMouseReadInterface(DBusListener):
    def __init__(self):
        super().__init__()

    def mouse_location(self):
        [x, y] = self.dbus_interface.GetMouseLocation()
        return [int(x), int(y)]

class KdeWindowInterface(DBusInterface, AbstractWindowInterface):
    def __init__(self):
        super().__init__()

    def get_window_info(self, window=None, traverse: bool=True) -> WindowInfo:
        """
        Returns a WindowInfo object containing the class and title.
        """
        window = self._active_window()
        return WindowInfo(wm_class=window['wm_class'], wm_title=window['wm_title'])

    def get_window_list(self):
        kwin_script = """const windows = workspace.windowList();
winJsonArr = [];
windows.forEach(function(w) {
    if ((!w.desktopWindow) && ((w.desktops).length > 0)) {
        winJsonArr.push({
            wm_class: w.resourceClass,
            wm_class_instance: null,
            wm_title: w.caption,
            workspace: w.desktops[0].x11DesktopNumber,
            desktop: w.desktops[0].id,
            pid: w.pid,
            id: w.internalId,
            frame_type: null,
            window_type: w.windowType,
            width: w.width,
            height: w.height,
            x: w.x,
            y: w.y,
            focus: w.active,
            in_current_workspace: null
        });
    }
});
result = JSON.stringify(winJsonArr, null, 0);"""
        result = KWinInterface.run_kwin_script(script, response_expected=True)
        if result:
            result = json.load(result)
        return result

    def get_window_title(self, window=None, traverse=True) -> str:
        """
        Returns the active window title
        """
        return self._active_window()['wm_title']

    def get_window_class(self, window=None, traverse=True) -> str:
        """
        Returns the window class of the currently focused window.
        """
        return self._active_window()['wm_class']


    def get_screen_size(self):
        x,y = self.dbus_interface.ScreenSize()
        return [int(x), int(y)]

    def get_active_window(self):
        return self._active_window()

    def get_active_desktop_index(self):
        return self._dbus_get_active_desktop_index()

    def close_window(self, window_id):
        self._dbus_close_window(window_id)

    def activate_window(self, window_id):
        self._dbus_activate_window(window_id)

    def move_resize_window(self, window_id, x, y , width, height):
        self._dbus_move_resize_window(window_id, x, y, width, height)

    def get_screensize(self):
        return self._dbus_get_screensize()

    def move_to_workspace(self, window_id, workspace_number):
        self._dbus_move_to_workspace(window_id, workspace_number)

    def switch_workspace(self, workspace_number):
        self._dbus_switch_workspace(workspace_number)

    def get_properties(self, window_id):
        return self._dbus_get_properties(window_id)

    def stick_window(self, window_id):
        self._dbus_stick_window(window_id)

    def unstick_window(self, window_id):
        self._dbus_unstick_window(window_id)

    def maximize_window(self, window_id, direction):
        self._dbus_maximize_window(window_id, direction)

    def unmaximize_window(self, window_id, direction):
        self._dbus_unmaximize_window(window_id, direction)

    def make_fullscreen_window(self, window_id):
        self._dbus_make_fullscreen_window(window_id)

    def unmake_fullscreen_window(self, window_id):
        self._dbus_unmake_fullscreen_window(window_id)

    def make_above_window(self, window_id):
        self._dbus_make_above_window(window_id)

    def unmake_above_window(self, window_id):
        self._dbus_unmake_above_window(window_id)

    def _active_window(self):
        #TODO probably can be done more efficiently with an additional dbus method in the gnome extension
        window_list = self._dbus_window_list()
        for window in window_list:
            if window['focus']:
                return window
        # TODO seeing this a lot when I use a script to call `gnome-screenshot -a`, suspect it's just related to that focus behaves differently when that app runs?
        logger.error(f"Unable to determine the active window. The window list: {window_list}")

        # @dlk3 - This happens when any GNOME session utility is active, like gnome-screenshot, the Activites screen, or the screen lock.  None of the windows in the
        # window_list have focus when those things do.  Need to return something, however, or get_active_window() above throws an exception that causes even more
        # problems - any keystrokes made on the GNOME session utility sit in the queue, preventing abbreviations being recognized, until the queue gets flushed
        # somehow.
        #
        # This seems to work to prevent the exceptions and the follow-on problems ...
        # Return an empty window object (Only really need wm_class and wm_title, but hey, why not do it all)
        empty_window = {
            'wm_class': '',
            'wm_class_instance': '',
            'wm_title': '',
            'workspace': None,
            'desktop': None,
            'pid': None,
            'id': None,
            'frame_type': None,
            'window_type': None,
            'width': None,
            'height': None,
            'x': None,
            'y': None,
            'focus': False,
            'in_current_workspace': False
        }
        return empty_window

    def _dbus_get_active_desktop_index(self):
        try:
            return self.dbus_interface.GetActiveWorkspaceIndex()
        except dbus.exceptions.DBusException as e:
            self.__init__() #reconnect to dbus
            return self.dbus_interface.GetActiveWorkspaceIndex()

    def _dbus_window_list(self):
        #TODO consider how/if error handling can be implemented
        try:
            return json.loads(self.dbus_interface.List())
        except dbus.exceptions.DBusException as e:
            self.__init__() #reconnect to dbus
            return json.loads(self.dbus_interface.List())

    def _dbus_close_window(self, window_id):
        #TODO consider how/if error handling can be implemented
        try:
            self.dbus_interface.Close(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Close(window_id)

    def _dbus_activate_window(self, window_id):
        try:
            self.dbus_interface.Raise(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Raise(window_id)

    def _dbus_move_resize_window(self, window_id, x, y, width, height):
        try:
            self.dbus_interface.MoveResize(window_id, x, y, width, height)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.MoveResize(window_id, x, y, width, height)

    def _dbus_move_window(self, window_id, x, y):
        try:
            self.dbus_interface.Move(window_id, x, y)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Move(window_id, x, y)

    def _dbus_resize_window(self, window_id, width, height):
        try:
            self.dbus_interface.Resize(window_id, width, height)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Resize(window_id, width, height)

    def _dbus_move_to_workspace(self, window_id, workspace_number):
        try:
            self.dbus_interface.MoveToWorkspace(window_id, workspace_number)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.MoveToWorkspace(window_id, workspace_number)

    def _dbus_get_screensize(self):
        try:
            return self.dbus_interface.ScreenSize()
        except dbus.exceptions.DBusException as e:
            self.__init__()
            return self.dbus_interface.ScreenSize()

    def _dbus_switch_workspace(self, workspace_number):
        try:
            return self.dbus_interface.SwitchWorkspace(workspace_number)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            return self.dbus_interface.SwitchWorkspace(workspace_number)

    def _dbus_get_properties(self, window_id):
        try:
            return json.loads(self.dbus_interface.Properties(window_id))
        except dbus.exceptions.DBusException as e:
            self.__init__()
            return json.loads(self.dbus_interface.Properties(window_id))

    def _dbus_stick_window(self, window_id):
        try:
            self.dbus_interface.Stick(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Stick(window_id)

    def _dbus_unstick_window(self, window_id):
        try:
            self.dbus_interface.UnStick(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.UnStick(window_id)

    def _dbus_maximize_window(self, window_id, direction):
        try:
            self.dbus_interface.Maximize(window_id, direction)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.Maximize(window_id, direction)

    def _dbus_unmaximize_window(self, window_id, direction):
        try:
            self.dbus_interface.UnMaximize(window_id, direction)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.UnMaximize(window_id, direction)

    def _dbus_make_fullscreen_window(self, window_id):
        try:
            self.dbus_interface.MakeFullscreen(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.MakeFullscreen(window_id)

    def _dbus_unmake_fullscreen_window(self, window_id):
        try:
            self.dbus_interface.UnMakeFullscreen(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.UnMakeFullscreen(window_id)

    def _dbus_make_above_window(self, window_id):
        try:
            self.dbus_interface.MakeAbove(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.MakeAbove(window_id)

    def _dbus_unmake_above_window(self, window_id):
        try:
            self.dbus_interface.UnMakeAbove(window_id)
        except dbus.exceptions.DBusException as e:
            self.__init__()
            self.dbus_interface.UnMakeAbove(window_id)

#  For standalone testing
if __name__ == "__main__":
    result = KdeWindowInterface.get_window_list()
    print(result)
