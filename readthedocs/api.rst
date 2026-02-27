Autokey Scripting API
=====================

The following collection of convenience class methods and properties are 
available for your use in AutoKey scripts.  They expose AutoKey-specific 
features for your use.  

AutoKey scripts are Python scripts, so almost any Python library can be 
imported to add additional capabilities when writng an AutoKey script.

The class names shown in these pages are extracted from the program source code 
during the autogeneration of these documentation pages..  These class names 
have been "aliased" in the AutoKey API to make them easier for you to use when 
writing a script.  For example, the `Keyboard class page`_ documents a class 
called ``autokey.scripting.Keyboard``.  When this class is used in a script it 
can be called as just ``keyboard``.  So the 
``autokey.scripting.Keyboard.press_key()`` method is actually called in a 
script as ``keyboard.press_key()``.  This same approach applies across all of 
the API classes documented here.

.. _Keyboard class page: keyboard.html

.. toctree::
   api/keyboard.rst
   api/mouse.rst
   api/store.rst
   api/qtdialog.rst
   api/gtkdialog.rst
   api/qtclipboard.rst
   api/gtkclipboard.rst
   api/system.rst
   api/window.rst
   api/engine.rst
   api/highlevel.rst
   api/common.rst
