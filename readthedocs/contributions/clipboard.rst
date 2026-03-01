Clipboard API Script
====================

I created this script to test the all of the methods in the clipboard API.  It might be useful as a demonstration of some of the things that are possible.

.. code:: python

    #  A script that tests (and demonstrates) the clipboard API methods
    
    #  Set this to an image file that exists on your system
    image_file = '~/src/autokey-wayland/readthedocs/editconfig.jpg'
    
    import datetime
    
    #  Enable script output to the Autokey application log,
    #  ~/.local/share/autokey/autokey.log
    logger = __import__("autokey.logger").logger.get_logger(__name__ + ".clipboard.script")
       
    logger.debug(f'The clipboard\'s current content = "{clipboard.get_clipboard()}"')    
    test_content = f'The current date and time are {datetime.datetime.now()}'
    logger.debug('Pushing test string onto clipboard')
    clipboard.fill_clipboard(test_content)
    logger.debug('Pulling text from clipboard')
    result = clipboard.get_clipboard()
    if result.decode('utf-8') == test_content:
        logger.debug('The text pulled matches the text pushed')
    else:
        logger.error(f'The text pushed, "{test_content}", does not match the text pulled, "{result}"')
    logger.debug('Pushing image file to clipboard, try creating a new image from the cliboard with a tool like GIMP')
    clipboard.set_clipboard_image(image_file)
    
    logger.debug(f'The primary (selection) clipboard\'s current content = "{clipboard.get_selection()}"')    
    test_content = f'The current date and time are {datetime.datetime.now()}'
    logger.debug('Pushing test string onto the primary clipboard')
    clipboard.fill_selection(test_content)
    logger.debug('Pulling text from the primary clipboard')
    result = clipboard.get_selection()
    if result.decode('utf-8') == test_content:
        logger.debug('The text pulled matches the text pushed')
    else:
        logger.error(f'The text pushed, "{test_content}", does not match the text pulled, "{result}"')
    