import os

#  Demonstrating how to output a string containing a Unicode character in 
#  Wayland and X11 environments, because it depends ...

#  If the script is running in a Wayland environment ...
if os.environ['XDG_SESSION_TYPE'] == 'wayland':

    # then it can output a string containing a Unicode character like this:
    character = '🥷'
    escape_code = character.encode('unicode_escape').decode('utf-8').lstrip('\\U0')
    keyboard.send_keys(f'This is the "ninja" character: <ctrl>+<shift>+u{escape_code} ', delay=50)
    time.sleep(0.3)   # Typing thread needs time to finish up before we send more
    keyboard.send_keys(' Scary!')
     
else:

    #  otherwise, this must be an X11 environment and the script can simply do this: 
    keyboard.send_keys('This the "ninja" character: 🥷 Scary!')
