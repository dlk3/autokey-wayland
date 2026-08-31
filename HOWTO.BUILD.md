# Fedora

The <code>fedora/mkpackage</code> script builds a source RPM and sends it to COPR to be built.

# Ubuntu

There are three scripts:

    debian/build.sh   - Builds the AutoKey debs on an Ubuntu system
    debian/mkpackage  - Builds the AutoKey debs by running debian/build.sh in an  
                        Ubuntu container.  It will also send the debs to my PPA.
                        I made this so that I could do builds from my Fedora 
		                workstation without resorting to an Ubuntu KVM.
    debian/update-ppa - Updates the PPA with the ```~/Downloads/autokey*.deb``` 
                        files produced by the mkpackage script
# Preparation

- Update debian/changelog and copy text over into CHANGELOG.md and fedora/autokey.spec
- Update AutoKey version number in:
  - lib/autokey/common.py
  - fedora/autokey.spec
- git tag v$VERSION
- pytest ~/src/autokey-wayland
- git commit -a -m "a comment"
- git push

# Do the Fedora Build

## To build Fedora RPMs on a Fedora Workstation:

This build uses local source, so be sure you're in the right branch with the right changes.

    cd ~/src/autopkey-wayland/fedora
    ./mkpackage

A SRPM package will be built locally and then forwarded to COPR where the actual RPM builds will be done.  The SRPM, SPEC and SOURCE files will all be left in the local ${HOME}/rpmbuild directory tree.

# Do the Ubuntu Build

## To build Ubuntu debs on a Fedora workstation:

This build uses the code from the GitHub repo.  By default it uses the "main" branch and updates my PPA - daveking.com:/opt/autokey-wayland-ppa, but, if the -t option is used, it uses the code in the "devel" branch and publishes the results to the test PPA - daveking.com:/opt/autokey-wayland-ppa-testing.

    cd ~/src/autokey-wayland/debian
    ./mkpackage -t

## To build Ubuntu debs on an Ubuntu workstation:

This build uses local source, so be sure you're in the right branch with the right changes.

    cd ~/src/autokey-wayland
    debian/build.sh

On Ubuntu, the output debs will be written to ~/src

