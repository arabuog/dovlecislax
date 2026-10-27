import unittest
from rows import Row, RowServo, ground_motion
import cv2
import numpy as np


def fruit(x,y):
    return (int(x*1280)-20,int(y*720)-24,40,24)


class RowTests(unittest.TestCase):
    def test_neighbouring_row_does_not_steal_target(self):
        row=Row()
        current=[fruit(.52,y) for y in (.36,.44,.55,.65)]
        neighbours=[fruit(.52+.17*(y-.23)/.43,y) for y in (.36,.44,.55,.7)]
        row.choose(current+neighbours,1280,720,0)
        self.assertEqual(row.choose(current[:-1]+neighbours,1280,720,1),current[-2])

    def test_row_end_waits_for_stable_absence(self):
        row=Row()
        row.choose([fruit(.52,.65)],1280,720,0)
        row.mark_collected(fruit(.52,.65),1280,720)
        row.choose([],1280,720,1)
        self.assertFalse(row.finished(2))
        self.assertTrue(row.finished(3.6))

    def test_detection_dropout_recovers_without_changing_row(self):
        row=Row()
        boxes=[fruit(.52,.6)]
        row.choose(boxes,1280,720,0)
        row.harvested=1
        row.choose([],1280,720,1)
        row.choose(boxes,1280,720,2)
        self.assertFalse(row.finished(10))

    def test_empty_unharvested_row_does_not_trigger_turn(self):
        row=Row()
        row.choose([fruit(.52,.6)],1280,720,0)
        row.choose([],1280,720,1)
        self.assertFalse(row.finished(100))

    def test_row_identity_moves_with_observed_target(self):
        row=Row()
        old=fruit(.52,.5)
        row.choose([old],1280,720,0)
        new=(old[0]+24,old[1]+30,old[2],old[3])
        row.observed_shift(old,new,1280,720)
        self.assertIn(new,row.members([new],1280,720))

    def test_straight_ahead_target_uses_forward_command(self):
        self.assertEqual(RowServo().action((.52,.4)).key,'w')
        self.assertEqual(RowServo().action((.52,.65)).key,'e')
        self.assertEqual(RowServo().action((.62,.4)).key,'pause')

    def test_row_tracking_never_strafes_or_reverses(self):
        for x in (.2,.52,.8):
            for y in (.3,.65,.76):
                self.assertNotIn(RowServo().action((x,y)).key,('a','s','d'))

    def test_hidden_remaining_fruit_prevents_row_change(self):
        row=Row()
        boxes=[fruit(.52,.4),fruit(.52,.65)]
        row.choose(boxes,1280,720,0)
        row.mark_collected(boxes[-1],1280,720)
        row.choose([],1280,720,1)
        self.assertFalse(row.finished(100))

    def test_e_handled_fruit_is_not_selected_again(self):
        row=Row()
        boxes=[fruit(.52,.4),fruit(.52,.65)]
        row.choose(boxes,1280,720,0)
        row.mark_collected(boxes[-1],1280,720)
        self.assertEqual(row.choose(boxes,1280,720,10),boxes[0])

    def test_camera_projection_preserves_same_row(self):
        row=Row()
        boxes=[fruit(.52,.4),fruit(.52,.65)]
        row.choose(boxes,1280,720,0)
        row.mark_collected(boxes[-1],1280,720)
        matrix=np.array([[1.,0.,120.],[0.,1.,15.],[0.,0.,1.]])
        self.assertTrue(row.reproject(matrix,1280,720))
        moved=[(x+120,y+15,w,h) for x,y,w,h in boxes]
        self.assertEqual(row.choose(moved,1280,720,10),moved[0])

    def test_ground_tracking_measures_camera_translation(self):
        rng=np.random.default_rng(8)
        previous=rng.integers(0,256,(360,640,3),dtype=np.uint8)
        current=cv2.warpAffine(previous,np.float32([[1,0,7],[0,1,4]]),(640,360))
        matrix=ground_motion(previous,current)
        self.assertIsNotNone(matrix)
        np.testing.assert_allclose(matrix[:2,2],[7,4],atol=.5)

    def test_untrackable_ground_does_not_invent_direction(self):
        blank=np.zeros((360,640,3),np.uint8)
        self.assertIsNone(ground_motion(blank,blank))
