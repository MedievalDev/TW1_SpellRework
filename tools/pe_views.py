"""One effect in ParticleEdit from several camera angles: py tools/pe_views.py out.png Folder/Effect [--reload]

--reload re-reads the effect from disk first (File > Reload file from disk),
for a loose copy that changed since ParticleEdit loaded it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'Desktop', 'wicked', 'tw1probe'))
import pe_cam  # noqa: E402
import pe_rec  # noqa: E402
from PIL import Image  # noqa: E402

SEP = chr(92)
# (wheel, right-drag dx, dy): front-above, lower and side, further out
VIEWS = [(-30, 0, 0), (-30, 0, -120), (-45, 200, -120)]


def main(argv):
    out, name = argv[0], argv[1].replace('/', SEP)
    pe_cam.command(0x813a)          # clear all scene checks: only this effect plays
    pe_rec.show(name)
    if '--reload' in argv:
        pe_cam.command(0x8105)
        pe_rec.show(name)
    w, h = 434, 398
    sheet = Image.new('RGB', (len(VIEWS) * w, 2 * h))
    for i, (wheel, dx, dy) in enumerate(VIEWS):
        pe_cam.command(0x80f6)
        pe_cam.wheel(wheel)
        if dx or dy:
            pe_cam.drag(dx, dy, 'right')
        fr = pe_cam.pump_active(4.0, grab_every=0.5)
        for j, f in enumerate((fr[min(3, len(fr) - 1)], fr[-1])):
            sheet.paste(f.resize((w, h)), (i * w, j * h))
    sheet.save(out)
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1:])
