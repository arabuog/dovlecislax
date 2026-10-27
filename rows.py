"""Keep a screen-space row identity instead of selecting the closest fruit anew."""
import numpy as np
import cv2
from navigation import Action, point


class Row:
    def __init__(self):
        self.line = None
        self.harvested = 0
        self.missing_since = None
        self.remaining = []
        self.collected = []

    def mark_collected(self, box, width, height):
        p = point(box, width, height)
        self.collected.append(p)
        self.remaining = [q for q in self.remaining if np.linalg.norm(q-p) > .04]
        self.harvested += 1

    def reproject(self, matrix, width, height):
        scale = np.diag((width, height, 1.))
        normal = np.linalg.inv(scale) @ matrix @ scale
        if self.line is not None:
            line = np.linalg.inv(normal).T @ np.array((1.,-self.line[0],-self.line[1]))
            if abs(line[0]) < .05:
                return False
            self.line = np.array((-line[1]/line[0],-line[2]/line[0]))
        for name in ('remaining','collected'):
            transformed=[]
            for p in getattr(self,name):
                q=normal @ np.array((*p,1.))
                if abs(q[2]) < .01:
                    return False
                transformed.append(q[:2]/q[2])
            setattr(self,name,transformed)
        return True

    def acquire(self, boxes, width, height):
        if not boxes:
            return None
        seed = min(boxes, key=lambda b: abs(point(b,width,height)[0]-.52)
                   + max(0,.66-point(b,width,height)[1])*.6)
        p = point(seed,width,height)
        # Seed the row through a perspective vanishing point, then fit its fruit.
        a = (p[0]-.52)/max(.1,p[1]-.23)
        self.line = np.array((a, p[0]-a*p[1]))
        members = self.members(boxes,width,height)
        if len(members) >= 3:
            pts = np.array([point(b,width,height) for b in members])
            if np.ptp(pts[:,1]) > .08:
                self.line = np.polyfit(pts[:,1],pts[:,0],1)
        return seed

    def members(self, boxes, width, height):
        if self.line is None:
            return []
        result=[]
        for box in boxes:
            p=point(box,width,height)
            tolerance = max(.012, .035*(p[1]-.23)/.43)
            if abs(p[0]-np.polyval(self.line,p[1])) <= tolerance:
                if not any(np.linalg.norm(p-q) < .04 for q in self.collected):
                    result.append(box)
        return result

    def observed_shift(self, old_box, new_box, width, height):
        if self.line is not None:
            dx,dy = point(new_box,width,height)-point(old_box,width,height)
            self.line[1] += dx-self.line[0]*dy

    def choose(self, boxes, width, height, now):
        if self.line is None:
            target=self.acquire(boxes,width,height)
        else:
            members=self.members(boxes,width,height)
            target=max(members,key=lambda b: point(b,width,height)[1],default=None)
        if self.line is not None:
            for box in self.members(boxes,width,height):
                p=point(box,width,height)
                if not any(np.linalg.norm(p-q) < .04 for q in self.remaining):
                    self.remaining.append(p)
        if target is None:
            if self.missing_since is None:
                self.missing_since=now
        else:
            self.missing_since=None
        return target

    def finished(self, now):
        return (self.harvested > 0 and not self.remaining and self.missing_since is not None
                and now-self.missing_since >= 2.5)


def ground_motion(previous, current):
    """Estimate a ground-plane projection. Return None for unreliable camera motion."""
    if previous.shape != current.shape:
        return None
    h,w=previous.shape[:2]
    a=cv2.cvtColor(previous,cv2.COLOR_BGR2GRAY)
    b=cv2.cvtColor(current,cv2.COLOR_BGR2GRAY)
    mask=np.zeros((h,w),np.uint8)
    mask[int(h*.35):int(h*.78),int(w*.1):int(w*.95)]=255
    mask[int(h*.55):,int(w*.38):int(w*.65)]=0
    points=cv2.goodFeaturesToTrack(a,250,.015,8,mask=mask)
    if points is None or len(points)<15:
        return None
    nxt,status,_=cv2.calcOpticalFlowPyrLK(a,b,points,None)
    if nxt is None:
        return None
    back,reverse,_=cv2.calcOpticalFlowPyrLK(b,a,nxt,None)
    if back is None:
        return None
    good=(status.ravel()==1)&(reverse.ravel()==1)&(np.linalg.norm((points-back).reshape(-1,2),axis=1)<1.5)
    src=points.reshape(-1,2)[good]
    dst=nxt.reshape(-1,2)[good]
    if len(src)<15:
        return None
    matrix,inliers=cv2.findHomography(src,dst,cv2.RANSAC,2.5)
    if matrix is None or inliers is None or inliers.sum()<12 or inliers.mean()<.6:
        return None
    supported=src[inliers.ravel().astype(bool)]
    if np.ptp(supported[:,0])<w*.25 or np.ptp(supported[:,1])<h*.12:
        return None
    if not np.all(np.isfinite(matrix)) or np.linalg.cond(matrix)>1e7:
        return None
    return matrix


class RowServo:
    def __init__(self, collect_y=.66):
        self.goal=collect_y

    def action(self, position):
        x,y=position
        if abs(x-.52) > .045:
            return Action('pause', 0)
        if y < self.goal-.035:
            return Action('w', .18 if y<self.goal-.12 else .06)
        if y > self.goal+.07:
            return Action('pause', 0)
        return Action('e',.05)

    def observe(self, *_):
        pass
