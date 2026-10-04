"""Contact sheet of ParticleEdit previews: py tools/pe_preview.py out.png [--zoom N] [--seconds S] Folder/Effect ...

Each effect is selected in ParticleEdit's scene tree, the camera reset and
zoomed (wheel N, negative = out), played for S seconds; two frames (early,
late) go into the sheet. ParticleEdit must be running; it is brought to the
front while it plays.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.expanduser('~'), 'Desktop', 'wicked', 'tw1probe'))
import pe_cam  # noqa: E402
import pe_rec  # noqa: E402
from PIL import Image  # noqa: E402

SEP = chr(92)


def main(argv):
    out = argv.pop(0)
    zoom, seconds = -8, 4.0
    names = []
    while argv:
        a = argv.pop(0)
        if a == '--zoom':
            zoom = int(argv.pop(0))
        elif a == '--seconds':
            seconds = float(argv.pop(0))
        else:
            names.append(a.replace('/', SEP))
    w, h = 434, 398
    sheet = Image.new('RGB', (len(names) * w, 2 * h))
    for i, n in enumerate(names):
        pe_rec.show(n)
        pe_cam.command(0x80f6)
        if zoom:
            pe_cam.wheel(zoom)
        fr = pe_cam.pump_active(seconds, grab_every=0.5)
        for j, f in enumerate((fr[min(3, len(fr) - 1)], fr[-1])):
            sheet.paste(f.resize((w, h)), (i * w, j * h))
    sheet.save(out)
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1:])
