---
title: "The S-Class Equipment Synergy Matrix: Mapping Mechanics to Items in MLBB"
date: "2026-09-04 10:00:00 +0530"
categories: ["Game Architecture", "Data Modeling"]
tags: ["mlbb", "game-design", "equipment-matrix", "database-schema", "2026"]
description: "A mechanics-first S-Class equipment taxonomy decoding how hero passives and skill rotations dictate optimal Physical, Magic, and Defense paths in Patch 2.1.95a."

Evaluating Mobile Legends: Bang Bang builds solely on static tier lists or surface-level win rates misses how the game is actually won. Patch 2.1.95a features 104 distinct items across Attack, Magic, Defense, Movement, Jungling, and Roaming categories. Slapping a rigid six-item loadout onto a hero profile fails because an item’s real power depends on whether its unique passives match the operational engine of a hero's kit. An **S-Class Equipment Synergy** is defined not by how frequently an item is bought, but by how completely it amplifies the baseline loop formed by a hero's Passive, Skill 1, Skill 2, and Ultimate. Moving to an S-Class mechanics matrix bridges the gap between raw hero data and dynamic, draft-adaptive item engines.

---

## The Foundation of S-Class Equipment Synergy

In an engine-driven database, an S-Class designation represents the mathematical intersection where an item's passive directly fuels the primary condition of a hero's ability kit. When an item profile fails to amplify that engine, its value falls off, regardless of how strong the item's baseline stats appear on paper.

```
+-------------------------------------------------------------------------+
|                        HERO OPERATIONAL ENGINE                          |
|             (Passive + Skill 1 + Skill 2 + Ultimate Mechanics)          |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           MECHANICAL DRIVER                             |
|       (Attack Speed Triggers, Multi-Hit Burn, Defense Conversions)      |
+-------------------------------------------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v                                                       v
+------------------------------------+   +------------------------------------+
|    S-CLASS OFFENSIVE MULTIPLIER    |   |     S-CLASS DEFENSIVE STABILIZER   |
|   Physical / Magic Core Triggers   |   |   Durability Loops / Sustain Amps  |
+------------------------------------+   +------------------------------------+

```

Consider how these equipment relationships function in practice:

* **The Trinity On-Hit Engine:** Claude and Moskov rely on Basic Attack triggers. Equipping them with Corrosion Scythe, Demon Hunter Sword, and Golden Staff turns each attack into current-HP shred while rapidly stacking attack speed.
* **The Continuous Burn Engine:** Valir and Chang'e deal rapid, low-damage ticks. Equipping them with Glowing Wand and Genius Wand applies percentage max-HP burn while continuously stripping flat Magic Defense.
* **The Stat-Conversion Engine:** Grock and Gatotkaca convert defensive stats into offensive pressure. Defense items like Blade Armor, Antique Cuirass, and Dominance Ice build both durability and kill potential simultaneously.

---

## The 35-Category Master S-Class Matrix

Below is the definitive mechanics-to-equipment breakdown for `MLBB_Hero_Database.md`. It links 35 kit mechanics to their S-Class item pathways across Physical, Magic, and Defense categories.

| # | Passive and Skills / Core Mechanic | S-Class Heroes | Physical Equipment | Magic Equipment | Defense Equipment |
| --- | --- | --- | --- | --- | --- |
| **01** | Basic Attack + Attack Speed | Miya, Melissa, Moskov, Claude | Corrosion Scythe + DHS + Golden Staff | Feather of Heaven | Wind of Nature / Rose Gold Meteor |
| **02** | Basic Attack + Critical | Bruno, Lesley, Irithel | Berserker's Fury + Blade of Despair + Malefic Roar | Low synergy | Wind of Nature / Immortality |
| **03** | Basic Attack + On-Hit | Karrie, Claude, Moskov, Sun | DHS + Golden Staff + Corrosion Scythe | Feather of Heaven | Rose Gold Meteor / Wind of Nature |
| **04** | Skill-Enhanced Basic Attack | Clint, Beatrix, Brody, Granger | Hunter Strike + Blade of Despair + Malefic Roar | Starlium Scythe | Rose Gold Meteor / Immortality |
| **05** | Sustained Physical DPS | Thamuz, Alpha, Freya, Yu Zhong, Terizla | War Axe + Corrosion Scythe + Hunter Strike | Low synergy | Queen's Wings + Oracle |
| **06** | Physical Burst | Saber, Hayabusa, Lancelot, Benedetta | Hunter Strike + Blade of Despair + Malefic Roar | Low synergy | Immortality / Rose Gold Meteor |
| **07** | Physical Execute | Balmond, Martis, Aldous, Saber | Blade of Despair + Hunter Strike + Malefic Roar | Low synergy | Queen's Wings / Immortality |
| **08** | Magic Burst | Eudora, Vexana, Kadita, Harley | Low synergy | Genius Wand + Holy Crystal + Divine Glaive | Winter Crown |
| **09** | Magic Poke | Xavier, Pharsa, Gord, Valir | Low synergy | Genius Wand + Glowing Wand + Holy Crystal | Winter Crown / Athena's Shield |
| **10** | Long-Range Artillery | Xavier, Pharsa, Novaria, Yve | Low synergy | Holy Crystal + Divine Glaive + Genius Wand | Winter Crown |
| **11** | Magic Multi-Hit / AoE | Chang'e, Odette, Yve, Zhuxin | Low synergy | Glowing Wand + Genius Wand + Holy Crystal | Winter Crown / Athena's Shield |
| **12** | Skill Spam / Low Cooldown | Cyclops, Harith, Lunox, Xavier | Low synergy | Enchanted Talisman + Genius Wand + Holy Crystal | Winter Crown |
| **13** | Mana / Resource Scaling | Cecilion, Alice, Gord | Low synergy | Clock of Destiny + Enchanted Talisman + Holy Crystal | Oracle / Winter Crown |
| **14** | Mark to Burst | Saber, Hayabusa, Gusion, Xavier | Hunter Strike + Blade of Despair + Malefic Roar | Genius Wand + Holy Crystal + Divine Glaive | Immortality / Winter Crown |
| **15** | Dash / Mobility to Damage | Lancelot, Benedetta, Joy, Ling | Hunter Strike + Blade of Despair + Malefic Roar | Low synergy | Brute Force Breastplate / Immortality |
| **16** | CC to Burst | Eudora, Aurora, Selena, Vexana, Kadita | Low synergy | Genius Wand + Holy Crystal + Divine Glaive | Winter Crown |
| **17** | CC to Sustained Damage | Ruby, Terizla, Martis, Paquito, Lapu-Lapu | War Axe + Hunter Strike + Queen's Wings | Low synergy | Oracle / Immortality |
| **18** | CC Chain / Frontline | Tigreal, Atlas, Minotaur, Khufra | Low synergy | Cursed Helmet | Dominance Ice + Antique Cuirass + Immortality |
| **19** | Taunt / Forced Targeting | Gatotkaca, Belerick | Low synergy | Cursed Helmet + Feather of Heaven | Dominance Ice + Oracle + Immortality |
| **20** | Terrain / Zone Control | Grock, Valir, Yve | War Axe | Glowing Wand + Holy Crystal | Dominance Ice / Antique Cuirass |
| **21** | HP to Damage | Hylos, Belerick, Gatotkaca | Low synergy | Cursed Helmet | Guardian Helmet + Oracle + Dominance Ice |
| **22** | Defense to Damage | Grock, Gatotkaca, Edith | War Axe | Holy Crystal / Feather of Heaven | Dominance Ice + Antique Cuirass + Blade Armor |
| **23** | HP to Healing / Regen | Uranus, Hylos, Belerick, Masha | Low synergy | Low synergy | Oracle + Guardian Helmet + Queen's Wings |
| **24** | Healing / Spell Vamp | Ruby, Yu Zhong, Thamuz, Uranus, Alpha | War Axe + Hunter Strike | Low synergy | Oracle + Queen's Wings |
| **25** | Shield to Damage | Esmeralda, Edith, Lolita | Low synergy | Holy Crystal | Oracle + Queen's Wings + Immortality |
| **26** | Damage Reflection | Belerick, Grock | Low synergy | Cursed Helmet | Blade Armor + Dominance Ice + Antique Cuirass |
| **27** | Transformation | Yu Zhong, Edith, Lukas, Lapu-Lapu, Suyou | War Axe + Hunter Strike + Blade of Despair | Feather of Heaven (where applicable) | Oracle + Queen's Wings + Immortality |
| **28** | Summon / Clone | Vexana, Zhask, Sun, Popol and Kupa | DHS + Corrosion Scythe | Glowing Wand + Holy Crystal | Immortality / Winter Crown |
| **29** | Global Ultimate / Pickoff | Aldous, Hayabusa, Moskov, Yi Sun-shin | Hunter Strike + Blade of Despair + Malefic Roar | Low synergy | Immortality |
| **30** | Split Push / Tower Pressure | Sun, Zilong, Argus, Masha | Corrosion Scythe + DHS + Golden Staff | Low synergy | Immortality / Rose Gold Meteor |
| **31** | Regeneration Tank | Uranus, Hylos, Belerick | Low synergy | Cursed Helmet | Guardian Helmet + Oracle + Dominance Ice |
| **32** | Anti-Dive / Peel | Lolita, Khufra, Diggie, Valir | Low synergy | Low synergy | Dominance Ice + Athena's Shield + Immortality |
| **33** | Healing Support | Estes, Floryn, Rafaela, Angela | Low synergy | Fleeting Time + Enchanted Talisman | Oracle + Dominance Ice |
| **34** | Shield Support | Angela, Mathilda, Lolita | Low synergy | Fleeting Time + Enchanted Talisman | Oracle + Athena's Shield |
| **35** | Ultimate Dependency | Atlas, Tigreal, Estes, Floryn, Minotaur | Low synergy | Fleeting Time | Dominance Ice + Immortality |

---

## The Core S-Plus Archetypes

Across the 35 categories, the equipment ecosystem consolidates into 15 foundational item engines that define competitive play in Patch 2.1.95a.

```
       +--------------------+          +--------------------+
       |  PHYSICAL ON-HIT   |          |    MAGIC BURST     |
       | Corrosion+DHS+Staff|          | Genius+Holy+Divine |
       +--------------------+          +--------------------+
                 \                               /
                  \                             /
                   v                           v
          +---------------------------------------------+
          |         S-PLUS EQUIPMENT ARCHETYPES         |
          +---------------------------------------------+
                   ^                           ^
                  /                             \
                 /                               \
       +--------------------+          +--------------------+
       |  PHYSICAL SUSTAIN  |          |   TANK FRONTLINE   |
       | War Axe+Wings+Hunt |          | Dominance+Antique  |
       +--------------------+          +--------------------+

```

| Archetype Cluster | Target Mechanics and Playstyles | Core Equipment Set | Mechanical Justification |
| --- | --- | --- | --- |
| **Attack-Speed On-Hit** | Miya, Melissa, Moskov, Claude, Karrie | Corrosion Scythe + Demon Hunter Sword + Golden Staff | Golden Staff converts unused critical chance into bonus attack speed, triggering DHS current-HP damage and Corrosion Scythe slows multiple times per second. |
| **Critical Burst** | Bruno, Lesley, Irithel | Berserker's Fury + Blade of Despair + Malefic Roar | Stacks extreme critical damage ratios with execution-range physical damage, using Malefic Roar to pierce frontline base armor. |
| **Physical Sustain** | Thamuz, Alpha, Yu Zhong, Terizla | War Axe + Hunter Strike + Queen's Wings | War Axe delivers stacking Physical Attack and Cooldown Reduction during brawls; Queen's Wings grants essential low-HP damage reduction and CDR resets. |
| **Assassin Burst** | Saber, Hayabusa, Lancelot, Ling | Hunter Strike + Blade of Despair + Malefic Roar | Maximizes flat and percentage armor shred to drop squishy priority targets within a single ability rotation. |
| **Physical Execute** | Balmond, Martis, Aldous | Blade of Despair + Hunter Strike + Malefic Roar | Leverages Blade of Despair's 25% attack boost against low-health targets, ensuring clean resets on true-damage or missing-HP executes. |
| **Magic Burst** | Eudora, Vexana, Kadita, Harley | Genius Wand + Holy Crystal + Divine Glaive | Strips flat Magic Defense via Genius Wand while Holy Crystal scales raw Magic Power, allowing Divine Glaive to pierce remaining defenses. |
| **Magic Poke** | Xavier, Pharsa, Gord, Valir | Genius Wand + Glowing Wand + Holy Crystal | Delivers sustained burn damage based on max HP while keeping movement speed high for safe kiting outside enemy engage ranges. |
| **Magic Artillery** | Xavier, Pharsa, Novaria, Yve | Holy Crystal + Divine Glaive + Genius Wand | Maximizes damage per spell cast across screen-wide ranges where multi-hit burn passives cannot be safely maintained. |
| **Magic Spam** | Cyclops, Harith, Lunox | Enchanted Talisman + Genius Wand + Holy Crystal | Solves mana consumption constraints and caps CDR, letting short-cooldown casters maintain non-stop spell rotations. |
| **Tank Frontline** | Tigreal, Atlas, Minotaur, Khufra | Dominance Ice + Antique Cuirass + Immortality | Dominance Ice reduces enemy attack speed and healing; Antique Cuirass blunts incoming physical skill combos; Immortality provides second-life insurance. |
| **HP Scaling Tank** | Hylos, Belerick, Gatotkaca | Guardian Helmet + Oracle + Dominance Ice | Boosts maximum health pools to fuel base abilities that scale with total HP, while Guardian Helmet provides sustained health regen out of combat. |
| **Regen and Sustain** | Uranus, Ruby, Yu Zhong, Thamuz | Oracle + Queen's Wings + Guardian Helmet | Oracle increases incoming shield strength and HP regeneration, turning built-in combat healing into unbreakable frontline sustain. |
| **Anti-Physical Defense** | Frontliners vs Heavy Physical Drafts | Antique Cuirass + Dominance Ice + Blade Armor | Blade Armor reflects basic attack damage back to the attacker while stacking physical armor to maximize Antique Cuirass's percentage damage mitigation. |
| **Anti-Magic Defense** | Frontliners vs Heavy Magic Drafts | Athena's Shield + Radiant Armor + Oracle | Neutralizes single-hit burst with Athena's Shield, mitigates multi-hit damage with Radiant Armor, and increases incoming shields via Oracle. |
| **Support Ultimate** | Estes, Floryn, Atlas, Tigreal | Fleeting Time + Enchanted Talisman + Oracle | Fleeting Time slashes ultimate cooldowns on takedowns, ensuring critical support abilities are available for every teamfight. |

---

## The Build Logic: Why Item Context Matters

The equipment sets detailed in this matrix are modular foundations rather than rigid six-slot shopping lists. Kit engines adapt to the match state.

```
       [ HERO IDENTIFIED ] 
               │
               ▼
[ IDENTIFY ENGINE & SCALING TAGS ] (e.g., Physical Sustain / True Damage Execute)
               │
               ▼
   [ SELECT CORE ENGINE ITEM ]    (e.g., War Axe for extended combat stacking)
               │
               ▼
  [ SELECT SUSTAIN ENABLER ]     (e.g., Queen's Wings for low-HP damage reduction)
               │
               ▼
  [ EVALUATE DRAFT COUNTERS ]    (Dominance Ice vs Healing / Radiant vs Magic Burn)
               │
               ▼
 [ FINAL ADAPTIVE 6-SLOT BUILD ]

```

* **Alpha's Sustain Engine:** Alpha relies on Beta's True Damage strafing runs, which scale with Physical Attack and cooldown cycling. Rushing raw burst leaves him vulnerable to being focused down. Building **War Axe**, **Queen's Wings**, and **Oracle** gives him the Cooldown Reduction and Spell Vamp needed to survive extended fights and trigger Beta continuously.
* **Moskov's Basic Attack Engine:** Moskov's basic attacks penetrate targets in a line, triggering on-hit passives across multiple enemies. Rushing flat physical attack ignores this strength; pairing **Corrosion Scythe**, **Demon Hunter Sword**, and **Golden Staff** melts frontlines and backlines simultaneously.
* **Balmond's Skill Rotation:** Balmond relies on repeated spins followed by an execute. He benefits from sustained combat duration over pure glass-cannon stats. **War Axe** and **Queen's Wings** keep him alive in the middle of teamfights, letting him wait for target HP bars to drop into his Ultimate execute window.

---

## Machine-Readable Hero Integration Schema

To use this logic within `MLBB_Hero_Database.md` and feed automated build generators, store hero profiles using structured metadata tags rather than static item strings:

```json
{
  "hero_id": "claude_01",
  "hero_name": "Claude",
  "role_legacy": ["Marksman"],
  "engine_classification": {
    "primary": "Basic_Attack_On_Hit",
    "secondary": ["Attack_Speed_Scaling", "Dash_Mobility_DPS"]
  },
  "scaling_dependencies": {
    "attack_speed": 1.0,
    "on_hit_procs": 1.0,
    "physical_penetration": 0.6,
    "movement_speed": 0.8
  },
  "s_class_synergy_rules": {
    "physical_core": [
      {
        "item_id": "demon_hunter_sword",
        "synergy_weight": 5.0,
        "amplification_target": "Dexter_Passive_Dual_Proc",
        "description": "Dexter copies basic attacks, triggering DHS current-HP damage twice per attack cycle."
      },
      {
        "item_id": "golden_staff",
        "synergy_weight": 4.8,
        "amplification_target": "Endless_Strike_Acceleration",
        "description": "Converts critical strike chance into raw Attack Speed while triggering on-hit passives every third hit."
      }
    ],
    "defense_core": [
      {
        "item_id": "wind_of_nature",
        "synergy_weight": 4.5,
        "amplification_target": "Active_Physical_Immunity",
        "description": "Grants complete physical damage immunity, allowing Claude to safely channel his Ultimate inside the enemy backline."
      }
    ]
  }
}

```

```json
{
  "hero_id": "hylos_01",
  "hero_name": "Hylos",
  "role_legacy": ["Tank"],
  "engine_classification": {
    "primary": "HP_To_Damage_Scaling",
    "secondary": ["Regeneration_Tank", "Mana_Resource_Scaling"]
  },
  "scaling_dependencies": {
    "max_hp": 1.0,
    "max_mana": 0.9,
    "hybrid_defense": 0.8
  },
  "s_class_synergy_rules": {
    "defense_core": [
      {
        "item_id": "guardian_helmet",
        "synergy_weight": 5.0,
        "amplification_target": "Passive_Thickened_Blood",
        "description": "Provides the massive raw HP pool required to maximize Ring of Punishment uptime and tick damage."
      },
      {
        "item_id": "dominance_ice",
        "synergy_weight": 4.7,
        "amplification_target": "Mana_Conversion_And_Anti_Heal",
        "description": "Grants bonus Mana which directly increases Hylos's Max HP pool via his passive, while reducing surrounding enemy attack speed."
      }
    ],
    "magic_core": [
      {
        "item_id": "cursed_helmet",
        "synergy_weight": 4.4,
        "amplification_target": "Burning_Soul_Aura",
        "description": "Converts Hylos's massive HP pool into passive percentage-health magic damage per second to nearby enemies."
      }
    ]
  }
}

```

By decoupling hero kits into mechanical engines and evaluating equipment based on functional amplification, your database moves beyond simple, outdated build lists. It transforms into an adaptive build engine that can dynamically itemize around hero synergies, patch adjustments, and live draft requirements.
