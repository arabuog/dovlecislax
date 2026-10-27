import queue
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from panel import Panel
from panel_settings import Settings
from simple_cycle import Cycle


class PanelTests(unittest.TestCase):
    def make_panel(self):
        panel=Panel.__new__(Panel)
        self.events=[]
        panel.keys=SimpleNamespace(keyDown=lambda k:self.events.append(('down',k)) or True,
            keyUp=SimpleNamespace(__wrapped__=lambda k,**kw:self.events.append(('up',k))))
        panel.root=SimpleNamespace(after=lambda *_:None,destroy=lambda:None)
        panel.listener=SimpleNamespace(is_alive=lambda:True,stop=lambda:None)
        panel.status=SimpleNamespace(set=lambda value:None)
        panel.cycle=Cycle(walk=1,rest=7,key='f')
        panel.pending=None
        panel.closed=False
        panel.held=set()
        panel.events=queue.SimpleQueue()
        panel.focused=lambda:True
        panel.configure=lambda:True
        return panel

    def test_countdown_does_not_send_keys_until_ready(self):
        p=self.make_panel()
        with patch('panel.time.monotonic',return_value=0):
            p.prepare()
        with patch('panel.time.monotonic',return_value=2):
            p.tick()
        self.assertEqual(self.events,[])
        with patch('panel.time.monotonic',return_value=3):
            p.tick()
        self.assertEqual(self.events,[('down','w')])

    def test_one_chosen_key_and_wait_not_repeated_presses(self):
        p=self.make_panel()
        p.cycle.start(0)
        for now in (0,1,1.06,2,7,8):
            with patch('panel.time.monotonic',return_value=now):
                p.tick()
        self.assertEqual(self.events,[('down','w'),('up','w'),('down','f'),('up','f')])

    def test_alt_tab_releases_key_and_stays_paused(self):
        p=self.make_panel()
        p.cycle.start(0)
        p.sync('w')
        p.focused=lambda:False
        p.tick()
        self.assertEqual(self.events,[('down','w'),('up','w')])
        self.assertEqual(p.cycle.phase,'idle')

    def test_n_cancels_wait_and_releases_action_key(self):
        p=self.make_panel()
        p.cycle.start(0)
        p.cycle.tick(1)
        p.sync('f')
        p.events.put('toggle')
        p.tick()
        self.assertEqual(self.events,[('down','f'),('up','f')])
        self.assertEqual(p.cycle.phase,'idle')

    def test_closing_releases_keys(self):
        p=self.make_panel()
        p.sync('w')
        p.close()
        self.assertTrue(p.closed)
        self.assertEqual(self.events,[('down','w'),('up','w')])


class SettingsTests(unittest.TestCase):
    def test_steps_and_romanian_decimal_separator(self):
        s=Settings.parse(dict(steps='6',step_seconds='0,3',key=' F ',wait='7'),{'e','f'})
        self.assertAlmostEqual(s.walk_seconds,1.8)
        self.assertEqual(s.key,'f')

    def test_invalid_and_reserved_inputs(self):
        base=dict(steps='6',step_seconds='.3',key='e',wait='7')
        for name,value in [('steps','2.5'),('steps','-1'),('wait','nan'),
                           ('wait','-1'),('step_seconds','inf'),('key','n'),
                           ('key','w'),('key','unknown')]:
            with self.assertRaises(ValueError):
                Settings.parse(dict(base,**{name:value}),{'e','n','w'})

    def test_zero_wait_is_supported(self):
        s=Settings.parse(dict(steps=1,step_seconds=.3,key='e',wait=0),{'e'})
        c=Cycle(s.walk_seconds,s.wait,s.key)
        c.start(0)
        self.assertEqual(c.tick(.3),'e')
        self.assertIsNone(c.tick(.36))
        self.assertEqual(c.tick(.37),'w')
