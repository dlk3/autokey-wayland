Autokey Scripting API
=====================

Note that the `class` paths are not relevant to everyday autokey scripting. Generally speaking you can call all of these modules directly;
::

  keyboard.send_keys("example document")
  clipboard.set_content("update clipboard")

Is all that you need to call a method in the keyboard/clipboard API, note that you do not have to worry about import statements.

For the Qt/Gtk pages, these are abstracted, Autokey will select the UI framework most appropriate, you only need to reference these in your scripts as;
::

  dialog.info_dialog("Info dialog", "Test info dialog")
  clipboard.set_content("clipboard content")

.. toctree::
   api/keyboard.rst
   api/mouse.rst
   api/store.rst
   api/qtdialog.rst
   api/qtclipboard.rst
   api/gtkdialog.rst
   api/gtkclipboard.rst
   api/system.rst
   api/window.rst
   api/engine.rst
   api/highlevel.rst
   api/common.rst
