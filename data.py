"""Data files of the SpellRework mod: PAR, language file, Tornado card art.

entries(lang, guid) returns the WD entries for build.py. Nothing here is
written into the game folder.

PAR (Update16 TwoWorlds.par as base):
- SoundPack SND_PUSHWAVE_HIT: the original names the cue MAGIC_PUSHWAVE_HIT,
  the sound bank has MAGIC_PUSH_WAVE_HIT - that is why Push Wave is silent.
- Dynamics SR_BURNING: flames on a burning unit (FIRESHIELD_WRK's look
  without its force field, which would push attackers away).
- Missiles MIS_TORNADO and MagicCard MAGIC_TORNADO (air, row 1, column 4).
- MIS_PUSH_WAVE: own brighter effect SR_PUSH_WAVE.prt, Dynamics SR_PUSH_HIT
  (Magic Hammer impact recoloured) on every unit it hits.
PAR references are (list << 16) | index; new entries are appended to the
end of their list, so no existing reference moves.
"""
import copy
import os
import sys

sys.path.insert(0, r'C:\Users\marco\Desktop\TwStuff\QuestForge')
import tw1_lan  # noqa: E402
import tw1_par  # noqa: E402

import pardump as P  # noqa: E402
import wdtool as W  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
SEP = chr(92)
ART = os.path.join(ROOT, 'art')

PAR_INNER = SEP.join(['Parameters', 'TwoWorlds.par'])
LAN_INNER = SEP.join(['Language', 'ZZ_SpellRework.lan'])
CARD_PRT = SEP.join(['Particles', 'Magic', 'TORNADO_CARD.prt'])
CARD_TEX = SEP.join(['Textures', 'Particles', 'Cards', 'AIR_TORNADO1.DDS'])
SWIRL_TEX = SEP.join(['Textures', 'Particles', 'Symbols', 'SR_TORNADO_SWIRL4.dds'])
CARD_ICON = SEP.join(['Textures', 'Interface', 'InventoryTextures', 'Particles', 'Magic', 'TORNADO_CARD.DDS'])

# Tornado missile: share of the magic damage per pulse, 4 pulses in 4 s
TORNADO_ELECTRIC = 21
TORNADO_PIERCING = 14


def find_entry(par, name):
    for li, (_u1, _u2, ents) in enumerate(par.lists):
        for ei, e in enumerate(ents):
            if e.name == name:
                return li, ei, e
    raise KeyError(name)


def ref(li, ei):
    return (li << 16) | ei


def append_clone(par, template, name):
    li, _ei, tmpl = find_entry(par, template)
    e = copy.deepcopy(tmpl)
    e.name = name
    par.lists[li][2].append(e)
    return li, len(par.lists[li][2]) - 1, e


def build_par():
    arc = os.path.join(W.GAME, 'WDFiles', 'Update16.wd')
    entry = W.find(arc, PAR_INNER)
    par = tw1_par.parse(W.read(arc, entry))

    # Push Wave sound: cue name as the sound bank spells it
    _li, _ei, snd = find_entry(par, 'SND_PUSHWAVE_HIT')
    assert snd.values[0] == 'MAGIC_PUSHWAVE_HIT', snd.values[0]
    snd.values[0] = 'MAGIC_PUSH_WAVE_HIT'

    # flames on burning units
    _li, _ei, burn = append_clone(par, 'FIRESHIELD_WRK', 'SR_BURNING')
    burn.values[15] = 0      # forcefieldType
    burn.values[16] = 0      # forcefieldAmount

    # Tornado missile: an area at the target like Poison Cloud, lightning look
    mli, mei, mis = append_clone(par, 'MIS_POISONCLOUD', 'MIS_TORNADO')
    _l, _e, storm = find_entry(par, 'MIS_LIGHTINGSTORM')
    _l, _e, emp = find_entry(par, 'MIS_LIGHTING')
    mis.values[1] = 'Magic' + SEP + 'TORNADO_MISSILE.prt'   # own effect (art/), see README
    mis.values[4] = emp.values[4]                         # SNDSET_EMP_MISSILE
    for i in range(12, 28):
        mis.values[i] = 0
    mis.values[12] = mis.values[13] = TORNADO_PIERCING     # misDamPiercing min/max
    mis.values[22] = mis.values[23] = TORNADO_ELECTRIC     # misDamElectric min/max
    mis.values[31] = 384                                   # 6 m radius
    mis.values[35] = 120                                   # 4 s
    mis.values[36] = 30                                    # a hit every second
    mis.values[45] = list(storm.values[45])                # LIGHTINGSTORM_HIT on struck units
    mis.values[47] = list(storm.values[47])

    # Tornado card: air school, first ring, the free slot (column 3, row 0)
    _l, _e, card = append_clone(par, 'MAGIC_POISONCLOUD', 'MAGIC_TORNADO')
    _l, _e, light = find_entry(par, 'MAGIC_LIGHTING')
    card.values[1] = 'Magic' + SEP + 'TORNADO_CARD.prt'
    card.values[24] = 0                  # cardMagicSchool: air
    card.values[25] = 1                  # cardRequiredMagicSchoolSkill
    card.values[27] = light.values[27]   # cardUsedMana (missile mana comes from the script)
    card.values[30] = light.values[30]   # cast animation
    card.values[31] = list(light.values[31])   # air cast effect
    card.values[47] = [ref(mli, mei)]    # $cardMissileID
    card.values[52] = [3, 0]             # cardMagicDialogInventoryPosition

    # Push Wave look: brighter wave (own copy of its effect), a wind impact on every unit it hits
    _l, _e, wave = find_entry(par, 'MIS_PUSH_WAVE')
    assert wave.values[1] == 'Magic' + SEP + 'PUSH_WAVE_HIT.prt', wave.values[1]
    wave.values[1] = 'Magic' + SEP + 'SR_PUSH_WAVE.prt'
    hli, hei, hit = append_clone(par, 'MAGICHAMMER_HIT', 'SR_PUSH_HIT')
    hit.values[1] = 'Magic' + SEP + 'SR_PUSH_UNIT_HIT.prt'
    assert wave.values[45] == [], wave.values[45]
    wave.values[45] = [ref(hli, hei)]    # $objectExplosionID
    return par, entry


def par_entry(guid):
    par, retail = build_par()
    data = tw1_par.build(par)
    check = tw1_par.parse(data)
    names = {e.name for e in check.entries()}
    assert {'MAGIC_TORNADO', 'MIS_TORNADO', 'SR_BURNING', 'SR_PUSH_HIT'} <= names
    return {'path': PAR_INNER, 'data': data, 'flags': retail['flags'], 'res': retail['res'],
            'id': retail['id'], 'guid': guid('TwoWorlds.par')}


def lan_entry(lang):
    import texts
    data = tw1_lan.build(texts.TEXTS[lang])
    return {'path': LAN_INNER, 'data': data, 'flags': 0x01, 'res': None, 'id': None, 'guid': None}


def art_entries():
    out = []
    for inner, name in ((CARD_PRT, 'TORNADO_CARD.prt'), (CARD_TEX, 'AIR_TORNADO1.DDS'),
                        (CARD_ICON, 'TORNADO_CARD.DDS'), (SWIRL_TEX, 'SR_TORNADO_SWIRL4.dds'),
                        (SEP.join(['Particles', 'Magic', 'TORNADO_MISSILE.prt']), 'TORNADO_MISSILE.prt'),
                        (SEP.join(['Particles', 'Magic', 'SR_PUSH_WAVE.prt']), 'SR_PUSH_WAVE.prt'),
                        (SEP.join(['Particles', 'Magic', 'SR_PUSH_UNIT_HIT.prt']), 'SR_PUSH_UNIT_HIT.prt')):
        path = os.path.join(ART, name)
        if not os.path.exists(path):
            raise SystemExit('missing art file ' + path + ' (run make_art.py)')
        out.append({'path': inner, 'data': open(path, 'rb').read(), 'flags': 0x01,
                    'res': None, 'id': None, 'guid': None})
    return out


def entries(lang, guid):
    return [par_entry(guid), lan_entry(lang)] + art_entries()
