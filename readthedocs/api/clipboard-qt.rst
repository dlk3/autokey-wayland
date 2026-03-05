clipboard API for the autokey-qt application on X11
====================================================

This class is invoked as the "clipboard" class in AutoKey scripts.  For example, the
"autokey.scripting.clipboard_qt.QtClipboard.fill_clipboard()" method documented below is
called as "clipboard.fill_clipboard()" in an AutoKey script.

There are three different implementations of the "clipboard" class, one for Wayland environments, one for X11/Gtk, and one for X11/Qt.  They all offer the exact same methods.  This the Qt implementation.

.. autoclass:: autokey.scripting.clipboard_qt.QtClipboard
   :members:
   :exclude-members: app, clipBoard