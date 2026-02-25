Introduction to Autokey for Wayland
===================================

AutoKey is a keyboard automation utility for the Linux desktop.  It can be used to automate repetitive keyboard and mouse tasks.  When **hotkeys** are pressed, or short **abbreviations** are typed, AutoKey assists the user by performing predefined actions with the keyboard or mouse.  When more complex action sequences are required, a script can be executed from a **hotkey** or **abbreviation** to perform a series of actions.

AutoKey, X11 and Wayland
========================

A version of AutoKey_ that runs on X11_ has been available as a supported package for most Linux distributions for a number of years.  The goal of the AutoKey for Wayland project is to provide a version of AutoKey that will function on systems that use the Wayland_ protocol and on systems that use the X11_ protocol.  

.. _AutoKey: https://github.com/autokey/autokey

Wayland_ is a new desktop protocol that has been slowly replacing X11_ in many distributions.  It offers additional security in desktop environments by controlling the degree to which applications can interact with desktop windows that are not their own.  This new level of security has had an impact on AutoKey.  Specifically, AutoKey's ability to modify desktop windows and read/write the contents of the clipboard has been affected.  See the `What Works & What Does Not`_ section for more specific details on the differences in capabilities across the two environments.

.. _Wayland: https://en.wikipedia.org/wiki/Wayland_(protocol)
.. _X11: https://en.wikipedia.org/wiki/X_Window_System
.. _What Works & What Does Not:
