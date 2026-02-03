---
name: set-health
description: Compare the MTG set against design guidelines. Use for comprehensive health checks to ensure the set follows best practices.
allowed-tools: Bash(python3 *)
---

Run the set health script:

```bash
python3 set-health.py
```

This will run a comprehensive health check against set-guidelines.md targets:

**Set Size Progress**
- Target: 261 cards (101C, 80U, 60R, 20M) for standard or 145 cards (60C, 40U, 35R, 10M) for small
- Show current count vs target for each rarity

**Color Balance**
- Target: ~18 commons per color, ~13 uncommons per color
- Flag colors that are under/over represented

**Creature/Spell Ratio**
- Target: 60-65% creatures at common
- Show current ratio

**Mana Curve Health**
- Target: Peak at 2-3 CMC, avg 2.5-3.5
- Flag if curve is too high or low

**Signpost Uncommons**
- Target: 10 two-color uncommons (one per guild)
- List which guilds have signposts and which are missing

**Removal Coverage**
- Target: 2-3 removal spells at common per color
- Flag colors lacking removal

**NWO Compliance**
- Target: Commons should average <25 words
- List commons that exceed complexity thresholds

**Missing Data**
- List cards missing required fields (type, color, rarity, cmc)

Provides an overall health score (0-100) and actionable summary.
