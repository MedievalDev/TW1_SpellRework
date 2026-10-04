# SpellRework - game test (all phases)

Install one of the two WDs from the release (see README), switch it on.

## Before you start

1. **Switch off `EnemyLevels.wd`** (Mod Manager or Mod Selector). It replaces
   the same script; with both on, one of them is silently ignored.
2. Also switch off `TW1_Probe.wd` (the burn probe), it replaces the campaign
   script as well.
3. And switch off **`Yamalin.wd`**: it carries its own `TwoWorlds.par`;
   with both on, either the Tornado card is missing or Yamalin's changes are.
   (ShaderFix, QuestLimit600 and Test381 do not collide.)
4. Start a **new game** (saves carry the old scripts).

Cards: trainer console `trainer.item MAGIC_TORNADO` (same for
`MAGIC_BLESS`, `MAGIC_OVERPOWER`, `MAGIC_CONCENTRATION`, `MAGIC_PUSH`,
`MAGIC_PUSH_WAVE`). If the item command does not take that form, put the
cards into a trader with the Quest Creator. A torch for Burn: any torch in
the left hand, Burn skill learned.

Write down for each point: works / does not work / odd, plus what you saw.

## 1. Is the mod loaded? (30 seconds)

Open the spell book, Air school.

- The Tornado card sits in the first row, fourth column, with its own
  picture (blue whirlwind) and the name "Tornado".
- One Blessing card on a slot: strength +18, dexterity +18, 78 s, 120 mana.
- Hover the Burn skill: chance 100 %, the new text (burning enemies keep
  fighting, +20 % per level).

## 2. Card stacking

- Blessing, 2 cards: +21/+21, 81 s, 125 mana. 3 cards: +24/+24, 84 s, 131.
- Overpower, 1 card: +10 %, 78 s, 120 mana; 2 cards: +20 %, 81 s, 125.
- Concentration, 1 card: +10 %, 126 s, 271 mana; 2 cards: +20 %, 132 s, 285.

## 3. Overpower: boost and fire nova

Stand among 3-4 wolves or goblins, cast Overpower.

- A fire ring shows around you for about 3 s, the enemies in 6 m lose HP
  (about 15 per second with one card).
- They burn: flames on them, they lose a little HP every second for at
  least 3 s, they do **not** die from the burning alone.
- The next fire bolt hurts more (+10 % per card).

## 4. Concentration: boost and lightning nova

Same group, cast Concentration.

- A lightning flash around you, the enemies in 6 m lose HP (40 with one card).
- About half of them stand stunned for 3 s (more with high air magic).

## 5. Burn skill

Torch in the left hand, Burn skill 3 or more, fight a bandit.

- Burn always works; the enemy burns (flames) for Burn-level seconds.
- The burning enemy keeps attacking and blocking (no jump back, not slower).
- Your strikes hurt clearly more while he burns (+60 % at level 3).
- Critical hits / stun strikes happen more often while he burns.

## 6. Tornado

Cast Tornado at a group of 3-4 enemies some metres away.

- At the target a blue-white cloud with a vortex symbol on the ground for 4 s;
  enemies in it take lightning hits about once a second (lightning effect on
  them).
- Enemies in it cannot walk out while it lasts; some stand stunned (more with
  a higher Stun skill).
- Mana cost about twice a Lightning bolt.

## 7. Push and Push Wave

Cast both 10-20 times at goblins or wolves.

- About half of the hit enemies fall over (with air magic 15 three of four).
- **Push Wave now makes a sound.**
- The Push Wave ring is clearly visible (white-blue, brighter than before),
  and every enemy it hits shows a short white-blue impact with a thump.

## 8. Anything odd

Enemies that freeze in a pose, cards with empty tooltips, a crash when
hovering or casting, green poison look on the Tornado, the game feeling
slower (the campaign tick now runs every second).

## What the test answers

| Point | Open question in the build |
|---|---|
| 3, 4 | does the damage ring on the caster hurt enemies? do the Dynamics effects show? |
| 3, 5 | does the burning damage-over-time tick run? |
| 6 | does the engine call the script for every unit the Tornado hits (hold + stun)? |
| 6 | does the recoloured effect look like a storm? |
| 7 | does the Push Wave play the impact on every unit it hits? |
