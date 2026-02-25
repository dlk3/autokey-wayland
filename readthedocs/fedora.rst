Installing AutoKey For Wayland on Fedora
========================================

AutoKey packages are available in a COPR repository for currently supported versions of Fedora.

Enable my COPR repository on your system::

    sudo dnf copr enable dlk/autokey

Install AutoKey::

    sudo dnf install autokey-gtk

If you have a prior version of AutoKey installed, this will upgrade/replace it.

See `Getting Started With AutoKey on Wayland`_ for help with issues specific to the Wayland environment that may affect you when you start using AutoKey on Wayland.

.. _Getting Started With AutoKey on Wayland: gettingstarted.html
