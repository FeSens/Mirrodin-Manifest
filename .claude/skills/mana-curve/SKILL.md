---
name: mana-curve
description: Analyze mana value (CMC) distribution across the MTG set. Use when checking if the mana curve is healthy for Limited play.
allowed-tools: Bash(python3 *)
---

Run the mana curve script:

```bash
python3 mana-curve.py
```

This will analyze all card files and provide a mana curve report:

1. Read all `.md` files with `tags: [card]` in frontmatter
2. Extract the `cmc` (converted mana cost) field from each card
3. Generate a report showing:
   - **Average CMC**: Overall average for the set
   - **CMC Distribution**: Count of cards at each mana value (0-7+) with visual ASCII bars
   - **Creature Curve**: Separate mana curve for creatures only
   - **By Rarity**: CMC distribution broken down by rarity
   - **By Card Type**: Average CMC for creatures vs instants/sorceries vs other

Target ranges from set-guidelines.md:
- Average CMC should be 2.5-3.5 for a healthy Limited format
- Peak should be at 2-3 CMC
- At least 20% of creatures should be 1-2 CMC (early drops)
