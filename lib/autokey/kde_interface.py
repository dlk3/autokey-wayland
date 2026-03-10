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
import re

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
        result = obj.run()

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
result = JSON.stringify(result);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
            return json.loads(result)

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
result = JSON.stringify(result);"""
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
            wm_class_instance: w.resourceClass,
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
            in_current_workspace: (w.desktops.find((d) => d == workspace.currentDesktop) !== null)
        });
    }
});
result = JSON.stringify(winJsonArr);"""
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
result = JSON.stringify(result);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
           return json.loads(result)

    """
    The rest of these methods support the window API
    """

    def get_active_window(self):
        """
        Ask KWin for the details for the currently focused window

        :return: A dictionary containing information a window
        :rtype: dictionary
        """
        window_list = self.get_window_list()
        for window in window_list:
            if window['focus']:
                return window
        #  If none of the windows in the list have focus, return an empty object
        logger.error(f"Unable to determine the active window. The window list: {window_list}")
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

    def get_active_desktop_index(self):
        kwin_script="""const d = workspace.currentDesktop;
result = d.x11DesktopNumber - 1;
result = JSON.stringify(result);"""
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
           return json.loads(result)

    def close_window(self, window_id):
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.closeWindow();
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

    def activate_window(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided for activate_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    workspace.activeWindow = w;
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

    def move_resize_window(self, window_id, x, y , width, height):
        if not window_id:
            logger.error('valid window_id not provided for move_resize_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    let obj = Object.assign({}, w.frameGeometry);
    obj.x = <x>;
    obj.y = <y>;
    obj.width = <width>;
    obj.height = <height>;
    w.frameGeometry = obj;
}""".replace('<window_id>', window_id)
        kwin_script = kwin_script.replace('<x>', str(x))
        kwin_script = kwin_script.replace('<y>', str(y))
        kwin_script = kwin_script.replace('<width>', str(width))
        kwin_script = kwin_script.replace('<height>', str(height))
        KWinInterface().run(kwin_script)

    def move_to_workspace(self, window_id, workspace_number):
        if not window_id:
            logger.error('valid window_id not provided for move_to_worspace()')
            return
        kwin_script = """let d = workspace.desktops.find((d) => d.x11DesktopNumber == <workspace_number>);
if (d) {
    let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
    if (w) {
        w.desktops = [d];
    }
}""".replace('<window_id>', window_id)
        kwin_script = kwin_script.replace('<workspace_number>', str(workspace_number + 1))
        KWinInterface().run(kwin_script)

    def switch_workspace(self, workspace_number):
        kwin_script = """let d = workspace.desktops.find((d) => d.x11DesktopNumber == <workspace_number>);
if (d) {
    workspace.currentDesktop = d;
}""".replace('<workspace_number>', str(workspace_number + 1))
        KWinInterface().run(kwin_script)

    def get_properties(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided for get_properties()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    result = JSON.stringify({
        is_modal: w.modal,
        is_shaded: w.shade,
        is_skip_taskbar: w.skipTaskbar,
        is_hidden: w.hidden,
        is_fullscreen: w.fullscreen,
        is_above: w.keepAbove
    });
} else {
    result = '';
}""".replace('<window_id>', window_id)
        result = KWinInterface().run(kwin_script, response_expected=True)
        if result:
           return json.loads(result)

    def stick_window(self, window_id):
        logger.warning('stick_window() not implemented for KDE/Wayland.  The sticky property is not exposed in the KWin script API.')
        return

    def unstick_window(self, window_id):
        logger.warning('unstick_window() not implemented for KDE/Wayland:  The sticky property is not exposed in the KWin script API.')
        return

    def maximize_window(self, window_id, direction):
        """
        direction:
            1 - horizontal
            2 - vertical
            3 - both
        """
        if not window_id:
            logger.error('valid window_id not provided for maximize_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.setMaximize(<maximize>);
}""".replace('<window_id>', window_id)
        if direction == 1:
            kwin_script = kwin_script.replace('<maximize>', 'false, true')
        elif direction == 2:
            kwin_script = kwin_script.replace('<maximize>', 'true, false')
        elif direction == 3:
            kwin_script = kwin_script.replace('<maximize>', 'true, true')
        else:
            logger.warning('maximize_window(direction) called with invalid value.  Must be 1 for horizontal, 2 for vertical, or 3 for both.')
            return
        KWinInterface().run(kwin_script)

    def unmaximize_window(self, window_id, direction):
        """
        direction:
            1 - horizontal
            2 - vertical
            3 - both
        """
        if not window_id:
            logger.error('valid window_id not provided for unmaximize_window()')
            return
        if direction not in [1,2,3]:
            logger.warning('unmaximize_window(direction) called with invalid value.  Must be 1 for horizontal, 2 for vertical, or 3 for both.')
            return
        kwin_script = """const direction = <direction>;
const w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    const s = workspace.clientArea(KWin.MaximizeArea, w);
    vert = (w.height > s.height);
    horiz = (w.width == s.width);
    if (direction == 1) {
        w.setMaximize(vert, false);
    } else if (direction == 2){
        w.setMaximize(false, horiz);
    } else if (direction == 3) {
        w.setMaximize(false, false);
    }
}""".replace('<window_id>', window_id)
        kwin_script = kwin_script.replace('<direction>', str(direction))
        KWinInterface().run(kwin_script)

    def make_fullscreen_window(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided for make_fullscreen_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.fullScreen = true;
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

    def unmake_fullscreen_window(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided for unmake_fullscreen_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.fullScreen = false;
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

    def make_above_window(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided make_above_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.keepAbove = true;
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

    def unmake_above_window(self, window_id):
        if not window_id:
            logger.error('valid window_id not provided for unmake_above_window()')
            return
        kwin_script = """let w = workspace.windowList().find((w) => w.internalId == '<window_id>');
if (w) {
    w.keepAbove = false;
}""".replace('<window_id>', window_id)
        KWinInterface().run(kwin_script)

