#  Check to make sure that the uinput device and Gnome Shell extension
#  that Aukey for Wayland needs are in place.  If, not, take steps to
#  make it so.

import dbus
import grp
import os
import subprocess

try:
    logger = __import__("autokey.logger").logger.get_logger(__name__)
except Exception:
    #  For standalone testing
    import logging
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

def waylandChecks():

    #  We only do this stuff when running under Wayland
    if os.environ['XDG_SESSION_TYPE'] != "wayland":
        return True

    #  Do we show popup message?
    show_popup = False

    #  Check the Gnome Shell extension
    ext_id = 'autokey-gnome-extension@autokey'
    try:
        proc = subprocess.run(f'gnome-extensions info {ext_id}', shell=True, capture_output=True, check=True)
        if 'Enabled: Yes' in proc.stdout.decode('utf-8'):
            logger.debug('waylandChecks() found the AutoKey Gnome Shell extension')
        else:
            logger.debug('waylandChecks() found the AutoKey Gnome Shell extension but it is disabled.  Attempting to enable it.')
            subprocess.run(f'gnome-extensions enable {ext_id}', shell=True, capture_output=True, check=True)
    except Exception:
        logger.critical('waylandChecks() did not find the AutoKey Gnome Shell extension, displaying popup')
        show_popup = True

    #  Check if user is in the user group
    group = 'input'
    user = os.getlogin()
    input_group = grp.getgrnam(group)
    if user in input_group.gr_mem or os.geteuid() == 0:
        logger.debug(f'waylandChecks() found the "{user}" userid in the "{group}" user group.')
    else:
        logger.critical(f'waylandChecks() did not find the "{user}" userid in the "{group}" user group, displaying popup.')
        show_popup = True

    if show_popup:
        message = f'Your user id is not configured to run AutoKey under Waland.  If this is your first time running AutoKey, try rebooting your system and starting AutoKey again.  Otherwise, try entering these two commands, then rebooting:\n\n<b>sudo usermod -a -G "{group}" "{user}"\n\ngnome-extensions install --force /usr/share/autokey/gnome-shell-extension/autokey-gnome-extension@autokey.shell-extension.zip</b>'
        title = 'AutoKey System Configuration Needed'
        subprocess.run(f"zenity --error --title='{title}' --text='{message}'", shell=True, check=True)
        return False

    return True

if __name__ == '__main__':
    if not waylandChecks():
        print('waylandChecks() returned False')
