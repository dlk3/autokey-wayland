#  Testing AutoKey on Wayland
Wayland support is limited to GNOME-based desktops.  It relies on a custom GNOME Shell extension to provide the information it needs about desktop windows.

This version of AutoKey still supports X11 desktops.  You should be able to switch between Wayland and X11 desktop environments without any problems.  AutoKey looks at the XDG_SESSION_TYPE environment variable to determine whether or not it is running in Wayland.

Basic testing of this version of AutoKey has been done on:
- Ubuntu 24.04 (GNOME Shell 46.0) - under Wayland and X11
- Fedora 40 Workstation (GNOME Shell 46.6) - under Wayland and X11 
- Fedora 41 Workstation (GNOME Shell 47.2) - under Wayland only, X11 is deprecated in this release

## 1) Clone the development version of AutoKey
```
#  Clone the "wayland" branch from my fork of the AutoKey repository
mkdir -p ~/src
cd ~/src
git clone https://github.com/dlk3/autokey --branch wayland
```
**NOTE** Assuming the pull request with my updates gets merged into the develop branch of the master AutoKey repository, once that is done the code can be cloned from that repo as well, using this command:
```
git clone https://github.com/autokey/autokey --branch develop
```
## 2a) Install Ubuntu system prereqs:
```
sudo apt update
sudo apt install make build-essential libcairo2-dev python3-venv gnome-shell-extension-manager -y
cd ~/src/autokey
xargs -a apt-requirements.txt sudo apt install -y
```
## 2b) Install Fedora system prereqs:
```
sudo dnf -y group install c-development
sudo dnf -y install git make cmake dbus-glib-devel python3-devel cairo-devel gobject-introspection-devel cairo-gobject-devel
cd ~/src/autokey
xargs -a rpm-requirements.txt sudo dnf -y install
```
## 3) Install AutoKey
**NOTE** If you only ever run under X11 and don't need Wayland support you can skip the next four steps and jump down to the "3.5 Install AutoKey in a Python virtual environment" step.
###  3.1) Install the autokey-gnome-extension GNOME Shell extension
```
cd ~/src/autokey/autokey-gnome-extension
make
gnome-extensions install autokey-gnome-extension@autokey.zip
```
###  3.2) Make system configuration changes to enable use of the uinput interface
```
#  Add a new udev rule configuration file that grants the "input" user group access to the /dev/uinput kernel device (copy these three lines together as one into a terminal window and press enter)
sudo tee /etc/udev/rules.d/10-autokey.rules > /dev/null <<EOF
KERNEL=="uinput", SUBSYSTEM=="misc", OPTIONS+="static_node=uinput", TAG+="uaccess", GROUP="input", MODE="0660"
EOF
```
### 3.3) Reboot
The GNOME Shell extension and the UDEV changes we have made require a system reboot to come into effect.
```
sudo shutdown -r now
```
### 3.4) Enable the GNOME Shell extension and add your userid to the "input" user group
Run this script:
```
~/src/autokey/autokey-user-config
```
You will be prompted to log off and log back on again after running that script.
###  3.5) Install AutoKey in a Python virtual environment
Using a virtual environment is highly recommended to ensure that the modules installed to support AutoKey do not conflict with your default Python environment.
```
#  Create the virtual environment in the ~/venv directory and activate it
python3 -m venv ~/venv
source ~/venv/bin/activate

#  Install prerequisite Python modules into the virtual environment
pip install packaging pyasyncore evdev
cd ~/src/autokey
pip install -r pip-requirements.txt
```
### 3.6) Run AutoKey
```
#  Backup your existing autokey configuration files, this new version of autokey will modify them:
cp -R ~/.config/autokey ~/.config/autokey-backup

#  Run autokey
cd ~/src/autokey/lib
python3 -m autokey.gtkui -vc
```
After AutoKey has been terminated, the Python virtual environment can be deactivated by entering the command ```deactivate``` at the command prompt, or by exiting the terminal window.

On subsequent runs, start AutoKey with these commands:
```
source ~/venv/bin/activate
cd ~/src/autokey/lib
python3 -m autokey.gtkui -v
```
**Important** When AutoKey starts, it does not open a window unless this is your very first time running AutoKey, i.e., the ```~/.config/autokey``` directory does not exist.  Instead, it places an "A" icon in the system tray through which its main window and other functions can be accessed.

If you are a GNOME desktop user, your desktop may not have a system tray and therefore it will appear that nothing happened when you started AutoKey.  To use AutoKey effectively you should install a GNOME Shell extension that adds a system tray to your desktop.  My personal favorite extension for this purpose is "AppIndicator and KStatusNotifierItem Support by 3v1n0" but there are other choices.  Ubuntu, for example, comes with the "Ubuntu Appindicators" extension already installed so this isn't a problem there.  Go to [https://extensions.gnome.org](https://extensions.gnome.org) to find, install, and manage GNOME Shell extensions on your desktop.

If you don't already have the AutoKey icons installed on your system from some prior version of AutoKey, AutoKey will show up in the system tray not as an "A" icon but as an unknown three dot icon.
Step 4 will fix that.

## 4) Installing the AutoKey icons
If you don't already have the AutoKey icons installed on your system from some prior version of AutoKey then install them:
```
mkdir ~/.local/share/icons   #  If you don't already have this directory
cd ~/src/autokey/config/
cp -vr *.png *.svg Humanity ubuntu-mono-* ~/.local/share/icons/
```
## 5) AutoKey doesn't see my keyboard/mouse when I'm on Wayland

AutoKey on Wayland tries to attach to all of the keyboards and mice attached to the system.  However, it only recognizes devices that have the word "keyboard" or "mouse" in their names so it may not have recognized your device(s).  You will get an error message from AutoKey if it can't recognize at least one keyboard and one mouse.  This section provides a more detailed explanation of the actions suggested by the error message.

To help AutoKey recognize all of the keyboards and mice that you use, you should add the names of the ones that AutoKey missed to the AutoKey configuration file to help it find them next time.

First step, you need the names of the devices you want to add.  When AutoKey is run with the "-v" option it outputs a list of all the devices it sees on the system, and the ones that it "grabbed" because it recognized them as keyboards or mice.  On my system that list looks like this:
```
2025-01-01 17:13:02,386 DEBUG - autokey.uinput_interface - The following devices are available on this system:
        Sleep Button
        Power Button
        Power Button
        Logitech K330
        Logitech ERGO M575
        PC Speaker
        Eee PC WMI hotkeys
        HDA NVidia HDMI/DP,pcm=3
        HDA NVidia HDMI/DP,pcm=7
        HDA NVidia HDMI/DP,pcm=8
        HDA NVidia HDMI/DP,pcm=9
        HDA Intel PCH Rear Mic
        HDA Intel PCH Front Mic
        HDA Intel PCH Line
        HDA Intel PCH Line Out Front
        HDA Intel PCH Line Out Surround
        HDA Intel PCH Line Out CLFE
        HDA Intel PCH Front Headphone
        Logitech K400
2025-01-01 17:13:02,386 DEBUG - autokey.uinput_interface - I grabbed these devices from that list: 
```
In my case, none of my devices have the words "keyboard" or "mouse" in their names so AutoKey wasn't able to recognize and didn't grab anything.  I got an error message saying that AutoKey couldn't find a keyboard device on my system.

To fix this I will update my AutoKey configuration file with the names of the keyboards and mice that AutoKey missed.

 1. I edit ~/.config/autokey/autokey.json and find these elements in the JSON object:

        "keyboard": null,
        "mouse": null,

 2. I add the names of my unrecognized keyboard and mouse devices.  In my case I have two keyboards so those are added as a list of names in the ```[ "name1", "name2" ]``` format.  I only use one mouse so its name can be entered as a single string.

        "keyboard": [
            "Logitech K330",
            "Logitech K400"
        ],
        "mouse": "Logitech ERGO M575",

Pay attention to where you put commas in JSON files.  JSON is very picky about that.

The Logitech K400 is a USB keyboard that I don't always have attached to the system, but I include it here so that AutoKey will recognize it when I do plug it in.  AutoKey can recognize new devices when they are plugged into a running system provided it knows their names, or their names have the words "keyboard" or "mouse" in them, same as before.

Now, when I restart AutoKey I see this in the log:

    2025-01-01 17:15:27,125 DEBUG - autokey.uinput_interface - I grabbed these devices from that list: 
            Logitech K330
            Logitech K400
            Logitech ERGO M575

AutoKey has recognized and "grabbed" all my input devices.
## 6) Some of my hotkey definitions changed and I didn't do it
This version of AutoKey works under both X11 and Wayland.  If you switch back and forth between these two environments, the names used for some of the modifier keys used in hotkey combinations can change and this can mess with your hotkey definitions.  This will eventually get fixed but it won't be a trivial effort.  For now the assumption is that most people will stay in either the X11 or Wayland environments and won't switch back and forth, making this a low-priority issue.  If that's an incorrect assumption, let us know with [a bug report](https://github.com/autokey/autokey/issues/new/choose).

## 7) Cleaning up after ourselves
To completely remove the test version of Autokey:
```
#  If you installed the AutoKey icon files in ~/.local/share/icons, then:
find ~/.local/share/icons -iwholename \*/autokey\* -delete

rm -fr ~/src/autokey
rm -fr ~/venv
gnome-extensions disable autokey-gnome-extension-autokey@autokey
gnome-extensions uninstall autokey-gnome-extension-autokey@autokey
sudo rm /etc/udev/rules.d/10-autokey.rules
sudo usermod -r -G input $USER
mv ~/.config/autokey-backup ~/.config/autokey
sudo shutdown -r now
```
