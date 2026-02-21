import os

#  Demonstrating how to output a string containing a Unicode character in 
#  Wayland and X11 environments, because it depends ...

#  If the script is running in a Wayland environment ...
if os.environ['XDG_SESSION_TYPE'] == 'wayland':

    # then it can output a string containing a Unicode character like this:
    keyboard.send_keys('This the "ninja" character: ') 
    character = '🥷'
    escape_code = character.encode('unicode_escape').decode('utf-8').lstrip('\\U0')
    keyboard.send_keys(f'<ctrl>+<shift>+u{escape_code} ', delay=50)  # The space at the end of the string is critical
     
else:

    #  otherwise, this must be an X11 environment and the script can simply do this: 
    keyboard.send_keys('This the "ninja" character: 🥷')
