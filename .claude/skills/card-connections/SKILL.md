---
name: card-connections
description: Analyze wikilink connections between cards. Use when identifying hub cards or checking card relationships.
allowed-tools: Bash(python3 *), Read, Grep, Glob
---

Analyze all card files and report on their connections (wikilinks):

1. Read all `.md` files with `tags: [card]` in frontmatter
2. For each card, extract:
   - **Outgoing links**: `[[wikilinks]]` found in the file content
   - **Incoming links**: Other files that link TO this card
3. Calculate total connections = incoming + outgoing

Generate a report showing:

**Top Connected Cards**
List the top 20 most connected cards with their counts:
```
1. Card Name - 15 connections (8 in, 7 out)
2. Another Card - 12 connections (6 in, 6 out)
...
```

**Full Connection List**
List ALL cards ordered by total connections (descending):
- Show card name, total connections, incoming, outgoing
- Group by connection tiers (10+, 5-9, 2-4, 1, 0)

**Connection Statistics**
- Average connections per card
- Median connections
- Cards with 0 connections (orphans)
- Most linked-to card (highest incoming)
- Most linking card (highest outgoing)

**Potential Hub Cards**
Identify cards with 5+ connections as potential "hub" cards that tie the set together thematically.
