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
import subprocess
import tempfile
import threading
import glob
import queue

from autokey.sys_interface.abstract_interface import AbstractSysInterface, AbstractWindowInterface, WindowInfo, queue_method

logger = __import__("autokey.logger").logger.get_logger(__name__)

#  Toggle extra debug log messages useful for tracing message flow
#  through queues and caches
VERBOSE = True

#  The name of the KWinListener DBus service.
DBUS_MOUSE_SERVICE_NAME='com.autokey.KdeMouseListener'

#  The definition for a DBus service that listens for a message from a
#  KWin script.
#
#  The XML in the docstring in this class is NOT a comment, it is the
#  DBus introspection detail that pydbus uses when it publishes this
#  service.
class KdeMouseListener(object):
    """
        <node>
            <interface name='com.autokey.KdeMouseListener'>
                <method name='Response'>
                    <arg type='s' name='response' direction='in'/>
                </method>
                <method name='Shutdown'/>
            </interface>
        </node>
    """
    def __init__(self):
        self.response_queue = queue.Queue()

    def Response(self, message):
        self.response_queue.put(message)
        if VERBOSE:
            logger.debug(f'KdeMouseListener queued a Response message:\n{json.loads(message)}')
        return True

    def Shutdown(self):
        self.response_queue.shutdown()
        loop.quit()
        return True

class KWinMouseInterface():

    def __init__(self, timeout=1):
        self.timeout = timeout
        self.response_cache = {}

        #  Start the DBus service thread
        self.loop = GLib.MainLoop()
        self.dbus_thread = threading.Thread(target=self._dbus_service)
        self.dbus_thread.start()

        #  Delete any old script files from the tmp directory
        fn_spec = os.path.join(tempfile.gettempdir(), 'autokey.kwin.mouse.script.*.js')
        for fn in glob.glob(fn_spec):
            os.unlink(fn)

    #  Method that runs the DBus service in a seperate thread
    def _dbus_service(self):
        self.listener = KdeMouseListener()
        bus = SessionBus()
        dbus_service = bus.publish(DBUS_MOUSE_SERVICE_NAME, self.listener)
        self.loop.run()

    #  Method to sutdown the DBus service thread and clean up KWin
    #  scripts and their temp files
    def cancel(self):
        self.loop.quit()
        self.dbus_thread.join()

        #  Erase the temporary script files
        fn_spec = os.path.join(tempfile.gettempdir(), 'autokey.kwin.mouse.script.*.js')
        for fn in glob.glob(fn_spec):
            os.unlink(fn)

    #  Method that loads a kwin_script into KWin.  Called by run() below.
    def _load_script(self, kwin_script, response_expected=False):
        if response_expected:
            service_path = '/' + DBUS_MOUSE_SERVICE_NAME.replace('.','/')
            kwin_script = kwin_script + f' callDBus("{DBUS_MOUSE_SERVICE_NAME}", "{service_path}", "{DBUS_MOUSE_SERVICE_NAME}", "Response", result);'

        bus = SessionBus()
        obj = bus.get('org.kde.KWin', '/Scripting')

        #  Save the KWin script in a temporary file
        (f, fn) = tempfile.mkstemp(prefix='autokey.kwin.mouse.script.', suffix='.js')
        with open(fn, 'w') as script_file:
            script_file.write(kwin_script)

        #  Load the script file into KWin
        return 'Script' + str(obj.loadScript(fn))

    #  Method that runs a kwin_script
    def run(self, kwin_script, script_name=None, response_expected=False):
        script_id = self._load_script(kwin_script, response_expected=response_expected)
        bus = SessionBus()
        obj = bus.get('org.kde.KWin', f'/Scripting/{script_id}')
        obj.run()

        if response_expected:
            try:
                #  Get the next response from the DBus service's queue
                response = json.loads(self.listener.response_queue.get(timeout=self.timeout))
            except queue.Empty:
                #  There wasn't anything in the queue, return the
                #  previous response from this service from the cache
                logger.error(f'timed out while waiting for response from {script_name}')
                if script_name in self.response_cache:
                    logger.error(f'Sending cached response for {script_name}')
                    return self.response_cache[script_name]
                logger.error(f'No cached response available for {script_name}')
                return
            #  If the response matches the script that's being called,
            #  return the reponse, otherwise log an error and return
            #  None.
            if response[0] == script_name:
                self.response_cache[script_name] = response[1]
                return response[1]
            else:
                logger.error(f'Unexpected response from {response[0]}, expected {script_name}')
                return

        #  Remove the script from Kwin
        obj.stop()
        os.unlink(fn)

class KdeMouseInterface():
    def __init__(self):
        super().__init__()
        self.kwin = KWinMouseInterface()

    def cancel(self):
        self.kwin.cancel()

    def mouse_location(self):
        """
        Returns the x/y coordinates of the mouse pointer

        :return: [x, y]
        :rtype: list
        """
        kwin_script = 'let result = JSON.stringify(["mouse_location", workspace.cursorPos]);'
        result = self.kwin.run(kwin_script, script_name='mouse_location', response_expected=True)
        if result:
            return [result['x'], result['y']]
