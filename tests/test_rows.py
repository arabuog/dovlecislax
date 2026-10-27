import unittest
from rows import Row, RowServo


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
        row.harvested=1
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
        self.assertEqual(RowServo().action((.62,.4)).key,'d')
