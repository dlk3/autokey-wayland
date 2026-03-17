===================================
Contributing to AutoKey for Wayland
===================================

Contributions to this project are more than welcome.  The preferred method for contributing something to the project is through `GitHub's Pull Request process`_.  Especially in current times, when we're all being inundated with AI slop, it's wise to introduce yourself and discuss your ideas with me before submitting something.  Open a draft PR or an Issue_, describing what you have in mind.  It will help things flow smoothly and, if I can give you any guidance I think might help, I will.

.. _Issue: https://github.com/dlk3/autokey-wayland/issues
.. _GitHub's Pull Request process: https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request-from-github-desktop#creating-a-pull-request

---------
Licensing
---------

AutoKey for Wayland uses the `General Public License v3.0`_.  Your contributions should conform to that license.

.. _General Public License v3.0: https://www.gnu.org/licenses/gpl-3.0.en.html

--------------------
Program Architecture
--------------------

There are two entry points into AutoKey, ``autokey-gtk`` and ``autokey-qt``.  The user selects
which of these to run based on their preferred environment.  The source for each of these is in
``lib/autokey/gtkapp.py`` and ``lib/autokey/qtapp.py`` respectively.  Each of these implements
``AutokeyApplication`` using the appropriate UI components, in ``lib/autokey/gtkui`` and 
``lib/autokey/qtui``.

Those apps pass execution to ``lib/autokey/autokey_app.py``.  It sets up the ``IoMediator``, ``ScriptRunner``, and ``PhraseRunner`` services.  The IoMediator examines the run-time
environment and selects the appropriate system integration components for X11 or Wayland
respectively.  With Wayland, much of the desktop integration is accomplished by interacting with
the desktop itself, i.e., GNOME/Mutter or KDE/Kwin.  Keyboard and mouse integration is done through the kernel's input event interface and evdev_.  A list of some of the AutoKey for Wayland modules involved follows.  This list is probably not complete but it should get you started.

.. _evdev: https://pypi.org/project/evdev/

X11-specific Components
-----------------------

- ``lib/autokey/interface.py``
- ``lib/autokey/iomediator/\*``
- ``lib/autokey/scripting/clipboard_gtk.py``
- ``lib/autokey/scripting/clipboard_qt.py``

Wayland-specific Components
---------------------------

- ``lib/autokey/scripting/clipboard_wayland.py``
- ``lib/autokey/uinput_interface.py``
- ``lib/autokey/wayland_checks.py``

Wayland/GNOME-specific components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``lib/autokey/gnome_interface.py``
- ``lib/autokey/scripting/window_gnome.py``

Wayland/KDE-specific components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``lib/autokey/kde_interface.py``
- ``lib/autokey/scripting/window_kde.py``