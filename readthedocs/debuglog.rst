Creating An AutoKey Debug Log
=============================
  
Whenever you report a problem, you should include a debug log in the issue report. To generate a debug log:

- Stop AutoKey, 
- Start AutoKey with the "-v" command line option in a terminal window, 
- Perform whatever actions are required to recreate the problem, 
- Stop AutoKey, 
- Copy and paste the debugging messages from the terminal into a file, 
- If the actions you performed involved typing any personally identifiable 
  information, or any passwords, edit the file to remove this information. In 
  debug mode, AutoKey logs every keystoke you make, 
- Drag and drop the file into the problem report.

You might be interested to know that the ``~/.local/share/autokey/autokey.log`` 
file also captures the log messages that AutoKey writes.  This file may not 
capture the exceptions that can occur when things go wrong so it's not the best
option for debugging problems.
