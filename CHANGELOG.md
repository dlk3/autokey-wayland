# Changelog

See [CHANGELOG.rst](https://github.com/autokey/autokey/blob/develop/CHANGELOG.rst) for the change history of the "official" AutoKey project.

## autokey-wayland project

- Forked project from the "develop" branch of the official [autokey/autokey project on GitHub](https://github.com/autokey/autokey/tree/develop).
- Corrected minor bugs in the Wayland integration code to enable it to run.
- Modified debug logging and error messages to provide additional useful information when problems occur.
- Migrated the autokey-gnome-extension project code into this project, as opposed to maintaining it in a separate project.
- Enhanced configuration code to support more than one keyboard and mouse at a time.
- Enhanced configuration code to support the hot-plugging of USB or Bluetooth keyboards and mice.
- Created spec file and build script to support building of Fedora RPMs.
