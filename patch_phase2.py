"""SpellRework phases 2-4 in the scripts: novas, Burn rework, Tornado, burn tick.

Runs after patch_phase1.py on src/. The logic lives in
rework/SpellRework.ech (RPGCompute) and rework/SpellReworkCampaign.ech
(campaign); build.py copies both into src/. Here only the hooks go in.

Phase 2 - second effects (Vince):
  Overpower: fire nova around the caster, enemies burn (Burn skill effect).
  Concentration: lightning nova, 3 s stun with 50-75 % (air magic skill).
Phase 3 - Burn rework:
  burn chance 100 %, burning = fire damage over time for 1-10 s (Burn
  level), +20 % strike damage per Burn level against a burning enemy
  (max +200 %), critical hit / stun / sword break / pull shield get double
  chance against a burning enemy, the burning enemy keeps fighting (no
  jump back, no slow-down).
Phase 4 - Tornado (new air card, row 1, column 4): an area at the target
  that hits for lightning and piercing damage several times; each enemy hit
  is held in place and may be stunned (chance from the Stun skill).
"""
import os

from patchlib import Patcher

ROOT = os.path.dirname(os.path.abspath(__file__))
R = Patcher(os.path.join(ROOT, 'src', 'RPGCompute'))
C = Patcher(os.path.join(ROOT, 'src', 'Campaigns'))

# ------------------------------------------------------------- Magic2.ech
# Side effects only here, in MakeMagicGenericOnUnit (the cast), never in
# PrepareMagicDataOnUnit: that one also builds the tooltips.
R.replace_once('Magic2.ech', '''    if(ptVal.GetPotionTicks()>0) pTarget.AddPotionValues(ptVal);
    pTarget.UpdateChangedUnitValues();
''', '''    if(ptVal.GetPotionTicks()>0) pTarget.AddPotionValues(ptVal);
    pTarget.UpdateChangedUnitValues();

    // SpellRework: second effects of Overpower and Concentration, Tornado on its targets
    if (bCanBeUsed && strCardName.EqualNoCase("MAGIC_OVERPOWER"))
    {
        SR_FireNova(pUnit, nCardCnt);
    }
    if (bCanBeUsed && strCardName.EqualNoCase("MAGIC_CONCENTRATION"))
    {
        SR_LightningNova(pUnit, nCardCnt);
    }
    if (strCardName.EqualNoCase("MAGIC_TORNADO"))
    {
        SR_TornadoOnTarget(pUnit, pTarget, nCardCnt);
    }
''')

# --------------------------------------------------------------- Magic.ech
# Tornado: every unit its missile hits gets MakeMagicGenericOnUnit (like Freezing Wave)
R.replace_once('Magic.ech', '''    if (strName.EqualNoCase("MAGIC_FREEZINGWAVE"))
    {
        mVal.SetMakeMagicGenericOnTarget(true);
    }
''', '''    if (strName.EqualNoCase("MAGIC_FREEZINGWAVE"))
    {
        mVal.SetMakeMagicGenericOnTarget(true);
    }
    if (strName.EqualNoCase("MAGIC_TORNADO"))
    {
        mVal.SetMakeMagicGenericOnTarget(true);
    }
''')
# Tornado mana: twice the usual missile cost of a first-ring spell (it hits an area several times)
R.replace_once('Magic.ech', '''        if(mcPar.GetRequiredMagicSchoolSkill()<2)nUsedMana = CalculateMagicDamage(pUnit, nMagicCardSlotNum)/2;
''', '''        if (strSRCard.EqualNoCase("MAGIC_TORNADO")) nUsedMana = CalculateMagicDamage(pUnit, nMagicCardSlotNum);
        else if(mcPar.GetRequiredMagicSchoolSkill()<2)nUsedMana = CalculateMagicDamage(pUnit, nMagicCardSlotNum)/2;
''')

# ---------------------------------------------------------------- Unit.ech
# Burn: always succeeds (Vince: probability 100 %)
R.replace_once('Unit.ech', '''    else if (nSkill == eSkillBurn)
    {
       nTmp = CalcChance(GetAttack(pUnit),nEnemyDefence);
       return (nTmp*(nSkillVal+4))/15;
    }
''', '''    else if (nSkill == eSkillBurn)
    {
       // SpellRework: a torch always sets the enemy on fire
       return 100;
    }
''')
# Critical hit, stun, sword break, pull shield: double chance against a burning enemy
R.replace_once('Unit.ech', '''function int CalcSkillChance(unit pUnit, int nSkill, unit pEnemy)
{
    //ASSERT((pEnemy != null) && pEnemy.IsUnit());
    if(!pEnemy || !pEnemy.IsUnit())return 100;
    return CalcSkillChance(pUnit, nSkill, pEnemy, 0, 0, 0);
''', '''function int CalcSkillChance(unit pUnit, int nSkill, unit pEnemy)
{
    int nSRChance;
    //ASSERT((pEnemy != null) && pEnemy.IsUnit());
    if(!pEnemy || !pEnemy.IsUnit())return 100;
    nSRChance = CalcSkillChance(pUnit, nSkill, pEnemy, 0, 0, 0);
    // SpellRework: +100 % chance against a burning enemy (the original text promised 300 %)
    if (SR_IsBurning(pEnemy) &&
        ((nSkill == eSkillCriticalHit) || (nSkill == eSkillStun) || (nSkill == eSkillSwordBrake) || (nSkill == eSkillPullShield)))
    {
        nSRChance = nSRChance * 2;
        if (nSRChance > 100) nSRChance = 100;
    }
    return nSRChance;
''')
# The burning enemy keeps fighting: a normal hit reaction instead of the jump back
R.replace_once('Unit.ech', '''    else if (nEnemyFightAction == eFightActionBurn)
    {
        nHitAction = eFightActionHitBurn;
    }
''', '''    else if (nEnemyFightAction == eFightActionBurn)
    {
        // SpellRework: burning enemies still defend and attack
        nHitAction = eFightActionHit;
    }
''')
# Burn skill hit: set on fire for Burn-level seconds, no slow-down
R.replace_once('Unit.ech', '''    else if (nSkill == eSkillBurn)
    {
        ASSERT((pEnemy != null) && pEnemy.IsUnit());
        ptVal = pEnemy.AddPotionValues("STATE_SLOWED");//XXXMD
        ptVal.SetPotionFlags(ePotionSlowDown);
        ptVal.SetPotionTicks( CalcBurnTime_SkillBurn(pUnit) * 30 );
        pEnemy.UpdateChangedUnitValues();
    }
''', '''    else if (nSkill == eSkillBurn)
    {
        ASSERT((pEnemy != null) && pEnemy.IsUnit());
        // SpellRework: burning (damage over time, flames) instead of slowed
        SR_SetBurning(pEnemy, CalcBurnTime_SkillBurn(pUnit));
    }
''')
# Strikes against a burning enemy: +20 % per Burn level of the attacker
R.replace_once('Unit.ech', '''        if(pEnemy!=null && pEnemy.IsUnit() && pEnemy.FindPotionWithFlags(ePotionDirtyTrick) >= 0)
        {
            nHitPercentMultiplier = nHitPercentMultiplier*2;
        }
''', '''        if(pEnemy!=null && pEnemy.IsUnit() && pEnemy.FindPotionWithFlags(ePotionDirtyTrick) >= 0)
        {
            nHitPercentMultiplier = nHitPercentMultiplier*2;
        }
        // SpellRework: strikes against a burning enemy (Burn skill)
        if(pEnemy!=null && pEnemy.IsUnit() && SR_IsBurning(pEnemy) && IsStrikeFightAction(nCurrentFightAction, false))
        {
            nHitPercentMultiplier = nHitPercentMultiplier * (100 + SR_BurnStrikeBonus(pUnit)) / 100;
        }
''')

# --------------------------------------------------- TwoWorldsCampaign.ec
# burn tick once a second; the original cleanup keeps its 3 s rhythm
C.replace_once('TwoWorldsCampaign.ec', '#include "..\\\\Common\\\\Stealing.ech"',
               '#include "..\\\\Common\\\\Stealing.ech"\n#include "SpellReworkCampaign.ech"')
C.replace_once('TwoWorldsCampaign.ec', '''state Nothing
{
    int i, nMission, nMissionsCnt;
    int anParties[];
    mission pMission;

    for (i = ePartyAnimals; i <= ePartyEvilWarriors; i++) anParties.Add(i);
''', '''state Nothing
{
    int i, nMission, nMissionsCnt;
    int anParties[];
    mission pMission;

    // SpellRework: burning units lose HP once a second
    SR_BurnTick();
    if (((GetGameTick() / 30) % 3) != 0) return Nothing, 30;

    for (i = ePartyAnimals; i <= ePartyEvilWarriors; i++) anParties.Add(i);
''')
C.replace_once('TwoWorldsCampaign.ec', '''            pMission.RemoveKilledUnitsOutsideStepRange(anParties, false, false);
        }
    }
    return Nothing, 3*30;
''', '''            pMission.RemoveKilledUnitsOutsideStepRange(anParties, false, false);
        }
    }
    return Nothing, 30;
''')

print('phase 2-4 applied:', ', '.join(R.write_all() + C.write_all()))
