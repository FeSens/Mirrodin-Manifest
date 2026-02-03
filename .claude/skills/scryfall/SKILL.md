---
name: scryfall
description: Search Scryfall for official Magic: The Gathering cards to compare with custom set designs. Use when looking up existing MTG cards, finding similar cards, or checking balance against official designs.
allowed-tools: WebFetch
---

Search Scryfall's API for Magic cards based on the user's query.

## Search Types

**1. Card Name Search (fuzzy)**
```
https://api.scryfall.com/cards/named?fuzzy=<card_name>
```
Use when user asks for a specific card by name.

**2. Full Search Query**
```
https://api.scryfall.com/cards/search?q=<query>
```
Use Scryfall syntax for complex searches. Common filters:
- `t:creature` - card type
- `o:"rules text"` - oracle text contains
- `c:r` - color (w/u/b/r/g)
- `cmc=3` - mana value
- `pow=2` - power
- `tou=3` - toughness
- `r:rare` - rarity (common/uncommon/rare/mythic)
- `set:mh2` - specific set
- `f:standard` - format legal
- `is:permanent` - permanent cards
- `keyword:flying` - has keyword

**3. Random Card**
```
https://api.scryfall.com/cards/random?q=<optional_query>
```

## Response Format

For each card found, display:
- **Name** and mana cost
- **Type line**
- **Rules text**
- **Power/Toughness** (if creature)
- **Rarity** and set
- **Scryfall link**

## Example Queries

User: "Find cards similar to my Gamble mechanic"
Search: `o:"reveal the top card" o:"mana value"` or `o:clash`

User: "Show me Gold token generators"
Search: `o:"create" o:"gold token"` or `o:"treasure token"`

User: "What 3-mana red burn spells exist?"
Search: `c:r cmc=3 t:instant o:damage`

User: "Find cards that double counters"
Search: `o:"double" o:"counters"`

## Comparing to Custom Cards

When the user wants to compare a custom card:
1. Read the custom card file first
2. Identify key mechanics/effects
3. Search Scryfall for similar official cards
4. Present comparisons for balance reference

## Rate Limiting

Scryfall asks for 50-100ms between requests. If searching multiple queries, space them out.
