import unittest
import cv2
import numpy as np
from navigation import Action, Scan, Servo, choose, follow


class NavigationTests(unittest.TestCase):
    def test_can_choose_neighbouring_rows(self):
        self.assertEqual(choose([(850,400,80,40)],1280,720),(850,400,80,40))
        self.assertEqual(choose([(250,400,80,40)],1280,720),(250,400,80,40))

    def test_rejects_tiny_distant_noise(self):
        self.assertIsNone(choose([(650,300,4,4)],1280,720))

    def test_servo_converges_from_both_sides_and_directions(self):
        # Closed-loop simulation with an independently specified camera response.
        for start in [(0.2,.4),(.85,.4),(.2,.72),(.85,.72)]:
            servo = Servo()
            p = np.array(start,dtype=float)
            rates = {'w':np.array((.01,.2)), 'd':np.array((-.24,.01))}
            for step in range(150):
                action = servo.action(p)
                if action.key == 'e':
                    break
                base = {'s':'w','a':'d'}.get(action.key,action.key)
                sign = -1 if action.key in ('s','a') else 1
                after = p+rates[base]*action.seconds*sign
                servo.observe(p,after,action)
                p = after
            self.assertEqual(action.key,'e', f'Failed from {start}: {p}')

    def test_does_not_collect_when_far_to_either_side(self):
        self.assertNotEqual(Servo().action((.2,.66)).key,'e')
        self.assertNotEqual(Servo().action((.8,.66)).key,'e')

    def test_scan_is_bounded_and_resettable(self):
        scan=Scan(3)
        self.assertEqual([scan.next() for _ in range(5)],[True,True,True,False,False])
        scan.reset()
        self.assertTrue(scan.next())

    def test_tracks_same_textured_object_instead_of_neighbour(self):
        rng=np.random.default_rng(7)
        before=np.zeros((240,320,3),np.uint8)
        before[90:130,100:160]=rng.integers(0,256,(40,60,3),dtype=np.uint8)
        after=cv2.warpAffine(before,np.float32([[1,0,9],[0,1,7]]),(320,240))
        result=follow(before,after,(100,90,60,40),[(109,97,60,40),(180,80,40,30)])
        self.assertEqual(result,(109,97,60,40))

    def test_rejects_unmatched_camera_cut(self):
        blank=np.zeros((240,320,3),np.uint8)
        self.assertIsNone(follow(blank,blank,(100,90,60,40),[(110,90,60,40)]))

    def test_bad_motion_does_not_corrupt_control_matrix(self):
        servo=Servo()
        initial=servo.matrix.copy()
        servo.observe((.5,.4),(.9,.8),Action('w',.1))
        np.testing.assert_array_equal(initial,servo.matrix)
