import unittest
from simple_cycle import Cycle


class SimpleCycleTests(unittest.TestCase):
    def test_walk_one_press_then_seven_seconds_rest(self):
        cycle=Cycle(walk=1.8,rest=7)
        cycle.start(0)
        self.assertEqual(cycle.tick(0),'w')
        self.assertEqual(cycle.tick(1.79),'w')
        self.assertEqual(cycle.tick(1.8),'e')
        self.assertEqual(cycle.tick(1.84),'e')
        self.assertIsNone(cycle.tick(1.86))
        self.assertIsNone(cycle.tick(8.85))
        self.assertEqual(cycle.tick(8.87),'w')

    def test_pause_cancels_each_phase_and_restart_begins_with_w(self):
        for t in (0,1.8,1.86):
            cycle=Cycle()
            cycle.start(0)
            cycle.tick(1.8 if t else 0)
            cycle.tick(t)
            cycle.pause()
            self.assertIsNone(cycle.tick(100))
            cycle.start(101)
            self.assertEqual(cycle.tick(101),'w')

    def test_lag_does_not_skip_rest_or_repeat_interaction(self):
        cycle=Cycle()
        cycle.start(0)
        self.assertEqual(cycle.tick(100),'e')
        self.assertIsNone(cycle.tick(200))
        self.assertIsNone(cycle.tick(206))
        self.assertEqual(cycle.tick(207),'w')

    def test_rejects_invalid_durations(self):
        for value in (0,-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                Cycle(walk=value)
