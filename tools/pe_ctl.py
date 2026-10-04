"""ParticleEdit controls by real keyboard input (MFC only takes edits typed into a focused field).

    import pe_ctl; pe_ctl.type_into(dialog_hwnd, ctrl_id, '2')
"""
import ctypes
import sys
import time

import win32api
import win32con
import win32gui
import win32process

sys.path.insert(0, r'C:\Users\marco\Desktop\wicked\tw1probe')
import pe_cam  # noqa: E402
import pe_tree  # noqa: E402

u32 = ctypes.windll.user32


def focus(h):
    pe_cam.activate()
    me = win32api.GetCurrentThreadId()
    other = win32process.GetWindowThreadProcessId(h)[0]
    u32.AttachThreadInput(me, other, True)
    try:
        win32gui.SetFocus(h)
    finally:
        u32.AttachThreadInput(me, other, False)
    time.sleep(0.15)


def key(vk, up=False):
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP if up else 0, 0)


def tap(vk, mod=None):
    if mod:
        key(mod)
    key(vk); key(vk, True)
    if mod:
        key(mod, True)
    time.sleep(0.05)


def type_text(text):
    for ch in text:
        vk = u32.VkKeyScanW(ord(ch))
        shift = (vk >> 8) & 1
        tap(vk & 0xFF, win32con.VK_SHIFT if shift else None)


def type_into(dlg, cid, text, commit=win32con.VK_TAB):
    h = win32gui.GetDlgItem(dlg, cid)
    focus(h)
    tap(ord('A'), win32con.VK_CONTROL)
    tap(win32con.VK_END); tap(win32con.VK_HOME, win32con.VK_SHIFT) if False else None
    win32gui.SendMessage(h, 0x00B1, 0, -1)       # EM_SETSEL all
    type_text(text)
    tap(commit)
    time.sleep(0.3)


def gettext(h):
    n = win32gui.SendMessage(h, win32con.WM_GETTEXTLENGTH, 0, 0)
    buf = win32gui.PyGetMemory if False else None
    b = ctypes.create_unicode_buffer(n + 2)
    u32.SendMessageW(h, win32con.WM_GETTEXT, n + 1, b)
    return b.value


def menu_state(cid, index=0):
    main = next(h for t, h in pe_tree.windows().items() if t.startswith('ParticleGen'))
    m = win32gui.GetSubMenu(win32gui.GetMenu(main), index)
    win32gui.SendMessage(main, win32con.WM_INITMENUPOPUP, m, 0)
    return u32.GetMenuState(m, cid, 0)
