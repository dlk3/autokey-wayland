window API on Wayland/Gnome
===========================

These API methods are available when running in a Wayland environment using the GNOME desktop.

This class is invoked as the "window" class in AutoKey scripts.  For example, the
"autokey.scripting.window_gnome.Window.activate()" method documented below is
called as "window.get_activate()" in an AutoKey script.

The Wayland environment does not allow AutoKey to control the windows on the desktop.  There are, therefore, fewer methods available in the Wayland version of this API class.  These methods are implemented through GNOME's extension API, not directly to X11, as is done in the X11 version of this API.

.. automodule:: autokey.common
   :no-members:

.. automodule:: autokey.gtkapp
   :no-members:

.. automodule:: autokey.scripting.window_gnome
   :no-members:

.. autoclass:: Window
   :members:
   :exclude-members: center_window, get_active_geometry, move_to_desktop, resize_move, set_property, switch_desktop, wait_for_exist, wait_for_focus
