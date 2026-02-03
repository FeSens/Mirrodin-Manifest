# Mirrodin Manifest - Comprehensive Set Analysis

*Analysis Date: February 2026*

---

## Executive Summary

**Mirrodin Manifest** is a 287-card custom MTG set (excluding 4 documentation files) featuring three core mechanics: GAMBLE, COMPOUND, and REDISTRIBUTE. The set has strong thematic cohesion and interesting mechanical hooks, but faces several balance concerns and structural gaps that need attention before being playtest-ready.

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total Cards | 287 | 261 | Over by 26 |
| Commons | 108 | 101 | Over by 7 |
| Uncommons | 93 | 80 | Over by 13 |
| Rares | 68 | 60 | Over by 8 |
| Mythics | 18 | 20 | Under by 2 |
| Creatures | 168 | ~156 (60%) | 59% - Good |

---

## 1. REMOVAL ANALYSIS

### Removal by Color

| Color | Common Removal | Uncommon+ Removal | Assessment |
|-------|----------------|-------------------|------------|
| **White** | Citizen's Arrest (exile, power 4+), Protective Ward (protection), Rally the Militia (token pump), Austerity Measure (redistribute) | Bailout Package (destroy artifact), Reprocessing Agent (temporary exile + -1/-1), Alignment Protocol Enforcer (exile w/ token) | **ADEQUATE** - Good conditional exile, needs unconditional removal |
| **Blue** | Freeze Protocol (tap-down), Forced Equalization (redistribute), Synod's Rejection (bounce/counter), Lattice Delay (bounce) | Credit Default (counter), Archive Scrubbing (graveyard exile/counter) | **ADEQUATE** - Standard blue tempo removal |
| **Black** | Soul Extraction (destroy + drain), Dross Executioner (ETB -2/-2), Execution Order (destroy power 2-), Toxic Resilience (deathtouch trick) | Burden Shift (redistribute + drain), Vindictive Redistribution (counter removal + drain), Market Crash (strip all counters) | **STRONG** - Excellent unconditional removal at common |
| **Red** | Furnace Bolt (2 damage), Volatile Reaction (3 damage to creature), Reckless Gambit (damage), Foundry Flames (burn) | Lucky Strike (3 + potential 3 more), Flames of Fortune (damage payoff), Pyromantic Gambit (X-spell) | **STRONG** - Multiple burn options at common |
| **Green** | Tangle Hunter (destroy artifact), Natural Reclamation (destroy artifact/enchantment), Nature's Rebuke (combat trick) | Tangle's Vengeance (fight small creatures) | **WEAK** - No creature fight spell at common, only artifact removal |

### Removal Assessment Summary

**Strengths:**
- Black has excellent removal density at all rarities
- Red has multiple efficient burn spells
- White has interesting conditional exile effects

**Weaknesses:**
- **GREEN LACKS FIGHT SPELLS AT COMMON** - This is a significant gap. Green needs 1-2 "fight" or "bite" effects at common to handle creatures.
- White's common removal (Citizen's Arrest) is very conditional (power 4+)
- Blue lacks a true bounce spell at common (Lattice Delay exists but need to verify)

### Recommendations for Removal:
1. **Add Green common fight spell** - "Tangle Duel" or similar ({2}{G} Sorcery - Target creature you control fights target creature you don't control)
2. **Add White common Pacifism variant** - Arrest effect for broader creature coverage
3. Consider adding a colorless common removal option for artifact-heavy format

---

## 2. WIN CONDITIONS ANALYSIS

### Big Finishers by Color

| Rarity | White | Blue | Black | Red | Green | Colorless/Multi |
|--------|-------|------|-------|-----|-------|-----------------|
| **Mythic** | The Grand Equalizer (5/5), Supreme Arbiter of Order (4/5), Central Bank Governor (4/5) | Recursive Self-Improvement, Lattice Overseer | Put-In, the Iron Despot (4/4), Master of Debt | Chaos Arbiter (5/4), The Great Furnace Awakened (7/7), Furnace Revolution | Tangle Titan (7/7) | Kha-Sino, Tromp, Zel-Ensk, The Darksteel Wall |
| **Rare** | Alignment Protocol Enforcer | Bubble Speculator, The Equalizer | Vindictive Redistribution | Pyromantic Gambit, All-In Gambler (4/3) | Jackpot Wurm (6/6+), Tangle's Vengeance | Various multicolor |

### Bomb Analysis

**Top Tier Bombs (Game-Ending Threats):**
1. **The Great Furnace Awakened** (7/7 haste trample, ETB damage) - Excellent finisher
2. **Tangle Titan** (7/7 trample reach, counters on all creatures) - Board-dominant
3. **Jackpot Wurm** (6/6 to 15/15 trample) - High variance but massive upside
4. **Supreme Arbiter of Order** (soft lock effect) - May be too oppressive
5. **The Grand Equalizer** (mass counter manipulation) - Build-around mythic

**Aggressive Win Conditions:**
- All-In Gambler (4/3 haste, potential 8 power)
- Chaos Arbiter (5/4 flying with spell copying)
- Furnace Revolution (mass Threaten effect)

**Alternate Win Conditions:**
- Debt-based damage through Debt tokens and Debt Ceiling combos
- Counter accumulation through Hype Cycle
- Mill through Archive Corruptor

### Assessment

**Strengths:**
- Each color has at least one exciting mythic/rare finisher
- Red and Green have the best raw power finishers
- Multiple paths to victory (combat, drain, counters)

**Weaknesses:**
- White's finishers are more controlling than aggressive
- Limited evasion at common for aggro decks
- Some finishers (Supreme Arbiter) may create non-games

---

## 3. -1/-1 COUNTER STRATEGY ANALYSIS

### Cards that Create or Interact with -1/-1 Counters

| Card | Color | Rarity | Effect |
|------|-------|--------|--------|
| **Dross Executioner** | B | Common | ETB -2/-2 until end of turn |
| **Simulated Labor Myr** | Colorless | Common | Tap: add {C}, put -1/-1 on non-Myr |
| **Inflation Harbinger** | R | Common | ETB puts -1/-1 on creatures with +1/+1 counters |
| **Reprocessing Agent** | W | Uncommon | Returns creature with two -1/-1 counters |
| **Put-In, the Iron Despot** | B | Mythic | {2}{B}: Target creature gets -1/-1 until end of turn |
| **Rusted Nim Conscript** | B | Common | Enters with rust counter giving -1/-1 |

### REDISTRIBUTE and -1/-1 Counter Interaction

The REDISTRIBUTE mechanic reads: *"Choose two permanents. Remove all counters from them, then each gets half that many counters, rounded down."*

**Key Insight:** REDISTRIBUTE can spread -1/-1 counters across multiple creatures, potentially killing them if they have low toughness.

**Example Scenario:**
1. Creature A has 4 -1/-1 counters on it
2. Redistribute between A and B (with 0 counters)
3. Both end up with 2 -1/-1 counters each
4. This kills 2-toughness creatures

### Persist Interaction WARNING

**CRITICAL BALANCE ISSUE:** The REDISTRIBUTE mechanic creates broken interactions with persist:

| Combo | Cards | Result |
|-------|-------|--------|
| Infinite Persist | The Equalizer + Kitchen Finks + Sac Outlet | The Equalizer removes -1/-1 counters from persist creatures, enabling infinite loops |
| Infinite Mana | Simulated Labor Myr + Devoted Druid + Sac Outlet | Simulated Labor enables infinite mana with Devoted Druid |
| Austerity Abuse | Austerity Minister + Kitchen Finks + Sac Outlet | Minister removes -1/-1 counter each upkeep, enabling persist loops |

### Assessment

**Current State:** The -1/-1 counter strategy is **underdeveloped within the set** but creates **broken interactions with external cards**.

**Recommendations:**
1. **Add "once per turn" clauses** to cards like Simulated Labor Myr and The Equalizer
2. **Clarify REDISTRIBUTE** to only redistribute counters of the same type (so -1/-1 counters stay as -1/-1)
3. **Add more -1/-1 synergies** if this is intended as a sub-theme
4. Consider a B/G -1/-1 counter archetype similar to Amonkhet if pursuing this design space

---

## 4. MECHANIC DISTRIBUTION

### GAMBLE Distribution (59 cards)

| Color | Common | Uncommon | Rare | Mythic | Total |
|-------|--------|----------|------|--------|-------|
| White | 0 | 0 | 0 | 0 | **0** |
| Blue | 2 | 4 | 3 | 0 | **9** |
| Black | 2 | 1 | 0 | 0 | **3** |
| Red | 6 | 7 | 3 | 1 | **17** |
| Green | 4 | 5 | 1 | 1 | **11** |
| Colorless | 0 | 1 | 2 | 0 | **3** |
| Multicolor | 1 | 1 | 2 | 1 | **5** |

**As-Fan Calculation (Commons):**
- 14 commons with GAMBLE / 108 total commons = ~1.3 GAMBLE cards per pack
- This is **adequate** for a scaling mechanic (target: 2.0-3.0)

**Assessment:** GAMBLE is **primarily Red-Green** with some Blue support. White has **ZERO** gamble cards, which is a design choice but may feel limiting in draft.

### COMPOUND Distribution (68 cards)

| Color | Cards | Notes |
|-------|-------|-------|
| All Colors | 68 | Broadly distributed across counter strategies |

**Assessment:** COMPOUND appears on cards that add counters of existing types. It's well-distributed but primarily supports +1/+1 counter strategies.

### REDISTRIBUTE Distribution (35 cards)

| Color | Common | Uncommon | Rare | Mythic | Total |
|-------|--------|----------|------|--------|-------|
| White | 1 | 2 | 1 | 1 | **5** |
| Blue | 1 | 1 | 1 | 0 | **3** |
| Black | 0 | 2 | 1 | 0 | **3** |
| Red | 0 | 0 | 1 | 0 | **1** |
| Green | 0 | 2 | 1 | 0 | **3** |
| Colorless | 0 | 0 | 0 | 0 | **0** |
| Multicolor | 0 | 3 | 3 | 1 | **7** |

**As-Fan Calculation:**
- 2 commons with REDISTRIBUTE / 108 commons = ~0.2 per pack
- This is **too low** for a main mechanic (target: 1.0-1.5 minimum)

**Assessment:** REDISTRIBUTE is **severely under-represented at common**. Drafters may not see enough redistribute cards to build around the mechanic.

### Mechanic Balance Recommendations

1. **Add 3-4 more REDISTRIBUTE commons** across colors
2. **Consider adding 1-2 White GAMBLE cards** to expand archetype options
3. **Create clearer signpost uncommons** for mechanic-based archetypes
4. **Red should have more REDISTRIBUTE** to mirror the political themes

---

## 5. MANA CURVE ANALYSIS

### Creature Distribution by CMC

| CMC | Count | Percentage | Target | Status |
|-----|-------|------------|--------|--------|
| 1 | 8 | 4.8% | 5-8% | GOOD |
| 2 | 34 | 20.2% | 20-25% | GOOD |
| 3 | 55 | 32.7% | 25-30% | SLIGHTLY HIGH |
| 4 | 38 | 22.6% | 15-20% | HIGH |
| 5 | 20 | 11.9% | 8-12% | GOOD |
| 6+ | 13 | 7.7% | 5-10% | GOOD |

### Assessment

**Average CMC:** ~3.1 (Target: 2.5-3.5)

The curve is **slightly top-heavy** with too many 3-4 drops and not enough aggressive 1-2 drops.

### Aggro Viability

**1-Drops (8 cards):**
- Citizen's Defender (W) - 1/2 conditional
- Simulated Labor Myr (Colorless) - 1/1 mana dork
- Few others

**2-Drops (34 cards):**
- Loan Shark (B) - 2/1 aggro
- Border Patrol Scout (W) - 2/1 flying
- Tangle Ambusher (G) - 2/2 flash
- Archive Diver (U) - 1/1
- And others

**Verdict:** Aggro is **marginally viable** but may struggle against the curve's midrange lean. Red-White and Red-Black aggro could work with the right draws.

### Recommendations

1. **Add 2-3 more aggressive 1-drops** in White and Red
2. **Reduce some 4-drops** or shift them to 3 mana
3. **Ensure each color has at least 2 playable 2-drops at common**

---

## 6. STRENGTHS OF THE SET

### Mechanical Excellence

1. **Thematic Cohesion:** The GAMBLE/COMPOUND/REDISTRIBUTE triangle creates meaningful tension between risk-taking, accumulation, and equality. This is philosophically interesting and mechanically sound.

2. **Counter Synergies:** The set has excellent internal synergy around counters. Cards like Hype Cycle (double counters), Market Crash (remove all counters), and various counter-placing effects create interesting board states.

3. **Debt Token Innovation:** The Debt token mechanic is novel and flavorful. It creates a unique "damage over time" effect that plays differently from traditional mechanics.

4. **Strong Build-Arounds:**
   - The House Edge (guaranteed gamble wins)
   - Kha-Sino, Fortune's Dealer (gamble lord)
   - Central Bank Governor (debt/redistribute lord)
   - Hype Cycle (counter manipulation saga)

5. **Flavorful Legendary Creatures:** Characters like Put-In, Tromp, Zel-Ensk, and Mak-Ron have clear real-world inspirations that add satirical depth without being heavy-handed mechanically.

### Limited Archetype Potential

Based on the cards reviewed, these archetypes appear well-supported:

| Archetype | Colors | Theme | Support Level |
|-----------|--------|-------|---------------|
| Gamble Tempo | UR | Spells + Gambling | **Strong** |
| Counter Accumulation | UG | +1/+1 Counters + COMPOUND | **Strong** |
| Debt Control | WB | Debt tokens + Life drain | **Medium** |
| Redistribute Control | WU | Counter manipulation | **Medium** |
| Artifact Aggro | BR | Artifact synergy + Aggro | **Medium** |
| Tangle Midrange | BG | Elves + Graveyard | **Medium** |
| Furnace Aggro | RW | Tokens + Burn | **Medium** |
| Myr Tribal | Colorless+ | Myr synergies | **Light** |

---

## 7. WEAKNESSES & GAPS

### Critical Issues

1. **REDISTRIBUTE Under-Represented at Common**
   - Only ~2 commons have REDISTRIBUTE
   - Drafters won't see the mechanic enough
   - Fix: Add 3-4 REDISTRIBUTE commons

2. **Green Lacks Common Creature Removal**
   - No fight spell at common
   - Only artifact/enchantment removal
   - Fix: Add "Tangle's Fury" ({1}{G} - Fight spell)

3. **Broken Combo Potential**
   - Simulated Labor Myr + Devoted Druid = Infinite mana
   - The Equalizer + Persist creatures = Infinite loops
   - Austerity Minister + Persist = Infinite sacrifices
   - Debt Ceiling + Default Cascade = Inescapable debt lock
   - Fix: Add "once per turn" restrictions or redesign

4. **Several Cards Marked "broken-needs-review"**
   - 16+ cards have this tag
   - Many create infinite combos with external cards
   - Fix: Systematic review and restriction additions

### Structural Issues

5. **Color Imbalance in GAMBLE**
   - White has ZERO gamble cards
   - This limits WR and WG archetype options
   - Consider adding 2-3 White gamble cards

6. **Over-sized Set**
   - 108 commons vs 101 target
   - 93 uncommons vs 80 target
   - Need to cut ~26 cards total

7. **Inconsistent Card Tagging**
   - Many cards tagged "unvetted"
   - Inconsistent balance assessment quality
   - Need systematic review pass

### Missing Elements

8. **No Clear Signpost Uncommons**
   - Need explicit 10 gold uncommons for draft archetypes
   - Some exist (Archive Corruptor for UB) but not all

9. **Limited Mana Fixing**
   - Only 6 lands in the set
   - Need dual land cycle at common or uncommon
   - Consider "Processing Lands" that ETB tapped + scry

10. **Weak 1-Drop Slot**
    - Only 8 creatures at CMC 1
    - Aggro decks need more options

---

## 8. RECOMMENDATIONS

### Immediate Priority (Before Playtesting)

#### Cards to Add:

1. **Tangle's Fury** (Green Common)
   ```
   {1}{G} - Instant
   Target creature you control fights target creature you don't control.
   ```

2. **5 REDISTRIBUTE Commons** (one per color)
   ```
   White: Equitable Distribution ({2}{W} - Sorcery - Redistribute among creatures with the greatest and least power)
   Blue: Data Normalization ({1}{U} - Instant - Redistribute. Scry 1)
   Black: Spite Tax ({1}{B} - Instant - Redistribute among up to two Debt tokens. Target opponent loses 2 life)
   Red: Volatile Equalization ({1}{R} - Sorcery - Redistribute among two creatures. Deal 1 damage to each of them)
   Green: Nature's Balance ({2}{G} - Sorcery - Redistribute among creatures you control. Put a +1/+1 counter on each)
   ```

3. **Common Dual Land Cycle**
   ```
   Processing Gate (5 lands)
   Land
   ~ enters tapped.
   {T}: Add {C} or {W/U/B/R/G}.
   When ~ enters, scry 1.
   ```

4. **2-3 More Aggressive 1-Drops**
   ```
   Foundry Conscript - {W} 1/1 "Gets +1/+0 when attacking alone"
   Spark Seeker - {R} 1/1 "Haste. Sacrifice at end of turn if it didn't deal combat damage"
   ```

#### Cards to Cut or Redesign:

1. **Simulated Labor Myr** - Add "Activate only once each turn"
2. **The Equalizer** - Change to "only redistribute among permanents you control"
3. **Austerity Minister** - Change to "At the beginning of your upkeep, you may remove..."
4. **Default Cascade + Debt Ceiling** - Either cut one or add "once per turn" clause
5. **Supreme Arbiter of Order** - Change to "tap up to two other nonland permanents"
6. **Central Planner** - Limit to "permanents with +1/+1 or -1/-1 counters"

### Medium Priority (Balance Pass)

1. Review all 16+ "broken-needs-review" cards
2. Standardize power/toughness distributions
3. Add missing signpost uncommons for all 10 archetypes
4. Cut 26 cards total to reach target set size (prioritize cutting weaker duplicative effects)

### Long-term (After Playtesting)

1. Evaluate Debt token damage rate (currently 1 per counter, may need adjustment)
2. Test GAMBLE variance feel (is 50/50 too swingy?)
3. Assess REDISTRIBUTE impact on game length
4. Balance mythic power levels relative to each other

---

## Appendix A: Color Statistics

| Color | Total | Common | Uncommon | Rare | Mythic |
|-------|-------|--------|----------|------|--------|
| White | 46 | 23 | 14 | 7 | 2 |
| Blue | 42 | 20 | 13 | 7 | 2 |
| Black | 45 | 22 | 13 | 7 | 3 |
| Red | 34 | 16 | 10 | 5 | 3 |
| Green | 32 | 16 | 9 | 5 | 2 |
| Colorless | 31 | 12 | 11 | 5 | 3 |
| Multicolor | ~57 | 0 | 23 | 32 | 3 |

**Note:** Red and Green appear under-represented at common compared to White, Blue, and Black.

---

## Appendix B: Cards Flagged for Review

The following cards have the "broken-needs-review" tag and require balance attention:

1. Academy Headmaster - Token generation + sacrifice value too high
2. Asylum Seeker - Solemnity creates permanent hexproof
3. Austerity Minister - Enables persist infinite combos
4. Bailout Facilitator - Reanimation + counters + sac draw is overloaded
5. Bubble Speculator - Can target opponent's permanents for forced sacrifice
6. Central Planner - Too broad counter redistribution
7. Chaos Arbiter - 50% spell copy with no mana cost
8. Default Cascade - Infinite debt lock with Debt Ceiling
9. Debt Ceiling - See above
10. Hype Cycle - 4x counter multiplication enables many combos
11. Market Crash - Dark Depths instant combo
12. Put-In, the Iron Despot - Sacrifice loop potential
13. Simulated Labor Myr - Infinite mana with Devoted Druid
14. Supreme Arbiter of Order - Near-complete stax lock
15. The Equalizer - Persist infinite loops
16. The Grand Equalizer - Mass counter strip too powerful
17. Furnace Revolution - Mycosynth Lattice combo

---

## Conclusion

**Mirrodin Manifest** is an ambitious and creative custom set with strong thematic resonance and interesting mechanical innovations. The GAMBLE/COMPOUND/REDISTRIBUTE triangle creates meaningful strategic choices, and the satirical world-building adds depth without overwhelming the gameplay.

However, the set requires significant balance work before playtesting:
- Fix broken combo enablers (persist loops, infinite mana)
- Add missing removal (Green fight spell)
- Increase REDISTRIBUTE presence at common
- Trim the set to target size

With these adjustments, Mirrodin Manifest has the potential to deliver a unique and memorable Limited experience.

---

*Analysis performed by Claude Opus 4.5*
*Card data parsed from /Users/felipebonetto/Documents/Obsidian/MTG-Set/cards/*
