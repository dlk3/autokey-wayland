Additional Technical Detail on Wayland, X11, and AutoKey
========================================================

One of the major design points for the Wayland_ desktop protocol is providing
a more secure platform for applications running on a shared desktop.
It provides additional security over what had previously been available in
the X Window environment.  To create a more secure environment, Wayland
imposes new restrictions on how applications can interact through
the desktop.

The Wayland_ protocol's restrictions prevent AutoKey from interacting
with the keyboard, mouse, clipboard, and desktop windows as freely as it did
under X11.  These restrictions also make the utilities AutoKey leveraged under X11
unavailable, like xrecord and xautomation.  In order to provide some level of
functionality, the AutoKey developers had to come up with alternative means of
integrating with the system.

Keyboard and Mouse Integration
------------------------------

For keyboard and mouse integration, AutoKey for Wayland makes use of the
"evdev_" event interface in the Linux kernel.  AutoKey interacts with "evdev"
through the "/dev/uinput" device.  By default, access to the "/dev/uinput"
device is restricted to the root user.  The AutoKey user must be granted
read/write access to the "/dev/uinput" device.  During AutoKey installation,
a new UDEV_ rule is installed, which changes the permissions for the
/dev/uinput device to allow access for the members of the "input" user
group.  The AutoKey user is added to that group.

Manipulating Desktop Windows
----------------------------

The Wayland protocol does not allow applications to interact with desktop
windows as X11 did.  There are no Wayland facilities that allow an
application to move, resize, close, or otherwise interact with a window.  Some
DTE (desktop environment) software, like GNOME or KDE, provides an API that
will return information about windows on the desktop.  GNOME, for example,
makes this information available to its desktop extensions.  AutoKey for
Wayland, therefore, installs an AutoKey-specific GNOME Shell extension and uses
its capabilities to implement a limited windows API.  A similar solution may
be available for KDE, so AutoKey may add support for KDE in the future.

Clipboard Integration
---------------------

The Wayland protocol imposes new restrictions on how applications interact with
the clipboard.  AutoKey is able to bypass some of those restrictions using a
utility program called wl-clipboard_.  This utility lets AutoKey read the
contents of the clipboard and push text and images to the clipboard.  Even with
this utility, however, Wayland still restricts AutoKey from reading content
selected on the desktop with the mouse or keyboard.

.. _Wayland: https://en.wikipedia.org/wiki/Wayland_(protocol)
.. _evdev: https://en.wikipedia.org/wiki/Evdev
.. _UDEV: https://www.man7.org/linux/man-pages/man7/udev.7.html
.. _wl-clipboard: https://github.com/bugaevc/wl-clipboard
