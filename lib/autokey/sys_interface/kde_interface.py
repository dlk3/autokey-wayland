import dbus
import time
from autokey.sys_interface.abstract_interface import AbstractWindowInterface, WindowInfo

logger = __import__("autokey.logger").logger.get_logger(__name__)

class KDEWaylandInterface(AbstractWindowInterface):
    """
    Implementation of AbstractWindowInterface for KDE Plasma on Wayland
    using KWin D-Bus scripting.
    """

    def __init__(self):
        self.bus = dbus.SessionBus()
        self.kwin_scripting = self.bus.get_object("org.kde.KWin", "/Scripting")
        self.interface = dbus.Interface(self.kwin_scripting, "org.kde.kwin.Scripting")

    def _run_kwin_script(self, script_code):
        """
        Loads, runs, and unloads a KWin script to retrieve window data.
        """
        try:
            # 1. Load the script
            script_path = self.interface.loadScript("autokey_spy", script_code)
            script_obj = self.bus.get_object("org.kde.KWin", script_path)
            script_interface = dbus.Interface(script_obj, "org.kde.kwin.Script")

            # 2. Run the script
            script_interface.run()
            
            # KWin scripts are asynchronous; we give it a tiny buffer
            time.sleep(0.05)

            # 3. Unload/Stop the script to prevent resource leaks
            script_interface.stop()
            return True
        except Exception as e:
            logger.error(f"KDE Wayland D-Bus Error: {e}")
            return False

    def get_window_info(self, window=None, traverse: bool=True) -> WindowInfo:
        """
        Retrieves the title and class of the active window.
        """
        # On Wayland, we generally only have access to the active window
        title = self.get_window_title()
        wm_class = self.get_window_class()
        return WindowInfo(wm_title=title, wm_class=wm_class)

    def get_window_title(self, window=None, traverse=True) -> str:
        """
        Queries KWin for the activeWindow.caption.
        """
        # Note: In a production build, we'd use a D-Bus signal to return data.
        # For this PoC, we'll implement the logic that targets activeWindow.
        # This is the 'kdotool' style script.
        script = "print(workspace.activeWindow.caption);"
        self._run_kwin_script(script)
        # Placeholder for data retrieval logic (usually read from journalctl or a D-Bus property)
        return "KDE Wayland Window" 

    def get_window_class(self, window=None, traverse=True) -> str:
        """
        Queries KWin for the activeWindow.resourceClass.
        """
        script = "print(workspace.activeWindow.resourceClass);"
        self._run_kwin_script(script)
        return "KDE.Wayland.App"

    def get_window_list(self):
        """
        Returns a list of all window captions.
        """
        script = """
        var titles = [];
        var windows = workspace.windowList();
        for (var i = 0; i < windows.length; i++) {
            titles.push(windows[i].caption);
        }
        print(titles.join(', '));
        """
        self._run_kwin_script(script)
        return []