import unittest
import numpy as np
from game_capture import GameCapture, Window


class Desktop:
    def __init__(self, *snapshots):
        self.snapshots = list(snapshots)

    def snapshot(self):
        if len(self.snapshots) > 1:
            return self.snapshots.pop(0)
        return self.snapshots[0]


class Screen:
    monitors = [dict(left=-1920, top=0, width=3840, height=1080)]

    def __init__(self):
        self.calls = []

    def grab(self, rect):
        self.calls.append(rect)
        return np.zeros((rect['height'], rect['width'], 4), np.uint8)


class CaptureTests(unittest.TestCase):
    def test_discord_is_not_captured(self):
        screen = Screen()
        game = GameCapture(Desktop(Window(1, 'Discord.exe', (0,0,1280,720))), screen)
        self.assertIsNone(game.grab())
        self.assertEqual(screen.calls, [])

    def test_launcher_is_not_treated_as_game(self):
        self.assertFalse(Window(1, 'FiveM.exe', (0,0,1280,720)).is_game)

    def test_window_on_second_monitor_uses_client_bounds(self):
        screen = Screen()
        window = Window(2, r'C:\FiveM\FiveM_b3095_GTAProcess.exe', (-1800,30,1280,720))
        frame = GameCapture(Desktop(window), screen).grab()
        self.assertEqual(frame.shape, (720,1280,3))
        self.assertEqual(screen.calls, [dict(left=-1800,top=30,width=1280,height=720)])

    def test_alt_tab_during_capture_discards_image(self):
        window = Window(2, 'FiveM_GTAProcess.exe', (0,0,1280,720))
        discord = Window(3, 'Discord.exe', (0,0,1280,720))
        self.assertIsNone(GameCapture(Desktop(window,discord), Screen()).grab())

    def test_hidden_minimized_and_offscreen_windows_are_not_captured(self):
        for window in [Window(1,'FiveM_GTAProcess.exe',(0,0,1280,720), minimized=True),
                       Window(1,'FiveM_GTAProcess.exe',(0,0,1280,720), visible=False),
                       Window(1,'FiveM_GTAProcess.exe',(1800,0,1280,720))]:
            screen = Screen()
            self.assertIsNone(GameCapture(Desktop(window),screen).grab())
            self.assertEqual(screen.calls, [])

    def test_no_foreground_process_is_not_captured(self):
        self.assertIsNone(GameCapture(Desktop(None),Screen()).grab())
