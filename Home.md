# AutoKey for Wayland

This fork of the [AutoKey](https://github.com/autokey/autokey) project enables the code that the official [AutoKey](https://github.com/autokey/autokey) project contains to support the Gnome/Wayland desktop, but which has not (yet) been enabled.  In the official project, this code is not functional due to a few minor bugs and the project owners have not accepted the fixes necessary to correct this.

This fork contains those fixes, plus some additional related changes and enhancements I have made to make AutoKey function properly in the Gnome/Wayland environment.

## Installation

### Fedora Packages

Packages for autokey-wayland are available in a COPR repository for currently supported versions of Fedora. 

1. Uninstall any existing AutoKey packages first.<br><br><code>$ sudo dnf uninstall autokey*</code><br><br>Your existing AutoKey configuration will be preserved.  If you want to be extra careful, make a backup copy of everything in your <code>~/.config/autokey</code> directory before uninstalling.

### Ubuntu/Debian Packages

Packages for Debian-based distributions like Ubuntu are available in a PPA repository.

1. Uninstall any existing AutoKey packages first.<br><br><code>$ sudo apt remove autokey*</code><br><br>Your existing AutoKey configuration will be preserved.  If you want to be extra careful, make a backup copy of everything in your <code>~/.config/autokey</code> directory before uninstalling.

### Installing manually from GitHub

1. You do not need to uninstall existing versions of AutoKey before doing a manual install.

## Support

Read the [FAQ](https://github.com/dlk3/autokey-wayland/wiki/FAQ-%E2%80%90-Frequently-Asked-Questions) first.

The [official AutoKey wiki](http://github.com/autokey/autokey/wiki) contains a lot of useful information about how to use AutoKey, including many example scripts and the like.  Make use of it.

You may post questions or bug reports to this project's [Issues](https://github.com/dlk3/autokey-wayland/issues) tracker and I will do my best to address them.  As always, questions that could be answered by reading documentation or by using a search engine will not receive much/any attention.  Problem reports should always be accompanied by a full copy of your <code>~/.local/share/autokey/autokey.log</code> file that captures the problem while running autokey with the verbose ("-v") command line option.

## Project Branches

[main](https://github.com/dlk3/autokey-wayland/tree/main) - the current release of the code
