Installing AutoKey for Wayland on Debian/Ubuntu
===============================================

AutoKey packages are available in a PPA (Personal Package Archive) repository that I host.

Enable my PPA on your system::

    curl -s --compressed "https://daveking.com/autokey-wayland-ppa/autokey-wayland-ppa.gpg" | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/autokey-wayland-ppa.gpg >/dev/null
    sudo curl -s --compressed -o /etc/apt/sources.list.d/autokey-wayland-ppa.list "https://daveking.com/autokey-wayland-ppa/autokey-wayland-ppa.list"

Install AutoKey::

    sudo apt update
    sudo apt install autokey-gtk

If you have the "official" version of AutoKey installed this will upgrade/replace it.

See `Getting Started With AutoKey on Wayland`_ for help with issues specific to the Wayland environment that may affect you when you start using AutoKey on Wayland.

.. _Getting Started With AutoKey on Wayland: gettingstarted.html
