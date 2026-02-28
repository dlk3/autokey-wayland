clipboard API
=============

These API methods are available when running in all environments.

This class is invoked as the "clipboard" class in AutoKey scripts.  For example, the
"autokey.scripting.clipboard_gtk.GtkClipboard.fill_clipboard()" method documented below is
called as "clipboard.fill_clipboard()" in an AutoKey script.

There are three different implementations of the "clipboard" class, one for Wayland environments, one for X11/Gtk, and one for X11/Qt.  They all offer the exact same methods, so only the GTK version is shown in this documentation.

.. autoclass:: autokey.scripting.clipboard_gtk.GtkClipboard
   :members:
   :exclude-members: app, clipBoard