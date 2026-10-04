"""Print PAR entries with field names: py pardump.py NAME [NAME ...] (prefix* allowed)."""
import json
import os
import sys

sys.path.insert(0, r'C:\Users\marco\Desktop\TwStuff\QuestForge')
import tw1_par  # noqa: E402
import wdtool as W  # noqa: E402

FIELDS = json.load(open(r'C:\Users\marco\Desktop\TwStuff\QuestForge\tw1_sdk_fields.json', encoding='utf-8'))
SEP = chr(92)


def load_par():
    arc = os.path.join(W.GAME, 'WDFiles', 'Update16.wd')
    e = W.find(arc, 'Parameters' + SEP + 'TwoWorlds.par')
    return tw1_par.parse(W.read(arc, e))


def columns(name, list_sheet=None):
    sheet = FIELDS['entries'].get(name) or list_sheet
    return sheet, FIELDS['sheets'].get(sheet, [])


def all_entries(par):
    for lst in par.lists:
        unk1, unk2, ents = lst
        sheet = None
        for e in ents:
            s = FIELDS['entries'].get(e.name)
            if s:
                sheet = s
                break
        for e in ents:
            yield e, sheet


if __name__ == '__main__':
    par = load_par()
    want = sys.argv[1:]
    for e, lsheet in all_entries(par):
        if not any(e.name == w or (w.endswith('*') and e.name.startswith(w[:-1])) for w in want):
            continue
        sheet, cols = columns(e.name, lsheet)
        print('==', e.name, sheet)
        for i, v in enumerate(e.values):
            print('  %2d %-34s %r' % (i, cols[i] if i < len(cols) else '?', v))


def by_id(par, ref):
    """Entry for a PAR reference id ((list << 16) | index)."""
    li, ei = ref >> 16, ref & 0xFFFF
    if 0 <= li < len(par.lists) and 0 <= ei < len(par.lists[li][2]):
        return par.lists[li][2][ei]
    return None


def list_sheet(par, li):
    for e in par.lists[li][2]:
        s = FIELDS['entries'].get(e.name)
        if s:
            return s
    return None


def show(par, e, sheet):
    _s, cols = columns(e.name, sheet)
    print('==', e.name, sheet)
    for i, v in enumerate(e.values):
        name = cols[i] if i < len(cols) else '?'
        extra = ''
        if name.startswith('$'):
            refs = v if isinstance(v, list) else [v]
            extra = '  -> ' + ', '.join((by_id(par, r).name if r and by_id(par, r) else str(r)) for r in refs)
        print('  %2d %-34s %r%s' % (i, name, v, extra))
