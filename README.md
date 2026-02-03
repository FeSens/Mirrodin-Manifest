# Mirrodin Manifest

*This is the only line added by a human: The political views of this set may not align with my own. I just think it's a fun idea. I didn't read every card or the lore before publishing this.*

**This entire Magic: The Gathering set was designed by Claude Opus 4.5, based on recent political events.**

A custom 291-card MTG set that transforms contemporary world events into the metallic dystopia of Mirrodin. The AI boom, economic inequality, political upheaval, and institutional failures are recast as faction conflicts on a plane where automation has replaced agency and gold has become the only refuge.

## The Premise

Mirrodin hasn't just survived the Phyrexians—it has evolved into a hyper-calculated corporate dystopia. The **Thought-Sync**, a network of sentient Myr, has begun to automate the very souls of its inhabitants. Political figures wage proxy wars. Workers are displaced by machines that can't do their jobs. And somewhere in the Quicksilver Sea, a private isle holds secrets that could topple empires.

## Core Mechanics

The set features three interlocking mechanics that create a **mechanical triangle** of ideological tension:

### 🎲 GAMBLE
> *Choose target opponent. You and that player reveal the top card of your libraries. Whoever reveals the card with greater mana value wins the gamble.*

Risk-based asymmetry. High-cost decks are "long-term investors." Scry effects become "market manipulation." The invisible hand, made visible.

### 📈 COMPOUND
> *Choose a permanent. Put a counter on it of a type already on it.*

Pure exponential growth. Value accumulates where value already exists. No redistribution. No fairness. The enemy of equality, mechanically and philosophically.

### ☭ REDISTRIBUTE
> *Choose two permanents. Remove all counters from them, then each gets half that many counters, rounded down.*

Forced equality that destroys value. Everyone loses something. Growth is flattened. Incentives disappear. Looks fair on paper—feels terrible in practice.

## The Factions

| Faction | Real-World Parallel | Themes |
|---------|---------------------|--------|
| **The Mer-Ikan Foundry** | United States | Borders, exile, "Core Purity" |
| **The En-Vidia Lattice** | NVIDIA / Big Tech | Processing Cores, computed futures |
| **The Deep-Sik Collective** | DeepSeek / Chinese AI | Efficiency over extravagance |
| **The Vault of Whispers** | Russia | "Special Acquisitions," Nim armies |
| **The Thought-Sync** | OpenAI / AGI movement | Promises of sentience, eternal optimism |
| **The Private Isle** | Epstein's network | Hidden ledgers, trafficking, elite complicity |

## Notable Characters

- **Tromp, the Gilded Sentinel** — A Loxodon artificer building a Darksteel Wall to keep out the "unrefined"
- **Sal-Tman, Prophet of the Core-Logic** — Promises true Myr sentience "within the year" (every year)
- **Put-In, the Iron Despot** — Wages "Special Acquisitions" with endless Nim conscripts
- **Zel-Ensk, the Resilient Spark** — *"I don't need a Blinkmoth transport; I need more Equipment."*
- **Liang-Wen, the Efficient Mind** — Built an empire from scraps the Foundry said were worthless
- **Ep-Styn, Keeper of the Private Isle** — *"The Golem did not dismantle himself."*

## Set Statistics

| Metric | Value |
|--------|-------|
| Total Cards | 291 |
| Creatures | 173 |
| Average CMC | 2.98 |
| Health Score | 94/100 |

### Rarity Distribution
- Commons: 101
- Uncommons: 80
- Rares: 60
- Mythic Rares: 20
- Lands: 30

## Design Philosophy

This set follows official Wizards of the Coast design guidelines:

- **New World Order (NWO)** — Commons average 15 words of rules text
- **Color Balance** — Equal representation across all five colors
- **10 Draft Archetypes** — Each color pair has a signpost uncommon
- **Removal Coverage** — All five colors have adequate removal
- **60% Creature Ratio** — Healthy Limited environment at common

## Repository Structure

```
/
├── *.md                    # Individual card files (Obsidian-compatible)
├── dashboard.html          # Interactive set statistics dashboard
├── spoilers.html           # Visual card spoiler gallery
├── generate-dashboard.py   # Dashboard generation script
├── generate-spoilers.py    # Spoiler page generation script
├── set-guidelines.md       # MTG design best practices reference
├── Lore.md                 # Full set lore and world-building
├── 🎲 GAMBLE.md            # Gamble mechanic documentation
├── COMPOUND.md             # Compound mechanic documentation
└── ☭REDISTRIBUTE.md       # Redistribute mechanic documentation
```

## Card File Format

Each card is a markdown file with YAML frontmatter:

```yaml
---
tags:
  - card
type: Creature
subtype: Human Artificer
color: Blue
mana_cost: "{2}{U}"
cmc: 3
rarity: Uncommon
power: 2
toughness: 2
set: Mirrodin Manifest
---
```

## Viewing the Set

### Interactive Dashboard
```bash
python3 generate-dashboard.py
open dashboard.html
```

### Card Spoilers
```bash
python3 generate-spoilers.py
open spoilers.html
```

## Obsidian Integration

This repository is designed as an [Obsidian](https://obsidian.md/) vault. Cards link to each other via `[[wikilinks]]`, creating a navigable web of mechanical and thematic connections.

## Sample Cards

### Displaced Worker
> *2W — Creature — Human*
>
> When Displaced Worker enters the battlefield, create a 0/1 colorless Myr artifact creature token.
>
> Sacrifice an artifact: Displaced Worker gets +2/+0 until end of turn.
>
> *"They said the Myr would free us. They meant free us from employment."*

### The Black Ledger
> *Legendary Artifact*
>
> When The Black Ledger enters the battlefield, each opponent reveals their hand.
>
> {T}: Look at the top card of target opponent's library.
>
> *Names. Dates. Transactions. The truth was never lost—only hidden.*

### Optimization Lie
> *Sorcery*
>
> Exile target creature. Its controller creates a 0/1 colorless Myr artifact creature token.
>
> *"Your position has been automated." The Myr that replaced her couldn't do her job. But it was cheaper to maintain.*

## License

This is a fan-created custom Magic: The Gathering set for educational and entertainment purposes. Magic: The Gathering is a trademark of Wizards of the Coast. This project is not affiliated with, endorsed, or sponsored by Wizards of the Coast.

---

*"I was promised the future. I got a very expensive autocomplete."*
— Flavor text, Trough of Disillusionment
