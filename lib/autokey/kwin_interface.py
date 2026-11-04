#  Copyright (C) 2026 AutoKey contributors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Keyboard and mouse interface for KDE Plasma on Wayland that needs neither root
nor access to /dev/input and /dev/uinput.

Input comes from the "AutoKey KWin Bridge" KWin plugin: it sends every key
event (with the active window's class and title) to AutoKey over D-Bus and
consumes AutoKey's hotkeys before they reach applications, like XGrabKey did
on X11.

Output goes through the kwin-input helper, which uses KWin's
org_kde_kwin_fake_input protocol (KWin only offers it to programs listed in a
.desktop file with X-KDE-Wayland-Interfaces=org_kde_kwin_fake_input). KWin maps
keysyms to the active keyboard layout, including characters that are not on
the keyboard.
"""

import os
import shutil
import subprocess
import threading
import time
import typing

from gi.repository import Gio, GLib

from autokey.model.button import Button
from autokey.model.key import Key, MODIFIERS
from autokey.sys_interface.abstract_interface import AbstractMouseInterface, AbstractSysInterface, WindowInfo

logger = __import__("autokey.logger").logger.get_logger(__name__)

BRIDGE_SERVICE = "org.autokey.KWinBridge"
BRIDGE_PATH = "/AutoKeyBridge"
BRIDGE_INTERFACE = "org.autokey.KWinBridge"

# Modifier mask used by the bridge
MASK_SHIFT, MASK_CONTROL, MASK_ALT, MASK_SUPER, MASK_ALT_GR = 1, 2, 4, 8, 16

# Keysyms (X11 / xkbcommon values)
KEYSYM_TO_KEY = {
    0xffe1: Key.LEFTSHIFT, 0xffe2: Key.RIGHTSHIFT,
    0xffe3: Key.LEFTCONTROL, 0xffe4: Key.RIGHTCONTROL,
    0xffe9: Key.LEFTALT, 0xffea: Key.RIGHTALT,
    0xffeb: Key.LEFTSUPER, 0xffec: Key.RIGHTSUPER,
    0xffed: Key.LEFTHYPER, 0xffee: Key.RIGHTHYPER,
    0xffe7: Key.LEFTMETA, 0xffe8: Key.RIGHTMETA,
    0xfe03: Key.ALT_GR,
    0xffe5: Key.CAPSLOCK, 0xff7f: Key.NUMLOCK,
    0xff09: Key.TAB, 0xfe20: Key.TAB,  # ISO_Left_Tab (Shift+Tab)
    0xff51: Key.LEFT, 0xff53: Key.RIGHT, 0xff52: Key.UP, 0xff54: Key.DOWN,
    0xff0d: Key.ENTER, 0xff08: Key.BACKSPACE, 0xff14: Key.SCROLL_LOCK,
    0xff61: Key.PRINT_SCREEN, 0xff13: Key.PAUSE, 0xff67: Key.MENU,
    0xff1b: Key.ESCAPE, 0xff63: Key.INSERT, 0xffff: Key.DELETE,
    0xff50: Key.HOME, 0xff57: Key.END, 0xff55: Key.PAGE_UP, 0xff56: Key.PAGE_DOWN,
    0xff9e: Key.NP_INSERT, 0xff9f: Key.NP_DELETE, 0xff9c: Key.NP_END,
    0xff99: Key.NP_DOWN, 0xff9b: Key.NP_PAGE_DOWN, 0xff96: Key.NP_LEFT,
    0xff9d: Key.NP_5, 0xff98: Key.NP_RIGHT, 0xff95: Key.NP_HOME, 0xff97: Key.NP_UP,
    0xff9a: Key.NP_PAGE_UP, 0xffaf: Key.NP_DIVIDE, 0xffaa: Key.NP_MULTIPLY,
    0xffab: Key.NP_ADD, 0xffad: Key.NP_SUBTRACT, 0xff8d: Key.ENTER,
    0x20: " ",
}
for _i in range(35):
    KEYSYM_TO_KEY[0xffbe + _i] = getattr(Key, "F%d" % (_i + 1))

# Numeric keypad with Num Lock on
KEYPAD_DIGITS = {
    0xffb0: "0", 0xffb1: "1", 0xffb2: "2", 0xffb3: "3", 0xffb4: "4", 0xffb5: "5",
    0xffb6: "6", 0xffb7: "7", 0xffb8: "8", 0xffb9: "9", 0xffae: ".",
}

KEY_TO_KEYSYM = {v: k for k, v in KEYSYM_TO_KEY.items() if isinstance(v, Key)}
KEY_TO_KEYSYM.update({
    Key.TAB: 0xff09, Key.ENTER: 0xff0d,
    Key.SHIFT: 0xffe1, Key.CONTROL: 0xffe3, Key.ALT: 0xffe9, Key.SUPER: 0xffeb,
    Key.HYPER: 0xffed, Key.META: 0xffe7,
})

MODIFIER_TO_MASK = {
    Key.SHIFT: MASK_SHIFT, Key.LEFTSHIFT: MASK_SHIFT, Key.RIGHTSHIFT: MASK_SHIFT,
    Key.CONTROL: MASK_CONTROL, Key.LEFTCONTROL: MASK_CONTROL, Key.RIGHTCONTROL: MASK_CONTROL,
    Key.ALT: MASK_ALT, Key.LEFTALT: MASK_ALT, Key.RIGHTALT: MASK_ALT,
    Key.SUPER: MASK_SUPER, Key.LEFTSUPER: MASK_SUPER, Key.RIGHTSUPER: MASK_SUPER,
    Key.META: MASK_SUPER, Key.LEFTMETA: MASK_SUPER, Key.RIGHTMETA: MASK_SUPER,
    Key.HYPER: MASK_SUPER, Key.LEFTHYPER: MASK_SUPER, Key.RIGHTHYPER: MASK_SUPER,
    Key.ALT_GR: MASK_ALT_GR,
}

BUTTON_NAMES = {Button.LEFT: "left", Button.MIDDLE: "middle", Button.RIGHT: "right",
                Button.BACKWARD: "back", Button.FORWARD: "forward"}


def char_keysym(char: str) -> int:
    """Keysym of a character (xkb_utf32_to_keysym)."""
    cp = ord(char)
    if 0x20 <= cp <= 0x7e or 0xa0 <= cp <= 0xff:
        return cp
    return 0x1000000 + cp


def keysym_char(keysym: int) -> typing.Optional[str]:
    """Character of a keysym for printable keys (the inverse of char_keysym)."""
    if 0x20 < keysym <= 0x7e or 0xa0 <= keysym <= 0xff:
        return chr(keysym)
    if 0x1000100 <= keysym <= 0x110ffff:
        return chr(keysym - 0x1000000)
    return None


def bridge_available() -> bool:
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        reply = bus.call_sync("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                              "NameHasOwner", GLib.Variant("(s)", (BRIDGE_SERVICE,)),
                              GLib.VariantType("(b)"), Gio.DBusCallFlags.NONE, 1000, None)
        return reply.unpack()[0]
    except GLib.Error:
        return False


def find_kwin_input() -> typing.Optional[str]:
    candidates = [os.environ.get("AUTOKEY_KWIN_INPUT", ""), shutil.which("kwin-input") or "",
                  os.path.expanduser("~/.local/opt/kwin-input/bin/kwin-input")]
    for candidate in candidates:
        if candidate and os.access(candidate, os.X_OK):
            return candidate
    return None


class KeyCode:
    """What the IoMediator passes back to lookup_string().

    The mediator first asks for the key with the modifiers in effect, then for
    the raw key. The bridge already resolved both from the keyboard layout.
    """

    def __init__(self, raw, effective):
        self.raw = raw
        self.effective = effective
        self._looked_up = False

    def __repr__(self):
        return "KeyCode(%r, %r)" % (self.raw, self.effective)


class KWinInterface(threading.Thread, AbstractSysInterface, AbstractMouseInterface):

    def __init__(self, mediator, app):
        threading.Thread.__init__(self, name="KWinInterface-thread", daemon=True)
        self.mediator = mediator
        self.app = app
        self.shutdown = False
        self._context = GLib.MainContext()
        self._loop = GLib.MainLoop(self._context)
        self._bus = None
        self._subscription = None
        self._hotkey_update_pending = False
        self._output_lock = threading.Lock()
        self._output = None
        self._modifiers_cleared = False
        self._kwin_input = find_kwin_input()
        if self._kwin_input is None:
            logger.error("kwin-input was not found, AutoKey can't type on Wayland")

    # Lifecycle ----

    def initialise(self):
        pass

    def run(self):
        self._context.push_thread_default()
        try:
            self._bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self._subscription = self._bus.signal_subscribe(
                BRIDGE_SERVICE, BRIDGE_INTERFACE, "KeyEvent", BRIDGE_PATH, None,
                Gio.DBusSignalFlags.NONE, self._on_key_event)
            self._call("Register")
            self._update_hotkeys()
            # Re-register if KWin restarts
            Gio.bus_watch_name_on_connection(self._bus, BRIDGE_SERVICE, Gio.BusNameWatcherFlags.NONE,
                                             self._on_bridge_appeared, None)
            logger.info("Connected to the AutoKey KWin bridge")
            self._loop.run()
        except GLib.Error as error:
            logger.error("Can't connect to the AutoKey KWin bridge: %s", error.message)
        finally:
            self._context.pop_thread_default()

    def cancel(self):
        self.shutdown = True
        self._context.invoke_full(GLib.PRIORITY_DEFAULT, self._loop.quit)
        with self._output_lock:
            if self._output is not None:
                try:
                    self._output.stdin.close()
                    self._output.wait(1)
                except (OSError, subprocess.TimeoutExpired):
                    self._output.kill()
                self._output = None

    def flush(self):
        pass

    def _call(self, method, args=None):
        return self._bus.call_sync(BRIDGE_SERVICE, BRIDGE_PATH, BRIDGE_INTERFACE, method, args, None,
                                   Gio.DBusCallFlags.NONE, 2000, None)

    def _on_bridge_appeared(self, connection, name, owner):
        try:
            self._call("Register")
            self._update_hotkeys()
        except GLib.Error as error:
            logger.warning("Re-registering with the KWin bridge failed: %s", error.message)

    # Input ----

    def _on_key_event(self, connection, sender, path, interface, signal, params):
        (keysym, shifted_keysym, altgr_keysym, scan_code, pressed, repeat, grabbed, modifiers,
         window_class, window_title) = params.unpack()
        window_info = WindowInfo(wm_title=window_title, wm_class=window_class)

        modifier = KEYSYM_TO_KEY.get(keysym)
        if modifier in MODIFIERS:
            if repeat:
                return
            if pressed:
                self.mediator.handle_modifier_down(modifier)
            else:
                self.mediator.handle_modifier_up(modifier)
            return

        if not pressed:
            return

        raw = self._key_string(keysym)
        if raw is None:
            return
        effective = raw
        if modifiers & MASK_ALT_GR and altgr_keysym:
            effective = self._key_string(altgr_keysym) or raw
        elif modifiers & MASK_SHIFT and shifted_keysym:
            effective = self._key_string(shifted_keysym) or raw
        if keysym in KEYPAD_DIGITS:
            raw = effective = KEYPAD_DIGITS[keysym]
        self.mediator.handle_keypress(KeyCode(raw, effective), window_info)

    @staticmethod
    def _key_string(keysym):
        if keysym in KEYSYM_TO_KEY:
            key = KEYSYM_TO_KEY[keysym]
            return key.value if isinstance(key, Key) else key
        return keysym_char(keysym)

    def lookup_string(self, key_code, shifted, num_lock, alt_grid):
        if not isinstance(key_code, KeyCode):
            return None
        # First call: the key as typed. Then: the raw key (no modifiers).
        if not key_code._looked_up:
            key_code._looked_up = True
            return key_code.effective
        return key_code.raw

    def handle_keypress(self, keyCode):
        pass

    def handle_keyrelease(self, keyCode):
        pass

    def handle_mouseclick(self, button, x, y):
        pass

    # Hotkeys ----

    def grab_hotkey(self, item):
        self._schedule_hotkey_update()

    def ungrab_hotkey(self, item):
        self._schedule_hotkey_update()

    def on_keys_changed(self):
        self._schedule_hotkey_update()

    def _schedule_hotkey_update(self):
        if self._hotkey_update_pending:
            return
        self._hotkey_update_pending = True

        def update():
            self._hotkey_update_pending = False
            self._update_hotkeys()
            return False

        source = GLib.timeout_source_new(100)
        source.set_callback(update)
        source.attach(self._context)

    def _update_hotkeys(self):
        if self._bus is None:
            return
        hotkeys = []
        config = self.app.configManager
        items = list(config.hotKeys) + [item for item in config.globalHotkeys if item.enabled]
        for item in items:
            entry = self._hotkey_entry(item)
            if entry is not None:
                hotkeys.append(entry)
        try:
            self._call("SetHotkeys", GLib.Variant("(a(uus))", (hotkeys,)))
            logger.debug("Registered %d hotkeys with the KWin bridge", len(hotkeys))
        except GLib.Error as error:
            logger.error("Can't register hotkeys with the KWin bridge: %s", error.message)

    @staticmethod
    def _hotkey_entry(item):
        key = getattr(item, "hotKey", None)
        if not key:
            return None
        mask = 0
        for modifier in item.modifiers or []:
            mask |= MODIFIER_TO_MASK.get(modifier, 0)
        if Key.is_key(key):
            keysym = KEY_TO_KEYSYM.get(Key(key))
        elif len(key) == 1:
            # Hotkeys use the unshifted key, like the bridge does
            keysym = char_keysym(key.lower())
        else:
            keysym = None
        if keysym is None:
            logger.warning("Unsupported hotkey key %r", key)
            return None
        regex = None
        try:
            regex = item.get_applicable_regex()
        except Exception:  # pragma: no cover - older models
            regex = getattr(item, "windowInfoRegex", None)
        pattern = regex.pattern if regex is not None else ""
        return (mask, keysym, pattern)

    # Output ----

    def _send(self, *args):
        """Run one kwin-input command line, e.g. ("key", "0xff0d")."""
        if self._kwin_input is None:
            return
        line = " ".join('"%s"' % str(a).replace("\\", "\\\\").replace('"', '\\"') for a in args)
        with self._output_lock:
            for _attempt in range(2):
                if self._output is None or self._output.poll() is not None:
                    self._output = subprocess.Popen([self._kwin_input, "-"], stdin=subprocess.PIPE,
                                                    stdout=subprocess.PIPE, text=True, bufsize=1)
                try:
                    self._output.stdin.write(line + "\n")
                    self._output.stdin.flush()
                    reply = self._output.stdout.readline().strip()
                    if reply != "ok":
                        logger.warning("kwin-input %s: %s", line, reply or "no reply")
                    return
                except (BrokenPipeError, OSError):
                    self._output = None

    @staticmethod
    def _keysym_arg(key):
        if isinstance(key, Key) or Key.is_key(key):
            keysym = KEY_TO_KEYSYM.get(Key(key))
        elif len(key) == 1:
            keysym = char_keysym(key)
        else:
            keysym = None
        if keysym is None:
            raise ValueError("Unsupported key %r" % (key,))
        return "0x%x" % keysym

    def send_string(self, string):
        if string:
            self._send("type", string)

    def send_key(self, key_name):
        if not (isinstance(key_name, Key) or Key.is_key(key_name)) and len(key_name) == 1:
            self._send("type", key_name)
        else:
            self._send("key", self._keysym_arg(key_name))

    def send_modified_key(self, key_name, modifiers):
        combo = [self._keysym_arg(m) for m in modifiers] + [self._keysym_arg(key_name)]
        self._send("key", "+".join(combo))

    def press_key(self, key_name):
        if key_name in MODIFIER_TO_MASK and self._modifiers_cleared:
            # Re-press the modifiers the user is still holding (AutoKey's
            # _reapply_modifiers after typing a phrase)
            self._modifiers_cleared = False
            self._call_quiet("RestoreModifiers")
            return
        self._send("keydown", self._keysym_arg(key_name))

    def release_key(self, key_name):
        if key_name in MODIFIER_TO_MASK and self.mediator.modifiers.get(key_name):
            # A modifier the user is physically holding (AutoKey's
            # _clear_modifiers before typing a phrase). A synthetic release
            # wouldn't change what applications see, the bridge releases the
            # real key for them.
            if not self._modifiers_cleared:
                self._modifiers_cleared = True
                self._call_quiet("ClearModifiers")
            return
        self._send("keyup", self._keysym_arg(key_name))

    def _call_quiet(self, method):
        try:
            self._call(method)
        except GLib.Error as error:
            logger.warning("KWin bridge %s failed: %s", method, error.message)

    def fake_keydown(self, key_name):
        self.press_key(key_name)

    def fake_keyup(self, key_name):
        self.release_key(key_name)

    def fake_keypress(self, key_name):
        self.send_key(key_name)

    def grab_keyboard(self):
        # The bridge ignores synthetic input, AutoKey never sees its own output
        pass

    def ungrab_keyboard(self):
        pass

    # Mouse ----

    def mouse_location(self):
        try:
            window_interface = self.mediator.windowInterface
            getter = getattr(window_interface, "get_mouse_position", None)
            if callable(getter):
                return getter()
        except Exception:
            pass
        logger.warning("mouse_location is not supported on KDE Wayland")
        return 0, 0

    def get_mouse_position(self):
        return self.mouse_location()

    def relative_mouse_location(self, window=None):
        return self.mouse_location()

    def move_cursor(self, xCoord, yCoord, relative=False, relative_self=False):
        if relative_self:
            self._send("moveby", xCoord, yCoord)
        else:
            self._send("move", xCoord, yCoord)

    def send_mouse_click(self, xCoord, yCoord, button, relative):
        if not relative:
            self._send("move", xCoord, yCoord)
        self._send("click", BUTTON_NAMES.get(Button(button), "left"))

    def send_mouse_click_relative(self, xoff, yoff, button):
        self._send("moveby", xoff, yoff)
        self._send("click", BUTTON_NAMES.get(Button(button), "left"))

    def mouse_press(self, xCoord, yCoord, button):
        self._send("move", xCoord, yCoord)
        self._send("mousedown", BUTTON_NAMES.get(Button(button), "left"))

    def mouse_release(self, xCoord, yCoord, button):
        self._send("move", xCoord, yCoord)
        self._send("mouseup", BUTTON_NAMES.get(Button(button), "left"))

    def scroll_down(self, number):
        self._send("scroll", number)

    def scroll_up(self, number):
        self._send("scroll", -number)
