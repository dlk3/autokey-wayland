#  Copyright (C) 2026  David King <dave@daveking.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License,
#  version 2, as published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License,
#  version 2, along with this program; if not, see 
#  <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.
#
#####################################################################

#  pytest test case

#  Test to make sure that the various changelogs have an entry for the version
#  about to built.

import os
import sys

PROJECT_PATH = f"{os.environ['HOME']}/src/autokey-wayland"

def test_changefile_entries():
    import subprocess

    #  Get the version from autokey.common
    sys.path.insert(0, PROJECT_PATH + '/lib')
    from autokey import common

    #  Check for an entry in the CHANGELOG.md file
    found = False
    with open(f'{PROJECT_PATH}/CHANGELOG.md', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.startswith(f'## AutoKey {common.VERSION}'):
               found = True
               break
    assert found

    #  Check for an entry in the debian/changelog file
    found = False
    with open(f'{PROJECT_PATH}/debian/changelog', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.startswith(f'autokey ({common.VERSION})'):
               found = True
               break
    assert found

    #  Check for an entry in the fedora/spec file
    found = False
    with open(f'{PROJECT_PATH}/fedora/autokey.spec', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if f'> - {common.VERSION}-' in row:
               found = True
               break
    assert found
