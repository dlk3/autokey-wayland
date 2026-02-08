# Ubuntu

There are two different scripts:

    debian/build.sh  - Builds the AutoKey debs on an Ubuntu system
    debian/mkpackage - Builds the AutoKey debs by running debian/build.sh in an  
                       Ubuntu container.  It will also send the debs to my PPA.
                       I made this so that I could do builds from my Fedora 
		               workstation without restorting to an Ubuntu KVM.

# Fedora

The <code>fedora/mkpackage</code> script builds a source RPM and sends it to COPR to be built.

# Common Preparation

- Update debian/changelog and copy text over into CHANGELOG.md and fedora/autokey.spec
- Update version number in:
  - PKG-INFO
  - lib/autokey/common.py
  - fedora/autokey.spec
- git tag $VERSION
- git commit -a -m "a comment"
- git push

# Starting the Ubuntu Build

## To build Ubuntu debs on a Fedora workstation:

Edit <code>debian/mkpackage</code> and make sure it's pointing at the right branch of the repo.  This build pulls its source from git, so make sure you've done your commits and pushes.

    cd ~/src/autokey-wayland/debian
    ./mkpackage

On Fedora, the output debs will be rsynced to my PPA server, unless the "-t" option is specified.  With "-t" they will be written into ${HOME}/Downloads instead.

## To build Ubuntu debs on an Ubuntu workstation:

This build uses local source, so be sure you're in the right branch with the right changes.

    cd ~/src/autokey-wayland
    debian/build.sh

On Ubuntu, the output debs will be written to ~/src

# Starting the Fedora Build

## To build Fedora RPMs on a Fedora Workstation:

This build uses local source, so be sure you're in the right branch with the right changes.

    cd ~/src/autopkey-wayland/fedora
    ./mkpackage

A SRPM package will be built locally and then forwarded to COPR where the actual RPM builds will be done.  The SRPM, SPEC and SOURCE files will all be left in the local ${HOME}/rpmbuild directory tree.
