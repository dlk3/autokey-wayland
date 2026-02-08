# Changelog

## autokey (0.97.1) noble; urgency=medium

### Features
  
  * AutoKey for Wayland

    * Forked project from the "develop" branch of the official autokey/autokey 
      project on GitHub.
    * Corrected minor bugs in the Wayland integration code to enable it to run.
    * Enhanced configuration code to support more than one keyboard and mouse at 
      a time.
    * Enhanced configuration code to support the hot-plugging of USB or Bluetooth 
      keyboards and mice.

  * Modified debug logging and error messages to provide additional useful 
    information when problems occur.

### Packaging

  * Migrated the autokey-gnome-extension project code into this project, as 
    opposed to maintaining it in a separate project.
  * Created spec file and build script to support building of Fedora RPMs.
  * Updated Debian build scripts.

 -- David King <dave@daveking.com>  Wed, 04 Feb 2026 20:49:49 -050

## Older Changes

See [CHANGELOG.rst](https://github.com/autokey/autokey/blob/develop/CHANGELOG.rst) for the change history of the "official" AutoKey project.