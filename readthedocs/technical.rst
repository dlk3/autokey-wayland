Implementing AutoKey for Wayland
================================

The Wayland protocol's restrictions prevent AutoKey from freely interacting 
with the keyboard, mouse. clipboard and desktop windows as freely as it did 
under X11.  These restrictions also make utilities AutoKey leveraged under X11 
unavailable, like xrecord and xautomation.  In order to provide some level of 
functionality, the AutoKey developers had to come up with alternative means of 
integrating with the system.

For keyboard and mouse inegration, AutoKey for Wayland makes use of the 
"evdev_" event interface in the Linux kernel.  AutoKey interacts with "evdev" 
throuh the "/dev/uinput" device.  The AutoKey user must be granted read/write 
access to the "/dev/uinput" device to allow this.  By default, access to the 
"/dev/uinput" device is restricted to the root user.  During AutoKey 
installation, a new UDEV_ rule is installed which changes the permissions for 
the /dev/uinput device to allow access for the members of the "input" user 
group.  The AutoKey user is added to that group.

The Wayland protocol does not allow applications to interact with desktop 
windows like X11 did.  There are no Wayland facilities that allow an 
application to move, resize, close, or otherwise interact with a window.  Some 
DTE (desktop environment) software, like GNOME or KDE, provides an API which 
will return information about windows on the desktop.  GNOME, for example, 
makes this information available to its desktop extensions.  AutoKey for 
Wayland therefore installs an AutoKey-specific GNOME Shell extension and uses 
its capabilities to implement a limited windows API.  A simillar solution may 
be available for KDE so AutoKey may add support for KDE in the future.

The Wayland protocol imposes new restrictions on how applications interact with 
the clipboard.  Under Wayland, only applications that have a window in focus on 
the desktop (currently active, front and center) can read or write to the 
clipboard.  A program like AutoKey, which spends most of its time running in 
the background, is not permitted access to the clipboard.  AutoKey users can 
avoid this restriction by always running their clipboard-dependent actions from 
AutoKey's pop-up task bar menu, what AutoKey calls its notifications menu.  If 
the phrases and scripts that use the clipboard are executed from the 
notification menu, then they are running from a window that has focus on the 
desktop and Wayland will permit them to access the clipboard.

When AutoKey does not have focus, clipboard actions will fail silently. AutoKey 
can still send paste commands (<ctrl>+v) to the desktop through the keyboard 
interface, but it cannot pre-load the clipboard with content beforehand like it 
can under X11.  The results of a paste keypress are therefore totally 
unpredictable.  It depends on what content is in the clipboard, placed there 
previously by other programs.

The clipboard restriction extends to selected text on the desktop.  AutoKey 
cannot read this text with it is the background.

.. _evdev: https://en.wikipedia.org/wiki/Evdev
.. _UDEV: https://www.man7.org/linux/man-pages/man7/udev.7.html
