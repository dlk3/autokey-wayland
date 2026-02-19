# Changelog

## AutoKey 0.97.2

### Bug Fixes

  * Fix errors in post-install and pre-remove package scriptlets 
  
## AutoKey 0.97.1

### Features
  
  * AutoKey now supports Gnome/Wayland desktop environments in addition to 
    X11 environments.
  * This project was forked from the "develop" branch of the "official" 
    [autokey/autokey](https://github.com/autokey/autokey) project on GitHub.
  * Corrected minor bugs in AutoKey's Wayland integration code.
  * Enhanced error messages in the Wayland integration to make them easier to 
    understand.
  * Added support for more than one keyboard and mouse at a time when 
    running in a Wayland environment.
  * Added support for the hot-plugging of USB or Bluetooth keyboards and mice.

### Packaging

  * Migrated the autokey-gnome-extension project code into this project, as 
    opposed to maintaining it in a separate project.
  * Created spec file and build script to support building of Fedora RPMs.
  * Modified the Debian and Fedora packages to include scriptlets that will
    properly configure the system so that AutoKey can function in a Wayland
    environment.
  * Added Debian package builds and a PPA repository.

 -- David King <dave@daveking.com>  Wed, 04 Feb 2026 20:49:49 -050

## Older Changes

See [CHANGELOG.HISTORY.rst](https://github.com/dlk3/autokey-wayland/blob/main/CHANGELOG.HISTORY.rst) for the change history of the "official" AutoKey project.
