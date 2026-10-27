import unittest
from collection import Collection


class CollectionTests(unittest.TestCase):
    def test_short_occlusion_does_not_confirm(self):
        c = Collection((100, 100, 80, 40), 0)
        self.assertEqual(c.update([], 3), 'waiting')
        self.assertEqual(c.update([], 9), 'waiting')
        self.assertEqual(c.update([(100, 100, 80, 40)], 9.8), 'waiting')
        self.assertEqual(c.update([], 10), 'waiting')
        self.assertEqual(c.update([], 11.1), 'disappeared')

    def test_persistent_target_times_out(self):
        c = Collection((100, 100, 80, 40), 0)
        self.assertEqual(c.update([(105, 103, 75, 38)], 19), 'timeout')

    def test_next_distant_target_does_not_block_disappearance(self):
        c = Collection((100, 100, 80, 40), 0)
        boxes = [(100, 40, 40, 20)]
        self.assertEqual(c.update(boxes, 9), 'waiting')
        self.assertEqual(c.update(boxes, 10.1), 'disappeared')
