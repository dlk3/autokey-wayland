What Works & What Does Not
==========================

Wayland is designed to close the X11 security holes that allowed one
application to spy on another through the desktop.  Since AutoKey depended on
these security holes to do what it does, AutoKey has some limitations when
running under Wayland.

What Works Under Wayland
------------------------

- Phrases
- Abbreviations
- Hotkeys
- Scripts

  - Some API methods are not supported or have limitations.  See `this table`_
  for a list of which APIs work and which do not.

.. _this table: apitable.html

What Behaves Differently Under Wayland
--------------------------------------

- Using <ctrl+v>, the clipboard, and the clipboard API in scripts:

  The Wayland protocol imposes new restrictions on how applications interact with
  the clipboard.  AutoKey is able to bypass some of those restrictions using a
  utility program called wl-clipboard_.  This utility lets AutoKey read the
  contents of the clipboard and push text and images to the clipboard.  Even with
  this utility, however, Wayland still restricts AutoKey from reading content
  selected on the desktop with the mouse or keyboard.

  Practically speaking what this means is that these two clipboard API methods
  are not available under Wayland.  The rest of the API works.

  - `clipboard.fill_selection()`_
  - `clipboard.get_selection()`_

.. _clipboard.fill_selection(): https://autokey-wayland.readthedocs.io/en/latest/api/gtkclipboard.html
.. _clipboard.get_selection(): https://autokey-wayland.readthedocs.io/en/latest/api/gtkclipboard.html

What Does Not Work Under Wayland
--------------------------------

- As described above, the "clipboard" API methods will not work in scripts that
  are executed using abbreviations or hot keys.
- Sending phrases using the <ctrl-v> method will not work when using
  abbreviations or hotkeys.
- Some of the script API methods do not work under Wayland.  See `this table`_
  for a list of which APIs work and which do not.
- The "highlevel" API methods are not supported.  These were implemented in X11
  using the xautomation utility, which is not available under Wayland.
- Recording and playing back mouse movements is not supported on Wayland.  This
  was implemented in X11 using the xrecord utility, which is not available under
  Wayland.

Which Desktops Support Wayland
------------------------------

Updated: February 22, 2026

+--------------+-------------------+-----------------+
| Desktop / WM | Wayland Support   | AutoKey Support |
+==============+===================+=================+
| GNOME Shell  | ✔️  Default       | ✔️              |
+--------------+-------------------+-----------------+
| KDE Plasma   | ✔️  Stable        |                 |
+--------------+-------------------+-----------------+
| XFCE         | 🚧 Experimental   |                 |
+--------------+-------------------+-----------------+
| Cinnamon     | 🚧 Experimental   |                 |
+--------------+-------------------+-----------------+
| MATE         | 🚧 In development |                 |
+--------------+-------------------+-----------------+
| Sway         | ✔️  Native        |                 |
+--------------+-------------------+-----------------+
| River        | ✔️  Native        |                 |
+--------------+-------------------+-----------------+
| Hyprland     | ✔️  Native        |                 |
+--------------+-------------------+-----------------+
| Wayfire      | ✔️  Native        |                 |
+--------------+-------------------+-----------------+
| Weston       | ✔️  Reference     |                 |
+--------------+-------------------+-----------------+
