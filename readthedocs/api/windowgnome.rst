window API on Wayland/Gnome
===========================

These API methods are available when running in a Wayland environment using the 
GNOME desktop.

This class is invoked as the "window" class in AutoKey scripts.  For example, the
"autokey.scripting.window_gnome.Window.activate()" method documented below is
called as "window.get_activate()" in an AutoKey script.

Due to Wayland's security constraints there are two window API methods that
cannot be implemented under Wayland: window.activate() and window.set_property().

.. automodule:: autokey.common
   :no-members:

.. automodule:: autokey.gtkapp
   :no-members:

.. automodule:: autokey.scripting.window_gnome
   :no-members:

.. autoclass:: Window
   :members:
   :exclude-members: activate, set_property
