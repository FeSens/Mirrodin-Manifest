---
name: color-breakdown
description: Analyze color distribution across the MTG set. Use when checking color balance or identifying gaps in color representation.
allowed-tools: Bash(python3 *)
---

Run the color breakdown script:

```bash
python3 color-breakdown.py
```

This will analyze all card files and provide a color breakdown report:

1. Read all `.md` files with `tags: [card]` in frontmatter
2. Extract the `color` field from each card's frontmatter
3. Generate a report showing:
   - **Overall Distribution**: Count of White, Blue, Black, Red, Green, Colorless, Multicolor cards
   - **Individual Color Appearances**: Count each color including appearances in multicolor cards
   - **By Rarity**: Break down color counts by Common, Uncommon, Rare, Mythic
   - **Multicolor Details**: List all multicolor cards with their color combinations

Use case: Ensure color balance across the set and identify gaps in color representation.
