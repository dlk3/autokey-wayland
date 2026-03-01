Window API Script
=================

I created this script to test the all of the methods in the window API.  It might be useful as a demonstration of some of the things that are possible.

.. code:: python

    #  A script that tests (and demonstrates) the window API methods
    
    #  Enable script output to the Autokey application log,
    #  ~/.local/share/autokey/autokey.log
    logger = __import__("autokey.logger").logger.get_logger(__name__ + ".window.script")
    
    import json
    import threading
    
    # Routine that runs in a separate thread to open a window to see if
    # the window.wait_for_exists() method will detect that event
    def open_dialog_window(title):
       time.sleep(2)
       dialog.info_dialog(title, message='I exist only for AutoKey window API testing.  Please be patient, you shouldn\'t need to do anything with me ...')
    
    # Start testing
    logger.debug('window API test begins')
    
    # Test getting window information using various search criteria
    windowList = window.get_window_list()   
    logger.debug(f'List of all windows = \n{json.dumps(windowList, indent=4)}')
    logger.debug(f'List of windows on workspace #2 = \n{json.dumps(window.get_window_list(filter_desktop=1), indent=4)}')
    
    logger.debug(f'Title of currently active window = "{window.get_active_title()}"')
    logger.debug(f'Class of currently active window = "{window.get_active_class()}"')
    (x, y, height, width) = window.get_active_geometry()
    logger.debug(f'Geometry of currently active window = "{width}x{height}+{x}+{y}"')
    if window.wait_for_focus(window.get_active_title()):
        logger.debug(f'"{window.get_active_title()}" window has focus.')
    else:
        logger.critical('window.wait_for_focus() did not return expected result')
    
    saved_title = window.get_active_title()
    saved_hexid = window.get_window_hex(':ACTIVE:')
    (x, y, height, width) = window.get_window_geometry(saved_hexid, by_hex=True)
    logger.debug(f'"{saved_title}" window\'s geometry is {width}x{height}+{x}+{y}')
    logger.debug(f'"{saved_title}" window\'s hexid is {saved_hexid}')
    
    #  Test moving windows around
    logger.debug(f'Moving "{saved_title}" window 100 pixels to the left and adding 500 pixels to its width')
    window.resize_move(saved_hexid, xOrigin=x-100, width=width+500, by_hex=True)
    
    logger.debug(f'In five seconds I will move the "{saved_title}" window to workspace #2, wait 2 seconds, and move it back')
    time.sleep(5)
    window.move_to_desktop(saved_hexid, 1, by_hex=True)
    time.sleep(2)
    logger.debug(f'List of windows on workspace #2 after the move = \n{json.dumps(window.get_window_list(filter_desktop=1), indent=4)}')
    window.move_to_desktop(saved_hexid, 0, by_hex=True)
    
    logger.debug(f'Centering the "{saved_title}" window')
    window.center_window(saved_hexid, win_width=-1, win_height=-1, by_hex=True)
    
    active_title = window.get_active_title()
    logger.debug(f'"{active_title}" window\'s geometry is {window.get_window_geometry(active_title)}')
    
    #  Test switching workspaces
    logger.debug(f'In 3 seconds I will switch to workspace #2, wait 3 seconds, and then switch back to workspace #1')
    time.sleep(3) 
    window.switch_desktop(1)
    time.sleep(3)
    window.switch_desktop(0)
    
    #  Test window.wait_for_exist().  We open a dialog window in a new thread,
    #  while this thread waits for it to appear.
    logger.debug('Waiting for a test window to appear')
    test_window_title = 'A test window'
    thread = threading.Thread(target=open_dialog_window, args=(test_window_title,))
    thread.start()
    if window.wait_for_exist(test_window_title):
        logger.debug(f'The test window appeared.')
    else:
        logger.critical('window.wait_for_exist() did not return expected result')
    logger.debug('Closing the test window in 3 seconds')
    time.sleep(3)
    window.close(test_window_title)
    
    logger.debug('window API test complete')
    
    thread.join()