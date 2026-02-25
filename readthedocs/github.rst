Manually Installing AutoKey for Wayland from GitHub
===================================================

It is possible to install the AutoKey for Wayland code locally and run that code in a Python virtual environment. This is useful if you are a developer who wants to work with the code, or if you're on a system for which there is no installation package available.

Some attempts to install AutoKey for Wayland using this procedure have revealed that software dependencies across different Linux distributions vary to the extent that they can break the procedure. If this happens to you, open an issue here, and I'll try to help you troubleshoot the problem. On the system where this happened to me, I was still able to successfully install AutoKey using the installation packages.

If you already have a "production" instance of AutoKey installed on your system using a distribution package, you do not need to remove it. The instance you are about to install manually will not interfere with your "production" installation, as long as you don't try to run them both at the same time. To be safe, you should back up the contents of your current AutoKey configuration directory before you start. A command like this would do the trick::

    cp -r ~/.config/autokey ~/.config/autokey-backup

If things go horribly wrong, you can always move the backup back into place and return to using your "production" instance.

After you have finished the install, see `Getting Started With AutoKey on Wayland`_ for help with issues specific to the Wayland environment that may affect you when you first start using AutoKey on Wayland.

.. _Getting Started With AutoKey on Wayland: gettingstarted.html

1) Clone the AutoKey for Wayland repository locally
---------------------------------------------------

The following commands will download the AutoKey for Wayland code into the ${HOME}/src/autokey-wayland directory on your system::

    mkdir -p ~/src
    cd ~/src
    git clone https://github.com/dlk3/autokey-wayland

If your system says that it does not have the git command, then do:

On Ubuntu::

    sudo apt install git

On Fedora::

    sudo dnf install git

2) Install system prerequisites
-------------------------------

a) Installing Ubuntu system prereqs::

    sudo apt update
    sudo apt install make build-essential libcairo2-dev python3-venv gnome-shell-extension-manager -y
    cd ~/src/autokey-wayland
    xargs -a apt-requirements.txt sudo apt install -y

b) Installing Fedora system prereqs::

    sudo dnf -y group install c-development
    sudo dnf -y install make cmake dbus-glib-devel python3-devel cairo-devel gobject-introspection-devel cairo-gobject-devel
    cd ~/src/autokey-wayland
    xargs -a rpm-requirements.txt sudo dnf -y install

3) Configure your system to run AutoKey
---------------------------------------
**NOTE:** If you are installing AutoKey just for X11 and you don't need Wayland support, you can skip all of step 3 and jump down to step 4, "Installing the AutoKey icons".

a) Install the autokey-gnome-extension\@autokey Gnome Shell extension

   Enter these three commands to build and install AutoKey's Gnome Shell extension::

      cd ~/src/autokey-wayland/autokey-gnome-extension
      make
      gnome-extensions install autokey-gnome-extension@autokey.shell-extension.zip

b) Make system configuration changes to enable the use of the uinput interface

   Copy in a new udev rules file that gives members of the "input" user group write access to the /dev/uinput kernel device::

      sudo cp ~/src/autokey-wayland/config/10-autokey.rules /etc/udev/rules.d/

c) Add your userid to the "input" user group

   Enter this command::

      sudo usermod -a -G input $(id -un)

d) Reboot

   For the previous three changes to come into effect, you must reboot::

      sudo shutdown -r now

e) Enable the Gnome Shell extension for your userid

   After you've logged back in, enter this command::

      gnome-extensions enable autokey-gnome-extension@autokey 

4) Install the AutoKey icons
----------------------------

If you have a "production" instance of AutoKey, these icons may already be installed. If you don't already have them, these commands will put them in place::

    mkdir ~/.local/share/icons   #  You may already have this directory
    cd ~/src/autokey-wayland/config
    cp -vr *.png *.svg Humanity ubuntu-mono-* ~/.local/share/icons/

5) Install AutoKey in a Python virtual environment
--------------------------------------------------

Using a virtual environment is highly recommended as doing so ensures that the modules installed to support AutoKey do not interfere with your system's regular Python environment.

1) Create the virtual environment::

    cd ~/src/autokey-wayland
    python3 -m venv --system-site-packages .venv
    source .venv/bin/activate

   The virtual environment has been created in the ~/src/autokey-wayland/.venv directory and it has been activated. Notice that your command prompt has been changed to indicate that you are now in the virtual environment.

2) Install prerequisite Python modules for AutoKey into the virtual environment::

    pip install packaging pyasyncore evdev
    pip install -r pip-requirements.txt

6) Run AutoKey from the virtual environment
-------------------------------------------

::

    cd ~/src/autokey-wayland/lib
    python3 -m autokey.gtkui -v

7) Exiting the virtual environment when you are finished with AutoKey
---------------------------------------------------------------------

After you terminate AutoKey, the virtual environment can be deactivated by entering::

    deactivate

Your command prompt will return to normal to signal that you've left the virtual environment.

8) Running AutoKey again
------------------------

Run AutoKey with these commands::

    source ~/src/autokey-wayland/.venv/bin/activate
    cd ~/src/autokey-wayland/lib
    python3 -m autokey.gtkui -v
    deactivate

You could put these commands into a startup script if you wanted to. Here's mine::

    #  Run AutoKey from source

    #  Check to see if AutoKey is already running
    if ps -ef | grep -iq "[p]ython.*autokey"; then
      echo "AutoKey is already running"
      exit 1
    fi

    source ~/src/autokey-wayland/.venv/bin/activate
    cd ~/src/autokey-wayland/lib
    python -m autokey.gtkui $@
    deactivate

Cleaning up after ourselves
---------------------------

To completely remove a manual installation of Autokey for Wayland::

    #  If you installed the AutoKey icon files in ~/.local/share/icons, then:
    find ~/.local/share/icons -iwholename \*/autokey\* -delete

    rm -fr ~/src/autokey-wayland
    gnome-extensions uninstall autokey-gnome-extension-autokey@autokey
    sudo rm /etc/udev/rules.d/10-autokey.rules
    sudo usermod -r -G input $(id -un)
    mv ~/.config/autokey-backup ~/.config/autokey
    sudo shutdown -r now

