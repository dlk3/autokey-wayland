"""Regression tests for KWin windows without a desktop assignment."""

import unittest

from autokey.kde_interface import KdeWindowInterface


class KWinStub:
    def __init__(self, desktops):
        self.desktops = desktops

    def run(self, *args, **kwargs):
        window = {
            'desktops': self.desktops,
            'resourceClass': 'KMail',
            'caption': 'Message',
            'pid': 123,
            'internalId': 'window-id',
            'windowType': 0,
            'width': 100,
            'height': 100,
            'x': 0,
            'y': 0,
            'active': True,
        }
        return [window, {'id': 'current', 'x11DesktopNumber': 2}]


class TestKdeWindowDesktops(unittest.TestCase):
    def test_active_window_with_no_desktops_uses_current_desktop(self):
        interface = object.__new__(KdeWindowInterface)
        interface.kwin = KWinStub([])

        window = interface.get_active_window()

        self.assertEqual(window['workspace'], 1)
        self.assertEqual(window['desktop'], 'current')
        self.assertTrue(window['in_current_workspace'])

    def test_active_window_with_desktop_keeps_its_assignment(self):
        interface = object.__new__(KdeWindowInterface)
        interface.kwin = KWinStub([{'id': 'other', 'x11DesktopNumber': 3}])

        window = interface.get_active_window()

        self.assertEqual(window['workspace'], 2)
        self.assertEqual(window['desktop'], 'other')
        self.assertFalse(window['in_current_workspace'])


if __name__ == '__main__':
    unittest.main()
