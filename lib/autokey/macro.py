import datetime
from abc import abstractmethod
import shlex

from autokey.model.key import Key, KEY_SPLIT_RE
from autokey import common

import autokey.scripting


if common.USED_UI_TYPE == "QT":
    from PyQt5.QtWidgets import QAction

    def _(text: str, args: tuple=None):
        """localisation function, currently returns the identity. If args are given, those are used to format
        text using the old-style % formatting."""
        if args:
            text = text % args
        return text

    class MacroAction(QAction):

        def __init__(self, menu, macro, callback):
            super(MacroAction, self).__init__(macro.TITLE, menu)
            self.macro = macro
            self.callback = callback
            self.triggered.connect(self.on_triggered)

        def on_triggered(self):
            self.callback(self.macro)

elif common.USED_UI_TYPE == "GTK":
    from gi.repository import Gtk


# Escape any escaped angle brackets
def encode_escaped_brackets(s):
    # If you need a literal '\' at the end of the macro args... IDK. Add a
    # space before the >?
    # If you need a literal \>, just add an extra \.
    # s.replace("\\\\", chr(27)) # ASCII Escape
    # Use arbitrary nonprinting ascii to represent escaped char.
    # Easier than having to parse escape chars.
    s = s.replace("\\<", chr(0x1e))  # Record seperator
    s = s.replace("\\>", chr(0x1f))  # unit seperator
    # s.replace(chr(27), "\\")
    return s


def decode_escaped_brackets(s):
    s = s.replace(chr(0x1e), '<')  # Record seperator
    s = s.replace(chr(0x1f), '>')  # unit seperator
    return s

def sections_decode_escaped_brackets(sections):
    for i, s in enumerate(sections):
        sections[i] = decode_escaped_brackets(s)


# This must be passed a string containing only one macro.
def extract_tag(s):
    if not isinstance(s, str):
        raise TypeError
    extracted = [p.split('>')[0] for p in s.split('<') if '>' in p]
    if len(extracted) == 0:
        return s
    else:
        return ''.join(extracted)


def split_key_val(s):
    # Split as if a shell argument.
    # Splits at spaces, but preserves spaces within quotes.
    pairs = shlex.split(s)
    return dict(pair.split('=', 1) for pair in pairs)


class MacroManager:

    def __init__(self, engine):
        self.macros = []

        self.macros.append(ScriptMacro(engine))
        self.macros.append(DateMacro())
        self.macros.append(FileContentsMacro())
        self.macros.append(CursorMacro())
        self.macros.append(SystemMacro(engine))
        self.macros.append(ClipboardMacro())

    def get_menu(self, callback, menu=None):
        if common.USED_UI_TYPE == "QT":
            for macro in self.macros:
                menu.addAction(MacroAction(menu, macro, callback))

        elif common.USED_UI_TYPE == "GTK":
            menu = Gtk.Menu()

            for macro in self.macros:
                menuItem = Gtk.MenuItem(macro.TITLE)
                menuItem.connect("activate", callback, macro)
                menu.append(menuItem)

            menu.show_all()

        return menu

    # Split expansion.string, expand and process its macros, then
    # replace with the results.
    def process_expansion_macros(self, content):
        # Split into sections with <> macros in them.
        # Using the Key split regex works for now.
        content = encode_escaped_brackets(content)
        content_sections = KEY_SPLIT_RE.split(content)

        for macroClass in self.macros:
            content_sections = macroClass.process(content_sections)

        return ''.join(content_sections)


class AbstractMacro:

    @property
    @abstractmethod
    def ID(self):
        pass
    @property
    @abstractmethod
    def TITLE(self):
        pass
    @property
    @abstractmethod
    def ARGS(self):
        pass

    def get_token(self):
        ret = "<%s" % self.ID
        # TODO: v not used in initial implementation? This results in something like "<%s a= b= c=>"
        ret += "".join((" " + k + "=" for k, v in self.ARGS))
        ret += ">"
        return ret

    def _get_args(self, macro):
        args = split_key_val(macro)
        expected_args = [arg[0] for arg in self.ARGS]
        expected_argnum = len(self.ARGS)

        for arg in expected_args:
            if arg not in args:
                raise ValueError("Missing mandatory argument '{}' for macro '{}'".format(arg, self.ID))
        for arg in args:
            if arg not in expected_args:
                raise ValueError("Unexpected argument '{}' for macro '{}'".format(arg, self.ID))
        return args

    def _extract_macro(self, section):
        content = extract_tag(section)
        content = decode_escaped_brackets(content)
        # type is space-separated from rest of macro.
        # Cursor macros have no space.
        if ' ' in content:
            macro_type, macro = content.split(' ', 1)
        else:
            macro_type, macro = (content, '')
        return macro_type, macro


    def process(self, sections):
        for i, section in enumerate(sections):
            # if MACRO_SPLIT_RE.match(section):
            if KEY_SPLIT_RE.match(section):
                macro_type, macro = self._extract_macro(sections[i])
                if macro_type == self.ID:
        # parts and i are required for cursor macros.
                    sections = self.do_process(sections, i)
        return sections

    @abstractmethod
    def do_process(self, sections, i):
        """ Returns updated sections """
        # parts and i are required for cursor macros.
        return sections


class CursorMacro(AbstractMacro):
    """
    C{<cursor>} - Positions the text cursor at the indicated text position. There may only be one <cursor> macro in a snippet.
    """

    ID = "cursor"
    TITLE = _("Position cursor")
    ARGS = []

    def do_process(self, sections, i):
        try:
            lefts = len(''.join(sections[i+1:]))
            sections.append(Key.LEFT * lefts)
            sections[i] = ''
        except IndexError:
            pass
        return sections


class ScriptMacro(AbstractMacro):
    """
    C{<script>} - Runs an autokey script. The script's stdout is inserted into the snippet.

    As of 0.96.0, Scripts outside of autokey can be executed by passing their absolute path (including ~, which is expanded to $HOME) to name= instead of a description.

    Currently, the args argument expects a string containing comma separated values (CSV). 
    The data is split at the , signs and is available as a list containing strings using the engine.get_macro_arguments() function. 
    If there is no comma in the input data, the resulting list will contain a single item. Currently, the args argument is required. 
    So if you don't need it, just feed in some dummy value. This behaviour might be improved in the future.

    Running a Script using the script macro poses some limitations:

    The keyboard built-in cannot be used. It is available and can in theory be used to type, but actually using it will break the Phrase processing.
        * Because all scripts are executed even before the trigger abbreviation is removed and the whole phrase is pasted/typed in one go, scripts can't be used to type anywhere in the phrase text.
    Simple rule: Do nothing that alters the current system GUI state.
        * Do not use keyboard to type/send keys.
        * Do not use mouse to do mouse clicks anywhere.
        * Do not use system.exec_command to execute GUI manipulation/automation tools, like xdotool.

    You may use the script to alter background system state, like starting or stopping system services, but simply restricting yourself to reading data in will yield the best results.
    """


    ID = "script"
    TITLE = _("Run script")
    ARGS = [("name", _("Name")),
            ("args", _("Arguments (comma separated)"))]

    def __init__(self, engine):
        self.engine = engine

    def do_process(self, sections, i):
        macro_type, macro = self._extract_macro(sections[i])
        args = self._get_args(macro)
        self.engine.run_script_from_macro(args)
        sections[i] = self.engine._get_return_value()
        return sections


class SystemMacro(AbstractMacro):
    """
    C{<system>} - Runs a system command. The command's stdout is inserted into the snippet.

    C{System.exec_command(args["command"], getOutput=True)} is used to run the command.

    Example: C{<system command="ls -l">}
    """

    ID = "system"
    TITLE = _("Run system command")
    ARGS = [("command", _("Command to be executed (including any arguments) - e.g. 'ls -l'")),]
            # ("getOutput", _("True or False, whether or not to set the return
            #     value to the script's stdout (blocks until script finishes). If
            #     false, "))]

    def __init__(self, engine):
        self.engine = engine

    def do_process(self, sections, i):
        macro_type, macro = self._extract_macro(sections[i])
        args = self._get_args(macro)
        self.engine.run_system_command_from_macro(args)
        sections[i] =  self.engine._get_return_value()
        return sections


class DateMacro(AbstractMacro):
    """
    C{<date>} - Inserts the current date and time. Has a C{format} parameter that allows you to set the format of the date/time string.

    Uses Python3's datetime.datetime.strftime() to format the date/time string.

    See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior for a full list of options.

    Example: C{<date format="%Y-%m-%d %H:%M:%S">}
    """

    ID = "date"
    TITLE = _("Insert date")
    ARGS = [("format", _("Format"))]

    def do_process(self, sections, i):
        macro_type, macro = self._extract_macro(sections[i])
        format_ = self._get_args(macro)["format"]
        date = datetime.datetime.now()
        date = date.strftime(format_)
        sections[i] = date
        return sections


class FileContentsMacro(AbstractMacro):
    """
    C{<file>} - Inserts the contents of a file. Has a C{name} parameter that allows you to set the name of the file.

    Reads a file from disk and inserts the file content into the phrase. The name parameter takes an absolute file path.
    The full file content is read into the system memory and then placed into the phrase, so restrict yourself to small text files.
    When using a 1MB large file, autokey will need about one million key strokes to type the content.
    Typically, text editors dislike raw binary data, so only use text files.

    This can be used to include another Phrase by specifying its full file path and treating it like an ordinary file.
    """

    ID = "file"
    TITLE = _("Insert file contents")
    ARGS = [("name", _("File name"))]

    def do_process(self, sections, i):
        macro_type, macro = self._extract_macro(sections[i])
        name = self._get_args(macro)["name"]

        with open(name, "r") as inputFile:
            sections[i] = inputFile.read()

        return sections

class ClipboardMacro(AbstractMacro):
    """
    C{<clipboard>} - Inserts the contents of the clipboard.

    :param clipboard:  The clipboard to use, defaults to "clipboard", can use "selection" to use the clipboard's selection.
    """


    ID = "clipboard"
    TITLE = _("Insert clipboard contents")
    ARGS = []

    def __init__(self):
        self.clipboard = autokey.scripting.Clipboard()

    def do_process(self, sections, i):
        macro_type, macro = self._extract_macro(sections[i])
        args = split_key_val(macro)
        if args.get("clipboard") and args.get("clipboard")=="selection":
            sections[i] = self.clipboard.get_selection()
        else:
            sections[i] = self.clipboard.get_clipboard()


        return sections