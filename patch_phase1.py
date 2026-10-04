"""SpellRework phase 1: Blessing, Overpower and Concentration values, knockdown for Push and Push Wave.

Applies to src/ (a copy of the SDK scripts, base/ stays untouched). Every
anchor must occur exactly once; all files are written only after every
anchor matched. Sources are CRLF and latin-1 (Polish comments), kept as is.

Spec from Vince (Discord 01.10.2026, ListGuideForAirSchool1.rtf):
- Overpower (fire): +10 % damage on the first offensive spell within 78 s,
  120 mana. Each further card +10 %, +3 s, +5-6 mana, max 20 cards (+200 %).
  The fire magic skill does not raise the damage.
- Concentration (air): +10 % within 126 s, 271 mana. Each further card
  +10 %, +6 s, +14-15 mana, max 20 cards.
- Blessing (air): +18 strength and dexterity for 78 s, 120 mana. Each
  further card +3/+3, +3 s, +5-6 mana.
- Push and Push Wave: knockdown, 50 % chance rising to 75 % with the
  caster's air magic skill.
"""
import os

from patchlib import Patcher

ROOT = os.path.dirname(os.path.abspath(__file__))
P = Patcher(os.path.join(ROOT, 'src', 'RPGCompute'))
replace_once = P.replace_once


# The shared numbers and helpers live in rework/SpellRework.ech; build.py
# copies that file into src/RPGCompute before the patches run.

# ------------------------------------------------------------------ RPGCompute.ec
replace_once('RPGCompute.ec', '#include "Unit.ech"', '#include "SpellRework.ech"\n#include "Unit.ech"')

# ------------------------------------------------------------------ Magic2.ech
replace_once('Magic2.ech', '''    else if (strName.EqualNoCase("MAGIC_OVERPOWER"))
    {
        nVal = (nSkill + nCardCnt)*30;
        ptVal.SetMagicEnhanceMissileDamageUpPercent(nVal);
        nVal = 50 - (nSkill + nCardCnt)*10;
        ptVal.SetMagicEnhanceManaUseUpPercent(MAX(nVal, 0));
        nTicks = GetMagicTicks(nCardCnt, nRequiredSkill,nSkill,3);
''', '''    else if (strName.EqualNoCase("MAGIC_OVERPOWER"))
    {
        // SpellRework: +10 % per card, no extra mana on the boosted spell
        ptVal.SetMagicEnhanceMissileDamageUpPercent(SR_BoostDamagePercent(nCardCnt));
        ptVal.SetMagicEnhanceManaUseUpPercent(0);
        nTicks = SR_OverpowerSeconds(nCardCnt) * 30;
''')
replace_once('Magic2.ech', '''    else if (strName.EqualNoCase("MAGIC_CONCENTRATION"))
    {
        nVal=CalculateMagicDamage(pUnit, nMagicCardSlotNum);
        ptVal.SetMagicEnhanceMissileDamageUpPercent(nVal);
        nTicks = GetMagicTicks(nCardCnt, nRequiredSkill,nSkill,3);
''', '''    else if (strName.EqualNoCase("MAGIC_CONCENTRATION"))
    {
        // SpellRework: +10 % per card
        ptVal.SetMagicEnhanceMissileDamageUpPercent(SR_BoostDamagePercent(nCardCnt));
        nTicks = SR_ConcentrationSeconds(nCardCnt) * 30;
''')
replace_once('Magic2.ech', '''    else if (strName.EqualNoCase("MAGIC_BLESS"))
    {
        ptVal.SetAddPoint(ePointsStrength, 2 + (nSkill + nCardCnt)*3);
        ptVal.SetAddPoint(ePointsDexterity, 2 + (nSkill + nCardCnt)*3);
//        ptVal.SetAddPoint(ePointsVitality, 2 + (nSkill + nCardCnt)*3);
        nTicks = GetMagicTicks(nCardCnt, nRequiredSkill,nSkill,3);
''', '''    else if (strName.EqualNoCase("MAGIC_BLESS"))
    {
        // SpellRework: +18 strength and dexterity, +3 each per further card
        ptVal.SetAddPoint(ePointsStrength, SR_BlessPoints(nCardCnt));
        ptVal.SetAddPoint(ePointsDexterity, SR_BlessPoints(nCardCnt));
        nTicks = SR_BlessSeconds(nCardCnt) * 30;
''')

# ------------------------------------------------------------------- Magic.ech
# Mana of the three spells. The booster cards (less mana) still apply after
# this, through the code that follows in GetMagicManaUse.
replace_once('Magic.ech', '''    else
    {
        nUsedMana = mcPar.GetUsedMana();
        if (nUsedMana == 0)
        {
            return nUsedMana;
        }

        nCardCnt = pUnit.GetMagicCardOnSlotCount(nMagicCardSlotNum);
''', '''    else if (strSRCard.EqualNoCase("MAGIC_OVERPOWER"))
    {
        nUsedMana = SR_OverpowerMana(pUnit.GetMagicCardOnSlotCount(nMagicCardSlotNum));
    }
    else if (strSRCard.EqualNoCase("MAGIC_CONCENTRATION"))
    {
        nUsedMana = SR_ConcentrationMana(pUnit.GetMagicCardOnSlotCount(nMagicCardSlotNum));
    }
    else if (strSRCard.EqualNoCase("MAGIC_BLESS"))
    {
        nUsedMana = SR_BlessMana(pUnit.GetMagicCardOnSlotCount(nMagicCardSlotNum));
    }
    else
    {
        nUsedMana = mcPar.GetUsedMana();
        if (nUsedMana == 0)
        {
            return nUsedMana;
        }

        nCardCnt = pUnit.GetMagicCardOnSlotCount(nMagicCardSlotNum);
''')

replace_once('Magic.ech', '''    int nIndex, nCnt, nUsedMana, nUsedMana2;
    MagicCardParams mcPar;
    PotionValues ptVal;
''', '''    int nIndex, nCnt, nUsedMana, nUsedMana2;
    MagicCardParams mcPar;
    PotionValues ptVal;
    string strSRCard;
''')
replace_once('Magic.ech', '''    mcPar = pUnit.GetMagicCardParamsOnSlot(nMagicCardSlotNum);

    if (mcPar.GetMagicType() == eMagicCardTypeMissile)
    {
        if(mcPar.GetRequiredMagicSchoolSkill()<2)nUsedMana = CalculateMagicDamage(pUnit, nMagicCardSlotNum)/2;
''', '''    mcPar = pUnit.GetMagicCardParamsOnSlot(nMagicCardSlotNum);
    strSRCard = pUnit.GetMagicCardIDOnSlot(nMagicCardSlotNum);

    if (mcPar.GetMagicType() == eMagicCardTypeMissile)
    {
        if(mcPar.GetRequiredMagicSchoolSkill()<2)nUsedMana = CalculateMagicDamage(pUnit, nMagicCardSlotNum)/2;
''')

# -------------------------------------------------------------------- Unit.ech
# GetHitFightAction: a hit by a pushing missile (Push, Push Wave) knocks the
# target down with SR_PushKnockdownChance. Units without a fall animation,
# or on a horse, are pushed as before.
replace_once('Unit.ech', '''            if (bByHitPushedMissile && !pUnit.IsOnHorse())
            {
                nHitAction = eFightActionHitPushed;
            }
''', '''            if (bByHitPushedMissile && !pUnit.IsOnHorse())
            {
                nHitAction = eFightActionHitPushed;
                // SpellRework: Push and Push Wave knock down
                if (pUnit.HaveFightActionAnimation(eFightActionHitFall, pEnemy) &&
                    (Rand(100) < SR_PushKnockdownChance(pEnemy)))
                {
                    nHitAction = eFightActionHitFall;
                    nAnimDelay = 0;
                }
            }
''')

print('phase 1 applied:', ', '.join(P.write_all()))
