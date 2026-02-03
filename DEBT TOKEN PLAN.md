# Debt Token System: 30-Card Design Plan

## Executive Summary

This plan introduces **Debt Tokens** as a "negative token" system that synergizes with the Redistribute mechanic. Unlike Gold tokens (positive value), Debt tokens harm their controller—fitting perfectly with the set's economic/political themes.

**Design Philosophy**: Simple token, complexity on cards. Embrace cross-format interactions as features.

---

## Token Definition

### Debt Token
**Token Artifact — Debt**

```
(Debt tokens enter the battlefield with a debt counter on them.)

At the beginning of your upkeep, you lose life equal to the number of
debt counters on this permanent, then sacrifice it.
```

**Standard Progression:**
| Turn | What Happens | Life Lost |
|------|--------------|-----------|
| Created | Enters with 1 debt counter | 0 |
| Your Upkeep | Lose 1 life, sacrifice | **1** |

**Base case: 1 damage on your next upkeep** — simple, immediate, like Treasure but negative.

**Design Principles:**
- **Single counter type** = simple like Treasure/Clue/Food tokens
- **Immediate impact** = creates urgency, not delayed confusion
- **Scalable** = Compound and other effects add debt counters for more damage
- **Redistribute-compatible** = debt counters can be moved between Debt tokens

---

## Cross-Format Interactions (EMBRACED)

### This set will be played alongside other MTG cards. Here's how Debt interacts:

| Other Cards | Interaction | Design Verdict |
|-------------|-------------|----------------|
| **Sacrifice outlets** (Ashnod's Altar, etc.) | Sac Debt before upkeep = avoid life loss | ✓ FEATURE: Costs activation. Default Cascade punishes. |
| **Proliferate** (Atraxa, Inexorable Tide) | Adds debt counters = more damage | ✓ FEATURE: Proliferate has a cost now |
| **Counter removal** (Hex Parasite, Vampire Hexmage) | Remove debt counters = reduce/avoid damage | ✓ FEATURE: Costs resources (life, mana, creatures) |
| **Solemnity** | Debt enters with 0 counters = 0 damage | ✓ FEATURE: 3-mana hoser does its job |
| **Affinity/Improvise** | Debt counts toward artifact costs | ✓ FLAVORFUL: Leveraging debt for short-term gain! |
| **Artifact destruction** | Destroy Debt before upkeep = avoid damage | ✓ FEATURE: Spending removal on a token |
| **Panharmonicon** | ETB triggers doubled (if any exist) | ✓ Doesn't affect base token |
| **Doubling Season** | Creates 2 Debt tokens + 2 counters each | ✓ Only doubles YOUR tokens (self-harm) |

**Key Insight**: Every "escape" costs resources. In Limited, these cards don't exist. In Constructed, dedicating resources to avoid Debt is still meaningful.

---

## Mechanical Synergies

### Redistribute + Debt
- **Move debt counters** between Debt tokens = equalize the damage
- **Strategic play**: Give opponent many small Debts, then Compound one to 5 counters, then redistribute to spread the pain
- **Defensive play**: Redistribute your big Debt's counters onto opponent's Debts

### Compound + Debt
- **Compound on Debt** → add debt counter → more damage when it triggers
- Stack Compound effects to create massive Debts (3, 4, 5+ damage)
- Creates tension: "Do I Compound my opponent's Debt or my creature's +1/+1 counters?"

### Gold Tokens + Debt
- Economic hedge: [[Inflation Hedge]] creates Gold when opponents get Debt
- Thematic opposition: real value (Gold) vs. paper promises (Debt)
- Flavor: "Hedge against the coming collapse"

### Hype Cycle + Debt
- [[Hype Cycle]] doubles ALL counters including debt counters
- A 1-counter Debt becomes 2-counter = 2 damage
- Risk/reward: doubling can backfire on your own Debts

---

## Broader MTG Ecosystem Considerations

### Why "Simple Token, Complexity on Cards"?

MTG tokens that see play are simple:
- **Treasure**: Sac for mana
- **Clue**: Pay 2, sac, draw
- **Food**: Pay 2, sac, gain 3 life
- **Blood**: Pay 1, discard, sac, draw

**Debt follows this pattern**: Enters with counter, upkeep trigger, sacrifice. One counter type, one trigger.

### Avoiding the "Parasitic Mechanic" Trap

A mechanic is **parasitic** if it only works within its own set (e.g., Splice onto Arcane). Debt avoids this by:

1. **Using standard counter types**: "Debt counter" is just a counter. Proliferate, Hex Parasite, and any counter manipulation work.
2. **Being an artifact token**: Interacts with artifact themes in Mirrodin, Kaladesh, Brothers' War, etc.
3. **Having sacrifice triggers**: Works with aristocrats themes (Zulaport Cutthroat, Blood Artist in other sets)
4. **Not requiring set-specific support**: A single Debt token is meaningful on its own.

### Format-Specific Behavior

| Format | Debt's Role |
|--------|-------------|
| **Limited (this set)** | Core pressure mechanic, few answers |
| **Standard** | Depends on artifact/sacrifice support in Standard |
| **Modern** | Artifact sacrifice outlets exist; creates interesting tension |
| **Legacy/Vintage** | Trivially answered but still a resource tax |
| **Commander** | Political tool; multiplayer Debt distribution |
| **Cube** | Scales with cube's counter/artifact themes |

### Cards That Answer Debt (from other sets)

These existing cards answer Debt — this is GOOD (answers should exist):

- **White**: Any artifact removal
- **Blue**: Bounce returns Debt to nowhere (tokens cease to exist)
- **Black**: Sacrifice outlets (Viscera Seer, etc.)
- **Red**: Artifact destruction (Shattering Spree)
- **Green**: Naturalize effects, counter removal (Thrun's effect style)
- **Colorless**: Hex Parasite, Vampire Hexmage

---

## Lore Integration

**The Credit Crisis of Mirrodin**

The Mer-Ikan Foundry's endless expansion requires endless resources. The High Artificers discovered they could finance today's projects with tomorrow's promises—**Debt Tokens**. At first, the system worked: growth seemed unlimited.

But debt compounds. The interest grows faster than the principal. Now, whole forge-districts are collapsing under the weight of debts they can never repay. The Central Bank Governor redistributes the burden, but redistribution doesn't eliminate debt—it just spreads the suffering.

**Key Characters:**
- **Vulture Capitalists**: Profit from others' financial collapse
- **Collection Agents**: Enforce payment through pain
- **Central Bank Governor**: The "savior" who spreads debt equally (making everyone equally miserable)
- **Loan Sharks**: Create debt on others for short-term gain

---

## The 30 Cards

### Category 1: Debt Creators (8 cards)

#### 1. Loan Shark
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | Black |
| Type | Creature — Human Rogue |
| Mana Cost | {1}{B} |
| P/T | 2/1 |

**Rules Text:**
> Whenever Loan Shark deals combat damage to a player, that player creates a Debt token.
>
> *(Debt tokens enter with a debt counter. At your upkeep, lose life equal to its debt counters, then sacrifice it.)*

**Flavor:** *"The first payment is always free."*

**Design Notes:**
- Black common creature
- Aggressive body that punishes unblocked attacks
- Primary debt-creation at common

---

#### 2. Predatory Lending
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | Black |
| Type | Instant |
| Mana Cost | {B} |

**Rules Text:**
> Target opponent creates a Debt token. You gain 2 life.

**Flavor:** *"Sign here. Don't read the fine print."*

**Design Notes:**
- Black common instant
- Cheap debt creation + life swing
- Enables aggro debt strategies

---

#### 3. Bailout Package
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | White |
| Type | Sorcery |
| Mana Cost | {2}{W} |

**Rules Text:**
> Destroy target artifact. Its controller creates two Debt tokens.

**Flavor:** *"The Foundry saves you—but the Foundry never forgets."*

**Design Notes:**
- White uncommon artifact removal
- "Help" that comes with strings attached
- Flavorful: bailouts create debt
- [[Lore]] connection: government intervention

---

#### 4. Credit Default
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Blue |
| Type | Instant |
| Mana Cost | {1}{U} |

**Rules Text:**
> Counter target spell unless its controller creates a Debt token or pays {3}.

**Flavor:** *"Your future is collateral."*

**Design Notes:**
- Blue uncommon counterspell
- Opponent chooses: debt or pay extra
- Creates interesting decisions
- Addresses Blue uncommon gap

---

#### 5. Myr Repo Unit
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Colorless |
| Type | Artifact Creature — Myr |
| Mana Cost | {3} |
| P/T | 2/2 |

**Rules Text:**
> When Myr Repo Unit enters the battlefield, target opponent creates a Debt token.

**Flavor:** *"Default detected. Initiating collection protocol."*

**Design Notes:**
- Colorless uncommon creature
- ETB debt creation works in any deck
- Artifact synergies with set's themes

---

#### 6. Vulture Capitalist
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | White/Black |
| Type | Creature — Human Advisor |
| Mana Cost | {2}{W}{B} |
| P/T | 3/4 |

**Rules Text:**
> Flying
>
> Whenever an opponent sacrifices a permanent, that player creates a Debt token.

**Flavor:** *"Crisis is opportunity."*

**Design Notes:**
- Orzhov rare creature
- Punishes sacrifice strategies
- Synergizes with aristocrats themes
- Creates debt during financial "crisis"

---

#### 7. Infrastructure Collapse
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Red |
| Type | Sorcery |
| Mana Cost | {3}{R}{R} |

**Rules Text:**
> Destroy all artifacts. For each artifact destroyed this way, its controller creates a Debt token.

**Flavor:** *"The bill for progress came due all at once."*

**Design Notes:**
- Red rare artifact sweeper
- Mass artifact destruction + mass debt
- [[Lore]] connection: En-Vidia Lattice collapse
- Pairs with [[Infrastructure Collapse]] mention in design notes

---

#### 8. Economic Warfare
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Blue/Black |
| Type | Enchantment |
| Mana Cost | {2}{U}{B} |

**Rules Text:**
> Whenever an opponent casts their second spell each turn, that player creates a Debt token.

**Flavor:** *"Every action has a cost. We ensure they pay it."*

**Design Notes:**
- Dimir rare enchantment
- Punishes busy turns
- Creates debt pressure over time
- [[Lore]] connection: sanctions and economic pressure

---

### Category 2: Debt Redistributors (7 cards)

#### 9. Debt Restructuring
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | White |
| Type | Sorcery |
| Mana Cost | {1}{W} |

**Rules Text:**
> Redistribute among all Debt tokens.

**Flavor:** *"The burden is now... shared."*

**Design Notes:**
- White common sorcery
- Core debt redistribution at common
- Redistributes BOTH time counters AND debt counters among all Debt tokens
- Can strategically accelerate some debts while delaying others
- [[☭REDISTRIBUTE]] primary access

---

#### 10. Austerity Measure
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | White |
| Type | Instant |
| Mana Cost | {W} |

**Rules Text:**
> Redistribute among target Debt token and target permanent with counters.

**Flavor:** *"Cuts must be made somewhere."*

**Design Notes:**
- White common instant
- Can move counters between Debt and +1/+1 counters
- Cheap trick for redistribute synergies
- Addresses White common gap

---

#### 11. Burden Shift
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Black |
| Type | Instant |
| Mana Cost | {1}{B} |

**Rules Text:**
> Redistribute among up to two target Debt tokens. Target opponent loses 2 life.

**Flavor:** *"Your debt becomes their debt. And they pay the price."*

**Design Notes:**
- Black uncommon instant
- Weaponized redistribution
- Flat 2 life loss keeps it simple while moving counters
- Can move time counters to accelerate opponent's debt
- [[☭REDISTRIBUTE]] Black access

---

#### 12. Socialized Losses
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | White/Blue |
| Type | Sorcery |
| Mana Cost | {1}{W}{U} |

**Rules Text:**
> Each player creates a Debt token. Then redistribute among all Debt tokens.

**Flavor:** *"Privatize the profits. Socialize the losses."*

**Design Notes:**
- Azorius uncommon sorcery
- Everyone gets debt, then equalized
- Perfect political commentary
- Signpost for WU control

---

#### 13. The Bailout
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | White |
| Type | Instant |
| Mana Cost | {2}{W}{W} |

**Rules Text:**
> Redistribute among all permanents with counters. For each Debt token that had counters redistributed to it, you gain 2 life.

**Flavor:** *"The Foundry always pays its debts—with other people's money."*

**Design Notes:**
- White rare instant
- Mass redistribution with life gain
- Rewards controlling many Debt tokens
- [[☭REDISTRIBUTE]] payoff card

---

#### 14. Central Bank Governor
| Property | Value |
|----------|-------|
| Rarity | Mythic |
| Color | White |
| Type | Legendary Creature — Human Advisor |
| Mana Cost | {3}{W}{W} |
| P/T | 4/5 |

**Rules Text:**
> At the beginning of each upkeep, redistribute among all Debt tokens.
>
> Whenever you redistribute, you may have target player create a Debt token.

**Flavor:** *"Stability requires... adjustments."*

**Design Notes:**
- White mythic legendary
- Ultimate debt/redistribute lord
- Creates + spreads debt automatically
- [[Lore]] connection: central banking critique

---

#### 15. Quantitative Destruction
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Blue/Red |
| Type | Sorcery |
| Mana Cost | {2}{U}{R} |

**Rules Text:**
> Each opponent creates X Debt tokens, where X is the number of artifacts you control. Then redistribute among all Debt tokens.

**Flavor:** *"Print money. Spread the consequences."*

**Design Notes:**
- Izzet rare sorcery
- Rewards artifact-heavy builds
- Mass debt creation + spread
- [[Lore]] connection: quantitative easing

---

### Category 3: Debt Profiteers (6 cards)

#### 16. Collection Agent
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | Black |
| Type | Creature — Human Rogue |
| Mana Cost | {2}{B} |
| P/T | 2/2 |

**Rules Text:**
> Whenever an opponent sacrifices a Debt token, you draw a card.

**Flavor:** *"I'm just here for what's owed."*

**Design Notes:**
- Black common creature
- Card draw when opponent's debt comes due
- Triggers when Debt timer runs out (sacrificed)
- Build-around for debt strategies
- Addresses Black common gap

---

#### 17. Debt Accumulator
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | Blue |
| Type | Creature — Vedalken Wizard |
| Mana Cost | {1}{U} |
| P/T | 1/3 |

**Rules Text:**
> {T}: Put a debt counter on target Debt token.

**Flavor:** *"Time is money. Specifically, your money."*

**Design Notes:**
- Blue common creature
- Active debt increase (more damage when it comes due)
- Can target your own or opponent's Debt
- Addresses Blue common gap

---

#### 18. Compound Interest
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Black |
| Type | Instant |
| Mana Cost | {1}{B} |

**Rules Text:**
> Put two debt counters on target Debt token.

**Flavor:** *"The debt grows faster than you can pay."*

**Design Notes:**
- Black uncommon instant
- Increases debt amount (more life lost when it comes due)
- Simple and direct debt acceleration
- Combat trick timing (instant before their upkeep)

---

#### 19. Debt Collector Myr
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Colorless |
| Type | Artifact Creature — Myr |
| Mana Cost | {2} |
| P/T | 1/1 |

**Rules Text:**
> Whenever an opponent sacrifices a Debt token, put a +1/+1 counter on Debt Collector Myr.

**Flavor:** *"Payment received. Processing."*

**Design Notes:**
- Colorless uncommon creature
- Grows when opponent's debt comes due
- Works in any debt-focused deck
- Artifact tribal support

---

#### 20. Foreclosure Notice
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Black |
| Type | Enchantment — Aura |
| Mana Cost | {2}{B} |

**Rules Text:**
> Enchant creature an opponent controls
>
> Enchanted creature's controller creates a Debt token at the beginning of their upkeep.
>
> When enchanted creature leaves the battlefield, you draw 2 cards.

**Flavor:** *"Default in 3... 2..."*

**Design Notes:**
- Black rare aura
- Recurring debt creation
- Draws cards when creature dies
- Creates pressure + card advantage

---

#### 21. Master of Debt
| Property | Value |
|----------|-------|
| Rarity | Mythic |
| Color | Black |
| Type | Legendary Creature — Human Warlock |
| Mana Cost | {3}{B}{B} |
| P/T | 4/4 |

**Rules Text:**
> Deathtouch
>
> Whenever an opponent creates a Debt token, you create a Treasure token.
>
> {2}{B}, {T}: Target opponent creates a Debt token.

**Flavor:** *"Your debt is my wealth."*

**Design Notes:**
- Black mythic legendary
- Turns opponent's debt into your treasure
- Active debt creation ability
- [[Gold Token]] inverse relationship

---

### Category 4: Debt Relief & Answers (5 cards)

#### 22. Debt Forgiveness
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | White |
| Type | Instant |
| Mana Cost | {1}{W} |

**Rules Text:**
> Destroy target Debt token. You gain life equal to the number of debt counters on it.

**Flavor:** *"Mercy is its own reward."*

**Design Notes:**
- White common instant
- Primary debt removal at common
- Life gain scales with debt amount (rewards destroying big debts)
- Addresses White common gap

---

#### 23. Bankruptcy Filing
| Property | Value |
|----------|-------|
| Rarity | Common |
| Color | Green |
| Type | Sorcery |
| Mana Cost | {G} |

**Rules Text:**
> Destroy all Debt tokens you control. You can't create Debt tokens until end of turn.

**Flavor:** *"The Tangle knows no currency."*

**Design Notes:**
- Green common sorcery
- Self-debt removal
- Green's philosophy: reject debt system
- Addresses Green common gap

---

#### 24. Jubilee Declaration
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | White |
| Type | Sorcery |
| Mana Cost | {2}{W}{W} |

**Rules Text:**
> Destroy all Debt tokens. Each player gains 2 life for each Debt token they controlled that was destroyed this way.

**Flavor:** *"All debts are forgiven. Begin again."*

**Design Notes:**
- White uncommon sorcery
- Mass debt removal
- Biblical jubilee reference
- [[Lore]] connection: debt relief programs

---

#### 25. Natural Economy
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Green |
| Type | Enchantment |
| Mana Cost | {1}{G} |

**Rules Text:**
> If you would lose life from a Debt token, prevent that life loss instead.
>
> At the beginning of your end step, remove a debt counter from a Debt token you control.

**Flavor:** *"The forest trades in sunlight, not promises."*

**Design Notes:**
- Green uncommon enchantment
- Passive debt protection (prevents Debt life loss entirely)
- Slowly reduces your debt counters (eventually to 0 = no damage)
- Green's nature-based economy rejects the debt system
- Cross-format: Strong hoser but only protects YOU

---

#### 26. Inflation Hedge
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Green/White |
| Type | Artifact |
| Mana Cost | {2}{G}{W} |

**Rules Text:**
> Whenever a Debt token enters the battlefield under an opponent's control, you create a Gold token.
>
> Sacrifice Inflation Hedge: Destroy all Debt tokens.

**Flavor:** *"When paper fails, gold endures."*

**Design Notes:**
- Selesnya rare artifact
- [[Gold Token]] synergy
- Creates gold when opponents get debt
- Emergency debt destruction
- [[Lore]] connection: gold rally

---

### Category 5: Debt Synergy Support (4 cards)

#### 27. Debt Ceiling
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | White/Blue |
| Type | Enchantment |
| Mana Cost | {1}{W}{U} |

**Rules Text:**
> Debt tokens enter the battlefield with two additional debt counters on them.
>
> Whenever a player would create one or more Debt tokens, they create that many plus one instead.

**Flavor:** *"The limit? What limit?"*

**Design Notes:**
- Azorius uncommon enchantment
- Amplifies all debt creation (more tokens + bigger debts)
- Debt enters with 3 debt counters instead of 1 = 3x damage when due
- Affects ALL players symmetrically
- Political commentary on debt ceilings

---

#### 28. Default Cascade
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Black/Red |
| Type | Enchantment |
| Mana Cost | {B}{R} |

**Rules Text:**
> Whenever a Debt token is destroyed or sacrificed, its controller creates a new Debt token.

**Flavor:** *"Pay one debt, create another."*

**Design Notes:**
- Rakdos uncommon enchantment
- Prevents easy debt removal
- Creates cascading debt
- Financial trap

---

#### 29. Interest Rate Hike
| Property | Value |
|----------|-------|
| Rarity | Uncommon |
| Color | Red |
| Type | Instant |
| Mana Cost | {1}{R} |

**Rules Text:**
> Put two debt counters on each Debt token.

**Flavor:** *"Adjustment effective immediately."*

**Design Notes:**
- Red uncommon instant
- Mass debt increase: every Debt now deals +2 damage
- Devastating when multiple Debts are in play (3 Debts = +6 total damage)
- Red's chaotic, destructive economics
- Cross-format: Works with ANY Debt tokens in any format

---

#### 30. Debt-to-Equity Swap
| Property | Value |
|----------|-------|
| Rarity | Rare |
| Color | Blue |
| Type | Instant |
| Mana Cost | {2}{U}{U} |

**Rules Text:**
> Target opponent sacrifices all Debt tokens they control. For each Debt token sacrificed this way, you draw a card and that player creates a 1/1 colorless Myr artifact creature token.

**Flavor:** *"Your debt becomes our property."*

**Design Notes:**
- Blue rare instant
- Converts debt to card advantage
- Opponent gets tokens (mixed blessing)
- Financial jargon flavor

---

## Distribution Summary

### By Color

| Color | Commons | Uncommons | Rares | Mythics | Total |
|-------|---------|-----------|-------|---------|-------|
| White | 3 | 2 | 1 | 1 | 7 |
| Blue | 2 | 1 | 1 | 0 | 4 |
| Black | 3 | 2 | 1 | 1 | 7 |
| Red | 0 | 1 | 1 | 0 | 2 |
| Green | 1 | 1 | 0 | 0 | 2 |
| White/Blue | 0 | 2 | 0 | 0 | 2 |
| Blue/Black | 0 | 0 | 1 | 0 | 1 |
| Blue/Red | 0 | 0 | 1 | 0 | 1 |
| Black/Red | 0 | 1 | 0 | 0 | 1 |
| White/Black | 0 | 0 | 1 | 0 | 1 |
| Green/White | 0 | 0 | 1 | 0 | 1 |
| Colorless | 0 | 2 | 0 | 0 | 2 |
| **Total** | **9** | **12** | **8** | **2** | **31** |

### By Rarity

| Rarity | Count | Notes |
|--------|-------|-------|
| Common | 9 | Addresses 9/29 common gap |
| Uncommon | 12 | Addresses 12/22 uncommon gap |
| Rare | 8 | Fills rare slots |
| Mythic | 2 | High-impact legendaries |

### Creature vs Non-Creature

| Type | Count |
|------|-------|
| Creatures | 12 |
| Non-Creatures | 18 |

---

## Gameplay Patterns

### Debt Aggro (Black-based)
1. T2: Loan Shark
2. T3: Attack → opponent creates Debt #1 (1 debt counter)
3. Opponent's T3 upkeep: loses 1 life from Debt #1
4. T4: Attack → Debt #2; cast Compound Interest on Debt #2 (+2 counters = 3 total)
5. Opponent's T4 upkeep: loses 3 life from Debt #2
6. **Total: 4 damage from debt over 2 attack cycles** — aggressive but fair

### Debt Control (White/Blue)
1. Deploy Socialized Losses (everyone gets Debt, then redistribute counters)
2. Play Central Bank Governor (creates Debt when you redistribute)
3. Redistribute to concentrate debt counters on opponent's Debts
4. Use Debt Forgiveness to destroy Debt + gain life
5. Opponents take increasing damage while you manage your exposure

### Debt Punisher (Black/Red)
1. Create debt with various effects (Loan Shark, Predatory Lending)
2. Deploy Default Cascade (when Debt is sacrificed, controller creates a new one)
3. Interest Rate Hike: +2 counters on ALL Debts = massive damage spike
4. Collection Agent draws cards when opponent's Debts are sacrificed

### Debt Protection (Green/White)
1. Natural Economy prevents Debt life loss entirely + removes counters
2. Inflation Hedge creates Gold when opponents get Debt
3. Bankruptcy Filing destroys all your Debts before they trigger
4. Debt Forgiveness as spot removal + life gain

### Cross-Format Considerations
- **In Limited**: No escape routes, Debt is pure pressure
- **In Constructed**: Sacrifice outlets exist but cost resources
- **In Commander**: Multiplayer politics — who gets the Debt?
- **With Proliferate**: Double-edged — adds to your Debts too!

---

## Key Card Relationships

```
Debt Creators → Debt Redistributors → Debt Profiteers
     ↓                    ↓                    ↓
  Loan Shark       Debt Restructuring    Collection Agent
  Predatory Lending    The Bailout       Master of Debt
  Credit Default   Central Bank Governor  Debt Collector Myr
```

```
Debt Tokens ←→ Redistribute Mechanic
     ↓                    ↓
Debt Counters      Counter Movement
     ↓                    ↓
More counters = More damage when sacrificed
Redistribute spreads/concentrates counters
```

---

## Redistribute + Debt: Strategic Depth

**Scenario**: You have Debt A (1 counter). Opponent has Debt B (4 counters).

**Before Redistribute:**
- Your Debt: deals 1 damage
- Opponent's Debt: deals 4 damage

**After Redistribute (total 5 counters → each gets 2, rounded down):**
- Your Debt: deals 2 damage (worse for you!)
- Opponent's Debt: deals 2 damage (better for them!)
- **1 counter lost to rounding** (inefficiency of forced equality)

**Key Insight**: Redistribute is NOT always good for you! Evaluate:
- Is your debt smaller? Redistribute hurts you.
- Is opponent's debt bigger? Redistribute helps them.
- **Strategic play**: Compound opponent's Debt to 5+ counters, THEN redistribute = they still have big Debt, yours grows

---

## Integration with Existing Cards

| Existing Card | Debt Synergy |
|---------------|--------------|
| [[Spite Redistributor]] | Redistributes Debt tokens; drains 2 life per redistribute |
| [[The Grand Equalizer]] | Mass redistributes ALL counters including debt counters |
| [[Counter Vulture]] | Gets +1/+1 when ANY redistribution happens |
| [[Hype Cycle]] | Doubles debt counters → double damage! |
| [[Compute Debt]] | Thematic pairing; different mechanical approach |
| [[Market Crash]] | Removes all counters → Debt deals 0 damage |
| [[COMPOUND]] | Add debt counter → more damage |

### External Format Synergies

| External Card | Interaction |
|---------------|-------------|
| [[Atraxa, Praetors' Voice]] | Proliferate adds debt counters = more damage |
| [[Ashnod's Altar]] | Sac Debt for {2} to avoid damage |
| [[Disciple of the Vault]] | Triggers when Debt dies |
| [[Solemnity]] | Debt enters with 0 counters = 0 damage |
| [[Hex Parasite]] | Pay life+mana to remove debt counters |
| [[Vampire Hexmage]] | Remove all counters = 0 damage |

---

## Thematic Summary

**The Economic Commentary:**
- Debt as a weapon of control
- Redistribution spreads pain but doesn't solve problems (rounding = loss)
- Compound interest accelerates suffering
- Bailouts that create more debt
- The choice between debt slavery and bankruptcy
- Gold as the only true safe haven
- Leveraging debt for short-term gain (Affinity flavor!)

**The Gameplay Feel:**
- Debt creates immediate pressure (triggers next upkeep)
- Simple token, complexity on cards
- Redistribute requires careful evaluation (not always beneficial!)
- Multiple viable strategies:
  - **Aggro**: Spam Debt, Compound for damage
  - **Control**: Redistribute to manage exposure
  - **Punisher**: Default Cascade + Interest Rate Hike
  - **Protection**: Natural Economy, Debt Forgiveness

**Cross-Format Design:**
- In Limited: Pure pressure mechanic, no easy escapes
- In Constructed: Sacrifice outlets exist but cost resources
- In Commander: Political tool — who gets cursed with Debt?
- With other counter cards: Proliferate is double-edged

---

## Next Steps

1. **Token File**: Create `Debt Token.md` with full definition
2. **Card Files**: Create individual `.md` files for each card
3. **Mechanic Update**: Update `☭REDISTRIBUTE.md` with Debt synergies
4. **Lore Update**: Add "Credit Crisis" section to `Lore.md`
5. **Playtesting**: Test debt damage progression and balance
