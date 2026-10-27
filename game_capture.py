"""Capture only the visible client area of the foreground FiveM game process."""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import ntpath
import re



@dataclass(frozen=True)
class Window:
    hwnd: int
    executable: str
    rect: tuple
    visible: bool = True
    minimized: bool = False

    @property
    def is_game(self):
        return bool(re.fullmatch(r'FiveM(?:_b\d+)?_GTAProcess\.exe',
                                 ntpath.basename(self.executable), re.IGNORECASE))


class WindowsDesktop:
    def __init__(self):
        self.user = ctypes.WinDLL('user32', use_last_error=True)
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.user.GetForegroundWindow.restype = wintypes.HWND
        self.user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        self.user.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user.IsIconic.argtypes = [wintypes.HWND]
        self.kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                          wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]

    def snapshot(self):
        hwnd = self.user.GetForegroundWindow()
        if not hwnd:
            return None
        pid = wintypes.DWORD()
        self.user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        # Metadata query only; does not read game memory.
        handle = self.kernel.OpenProcess(0x1000, False, pid.value)
        if not handle:
            return None
        try:
            size = wintypes.DWORD(32768)
            path = ctypes.create_unicode_buffer(size.value)
            if not self.kernel.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(size)):
                return None
        finally:
            self.kernel.CloseHandle(handle)
        rect = wintypes.RECT()
        origin = wintypes.POINT(0, 0)
        if not self.user.GetClientRect(hwnd, ctypes.byref(rect)):
            return None
        if not self.user.ClientToScreen(hwnd, ctypes.byref(origin)):
            return None
        return Window(int(hwnd), path.value,
                      (origin.x, origin.y, rect.right-rect.left, rect.bottom-rect.top),
                      bool(self.user.IsWindowVisible(hwnd)), bool(self.user.IsIconic(hwnd)))


class GameCapture:
    def __init__(self, desktop, capture):
        self.desktop = desktop
        self.capture = capture

    def source(self):
        window = self.desktop.snapshot()
        if window is None or not window.is_game or not window.visible or window.minimized:
            return None
        left, top, width, height = window.rect
        desktop = self.capture.monitors[0]
        if (width < 320 or height < 240 or left < desktop['left'] or top < desktop['top']
                or left+width > desktop['left']+desktop['width']
                or top+height > desktop['top']+desktop['height']):
            return None
        return window

    def grab(self):
        import numpy as np
        before = self.source()
        if before is None:
            return None
        x, y, w, h = before.rect
        frame = np.array(self.capture.grab(dict(left=x, top=y, width=w, height=h)))
        # Discard pixels if the user switched applications or moved the window.
        if self.source() != before:
            return None
        return frame[:, :, :3].copy()
