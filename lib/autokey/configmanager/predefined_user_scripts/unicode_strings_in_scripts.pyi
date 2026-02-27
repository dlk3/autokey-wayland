import os

#  Demonstrating how to output a string containing a Unicode character in 
#  Wayland and X11 environments, because it depends ...

#  If the script is running in a Wayland environment ...
if os.environ['XDG_SESSION_TYPE'] == 'wayland':

    # we'll create a function to prevent having to write duplicate
    # code when we need to handle more than just one character
    def getEscapeCode(character):
        escape_code = character.encode('unicode_escape').decode('utf-8').lstrip('\\U0')
        return f'<ctrl>+<shift>+u{escape_code}+<enter>'
    
    # then we can output a string containing a Unicode character like this:
    keyboard.send_keys(f'This is the "ninja" character: {getEscapeCode('🥷')}')
    #  the Unicode character needs to be the last character in the string, and
    #  then we need to take a short break to let the typing thread catch up 
    #  before sending more text.
    time.sleep(0.3)
    keyboard.send_keys(' Scary!')
     
else:

    #  otherwise, this must be an X11 environment and the script can simply be this: 
    keyboard.send_keys('This the "ninja" character: 🥷 Scary!')
