What Works & What Does Not
==========================

Wayland is designed to close the X11 security holes that allowed one application to spy on another through the desktop.  Since AutoKey depended on these security holes to do what it does, AutoKey has some limitations when running under Wayland.

What Works Under Wayland
------------------------

- Phrases
- Abbreviations
- Hotkeys
- Scripts

  - Some API methods are not supported or have limitations.  See `this table`_ for a list of which APIs work and which do not.

.. _this table: apitable.html

What Behaves Differently Under Wayland
--------------------------------------

- Using <ctrl+v>, the clipboard, and the clipboard API in scripts:
   
  Wayland security prevents any application that does not have focus on the desktop from accessing the clipboard.  For hot keys and abbreviations, AutoKey functions as a background application.  Wayland will not allow it to push content onto the clipboard, so sending text and images via the clipboard won't work there.  If you put those same functions into AutoKey's notification menu, however, they will work just fine.  When the notification menu is open, AutoKey now has a window that has focus on the desktop, and Wayland will allow it to interact with the clipboard.


What Does Not Work Under Wayland
--------------------------------

- As described above, the clipboard API methods will not work in scripts that are executed using abbreviations or hot keys.
- Sending phrases using the <ctrl-v> method will not work when using abbreviations or hotkeys.
- Some of the script API methods do not work under Wayland.  See `this table`_ for a list of which APIs work and which do not.

Which Desktops Support Wayland
------------------------------

Updated: February 22, 2025

+--------------+-------------------+-----------------+
| Desktop / WM | Wayland Support   | AutoKey Support |
+==============+===================+=================+
| GNOME Shell  | ✔️ Default        | ✔️              |
+--------------+-------------------+-----------------+
| KDE Plasma   | ✔️ Stable         |                 |
+--------------+-------------------+-----------------+
| XFCE         | 🚧 Experimental   |                 |
+--------------+-------------------+-----------------+
| Cinnamon     | 🚧 Experimental   |                 |
+--------------+-------------------+-----------------+
| MATE         | 🚧 In development |                 |
+--------------+-------------------+-----------------+
| Sway         | ✔️ Native         |                 |
+--------------+-------------------+-----------------+
| River        | ✔️ Native         |                 |
+--------------+-------------------+-----------------+
| Hyprland     | ✔️ Native         |                 |
+--------------+-------------------+-----------------+
| Wayfire      | ✔️ Native         |                 |
+--------------+-------------------+-----------------+
| Weston       | ✔️ Reference      |                 |
+--------------+-------------------+-----------------+
