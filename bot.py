"""Experimental visual navigation on Windows. F3 toggles; Ctrl+C exits."""
import argparse
import ctypes
import sys
import threading
import time

import cv2
from detector import detect
from navigation import choose, follow, point
from rows import Row, RowServo, ground_motion
from game_capture import GameCapture, WindowsDesktop


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--collect-y', type=float, default=.66)
    parser.add_argument('--wait', type=float, default=9)
    parser.add_argument('--turn-pixels', type=int, default=1800,
                        help='Mouse movement for one 180-degree row turn; MUST be calibrated')
    parser.add_argument('--row-shift', type=float, default=.65,
                        help='Seconds of sideways movement between rows; requires calibration')
    parser.add_argument('--max-minutes', type=float, default=120)
    args = parser.parse_args()
    if not .4 <= args.collect_y <= .73 or not 1 <= args.wait <= 30:
        parser.error('collect-y must be .4–.73; wait must be 1–30 seconds')
    if not 100 <= args.turn_pixels <= 10000 or args.max_minutes <= 0 or not .1 <= args.row_shift <= 3:
        parser.error('turn-pixels: 100–10000; row-shift: .1–3; max-minutes must be positive')
    if sys.platform != 'win32':
        parser.error('Game control requires Windows. Portable tests run on Linux.')
    import mss
    import pydirectinput as keys
    from pynput import keyboard
    ctypes.windll.user32.SetProcessDPIAware()
    keys.PAUSE = .01
    active = threading.Event()
    lock = threading.RLock()
    held = set()
    pressed = set()
    generation = 0
    desktop = WindowsDesktop()

    def focused():
        window = desktop.snapshot()
        return window is not None and window.is_game and window.visible and not window.minimized

    def release():
        with lock:
            for key in list(held):
                # A mouse-corner failsafe must never prevent key release.
                keys.keyUp.__wrapped__(key, _pause=False)
                held.discard(key)

    def pause(reason):
        nonlocal generation
        with lock:
            active.clear()
            generation += 1
            release()
        print(reason, flush=True)

    def on_press(key):
        nonlocal generation
        if key == keyboard.Key.f3 and key not in pressed and not args.preview:
            with lock:
                if active.is_set():
                    pause('Pauză. Taste eliberate.')
                elif focused():
                    generation += 1
                    active.set()
                    print('Pornit: navigare vizuală experimentală.', flush=True)
                else:
                    print('Pune FiveM în prim-plan înainte de F3.', flush=True)
        pressed.add(key)

    def on_release(key):
        pressed.discard(key)

    def pulse(key, seconds, token, sprint=False):
        with lock:
            if not active.is_set() or token != generation:
                return False
            if not focused():
                pause('Focus pierdut.')
                return False
            wanted = {key,'shift'} if sprint else {key}
            for old in list(held-wanted):
                keys.keyUp.__wrapped__(old, _pause=False)
                held.discard(old)
            for new in sorted(wanted-held):
                held.add(new)
                if not keys.keyDown(new):
                    pause('Windows nu a acceptat comanda de tastatură.')
                    return False
        try:
            end = time.monotonic()+seconds
            while active.is_set() and token == generation and time.monotonic() < end:
                if not focused():
                    pause('Focus pierdut.')
                    return False
                time.sleep(.01)
            return active.is_set() and token == generation
        finally:
            if key != 'w' or not active.is_set() or token != generation:
                release()

    def rotate(token, direction):
        release()
        # Small interruptible movements, rather than one long mouse operation.
        for _ in range(36):
            with lock:
                if not active.is_set() or token != generation:
                    return False
                if not focused():
                    pause('Focus pierdut.')
                    return False
                keys.moveRel(direction*round(args.turn_pixels/36), 0, relative=True)
            time.sleep(.015)
        return True

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    session = -1
    target = previous = pending = collecting = None
    motion_previous = None
    motion_lost_since = None
    row = Row()
    row_index = 0
    servo = RowServo(args.collect_y)
    failures = 0
    attempts = 0
    target_since = started = time.monotonic()
    print('F3: pornire/pauză. Ctrl+C: închidere. Mod experimental, nu garanție de acoperire.')
    try:
        with mss.mss() as capture:
            source = GameCapture(desktop, capture)
            last_size = None
            notice_at = 0
            while listener.is_alive():
                frame = source.grab()
                if frame is None:
                    if active.is_set():
                        pause('Captură suspendată: FiveM trebuie să fie vizibil și în prim-plan.')
                    if time.monotonic() - notice_at > 5:
                        print('Aștept fereastra jocului FiveM în prim-plan. Discord nu este capturat.', flush=True)
                        notice_at = time.monotonic()
                    if args.preview and cv2.waitKey(30) & 255 == ord('q'):
                        break
                    time.sleep(.1)
                    continue
                if last_size is not None and frame.shape[:2] != last_size:
                    target = previous = pending = collecting = None
                    if active.is_set():
                        pause('Dimensiunea jocului s-a schimbat; apasă F3 pentru reluare.')
                last_size = frame.shape[:2]
                h, w = frame.shape[:2]
                boxes = detect(frame)
                if args.preview:
                    selected = row.choose(boxes, w, h, time.monotonic())
                    for box in boxes:
                        x,y,bw,bh = box
                        color = (0,255,0) if box != selected else (255,0,255)
                        cv2.rectangle(frame,(x,y),(x+bw,y+bh),color,2)
                    cv2.circle(frame,(int(.52*w),int(args.collect_y*h)),8,(255,255,255),2)
                    cv2.imshow('Detectare: Q inchide; fara comenzi in joc',frame)
                    if cv2.waitKey(30) & 255 == ord('q'):
                        break
                    continue
                if not active.is_set():
                    time.sleep(.05)
                    continue
                token = generation
                if session != token:
                    session = token
                    target = previous = pending = collecting = None
                    row = Row()
                    row_index = 0
                    servo = RowServo(args.collect_y)
                    failures = attempts = 0
                    target_since = started = time.monotonic()
                    motion_previous = None
                    motion_lost_since = None
                if not focused():
                    pause('Focus pierdut.')
                    continue
                now = time.monotonic()
                if motion_previous is not None and row.line is not None:
                    matrix = ground_motion(motion_previous, frame)
                    if matrix is None or not row.reproject(matrix,w,h):
                        release()
                        if motion_lost_since is None:
                            motion_lost_since = now
                        elif now-motion_lost_since > .7:
                            pause('Direcția rândului nu mai poate fi urmărită; nu aleg alt rând.')
                        time.sleep(.05)
                        continue
                    motion_lost_since = None
                motion_previous = frame
                if now-started > args.max_minutes*60:
                    pause('Limită de sesiune atinsă.')
                    continue
                if collecting is not None:
                    if now < collecting:
                        time.sleep(.05)
                        continue
                    print('Așteptarea după E s-a terminat; continui același rând.',flush=True)
                    collecting = target = previous = pending = None
                    continue
                if target is not None and previous is not None:
                    matched = follow(previous,frame,target,boxes)
                    if matched is not None:
                        if pending is not None:
                            servo.observe(point(target,w,h),point(matched,w,h),pending)
                        target = matched
                    else:
                        release()
                        target = None
                    pending = None
                if target is None:
                    target = row.choose(boxes,w,h,now)
                    target_since = now
                if target is None:
                    release()
                    if row.finished(now):
                        direction = 1 if row_index % 2 == 0 else -1
                        print('Rând fără ținte vizibile; încerc trecerea la următorul.',flush=True)
                        if pulse('d' if direction>0 else 'a',args.row_shift,token):
                            rotate(token,direction)
                        row_index += 1
                        row = Row()
                        motion_previous = None
                        previous = pending = None
                        servo = RowServo(args.collect_y)
                        time.sleep(.4)
                    elif row.line is None:
                        pause('Nu găsesc un rând. Câmp complet nu este confirmat.')
                    elif row.missing_since is not None and now-row.missing_since > 6:
                        pause('Mai există poziții memorate pe rând, dar nu le pot vedea. Nu schimb rândul.')
                    else:
                        time.sleep(.1)
                    continue
                if now-target_since > 25:
                    pause('Nu pot ajunge la ținta de pe rând. Oprit fără rotire.')
                    continue
                action = servo.action(point(target,w,h))
                previous = frame
                sprint = action.key == 'w' and point(target,w,h)[1] < args.collect_y-.12
                if pulse(action.key,action.seconds,token,sprint=sprint):
                    if action.key == 'e':
                        row.mark_collected(target,w,h)
                        collecting = time.monotonic()+args.wait
                        previous = pending = None
                        attempts = 0
                    else:
                        pending = action
                # Let camera/animation settle before estimating displacement.
                time.sleep(.02 if action.key == 'w' else .12)
    finally:
        pause('Oprit.')
        listener.stop()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
