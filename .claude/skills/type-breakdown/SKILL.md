---
name: type-breakdown
description: Detailed analysis of card types and creature subtypes. Use when tracking tribal synergies or ensuring type diversity.
allowed-tools: Bash(python3 *)
---

Run the type breakdown script:

```bash
python3 type-breakdown.py
```

This will analyze all card files and provide a type breakdown report:

1. Read all `.md` files with `tags: [card]` in frontmatter
2. Extract `type` and `subtype` fields from frontmatter
3. Generate a report showing:
   - **Card Types**: Count of Creature, Instant, Sorcery, Enchantment, Artifact, Land, Planeswalker
   - **Creature Subtypes**: List all creature types with counts (e.g., Human: 12, Myr: 8)
   - **Tribal Support**: Identify types with 4+ cards (potential tribal themes)
   - **Power/Toughness Distribution**: For creatures, show P/T combinations and averages
   - **By Rarity**: Type distribution at each rarity level

Highlights:
- Types with strong tribal presence (6+ cards)
- Missing common card types
- Unusual P/T stat lines
