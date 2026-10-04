"""Picture of a ParticleEdit window by PrintWindow (works under other windows): py pe_shot.py <title prefix> <out.png> [scale]"""
import ctypes
import sys

import win32gui
import win32ui
from PIL import Image

sys.path.insert(0, r'C:\Users\marco\Desktop\wicked\tw1probe')
import pe_tree  # noqa: E402


def shot(prefix, out, scale=1.0):
    h = next(v for k, v in pe_tree.windows().items() if k.startswith(prefix))
    l, t, r, b = win32gui.GetWindowRect(h)
    w, hh = r - l, b - t
    hdc = win32gui.GetWindowDC(h)
    src = win32ui.CreateDCFromHandle(hdc)
    mem = src.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src, w, hh)
    mem.SelectObject(bmp)
    ctypes.windll.user32.PrintWindow(h, mem.GetSafeHdc(), 2)
    info = bmp.GetInfo()
    img = Image.frombuffer('RGB', (info['bmWidth'], info['bmHeight']), bmp.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
    mem.DeleteDC(); src.DeleteDC(); win32gui.ReleaseDC(h, hdc); win32gui.DeleteObject(bmp.GetHandle())
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    img.save(out)
    return (l, t, r, b)


if __name__ == '__main__':
    print(shot(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0))
