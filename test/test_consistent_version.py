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

#  Test to make sure that the version number is consistent across the various
#  files in this project

def test_consistent_version():
    import os
    import sys
    import subprocess

    PROJECT_PATH = f"{os.environ['HOME']}/src/autokey-wayland"

    #  Get the git tag for this branch
    env = os.environ.copy()
    env["GIT_DIR"] = f"{PROJECT_PATH}/.git"
    cmd = "git describe --tags $(git rev-list --tags='v[0-9].[0-9]*' --max-count=1)"
    proc = subprocess.run(cmd, capture_output=True, env=env, shell=True)
    version = proc.stdout.decode('utf-8').strip()
    assert version

    #  Check the version in the debian/mkpackage file
    with open(f'{PROJECT_PATH}/debian/mkpackage', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.startswith('VERSION='):
               mkpackage_version = row.split('=')[1]
               mkpackage_version = mkpackage_version.strip("\n'")
               break
    assert version == mkpackage_version

    #  Check the version in the fedora/autokey.spec file
    with open(f'{PROJECT_PATH}/fedora/autokey.spec', 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.startswith('Version:'):
               specfile_version = row.split(':')[1]
               specfile_version = specfile_version.strip("\n\tv")
               break
    assert version.lstrip('v') == specfile_version
              
    #  Check the version variable used inside AutoKey
    sys.path.insert(0, PROJECT_PATH + '/lib')
    from autokey import common
    assert version.lstrip('v') == common.VERSION
