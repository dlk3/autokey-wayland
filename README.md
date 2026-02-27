# AutoKey for Wayland (and X11, too)

This fork of the [AutoKey](https://github.com/autokey/autokey) project enables 
the unreleased code that the "develop" branch of the official 
[AutoKey](https://github.com/autokey/autokey) project contains to support the 
Gnome/Wayland desktop.  This fork contains fixes, plus additional changes and 
enhancements, to make AutoKey function properly in both the X11 and 
Gnome/Wayland environments.  

**Important:** This version of AutoKey currently only works with Gnome desktops 
under Wayland.  Under X11, it continues to work with any desktop environment. 
I hope to extend Wayland support to KDE shortly, and to other desktop environments 
in the future.

## Project Documentation

The [project documentation](https://autokey-wayland.readthedocs.io/en/latest/) 
web site includes information on:

* [What Works & What Does Not](https://autokey-wayland.readthedocs.io/en/latest/whatworks.html)
* [Installation Instructions](https://autokey-wayland.readthedocs.io/en/latest/installation.html)

Ubuntu/Debian and Fedora installation packages are available.  The AutoKey for 
Wayland code may also be cloned from GitHub, configured, and run manually on any
system.

## Support

Read the 
[Troubleshooting](https://autokey-wayland.readthedocs.io/en/latest/troubleshoot.html) 
section of the documentation website.

The [official AutoKey wiki](http://github.com/autokey/autokey/wiki) contains a 
lot of useful information about how to use AutoKey, including many example 
scripts and the like.  Make use of it.

You may post questions or bug reports to this project's 
[Issues](https://github.com/dlk3/autokey-wayland/issues) tracker, and I will do 
my best to address them.  As always, questions that could be answered by 
reading documentation or by using a search engine will not receive much/any 
attention.  Problem reports should always be accompanied by a full copy of your 
<code>~/.local/share/autokey/autokey.log</code> file that captures the problem 
while running autokey with the verbose ("-v") command line option.  See the 
[debug log](https://autokey-wayland.readthedocs.io/en/latest/debuglog.html) section 
of the documentation for instructions.

## Project Branches

[main](https://github.com/dlk3/autokey-wayland/tree/main) - the current development code.

For more stable code, see the [Releases](https://github.com/dlk3/autokey-wayland/releases).
