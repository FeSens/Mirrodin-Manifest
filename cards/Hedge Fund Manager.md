---
tags:
  - card
  - broken-needs-review
type: Creature
subtype: Human Advisor
color: Blue
mana_cost: "{2}{U}{U}"
cmc: 4
rarity: Rare
power: 2
toughness: 3
set: Mirrodin Manifest
---

# Hedge Fund Manager

## Card Type Line
Creature — Human Advisor

## Rules Text
> When Hedge Fund Manager enters the battlefield, create three Gold tokens.
>
> Whenever you sacrifice a Gold token, Gamble. If you win the gamble, create two Gold tokens.
>
> At the beginning of your end step, sacrifice a Gold token.

## Flavor Text
> *"Risk is just opportunity in disguise."*

## Image Prompt
> Hedge Fund Manager, Human Advisor from Mirrodin Manifest. Setting: The Seat of the Synod — a private office overlooking the Lattice data streams. Mood: Corrupted triumph, false promise. Pose: Seated confidently, arms spread as gold tokens orbit and multiply around them, some winking out of existence. Key visual elements: Chrome-threaded suit, holographic charts spiraling upward then crashing down, eyes reflecting calculated risk. Style reference: Greg Staples meets Nils Hamm. Color palette: Steel blue, chrome, gold, bright data-light.

## Design Notes
- Creates Gold (capital)
- [[🎲 GAMBLE]] on sacrifice = leveraged bets
- Must sacrifice each turn = fees/losses
- Win = exponential growth, synergizes with [[COMPOUND]]
- Lose = capital destruction
- Lore connection: [[Lore#The Glimmervoid Rally (Gold Rally)]] - high finance gambling
- Pairs with: [[The House Edge]], [[Bubble Speculator]], [[The Rigged Game]]

## Outside of this set interactions
- **Notable Synergies:** [[Sensei's Divining Top]] (rig every gamble to win), [[Clock of Omens]] (tap Golds before sacrificing), [[Krark, the Thumbless]] (coin flip synergy commander)
- **BROKEN COMBOS:** Library manipulation ([[Sensei's Divining Top]], [[Brainstorm]]) + Hedge Fund Manager = Every gamble wins. Win = create 2 Gold. Sacrifice 1 Gold at end step, win gamble, make 2 more. Net +1 Gold per turn. With multiple sacrifice outlets, go infinite. Sacrifice Gold -> Gamble -> Win -> Create 2 Gold. If you can guarantee wins and sacrifice Golds at will, each Gold becomes 2, which becomes 4, which becomes 8... INFINITE MANA with guaranteed gamble wins and a sacrifice outlet.
- **Balance Assessment:** POTENTIALLY BROKEN - With library manipulation to guarantee gamble wins plus any sacrifice outlet, this generates unbounded Gold tokens over time. With an instant-speed sacrifice outlet and rigged gambles, this goes functionally infinite. The forced end-step sacrifice limits but doesn't stop abuse.
