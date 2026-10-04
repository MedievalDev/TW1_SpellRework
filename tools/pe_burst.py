"""Frames of a short effect in ParticleEdit, densely from its start: py tools/pe_burst.py out.png [--zoom N] Folder/Effect ...

One row per effect, six frames over the first 1.2 s.
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
    zoom = -15
    names = []
    while argv:
        a = argv.pop(0)
        if a == '--zoom':
            zoom = int(argv.pop(0))
        else:
            names.append(a.replace('/', SEP))
    w, h = 325, 298
    cols = 6
    sheet = Image.new('RGB', (cols * w, len(names) * h))
    for i, n in enumerate(names):
        pe_cam.command(0x813a)
        pe_rec.show(n)
        pe_cam.command(0x80f6)
        pe_cam.wheel(zoom)
        pe_cam.pump_active(1.5)                 # let the first cycle end
        fr = pe_cam.pump_active(1.3, grab_every=0.2)
        for j, f in enumerate(fr[:cols]):
            sheet.paste(f.resize((w, h)), (j * w, i * h))
    sheet.save(out)
    print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1:])
