# MTG Set Design Guidelines & Best Practices

A comprehensive guide for designing a successful Magic: The Gathering custom set, with special attention to Limited (Draft/Sealed) and Cube environments.

---

## Table of Contents

1. [Set Structure & Skeleton](#set-structure--skeleton)
2. [Rarity Distribution](#rarity-distribution)
3. [Color Balance](#color-balance)
4. [Draft Archetypes & Signpost Uncommons](#draft-archetypes--signpost-uncommons)
5. [Mechanic Design](#mechanic-design)
6. [New World Order (Complexity Management)](#new-world-order-complexity-management)
7. [Mana Curves](#mana-curves)
8. [Creature & Spell Ratios](#creature--spell-ratios)
9. [Removal Design](#removal-design)
10. [Mana Fixing](#mana-fixing)
11. [As-Fan & Theme Density](#as-fan--theme-density)
12. [Cube-Specific Considerations](#cube-specific-considerations)
13. [Playtesting](#playtesting)
14. [Common Mistakes to Avoid](#common-mistakes-to-avoid)

---

## Set Structure & Skeleton

### Standard Set Size (Draft Booster Era)

| Rarity | Count |
|--------|-------|
| **Commons** | 101 |
| **Uncommons** | 80 |
| **Rares** | 60 |
| **Mythic Rares** | 20 |
| **Basic Lands** | 20 |
| **Total** | **281** (261 non-land) |

**Small Set:**
- 60 Commons
- 40 Uncommons
- 35 Rares
- 10 Mythic Rares
- **Total: ~145 cards**

### Design Skeleton Principle

A design skeleton is your set's structural blueprint. Before designing individual cards, map out:
- How many cards of each color at each rarity
- Where your mechanics appear
- Which slots support which archetypes

> *"Oftentimes, elements are good designs in a vacuum but fail to serve a larger function in the set. If a card does not advance the larger set around it, no matter how good a design it is, it needs to go."*

**Source:** [Nuts & Bolts #13: Design Skeleton Revisited](https://magic.wizards.com/en/news/making-magic/nuts-bolts-13-design-skeleton-revisited-2021-03-22)

---

## Rarity Distribution

### Per-Color Breakdown (Standard Set)

| Rarity | Per Color | Colorless/Gold | Total |
|--------|-----------|----------------|-------|
| Common | 18-19 | 6-11 | 101 |
| Uncommon | 13-14 | 10-15 (includes signposts) | 80 |
| Rare | 10-11 | 5-10 | 60 |
| Mythic | 3-4 | 3-5 | 20 |

### The Uncommon Pinch Point

Uncommons are the **most constrained rarity**:
- Cards get pushed UP from common for complexity
- Cards get pushed DOWN from rare to matter more in Limited
- This creates a very tight fit

> *"Uncommons are famous among Magic designers for being the pinch point of the set."*

### Rare/Mythic Philosophy

- Rares provide **excitement**, not structure
- Mythics should feel special and impactful
- Don't put essential Limited infrastructure at rare

**Source:** [Nuts & Bolts #4: Higher Rarities](https://magic.wizards.com/en/news/making-magic/nuts-bolts-higher-rarities-2012-02-27)

---

## Color Balance

### The Golden Rule

**Commons, uncommons, and rares must be color-balanced.**

Each color should have approximately equal representation at each rarity. Imbalance makes certain colors over- or under-drafted.

### Standard Distribution

| Rarity | White | Blue | Black | Red | Green | Colorless | Multicolor |
|--------|-------|------|-------|-----|-------|-----------|------------|
| Common (101) | 18 | 18 | 18 | 18 | 18 | 9-11 | 0 |
| Uncommon (80) | 13 | 13 | 13 | 13 | 13 | 5 | 10 (signposts) |
| Rare (60) | 10 | 10 | 10 | 10 | 10 | 5 | 5 |
| Mythic (20) | 3 | 3 | 3 | 3 | 3 | 2-3 | 2-3 |

### Color Pie Respect

> *"You're perfectly allowed to design a monoblue creature with double strike or a monowhite sorcery that makes opponents discard cards — but be prepared to catch severe criticism for it."*

- Bends are acceptable with strong justification
- Breaks should be extremely rare
- Flavor does not justify breaking the color pie

**Source:** [MTGNexus - So You Want to Build a Set](https://www.mtgnexus.com/articles/1081-so-you-want-to-build-a-set-part-1-what-should-you-respect)

---

## Draft Archetypes & Signpost Uncommons

### The 10 Color Pair Archetypes

Every Limited set should have **10 two-color draft archetypes**, one for each color pair:

| Color Pair | Common Archetype Themes |
|------------|------------------------|
| WU (Azorius) | Flyers, ETB, Control |
| UB (Dimir) | Control, Graveyard, Mill |
| BR (Rakdos) | Aggro, Sacrifice |
| RG (Gruul) | Midrange, Power matters |
| GW (Selesnya) | Tokens, +1/+1 counters, Go-wide |
| WB (Orzhov) | Lifegain, Aristocrats |
| UR (Izzet) | Spells-matter, Artifacts |
| BG (Golgari) | Graveyard, +1/+1 counters |
| RW (Boros) | Aggro, Equipment, Tokens |
| GU (Simic) | +1/+1 counters, Ramp |

### Signpost Uncommons

**Every archetype needs a signpost uncommon** — a gold two-color card that:
1. Signals the archetype's theme to drafters
2. Provides mechanical glue for the deck
3. Acts as a draft signal (if you see it late, the archetype is open)

> *"Don't be afraid to push the power level a bit beyond what you might do for a normal uncommon. Make them pickable — maybe even first-pick pickable."*

### Archetype Support Structure

Each two-color archetype should have **at least 6 support cards**:
- 2x monocolor Commons (one per color)
- 2x monocolor Uncommons (one per color)
- 2x multicolor Uncommons (including signpost)

**Sources:** [Beacon of Creation - Signposts 101](https://www.beaconofcreation.com/2023/04/21/signposts-101/), [MTGNexus - Draft Archetypes](https://www.mtgnexus.com/articles/1091-sywtbas-draft-archetypes)

---

## Mechanic Design

### Number of Mechanics

A typical set has **3-5 named mechanics**:
- 1-2 flagship mechanics (appear frequently, define the set)
- 1-2 secondary mechanics (support themes)
- 1 returning mechanic (optional, adds familiarity)

### Mechanic Spread

> *"Having a mechanic that only appears on creatures is fine, but you should try to have another mechanic that appears on instants and sorceries, or another that can appear on all card types."*

Spread mechanics across:
- **Card types:** Creatures, instants, sorceries, enchantments, artifacts
- **Colors:** Every color should have something new to explore
- **Rarities:** Most mechanics should appear at common

### Keyword Viability Test

Before creating a keyword, ask:
- Can this appear on 5+ cards? 10+? 20+?
- Does it create interesting gameplay decisions?
- Is it simple enough to remember?

> *"Custom magic players are far too eager to create new keywords for things when what they really want to design is a card, rather than a keyword."*

**Source:** [MTG Salvation - Choosing Set Mechanics](https://www.mtgsalvation.com/forums/magic-fundamentals/custom-card-creation/600815-article-choosing-set-mechanics)

---

## New World Order (Complexity Management)

### Core Principle

> *"Commons should never be very complex."*

New World Order (NWO) manages complexity by rarity:
- **Commons:** Simple, low complexity
- **Uncommons:** Medium complexity allowed
- **Rares/Mythics:** High complexity acceptable

### Why It Matters

Commons make up the majority of cards new players own. Keeping them simple:
- Lowers barrier to entry
- Reduces board complexity
- Makes Limited games more readable

### NWO Guidelines for Commons

1. **No more than one other card affected** — Commons shouldn't require tracking multiple permanents
2. **Minimal text** — Keep word count low
3. **Familiar effects** — Use established patterns
4. **Vanilla/French vanilla creatures are good** — Don't fear simplicity

### Complexity Budget

You have a limited "complexity budget" at common. Spend it wisely:
- A set can have some complex commons, but not many
- "Red-flag" complex commons during review
- If a card is too complex for common, move it to uncommon

### NWO Does NOT Mean

- Commons can't be powerful (a vanilla 8/8 for 2 mana is simple but strong)
- Sets can't have depth (complexity shifts to higher rarities)
- Every common must be boring

**Sources:** [Wizards - New World Order](https://magic.wizards.com/en/news/making-magic/new-world-order-2011-12-05), [MTG Salvation - NWO + Redflagging Primer](https://www.mtgsalvation.com/forums/magic-fundamentals/custom-card-creation/578926-primer-nwo-redflagging)

---

## Mana Curves

### Limited Deck Mana Curve

The ideal Limited deck curve (40 cards, 17 lands, 23 spells):

| CMC | Number of Cards |
|-----|-----------------|
| 1 | 0-2 |
| 2 | 5-8 |
| 3 | 5-7 |
| 4 | 2-6 |
| 5+ | 0-4 |

> *"Most Limited curves start at two mana, because one-mana creatures are quickly made obsolete."*

### The "Hump" at 3-4

Distribute creatures with the curve's peak at 3-4 mana. This is where most Limited action happens.

### One-Drops in Limited

One-drops have **diminishing returns** — they're good turn one but become obsolete quickly. This is the largest gap between Limited and Constructed.

### Aggro vs Control Curves

**Aggro:**
- 6-9 creatures under 3 mana
- 5-10 creatures at 3-4 mana
- 2-3 cards above 4 mana

**Control/Midrange:**
- Fewer low-cost spells
- Peak at 3-4 mana
- More 5+ mana finishers

**Sources:** [Wizards - How to Build a Mana Curve](https://magic.wizards.com/en/news/feature/how-build-mana-curve-2017-05-18), [Draftsim - Mana Curves](https://draftsim.com/mtg-mana-curve/)

---

## Creature & Spell Ratios

### Standard Limited Deck Composition

| Category | Count |
|----------|-------|
| Creatures | 15-17 |
| Non-creatures | 6-8 |
| Lands | 17 |
| **Total** | 40 |

### Set-Level Creature Ratio

At common, aim for approximately:
- **60-65% creatures**
- **35-40% non-creatures** (instants, sorceries, enchantments, artifacts)

This ensures players can reliably build creature-based decks.

### Aggro Needs More Creatures

Aggro decks need at least 15 creatures. Design your commons to support this.

**Source:** [MTG Arena Zone - Limited Strategy Guide](https://mtgazone.com/mtg-limited-strategy-a-guide-to-drafting-deck-building-and-tactics/)

---

## Removal Design

### Removal at Common

Every color needs access to removal at common:
- **White:** Pacifism effects, conditional exile
- **Blue:** Bounce, tap-down
- **Black:** Destroy/kill spells, -X/-X effects
- **Red:** Direct damage
- **Green:** Fight effects, artifact/enchantment removal

### Removal Density

A healthy Limited format needs:
- 2-3 common removal spells per color
- 1-2 premium removal spells at uncommon per color
- Rare removal can be splashy but shouldn't be required

### The Problem with Sparse Removal

> *"Good removal is rare" makes Limited "about beating your opponent down with dumb creatures" — linear and uninteractive.*

### Removal Quality Gradient

- **Common:** Conditional, inefficient, or narrow
- **Uncommon:** Efficient but still limited
- **Rare:** Premium, unconditional, or bonus effects

---

## Mana Fixing

### Mana Fixing at Common

For a **two-color focused** set:
- Light fixing (1-2 common cycles)
- Tapped dual lands or mana rocks

For a **multicolor focused** set:
- Heavy fixing (multiple common cycles)
- Consider tri-lands or better duals

### The Goldilocks Problem

> *"Too many dual lands in a Limited environment can dilute it into multicolor good stuff strategies."*

Balance fixing to:
- Enable two-color decks consistently
- Allow splashing as a cost (not free)
- Prevent 4-5 color goodstuff from dominating

### Common Dual Land Cycles

Good options for common fixing:
- **Gain lands** (ETB tapped, gain 1 life)
- **Basic land types** (fetchable but ETB tapped)
- **Artifact duals** (add synergy dimension)

**Source:** [Wizards - Mana with All the Fixin's](https://magic.wizards.com/en/news/making-magic/mana-all-fixins-2009-03-23)

---

## As-Fan & Theme Density

### What is As-Fan?

**As-fan** = the average number of cards with a theme/mechanic in any random booster pack.

- As-fan of 1 = 1 card per pack on average
- As-fan of 2 = 2 cards per pack on average

### Calculating As-Fan

For a mechanic on X commons in a 101-common set with 10 commons per pack:
```
As-fan = X × (10 / 101)
```

Example: A mechanic on 15 commons has an as-fan of ~1.5 (15 × 0.099 ≈ 1.49)

### Theme Density Guidelines

| Theme Type | Recommended As-Fan |
|------------|-------------------|
| Threshold 1 (need one card) | 1.0-1.5 |
| Scaling (more is better) | 2.0-3.0 |
| Build-around | 0.5-1.0 |

### Getting As-Fan Right

> *"Getting the as-fan right is tricky, and Wizards spends a lot of time playtesting to get it right."*

If your theme isn't showing up enough in draft, you need more cards at common supporting it.

**Source:** [Nuts & Bolts #12: Limited (Themes)](https://magic.wizards.com/en/news/making-magic/nuts-bolts-12-part-2-limited-themes-2020-03-16)

---

## Cube-Specific Considerations

### Cube Sizes

| Size | Players | Notes |
|------|---------|-------|
| 360 | 8 | Minimum for full draft, tight balance |
| 450 | 8 | Some variance, easier to build |
| 540 | 8-10 | Good variety |
| 720 | 8-12 | High variance, harder to balance |

> *"Starting with the 360-card minimum is recommended for first-time builders."*

### The 3:2:1 Ratio (Aggro:Midrange:Control)

For balanced cube archetypes:
- **3 parts Aggro creatures**
- **2 parts Midrange creatures**
- **1 part Control creatures**

> *"It wasn't until aggro made up roughly 1/3 of the decks at the table that control really started to be challenged."*

### Cross-Pollination

Cards should support multiple archetypes:
- Mana dorks work in ramp AND Upheaval decks
- Swords to Plowshares is good in ANY white deck
- Sacrifice outlets work in aristocrats AND reanimator

> *"While you should include powerful cards to support each archetype, it's also important to include cards that work in multiple archetypes."*

### Avoid Over-Supporting

> *"Over supporting archetypes can feel forced in draft and actually reduce the number of interesting directions you can take decks."*

Don't include too many narrow cards that only work in one deck.

### Singleton Principle

Cubes are typically **singleton** (one copy of each card):
- More variety per draft
- Better balance
- Harder to force specific strategies

### Cube Average CMC

- **Aggro-focused:** ~2.5-3.0 average CMC
- **Balanced:** ~3.0 average CMC
- **Midrange/Control-focused:** ~3.0-3.5 average CMC

**Sources:** [Wizards - Building Your First Cube](https://magic.wizards.com/en/news/feature/building-your-first-cube-2016-05-19), [Riptide Lab - Cube Academy](https://riptidelab.com/cube-academy/building-your-first-cube/), [Star City Games - How To Balance Limited Archetypes](https://articles.starcitygames.com/magic-the-gathering/how-to-balance-limited-archetypes-for-cube/)

---

## Playtesting

### When to Start

> *"You can start playtesting as soon as you've filled in your commons."*

Don't wait until the set is "done" — early playtesting reveals fundamental issues.

### Playtesting Goals

1. **Test mechanics** — Are they fun? Too complex? Too weak?
2. **Test archetypes** — Are all 10 color pairs viable?
3. **Test mana curves** — Do games flow well?
4. **Test removal** — Is there enough? Too much?

### Playtesting Rules

> *"Remember to prioritize playing different colors and themes from playtest to playtest. The goal isn't to win, it's to experience the set."*

- Draft different archetypes each session
- Take notes on what works and what doesn't
- Be willing to kill your darlings

### Iteration Cycle

1. Playtest
2. Identify problems
3. Make targeted changes
4. Playtest again
5. Repeat

---

## Common Mistakes to Avoid

### Design Mistakes

1. **Strictly better cards** — Don't obsolete existing cards
2. **Over-complexity at common** — Respect NWO
3. **Breaking the color pie** — Flavor doesn't justify breaks
4. **Too many keywords** — Only create keywords that appear on 5+ cards
5. **Cards that don't serve the set** — Every card should advance the set's goals

### Limited Environment Mistakes

1. **Unbalanced colors** — All five colors should be viable
2. **Missing removal** — Every color needs ways to interact
3. **No signpost uncommons** — Archetypes need clear signals
4. **Wrong as-fan** — Themes need enough density to draft
5. **Insufficient mana fixing** — Players need to cast their spells

### Cube Mistakes

1. **No aggro support** — Aggro needs deliberate inclusion
2. **Too many narrow cards** — Cross-pollination matters
3. **Power level imbalance** — All colors should be roughly equal
4. **Ignoring mana curves** — Cube needs playable cards at all CMCs
5. **Not playtesting** — The only way to find problems

---

## Quick Reference: Set Checklist

### Before Finalizing Your Set

- [ ] 101 Commons (color-balanced: ~18 per color + colorless)
- [ ] 80 Uncommons (color-balanced: ~13 per color + 10 gold signposts)
- [ ] 60 Rares (color-balanced: ~10 per color + gold/colorless)
- [ ] 20 Mythic Rares (color-balanced: ~3 per color + gold/colorless)
- [ ] 10 Signpost Uncommons (one per color pair)
- [ ] 10 Viable Draft Archetypes
- [ ] 3-5 Named Mechanics
- [ ] Removal at common in every color
- [ ] Mana fixing appropriate for multicolor density
- [ ] NWO-compliant commons
- [ ] Playtested multiple times

### For Cube Conversion

- [ ] 4x each Common
- [ ] 2x each Uncommon
- [ ] 1x each Rare/Mythic
- [ ] Aggro:Midrange:Control ratio ~3:2:1
- [ ] Cross-pollinating cards included
- [ ] Singleton structure considered

---

## Sources & Further Reading

### Official Wizards Resources
- [Nuts & Bolts Series (Mark Rosewater)](https://magic.wizards.com/en/news/making-magic/nuts-bolts-13-design-skeleton-revisited-2021-03-22)
- [New World Order](https://magic.wizards.com/en/news/making-magic/new-world-order-2011-12-05)
- [Building Your First Cube](https://magic.wizards.com/en/news/feature/building-your-first-cube-2016-05-19)

### Community Resources
- [MTGNexus - So You Want to Build a Set](https://www.mtgnexus.com/articles/1081-so-you-want-to-build-a-set-part-1-what-should-you-respect)
- [MTGNexus - Draft Archetypes](https://www.mtgnexus.com/articles/1091-sywtbas-draft-archetypes)
- [Beacon of Creation - Signposts 101](https://www.beaconofcreation.com/2023/04/21/signposts-101/)
- [MTG Salvation - NWO Primer](https://www.mtgsalvation.com/forums/magic-fundamentals/custom-card-creation/578926-primer-nwo-redflagging)
- [MTG Salvation - Set Skeletons Primer](https://www.mtgsalvation.com/forums/magic-fundamentals/custom-card-creation/597944-primer-set-skeletons)

### Cube Resources
- [Riptide Lab - Cube Academy](https://riptidelab.com/cube-academy/building-your-first-cube/)
- [Lucky Paper - Cube Power Level Guide](https://luckypaper.co/articles/cube-power-level-a-users-guide/)
- [Star City Games - Balancing Limited Archetypes](https://articles.starcitygames.com/magic-the-gathering/how-to-balance-limited-archetypes-for-cube/)
- [Cool Stuff Inc - Comprehensive Cube Archetypes](https://www.coolstuffinc.com/a/adammelfa-seo-07172024-the-comprehensive-guide-to-cube-archetypes-what-goes-into-a-cube)

### Limited Strategy
- [MTG Arena Zone - Limited Strategy Guide](https://mtgazone.com/mtg-limited-strategy-a-guide-to-drafting-deck-building-and-tactics/)
- [Draftsim - Mana Curve Guide](https://draftsim.com/mtg-mana-curve/)
- [Draftsim - Lands in Limited](https://draftsim.com/mtg-40-card-deck-number-of-lands/)
