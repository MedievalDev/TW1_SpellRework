"""Build the SpellRework mod.

    py build.py              out/SpellRework.wd (English texts) and out/SpellRework_DE.wd (German)
    py build.py --install    also copy the German one into <Game>/Mods as SpellRework.wd and switch it on
    py build.py --install-en the same with the English texts

Steps: fresh copy of the SDK scripts (base/ -> src/), copy rework/*.ech,
run the patch scripts, compile RPGCompute and the campaign with the SDK
compiler, build the PAR, the language file and the card art (data.py),
pack one WD per language.

Script entries keep the retail metadata (flags 0x3b, resource name, class
id) with a NEW GUID each - the engine keys scripts by GUID, the retail one
would make it keep the original. GUIDs are kept in guids.json so every
rebuild is the same script for the engine.
"""
import json
import os
import shutil
import subprocess
import sys

import wdtool as W

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, 'base')
SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'out')
SEP = chr(92)
EARTHC = SEP.join(['D:', 'Games', 'TwoWorldsSDK', 'Tools', 'EarthC.bat'])
GUIDS = os.path.join(ROOT, 'guids.json')
PATCHES = ['patch_phase1.py', 'patch_phase2.py']

# (source folder in src, .ec file, path inside the game archives)
SCRIPTS = [
    ('RPGCompute', 'RPGCompute.ec', SEP.join(['Scripts', 'RPGCompute', 'RPGCompute.eco'])),
    ('Campaigns', 'TwoWorldsCampaign.ec', SEP.join(['Scripts', 'Campaigns', 'TwoWorldsCampaign.eco'])),
]
REWORK = [('SpellRework.ech', 'RPGCompute'), ('SpellReworkCampaign.ech', 'Campaigns')]


def fresh_copy():
    """src = base again, without deleting the folder (a shell may sit in it)."""
    for dirpath, _dirs, names in os.walk(SRC):
        for n in names:
            rel = os.path.relpath(os.path.join(dirpath, n), SRC)
            if not os.path.exists(os.path.join(BASE, rel)):
                os.remove(os.path.join(dirpath, n))
    shutil.copytree(BASE, SRC, dirs_exist_ok=True)
    for folder, ec, _inner in SCRIPTS:
        eco = os.path.join(SRC, folder, ec + 'o')
        if os.path.exists(eco):
            os.remove(eco)
    for name, folder in REWORK:
        shutil.copy2(os.path.join(ROOT, 'rework', name), os.path.join(SRC, folder, name))


def compile_script(folder, ec):
    cwd = os.path.join(SRC, folder)
    r = subprocess.run(['cmd', '/c', EARTHC, ec], cwd=cwd, capture_output=True, text=True, encoding='latin-1')
    out = (r.stdout + r.stderr).strip()
    eco = os.path.join(cwd, ec + 'o')
    if 'error' in out.lower() or not os.path.exists(eco):
        raise SystemExit('compile %s failed:\n%s' % (ec, out))
    if 'warning' in out.lower():
        print(out)
    with open(eco, 'rb') as f:
        return W.eco_body(f.read())


def guid(key):
    data = json.load(open(GUIDS)) if os.path.exists(GUIDS) else {}
    if key not in data:
        # keep the GUID of the first phase-1 build
        old = os.path.join(ROOT, 'guid_rpgcompute.txt')
        data[key] = open(old).read().strip() if key == 'RPGCompute' and os.path.exists(old) else os.urandom(16).hex()
        json.dump(data, open(GUIDS, 'w'), indent=1)
    return bytes.fromhex(data[key])


def script_entries():
    files = []
    for folder, ec, inner in SCRIPTS:
        body = compile_script(folder, ec)
        _arc, retail = W.latest(inner)
        files.append({'path': inner, 'data': body, 'flags': retail['flags'], 'res': retail['res'],
                      'id': retail['id'], 'guid': guid(folder)})
        print('compiled %-22s %7d bytes' % (ec, len(body)))
    return files


def main():
    fresh_copy()
    for p in PATCHES:
        subprocess.run([sys.executable, os.path.join(ROOT, p)], check=True)
    scripts = script_entries()
    import data
    os.makedirs(OUT, exist_ok=True)
    outs = {}
    for lang, name in (('en', 'SpellRework.wd'), ('de', 'SpellRework_DE.wd')):
        files = scripts + data.entries(lang, guid)
        out = os.path.join(OUT, name)
        W.build(out, files)
        for f in files:
            chk = W.find(out, f['path'])
            assert W.read(out, chk) == f['data'], f['path']
        outs[lang] = out
        print('built', out, '-', len(files), 'files')
    target = None
    if '--install' in sys.argv:
        target = outs['de']
    elif '--install-en' in sys.argv:
        target = outs['en']
    if target:
        import winreg
        mods = os.path.join(W.GAME, 'Mods')
        shutil.copy2(target, os.path.join(mods, 'SpellRework.wd'))
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Reality Pump\TwoWorlds\Mods') as k:
            winreg.SetValueEx(k, 'SpellRework.wd', 0, winreg.REG_DWORD, 1)
        print('installed and switched on:', os.path.join(mods, 'SpellRework.wd'), '(%s)' % os.path.basename(target))


if __name__ == '__main__':
    main()
