Introduction to Autokey for Wayland
===================================

AutoKey is a keyboard automation utility for the Linux desktop.  It can be used 
to automate repetitive keyboard and mouse tasks.  When hotkeys are pressed or 
short abbreviations are typed, AutoKey assists the user by performing 
predefined actions with the keyboard or mouse.  When more complex action 
sequences are required, a Python script can be executed from a hotkey or 
abbreviation to perform a series of actions.

A version of AutoKey_ that runs on X11_ has been available as a supported 
package for most Linux distributions for a number of years.  The goal of the 
`AutoKey for Wayland`_ project is to provide a version of AutoKey that will 
function on systems that use the Wayland_ protocol as well as on those that use 
X11_.  

The `AutoKey for Wayland`_ project is a fork of the AutoKey_ project.  It builds 
on work done in the "develop" branch of that project to create the facilities 
that AutoKey needs to operate in a Wayland environment.  An "official" version 
of AutoKey based on that work has not yet been released.

This project is still in development, and the code is unstable.  Use it at your 
own risk.  

AutoKey, X11 and Wayland
------------------------

Wayland_ is a new desktop protocol that has been slowly replacing X11_ in many 
distributions.  It offers additional security in desktop environments by 
severely restricting the degree to which applications can interact with desktop 
windows that are not their own.  This new level of security has required a 
number of changes to adapt to the new environment.  Also, there are a few 
functions that AutoKey can no longer perform in the Wayland environment.   See 
the `What Works & What Does Not`_ section for more specific details on the 
differences in capability across the two environments.

AutoKey uses completely different techniques under Wayland to communicate with 
the keyboard/mouse, the clipboard, and the desktop.  This is largely 
transparent to the general AutoKey user, but power users may encounter some of 
these differences.  See the `Technical Details`_ page for a brief discussion of 
these changes.

.. _AutoKey: https://github.com/autokey/autokey
.. _AutoKey for Wayland: https://github.com/dlk3/autokey-wayland
.. _Wayland: https://en.wikipedia.org/wiki/Wayland_(protocol)
.. _X11: https://en.wikipedia.org/wiki/X_Window_System
.. _What Works & What Does Not: whatworks.html
.. _Technical Details: technical.html
