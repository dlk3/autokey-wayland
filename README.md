# AutoKey for Wayland

This fork of the [AutoKey](https://github.com/autokey/autokey) project enables the code that the official [AutoKey](https://github.com/autokey/autokey) project contains to support the Gnome/Wayland desktop.  In the official project, this code is not functional due to a few minor bugs and the project owners have not accepted the fixes necessary to correct this.  This fork contains those fixes, plus some additional related changes and enhancements I have made to make AutoKey function properly in the Gnome/Wayland environment.  This fork continues to support X11 desktops.

**Important** This version of AutoKey currently only works with Gnome desktops under Wayland.  Under X11, it continues to work with any desktop environment.  We hope to extend Wayland support to include other desktop environments over time.

[What Works & What Does Not](https://github.com/dlk3/autokey-wayland/wiki/What-Works-&-What-Does-Not)

Ubuntu/Debian and Fedora installation packages are available.  AutoKey also may be cloned from GitHub, configured, and run manually.

[Installation Instructions](https://github.com/dlk3/autokey-wayland/wiki/Installing-AutoKey-for-Wayland)

## Support

Read the [FAQ](https://github.com/dlk3/autokey-wayland/wiki/FAQ-%E2%80%90-Frequently-Asked-Questions) first.

The [official AutoKey wiki](http://github.com/autokey/autokey/wiki) contains a lot of useful information about how to use AutoKey, including many example scripts and the like.  Make use of it.

You may post questions or bug reports to this project's [Issues](https://github.com/dlk3/autokey-wayland/issues) tracker and I will do my best to address them.  As always, questions that could be answered by reading documentation or by using a search engine will not receive much/any attention.  Problem reports should always be accompanied by a full copy of your <code>~/.local/share/autokey/autokey.log</code> file that captures the problem while running autokey with the verbose ("-v") command line option.  See the [FAQ](https://github.com/dlk3/autokey-wayland/wiki/FAQ-%E2%80%90-Frequently-Asked-Questions#attaching-an-autokey-debug-log-to-a-problem-issues-report) for instructions.

## Project Branches

[main](https://github.com/dlk3/autokey-wayland/tree/main) - the current code
