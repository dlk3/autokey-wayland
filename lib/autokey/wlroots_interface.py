import threading

import gi
gi.require_version('Libxfce4windowing', '0.0')
from gi.repository import Libxfce4windowing as Xfw
from gi.repository import GLib

from autokey import common
from autokey.sys_interface.abstract_interface import AbstractWindowInterface, WindowInfo

logger = __import__("autokey.logger").logger.get_logger(__name__)


class WlrootsWindowInterface(AbstractWindowInterface):

    def __init__(self):
        self._screen = Xfw.Screen.get_default()
        self._seat = None
        seats = self._screen.get_seats()
        if seats:
            self._seat = seats[0]
        if common.USED_UI_TYPE != "GTK":
            self._mainloop = GLib.MainLoop()
            self._mainloop_thread = threading.Thread(
                target=self._mainloop.run,
                daemon=True,
                name="wlroots-glib-mainloop"
            )
            self._mainloop_thread.start()
        logger.debug("WlrootsWindowInterface initialized")

    def cancel(self):
        if hasattr(self, '_mainloop') and self._mainloop.is_running():
            self._mainloop.quit()

    def get_window_info(self, window=None, traverse=True):
        active = self._screen.get_active_window()
        if active is None:
            return WindowInfo(wm_title='', wm_class='')
        class_ids = active.get_class_ids()
        wm_class = class_ids[0] if class_ids else ''
        return WindowInfo(wm_title=active.get_name() or '', wm_class=wm_class)

    def get_window_title(self, window=None, traverse=True):
        active = self._screen.get_active_window()
        if active is None:
            return ''
        return active.get_name() or ''

    def get_window_class(self, window=None, traverse=True):
        active = self._screen.get_active_window()
        if active is None:
            return ''
        class_ids = active.get_class_ids()
        return class_ids[0] if class_ids else ''

    def get_window_list(self):
        result = []
        active = self._screen.get_active_window()
        self._window_map = {}
        for w in self._screen.get_windows():
            wid = id(w)
            self._window_map[wid] = w
            class_ids = w.get_class_ids()
            wm_class = class_ids[0] if class_ids else ''
            is_active = (active is not None and w == active)
            ws = w.get_workspace()
            result.append({
                'wm_class': wm_class,
                'wm_title': w.get_name() or '',
                'focus': is_active,
                'x': 0, 'y': 0, 'width': 0, 'height': 0,
                'id': wid,
                'pid': None,
                'workspace': ws.get_number() if ws else None,
                'desktop': ws.get_number() if ws else None,
                'in_current_workspace': w.is_in_viewport(ws) if ws else True,
            })
        return result

    def get_active_window(self):
        active = self._screen.get_active_window()
        if active is None:
            return self._empty_window()
        if not hasattr(self, '_window_map'):
            self._window_map = {}
        self._window_map[id(active)] = active
        return self._window_to_dict(active, is_active=True)

    def get_screen_size(self):
        monitors = self._screen.get_monitors()
        if not monitors:
            return [0, 0]
        max_x = max_y = 0
        for mon in monitors:
            geo = mon.get_logical_geometry()
            max_x = max(max_x, geo.x + geo.width)
            max_y = max(max_y, geo.y + geo.height)
        return [max_x, max_y]

    def get_active_desktop_index(self):
        wm = self._screen.get_workspace_manager()
        for ws in wm.list_workspaces():
            if ws.get_state() & Xfw.WorkspaceState.ACTIVE:
                return ws.get_number()
        return 0

    def close_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.close(0)

    def activate_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.activate(self._seat, 0)

    def move_resize_window(self, window_id, x, y, width, height):
        w = self._find_window(window_id)
        if w:
            try:
                from gi.repository import Gdk
                rect = Gdk.Rectangle()
                rect.x, rect.y, rect.width, rect.height = x, y, width, height
                w.set_geometry(rect)
            except Exception:
                logger.warning("set_geometry not supported on this compositor")

    def move_to_workspace(self, window_id, workspace_number):
        w = self._find_window(window_id)
        if w:
            wm = self._screen.get_workspace_manager()
            for ws in wm.list_workspaces():
                if ws.get_number() == workspace_number:
                    w.move_to_workspace(ws)
                    return

    def switch_workspace(self, workspace_number):
        wm = self._screen.get_workspace_manager()
        for ws in wm.list_workspaces():
            if ws.get_number() == workspace_number:
                ws.activate()
                return

    def get_properties(self, window_id):
        w = self._find_window(window_id)
        if w:
            return self._window_to_dict(w, w.is_active())
        return self._empty_window()

    def stick_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_pinned(True)

    def unstick_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_pinned(False)

    def maximize_window(self, window_id, direction):
        w = self._find_window(window_id)
        if w:
            w.set_maximized(True)

    def unmaximize_window(self, window_id, direction):
        w = self._find_window(window_id)
        if w:
            w.set_maximized(False)

    def make_fullscreen_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_fullscreen(True)

    def unmake_fullscreen_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_fullscreen(False)

    def make_above_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_above(True)

    def unmake_above_window(self, window_id):
        w = self._find_window(window_id)
        if w:
            w.set_above(False)

    def _find_window(self, window_id):
        if hasattr(self, '_window_map') and window_id in self._window_map:
            return self._window_map[window_id]
        for w in self._screen.get_windows():
            title = w.get_name() or ''
            class_ids = w.get_class_ids()
            wm_class = class_ids[0] if class_ids else ''
            if str(window_id) in (title, wm_class):
                return w
        return None

    def _window_to_dict(self, w, is_active):
        class_ids = w.get_class_ids()
        wm_class = class_ids[0] if class_ids else ''
        ws = w.get_workspace()
        return {
            'wm_class': wm_class,
            'wm_title': w.get_name() or '',
            'focus': is_active,
            'x': 0, 'y': 0, 'width': 0, 'height': 0,
            'id': id(w),
            'pid': None,
            'workspace': ws.get_number() if ws else None,
            'desktop': ws.get_number() if ws else None,
            'in_current_workspace': True,
            'is_maximized': w.is_maximized(),
            'is_maximized_vert': w.is_maximized(),
            'is_fullscreen': w.is_fullscreen(),
            'is_above': w.is_above(),
            'is_minimized': w.is_minimized(),
            'is_pinned': w.is_pinned(),
        }

    @staticmethod
    def _empty_window():
        return {
            'wm_class': '', 'wm_title': '', 'focus': False,
            'x': 0, 'y': 0, 'width': 0, 'height': 0,
            'id': None, 'pid': None, 'workspace': None,
            'desktop': None, 'in_current_workspace': False,
        }


class FallbackMouseInterface:

    def __init__(self):
        pass

    def mouse_location(self):
        # labwc doesn't expose cursor position through any IPC protocol.
        # Wayland by design prevents clients from querying global pointer state.
        # Compositors with IPC (e.g. Sway) can override this with actual values.
        return (0, 0)
