Creating An AutoKey Debug Log
=============================
  
Whenever you report a problem, you should include a debug log in the issue report. To generate a debug log:

- Stop AutoKey,
- Erase the existing log file: ``~/.local/autokey/autokey.log``,
- Start AutoKey with the "-v" command line option,
- Perform whatever actions are required to recreate the problem,
- Stop AutoKey,
- If the actions you performed involved typing any personally identifiable information, or any passwords, edit the ``~/.local/share/autokey/autokey.log`` file to remove this information. In debug mode, AutoKey logs every keystoke you make,
- Drag and drop the ``~/.local/share/autokey/autokey.log`` file into the problem report.
