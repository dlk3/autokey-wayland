# Changelog

## AutoKey 0.97.3

### New Features
  * The clipboard API methods have now been implemented using the
    [wl-clipboard](https://github.com/bugaevc/wl-clipboard) utility.  They
    should all work as expected now.

  * A new sample script demonstrating how to send strings containing Unicode
    via the keyboard using the ```keyboard.send_keys()``` method.  This will
    only be created on new installs where no ```~/.config/autokey``` directory
    exists.  Others can copy the script source from [here](https://github.com/dlk3/autokey-wayland/blob/main/lib/autokey/configmanager/predefined_user_scripts/unicode_strings_in_scripts.pyi). 

    This script works for me in both an X11 and a Wayland environment.  I'll
    be interested to hear what environment you are using if it doesn't work for
    you.  Please don't be shy about opening an [issue](https://github.com/dlk3/autokey-wayland/issues).

    I already have #22 open to try to make the Wayland-side code simpler than
    it is.
    
### Bug Fixes

  * The scripting API documentation has been regenerated for AutoKey for Wayland.
    There's [a link](https://html-preview.github.io/?url=https://raw.githubusercontent.com/dlk3/autokey-wayland/main/doc/scripting/index.html) 
    to it from the [wiki](https://github.com/dlk3/autokey-wayland/wiki).  
    It needs some love to make it a bit prettier but at least it provides access
    to updated docs that conform to the latest version of the source.

 -- David King <dave@daveking.com>  Fri, 20 Feb 2026 21:11:00 -050

## AutoKey 0.97.2

### New Features

  * Added a "delay" option for the keyboard.send_keys() API method that makes
    AutoKey type more slowly.  For the moment, this only works on Wayland.
    It will be ignored when running on an X11 system.  I hope to change that 
    soon.  

    Usage:

    ```keyboard.send_keys('type this string', delay=50)``` 

    The ```delay=50``` will cause there to be a 50 microsecond delay between 
    each character in the string as AutoKey types it out.  I have found this 
    useful when sending Unicode characters using the keyboard, when typing too 
    quickly can overwhelm the system, resulting in garbled output: 

    ```keyboard.send_keys('<ctrl>+<shift>+u1f44c ', delay=50)```

### Bug Fixes

  * Fix errors in post-install and pre-remove package scriptlets
  * Handle non-fatal exception seen during first-time use on Debian 13.3 test
    system - #16
  * Change the sample phrases and scripts so that they do not rely on the
    clipboard API which does not work on Wayland systems in backgrounded apps 
    - #17, #18
  
 -- David King <dave@daveking.com>  Fri, 20 Feb 2026 21:11:00 -050

## AutoKey 0.97.1

This project was forked from the "develop" branch of the "official" 
[autokey/autokey](https://github.com/autokey/autokey) project on GitHub.

### New Features
  
  * AutoKey now supports Gnome/Wayland desktop environments in addition to 
    X11 environments.
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
