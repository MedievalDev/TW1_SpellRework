"""Extract particle files from Graphics.wd into ref/ and list the files they reference.

    py tools/prtrefs.py Magic/POISONCLOUD_MISSILE.prt ...
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import wdtool as W  # noqa: E402

SEP = chr(92)
ARC = os.path.join(W.GAME, 'WDFiles', 'Graphics.wd')
REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ref')

for n in sys.argv[1:]:
    inner = SEP.join(['Particles'] + n.replace('/', SEP).split(SEP))
    e = W.find(ARC, inner)
    d = W.read(ARC, e)
    open(os.path.join(REF, os.path.basename(inner)), 'wb').write(d)
    print(n, len(d))
    for m in sorted(set(re.findall(rb'[A-Za-z0-9_\ ]{3,}\.(?:DDS|dds|prt|tga|vdf|wav|mtr)', d))):
        print('   ', m.decode())
