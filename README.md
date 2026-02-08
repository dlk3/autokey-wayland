# AutoKey for Wayland

This fork of the [AutoKey](https://github.com/autokey/autokey) project enables the code that the official [AutoKey](https://github.com/autokey/autokey) project contains to support the Gnome/Wayland desktop.  In the official project, this code is not functional due to a few minor bugs and the project owners have not accepted the fixes necessary to correct this.  This fork contains those fixes, plus some additional related changes and enhancements I have made to make AutoKey function properly in the Gnome/Wayland environment.

## Installation

### Fedora Packages

AutoKey packages are available in a COPR repository for currently supported versions of Fedora. 

Enable my COPR repository on your system:

    sudo dnf copr enable dlk/autokey
        
Install AutoKey:

    sudo dnf install autokey-gtk

If you have the "official" version of AutoKey installed this will upgrade/replace it.

### Ubuntu/Debian Packages

Enable my PPA on your system:

     curl -s --compressed "https://daveking.com/autokey-wayland-ppa/autokey-wayland-ppa.gpg" | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/autokey-wayland-ppa.gpg >/dev/null
     sudo curl -s --compressed -o /etc/apt/sources.list.d/autokey-wayland-ppa.list "https://daveking.com/autokey-wayland-ppa/autokey-wayland-ppa.list"

Install AutoKey:

     sudo apt update
     sudo apt install autokey-gtk

If you have the "official" version of AutoKey installed this will upgrade/replace it.

### Installing manually from GitHub

You can clone this GitHub repository and run AutoKey from within it using a Python virtual environment.  See the [Installing AutoKey for Wayland](https://github.com/dlk3/autokey-wayland/wiki/Installing-AutoKey-for-Wayland) instructions page for details.  This is a good option to choose if you intend to do your own hacking on AutoKey.

## Support

Read the [FAQ](https://github.com/dlk3/autokey-wayland/wiki/FAQ-%E2%80%90-Frequently-Asked-Questions) first.

The [official AutoKey wiki](http://github.com/autokey/autokey/wiki) contains a lot of useful information about how to use AutoKey, including many example scripts and the like.  Make use of it.

You may post questions or bug reports to this project's [Issues](https://github.com/dlk3/autokey-wayland/issues) tracker and I will do my best to address them.  As always, questions that could be answered by reading documentation or by using a search engine will not receive much/any attention.  Problem reports should always be accompanied by a full copy of your <code>~/.local/share/autokey/autokey.log</code> file that captures the problem while running autokey with the verbose ("-v") command line option.  See the [FAQ](https://github.com/dlk3/autokey-wayland/wiki/FAQ-%E2%80%90-Frequently-Asked-Questions#attaching-an-autokey-debug-log-to-a-problem-issues-report) for instructions.

## Project Branches

[main](https://github.com/dlk3/autokey-wayland/tree/main) - the current release of the code
