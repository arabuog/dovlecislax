import unittest
from interaction import Interaction
from navigation import Action


class InteractionTests(unittest.TestCase):
    def test_distant_small_fruit_requires_w_not_e(self):
        gate=Interaction()
        for now in (0,1,10,100):
            self.assertEqual(gate.guard(Action('e',.05),(650,450,20,12),1280,720,now).key,'w')

    def test_near_fruit_requires_stable_position_before_one_press(self):
        gate=Interaction()
        gate.observe_forward((630,350,55,30),(620,420,85,45),1280,720)
        box=(620,420,85,45)
        self.assertEqual(gate.guard(Action('e',.05),box,1280,720,0).key,'wait')
        self.assertEqual(gate.guard(Action('e',.05),box,1280,720,.4).key,'e')
        gate.fired(.4)
        self.assertNotEqual(gate.guard(Action('e',.05),box,1280,720,.5).key,'e')

    def test_no_second_press_without_actual_forward_progress(self):
        gate=Interaction()
        gate.fired(0)
        box=(620,420,85,45)
        for now in (10,20,30):
            self.assertEqual(gate.guard(Action('e',.05),box,1280,720,now).key,'w')

    def test_first_press_requires_approach_too(self):
        gate=Interaction()
        box=(620,420,85,45)
        for now in (0,10,20):
            self.assertEqual(gate.guard(Action('e',.05),box,1280,720,now).key,'w')

    def test_next_press_after_observed_approach_and_stability(self):
        gate=Interaction()
        gate.fired(0)
        gate.new_target()
        gate.observe_forward((630,350,55,30),(620,420,85,45),1280,720)
        box=(620,420,85,45)
        self.assertEqual(gate.guard(Action('e',.05),box,1280,720,10).key,'wait')
        self.assertEqual(gate.guard(Action('e',.05),box,1280,720,10.4).key,'e')

    def test_lost_target_resets_approach_evidence(self):
        gate=Interaction()
        gate.observe_forward((630,350,55,30),(620,420,85,45),1280,720)
        gate.new_target()
        self.assertEqual(gate.forward_progress,0)

    def test_alignment_command_is_preserved(self):
        gate=Interaction()
        self.assertEqual(gate.guard(Action('a',.06),(620,420,85,45),1280,720,0).key,'a')
