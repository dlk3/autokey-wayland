window API implementation for X11 environments
==============================================

This class is invoked as the "window" class in AutoKey scripts.  For example, the
"autokey.scripting.window_gnome.Window.activate()" method documented below is
called as "window.activate()" in an AutoKey script.

There are two different implementations of the "window" class, one for GNOME/Wayland
environments one for X11.  This is the X11 version.

.. automodule:: autokey.common
   :no-members:

.. automodule:: autokey.gtkapp
   :no-members:

.. automodule:: autokey.scripting.window
   :no-members:

.. autoclass:: Window
   :members:
