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

from gi.repository import GLib
from pydbus import SessionBus
import json
import os
import tempfile
import threading
import time
import uuid

from autokey.sys_interface.abstract_interface import AbstractSysInterface, AbstractMouseInterface, AbstractWindowInterface, WindowInfo

logger = __import__("autokey.logger").logger.get_logger(__name__)

#  The name of the KWinListener DBus service.
DBUS_SERVICE_NAME='com.autokey.KWinListener'

loop = GLib.MainLoop()

#  The definition for a DBus service that listens for a message from a
#  KWin script.
class KWinListener(object):
    """
        <node>
            <interface name='com.autokey.KWinListener'>
                <method name='Response'>
                    <arg type='s' name='response' direction='in'/>
                </method>
            </interface>
        </node>
    """
    def __init__(self):
        self.result = None

    def Response(self, message):
        self.result = message
        loop.quit()

    def _timeout(self):
        loop.quit()

class KWinInterface():

    def _run_script(self, kwin_script, response_expected=False, listener_timeout=5, unique_id=None):
        """
        Loads a KWin script into KWin and executes it.

        :param script: The KWin script's code
        :type script: string
        :keyword response_expected: Flag indicating whether or not a
        KWinListener service needs to be set up to collect data from the
        KWin script when it runs.
        :type response_expected: boolean
        :keyword listener_timeout: The number of seconds to wait for the
        KWinListener service to become ready. Only meaningful when
        response_expected = True.
        :keyword unigue_id:  A value used to associate this script with
        the KWinLister DBus service that awaits it's response.  Only
        meaningful when response_expected = True.
        :type unique_id: string
        """

        bus = SessionBus()

        if response_expected:
            #  Wait for KWinListener service to be ready, or until
            #  timeout expires
            found = False
            start_time = time.time()
            while not found:
                try:
                    service_path = '/' + DBUS_SERVICE_NAME.replace('.','/') + '/' + unique_id
                    obj = bus.get(DBUS_SERVICE_NAME, service_path)
                    obj.Introspect()
                    found = True
                except Exception as e:
                    time.sleep(0.1)
                if time.time() - listener_timeout > start_time:
                    return

        #  Save the KWin script in a temporary file
        (f, fn) = tempfile.mkstemp(prefix='autokey.kwin.script.', suffix='.js')
        with open(fn, 'w') as script_file:
            script_file.write(kwin_script)

        #  Load the file into KWin
        obj = bus.get('org.kde.KWin', '/Scripting')
        script_id = str(obj.loadScript(fn))

        #  Run the script
        obj = bus.get('org.kde.KWin', f'/Scripting/Script{script_id}')
        obj.run()

        #  Unload the script
        obj = bus.get('org.kde.KWin', '/Scripting')
        obj.unloadScript(fn)

        #  Delete the temporary file
        os.unlink(fn)

    def run(self, kwin_script, listener_timeout=10, response_expected=False):
        """
        This is the entrypoint into KWinInterface.  This method executes
        a KWin script and, optionally, receives the results.

        :param script: The KWin script code
        :type script: string
        :keyword response_expected: Flag indicating whether or not
        a response is expected to be returned byt the KWIN script.
        :type response_expected: boolean
        :keyword listener_timeout: The number of seconds to wait for
        the KWin script to send a response. Only meaningful when
        response_expected = True.
        """
        bus = SessionBus()

        unique_id = str(uuid.uuid4()).replace('-', '')

        if response_expected:
            service_path = '/' + DBUS_SERVICE_NAME.replace('.','/') + '/' + unique_id

            #  Add a line to the kwin_script that contains the call that
            #  sends the script's output back via our KWinListener DBus
            #  service.  Note that the kwin_script must put the data
            #  being sent into the "result" variable.
            kwin_script = kwin_script + f'\ncallDBus("{DBUS_SERVICE_NAME}", "{service_path}", "{DBUS_SERVICE_NAME}", "Response", result)'

            #  Send the script to KWin in a separate thread, so that a
            #  KWinListener DBus service can be started at the same time,
            #  listening for the script's reply message.
            t = threading.Thread(target=self._run_script, args=(kwin_script,), kwargs={'response_expected': response_expected, 'listener_timeout': listener_timeout, 'unique_id': unique_id})
            t.start()

            #  Start the KWinListener DBus service
            bus = SessionBus()
            listener = KWinListener()
            dbus_service = bus.publish(DBUS_SERVICE_NAME, (unique_id, listener))
            GLib.timeout_add_seconds(listener_timeout, listener._timeout)
            loop.run()
            #  Execution pauses here, until a DBus message is recieved
            #  or the timeout is reached.
            dbus_service.unpublish()

            #  Close the KWin script sending thread
            t.join()

            #  If the timeout expired, either the script code is broken
            #  or the timeout value isn't long enough
            if not listener.result:
                logger.error(f'Timeout expired before KWin script returned a result:\nDBUus service path: {service_path}\nKWin script:\n{kwin_script}')
            else:
                return listener.result

        else:
            #  Run the KWin script without waiting for a response
            self._run_script(kwin_script)

class KdeMouseReadInterface():
    def __init__(self):
        pass

    def mouse_location(self):
        """
        Returns the x/y coordinates of the mouse pointer

        :return: [x, y]
        :rtype: list
        """
        kwin_script = """const x = workspace.cursorPos.x;
const y = workspace.cursorPos.y;
result = [x, y];
result = JSON.stringify(result, null, 4);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
            return result

class KdeWindowInterface(AbstractWindowInterface):
    def __init__(self):
        super().__init__()

    def get_window_info(self, window=None, traverse: bool=True) -> WindowInfo:
        """
        Ask KWin for title and class of the currently focused window.

        :return: (wm_title, wm_class)
        :rtype: WindowInfo
        """
        kwin_script = """const w = workspace.activeWindow;
result = {
    'wm_class': w.resourceName,
    'wm_title': w.caption
};
result = JSON.stringify(result, null, 4);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
            result = json.loads(result)
            return WindowInfo(wm_title=result['wm_title'], wm_class=result['wm_class'])
        else:
            return WindowInfo(wm_title='unknown', wm_class='unknown')

    def get_window_list(self):
        """
        Ask KWin for a list of all the windows on the desktop

        :return: An array containing information about each window
        :rtype: list of dictionaries
        """
        kwin_script = """const windows = workspace.windowList();
winJsonArr = [];
windows.forEach(function(w) {
    if ((!w.desktopWindow) && ((w.desktops).length > 0)) {
        winJsonArr.push({
            wm_class: w.resourceClass,
            wm_class_instance: null,
            wm_title: w.caption,
            workspace: w.desktops[0].x11DesktopNumber - 1,
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
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
            result = json.loads(result)
            return result
        else:
            return []

    def get_window_title(self, window=None, traverse=True) -> str:
        """
        Returns the window title of the currently focused window.

        :return: window title
        :rtype: string
        """
        result = self.get_window_info()
        if result:
            return result[0]

    def get_window_class(self, window=None, traverse=True) -> str:
        """
        Returns the window class of the currently focused window.

        :return: window class
        :rtype: string
        """
        result = self.get_window_info()
        if result:
            return result[1]

    def get_screen_size(self):
        """
        Returns the width and height of the display

        :return: [width, height]
        :rtype: list
        """
        kwin_script="""const w = workspace.activeScreen.geometry;
result = [w.width, w.height];
result = JSON.stringify(result, null, 4);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
           return result

    """
    The rest of these methods support the window API
    """

    def get_active_window(self):
        raise NotImplementedError
        return self._active_window()

    def get_active_desktop_index(self):
        raise NotImplementedError
        return self._dbus_get_active_desktop_index()

    def close_window(self, window_id):
        raise NotImplementedError
        self._dbus_close_window(window_id)

    def activate_window(self, window_id):
        raise NotImplementedError
        self._dbus_activate_window(window_id)

    def move_resize_window(self, window_id, x, y , width, height):
        raise NotImplementedError
        self._dbus_move_resize_window(window_id, x, y, width, height)

    def get_screensize(self):
        raise NotImplementedError
        return self._dbus_get_screensize()

    def move_to_workspace(self, window_id, workspace_number):
        raise NotImplementedError
        self._dbus_move_to_workspace(window_id, workspace_number)

    def switch_workspace(self, workspace_number):
        raise NotImplementedError
        self._dbus_switch_workspace(workspace_number)

    def get_properties(self, window_id):
        raise NotImplementedError
        return self._dbus_get_properties(window_id)

    def stick_window(self, window_id):
        raise NotImplementedError
        self._dbus_stick_window(window_id)

    def unstick_window(self, window_id):
        raise NotImplementedError
        self._dbus_unstick_window(window_id)

    def maximize_window(self, window_id, direction):
        raise NotImplementedError
        self._dbus_maximize_window(window_id, direction)

    def unmaximize_window(self, window_id, direction):
        raise NotImplementedError
        self._dbus_unmaximize_window(window_id, direction)

    def make_fullscreen_window(self, window_id):
        raise NotImplementedError
        self._dbus_make_fullscreen_window(window_id)

    def unmake_fullscreen_window(self, window_id):
        raise NotImplementedError
        self._dbus_unmake_fullscreen_window(window_id)

    def make_above_window(self, window_id):
        raise NotImplementedError
        self._dbus_make_above_window(window_id)

    def unmake_above_window(self, window_id):
        raise NotImplementedError
        self._dbus_unmake_above_window(window_id)

    def _active_window(self):
        raise NotImplementedError
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
