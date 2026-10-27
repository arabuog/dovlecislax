import unittest
import cv2
import numpy as np
from detector import detect


class DetectorTests(unittest.TestCase):
    def test_detects_separate_orange_targets(self):
        frame = np.zeros((1080, 1350, 3), np.uint8)
        cv2.ellipse(frame, (320, 520), (40, 25), 0, 0, 360, (0, 160, 255), -1)
        cv2.ellipse(frame, (1000, 460), (30, 20), 0, 0, 360, (0, 160, 255), -1)
        self.assertEqual(len(detect(frame)), 2)

    def test_excludes_hud_and_player(self):
        frame = np.zeros((1080, 1350, 3), np.uint8)
        for center in [(1100, 80), (100, 950)]:
            cv2.ellipse(frame, center, (35, 25), 0, 0, 360, (0, 160, 255), -1)
        self.assertEqual(detect(frame), [])

    def test_nearby_pumpkin_is_not_masked(self):
        frame = np.zeros((720, 1280, 3), np.uint8)
        cv2.ellipse(frame, (665, 465), (40, 25), 0, 0, 360, (0, 160, 255), -1)
        self.assertEqual(len(detect(frame)), 1)

    def test_no_target(self):
        self.assertEqual(detect(np.zeros((1080, 1350, 3), np.uint8)), [])


if __name__ == '__main__':
    unittest.main()
