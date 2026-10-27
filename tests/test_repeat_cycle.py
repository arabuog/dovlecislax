import unittest
from panel_settings import Settings
from repeat_cycle import RepeatCycle
from tests import test_panel as fixtures
from unittest.mock import patch


def keys(value):
    return set(value) if isinstance(value,(set,frozenset)) else ({value} if value else set())


class RepeatTests(unittest.TestCase):
    def trace(self,cycle,until):
        old=set()
        events=[]
        for i in range(int(until*100)+1):
            now=i/100
            wanted=keys(cycle.tick(now))
            for key in old-wanted:
                events.append((now,'up',key))
            for key in wanted-old:
                events.append((now,'down',key))
            old=wanted
        return events

    def test_three_presses_after_walk_and_full_rest_after_last_release(self):
        cycle=RepeatCycle(walk=1,rest=7,settle=.25,press=.2,repeats=3)
        cycle.start(0)
        events=self.trace(cycle,9.5)
        presses=[t for t,kind,key in events if kind=='down' and key=='e']
        self.assertEqual(len(presses),3)
        self.assertGreaterEqual(presses[0],1.25)
        last_up=max(t for t,kind,key in events if kind=='up' and key=='e')
        walks=[t for t,kind,key in events if kind=='down' and key=='w']
        self.assertEqual(len(walks),2)
        self.assertGreaterEqual(walks[1]-last_up,7)

    def test_four_presses_during_walk_do_not_release_w(self):
        cycle=RepeatCycle(walk=2,rest=7,press=.2,repeats=4,during_walk=True)
        cycle.start(0)
        events=self.trace(cycle,2.1)
        self.assertEqual(sum(kind=='down' and key=='e' for _,kind,key in events),4)
        self.assertEqual([(t,kind) for t,kind,key in events if key=='w'],[(0.,'down'),(2.,'up')])
        self.assertTrue(all(t<2 for t,kind,key in events if key=='e'))

    def test_count_resets_on_next_cycle(self):
        cycle=RepeatCycle(walk=1,rest=.5,press=.1,repeats=2,during_walk=True)
        cycle.start(0)
        events=self.trace(cycle,2.6)
        self.assertEqual(sum(kind=='down' and key=='e' for _,kind,key in events),4)

    def test_long_scheduler_stall_drops_presses_instead_of_sending_after_walk(self):
        cycle=RepeatCycle(walk=1,rest=7,press=.1,repeats=3,during_walk=True)
        cycle.start(0)
        self.assertEqual(keys(cycle.tick(0)),{'w','e'})
        self.assertIsNone(cycle.tick(5))
        self.assertIsNone(cycle.tick(6))
        self.assertEqual(cycle.sent,1)

    def test_invalid_counts_or_too_short_walk_are_rejected(self):
        for repeats in (0,-1,2.5,1001):
            with self.assertRaises(ValueError):
                RepeatCycle(repeats=repeats)
        with self.assertRaises(ValueError):
            Settings.parse(dict(steps=1,step_seconds=.3,key='e',wait=7,repeats=10,during_walk=True),{'e'})

    def test_old_saved_settings_default_to_one_press_after_walking(self):
        s=Settings.parse(dict(steps=6,step_seconds=.3,key='e',wait=7),{'e'})
        self.assertEqual(s.repeats,1)
        self.assertFalse(s.during_walk)

    def test_panel_pause_releases_w_and_action_together(self):
        helper=fixtures.PanelTests()
        p=helper.make_panel()
        p.cycle=RepeatCycle(walk=2,repeats=4,press=.2,during_walk=True)
        p.cycle.start(0)
        with patch('panel.time.monotonic',return_value=0):
            p.tick()
        self.assertEqual(p.held,{'w','e'})
        p.events.put('toggle')
        p.tick()
        self.assertEqual(p.held,set())
        self.assertCountEqual([key for kind,key in helper.events if kind=='up'],['w','e'])
