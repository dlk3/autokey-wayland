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

What Does Not Work Under Wayland
--------------------------------

- There are two scripting API window methods that do not work in Wayland, 
  window.activate() and window.set_property().  See the `this table`_ for exact 
  details on which scripting API methods work under Wayland and which ones don't.
- The "highlevel" API methods are not supported.  These were implemented in X11
  using the xautomation utility, which is not available under Wayland.
- Recording and playing back mouse movements is not supported on Wayland.  This
  was implemented in X11 using the xrecord utility, which is not available under
  Wayland.

.. _this table: apitable.html

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
