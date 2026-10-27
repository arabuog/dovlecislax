"""N toggles a timed forward/interact loop on Windows. No screen capture."""
import argparse
import sys
import threading
import time
from simple_cycle import Cycle


def main():
    parser=argparse.ArgumentParser(description='W, E o dată, pauză 7 secunde; N pornire/pauză.')
    parser.add_argument('--walk',type=float,default=1.8,help='Seconds holding W per cycle')
    parser.add_argument('--wait',type=float,default=7.0,help='Seconds after releasing E')
    args=parser.parse_args()
    try:
        cycle=Cycle(args.walk,args.wait)
    except ValueError as error:
        parser.error(str(error))
    if sys.platform != 'win32':
        parser.error('Controlul tastelor necesită Windows.')
    import pydirectinput as keys
    from pynput import keyboard
    from game_capture import WindowsDesktop
    desktop=WindowsDesktop()
    keys.PAUSE=0
    lock=threading.RLock()
    held=set()
    n_down=False

    def focused():
        window=desktop.snapshot()
        return window is not None and window.is_game and window.visible and not window.minimized

    def sync(wanted):
        for key in list(held-({wanted} if wanted else set())):
            # Key releases remain possible even if the mouse-corner failsafe fires.
            keys.keyUp.__wrapped__(key,_pause=False)
            held.discard(key)
        if wanted and wanted not in held:
            held.add(wanted)
            if not keys.keyDown(wanted):
                raise RuntimeError('Windows nu a acceptat apăsarea tastei.')

    def pause(reason):
        cycle.pause()
        sync(None)
        print(reason,flush=True)

    def on_press(key):
        nonlocal n_down
        if (getattr(key,'char',None) or '').lower() != 'n':
            return
        with lock:
            if n_down:
                return
            n_down=True
            if cycle.phase != 'idle':
                pause('Pauză; taste eliberate.')
            elif focused():
                cycle.start(time.monotonic())
                print('Pornit.',flush=True)
            else:
                print('Revino în FiveM înainte să apeși N.',flush=True)

    def on_release(key):
        nonlocal n_down
        if (getattr(key,'char',None) or '').lower() == 'n':
            with lock:
                n_down=False

    listener=keyboard.Listener(on_press=on_press,on_release=on_release)
    print(f'MOD SIMPLU: W {args.walk:g}s → E o dată → pauză {args.wait:g}s → repetă.',flush=True)
    print('N: pornire/pauză. Ctrl+C în consolă: închidere. Fără detecție sau rotire.',flush=True)
    try:
        listener.start()
        while listener.is_alive():
            with lock:
                if cycle.phase != 'idle' and not focused():
                    pause('FiveM nu mai este în prim-plan; pauză.')
                else:
                    sync(cycle.tick(time.monotonic()))
            time.sleep(.01)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        with lock:
            pause('Oprit.')


if __name__ == '__main__':
    main()
