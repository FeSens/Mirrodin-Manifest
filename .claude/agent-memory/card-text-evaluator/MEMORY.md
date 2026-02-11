# Card Text Evaluator Memory

## Key Set Mechanics Reference
- **COMPOUND**: Choose a permanent, add a counter of a type already on it (single target, mandatory)
- **REDISTRIBUTE**: Choose two permanents, remove all counters, each gets half (rounded down)
- **GAMBLE**: Compare top card mana values with opponent, higher wins

## Token Definitions
- **Debt Token**: Artifact - Debt. Enters with TWO debt counters. Upkeep: lose 1 life, remove a debt counter. When last counter removed, sacrifice. (Updated 2026-02-09)
- **Gold Token**: Artifact - Gold. Enters with value counter. Sacrifice: add {C} for each value counter

## Common Templating Issues Found

### 0. Flavor Text Placement
- WRONG: Flavor text embedded in Rules Text section (found in Foundry Air Command, Optimization Lie)
- RIGHT: Flavor text ONLY in dedicated ## Flavor Text section

### 1. Wiki-Links in Rules Text
- WRONG: `[[Debt Token|Debt tokens]]` in rules text
- RIGHT: Plain text "Debt tokens" - wiki-links are for design notes only

### 2. Emoji in Rules Text
- NEVER use emoji in rules text (e.g., dice emoji for gamble)
- Keep rules text clean and MTG-standard

### 3. Keyword Action Triggers
- WRONG: "Whenever a player redistributes"
- RIGHT: "Whenever a permanent is redistributed" (keyword actions trigger on the effect, not the player)

### 2. Variable References in Effects
- WRONG: "look at that many cards... where X is the number"
- RIGHT: "look at the top X cards... where X is the number of [counters] on [cardname]"
- Always use "X" consistently and define it properly

### 3. Sequencing in Upkeep Triggers
- WRONG: "draw cards equal to counters, then deal damage, then remove counters"
- RIGHT: "remove all counters, draw cards equal to removed, deal that much damage"
- Remove counters FIRST to establish the number, then reference it

### 4. Token Reminder Text
- When a card creates a token with custom rules, include reminder text defining the token
- Format: *(A [Token] is an artifact with "[rules]" and "[rules].")*

### 5. Type Field Mismatches
- WRONG: `type: Creature` in frontmatter but "Artifact Creature" in type line
- RIGHT: Keep frontmatter type and card type line synchronized

### 6. Color Array Format
- WRONG: `color: Blue/Black` (slash notation)
- RIGHT: Use YAML array format:
  ```yaml
  color:
    - Blue
    - Black
  ```

### 7. Capitalization of Types
- "Treasure" is capitalized (it's a card type/subtype)
- "at the end of combat" not "at end of combat"

## Mechanic-Specific Reminder Text Templates

### GAMBLE (full reminder)
*(To gamble, you and that player each reveal the top card of your libraries. Whoever reveals the card with greater mana value wins. If equal, the active player wins.)*

### COMPOUND (full reminder)
*(To compound, put a counter on it of a type already on it.)*

### REDISTRIBUTE (full reminder)
*(To redistribute, remove all counters from both, then put half that many counters, rounded down, on each of them of the types removed this way.)*

### Debt Token (full reminder - UPDATED 2026-02-09)
*(A Debt token is an artifact that enters with two debt counters and "At the beginning of your upkeep, you lose 1 life, then remove a debt counter from this. When the last debt counter is removed, sacrifice it.")*

### Debt Token (short form)
*(It's an artifact that enters with two debt counters and "At the beginning of your upkeep, you lose 1 life, then remove a debt counter from this. When the last debt counter is removed, sacrifice it.")*

## Specific Fix Patterns

### "Cast without paying mana cost"
- Always add restrictions at uncommon or below
- Pattern: "nonland card with mana value 4 or less"
- Prevents Omniscience/Enter the Infinite type blowouts

### Death triggers referencing counters
- WRONG: "counters that were on it"
- RIGHT: "counters on it as it last existed on the battlefield"

### Once per turn limiters
- Add to card draw triggers that could go infinite with cost reducers
- Pattern: "Once each turn, whenever you cast..."

### Nonland permanents
- Use to prevent Dark Depths combo (3 mana 20/20)
- Use for mass counter removal effects

## Power Level Guidelines

### By Rarity
- **Common**: Simple, NWO-compliant, limited synergy enablers (1/3 stats with tap ability is fine)
- **Uncommon**: Moderate complexity, build-around potential (2/2 flying with conditional growth is fine)
- **Rare**: Complex interactions, strong effects with drawbacks (draw X, take X damage is risky)

### Red Flags for "Broken"
- Cards that draw multiple cards with minimal setup cost
- Infinite combo enablers without sufficient mana/tap costs
- Sorcery-speed restrictions missing on repeatable untap effects

## Complexity Reduction Patterns (Simplification Pass)

### Common Anti-Patterns Found
1. **Three+ abilities on non-mythics** - Cut the weakest/most niche ability
2. **Conditional within conditional** - e.g. "if it has 3+ counters, draw" on an already-complex card. Remove the inner condition.
3. **Useless restrictions on tokens** - "can't block" on a 1/1 you're meant to sacrifice adds text without gameplay
4. **Tribal bonuses split by type** - "For each Zombie... for each Elf..." on a single spell. Pick one bonus or make it generic.
5. **Opponent-only abilities on your cards** - e.g. Aura on opponent's creature creating Debt for YOU. Fix the controller.
6. **Counter-based ETB on commons** - Use static +1/+1 instead of "put a +1/+1 counter" when counter synergy isn't needed
7. **"Only X may activate" clauses** - Often removable; use simpler "until leaves the battlefield" templating
8. **Supply/tracking counters on self** - If a creature just grows from its own triggers, cut the counter tracking

### Aura Simplification at Common
- WRONG: ETB counter + vigilance + type change + exile protection (4 effects)
- RIGHT: Static +1/+1 + vigilance + type change (3 effects, no counter tracking)

### Simplification Patterns (Batch C-D)
1. **Token-multiplying replacement effects** - "that many plus one" on top of counter additions = exponential. Pick ONE axis.
2. **Variable-X activated abilities** - "{T}, Remove X: do X things with MV X" is triple-variable. Use fixed costs at uncommon.
3. **Wordy triggered destroy** - "deals combat damage to creature, destroy it" = just use deathtouch keyword.
4. **Redundant duration clauses** - "+2/+0 until end of turn and first strike until end of turn" = single "until end of turn".
5. **Hexproof on slow tokens** - If token takes 3+ turns, skip hexproof; let it be interactive.
6. **Conditional indestructible via counter tracking** - Hidden memory complexity; cut or simplify.

### Simplification Patterns (Batch E: P-S cards)
1. **Two separate tap abilities on a common** - Merge into one modal/conditional ability or cut one.
2. **"Can't be blocked by X or Y" clauses** - Pick ONE evasion clause to avoid text bloat.
3. **Mana value restrictions on combat damage triggers** - "destroy artifact MV 4+" is an unnecessary gate. Just "destroy target artifact."
4. **Legendary-only restrictions on artifacts** - Unless flavor demands it, "target creature" is cleaner than "target legendary creature."
5. **Dual activated abilities on artifacts** - Two costs for two modes = decision paralysis. One clean ability is better.
6. **"When you do" reflexive triggers on upkeep** - Use "and" for simple sequential effects (remove counter and lose life).
7. **4 abilities on mythics** - Even mythics benefit from cutting to 3. One keyword + two text abilities is the sweet spot.
8. **Mana production with conditional life loss** - Overly complex; just reduce the mana amount to balance instead.

### Simplification Patterns (Batch F: Tangle/The cards)
1. **Dual-mode sorceries tracking turn state** - "count counters removed this turn, sacrifice that many; if none, do alternate mode" = two cards crammed into one. Pick the simpler mode.
2. **3-ability mythic artifacts where one ability is a mini-game** - Named Thoughtseize + evidence accumulation + ultimate = three cards. Cut the middle ability and let the first do the accumulation.
3. **4-chapter sagas with chapter IV undoing chapter II** - Chapter IV returning exiled cards creates feel-bad. Cut to 3 chapters, fold the return into chapter III as cost/consequence.
4. **Replacement draw effects** - "Whenever a player would draw... instead look at top 2, put 1 in hand, put 1 on bottom" = functionally a new card type of draw. Overly parasitic. Simplify to a scry rider on draws.
5. **Activated abilities that prevent damage AND remove counters** - Two effects per activation at common. Just let the counter removal be the ability; the damage prevention is gravy text.
6. **Leaves-battlefield triggers dumping to graveyard** - "exiled cards go to graveyard" is punitive and confusing. "Return to hand" is simpler and more interactive.
7. **Free cast stapled onto draw-and-drain** - Draw + life loss + free cast = three distinct effects on one sorcery. Two is enough.

### Simplification Patterns (Batch G: M-P cards)
1. **Upkeep counter accumulation -> static effect** - "At upkeep, put -1/-1 counter on each non-X" can become "Non-X creatures you control get -1/-1" for same flavor without counter tracking.
2. **Non-standard creature type restrictions** - "Can't block Unforged creatures" where Unforged isn't a creature type. Remove the restriction entirely.
3. **Card draw on top of complex ETBs at rare** - Rare with keyword + complex ETB + activated card draw = too much. Cut the card draw.
4. **Conditional ETB as triggered -> replacement effect** - "When ETB, if not token, put counter" can be "ETB with counter if not token" -- saves a trigger stack.
5. **Wordy mass counter manipulation** - "Choose any number, remove all counters, put half back rounded down, then bonus" = one long sentence. Combine the half + bonus into one math expression.

### Simplification Patterns (Batch H: T-Z cards)
1. **Counters that do nothing mechanically** - Construction counters on Tromp accumulated but no ability referenced them. Remove tracking counters that have no payoff.
2. **Separate state trigger for counter depletion** - "When no counters, sacrifice and draw 3" as separate trigger = extra text. Fold into the activation: "If no counters remain, sacrifice and draw."
3. **4 abilities on uncommon creatures** - Defender + ETB tokens + hexproof lord + activated pump = too much. Cut hexproof (the least interactive ability).
4. **Upkeep sacrifice for no-counters state** - "At upkeep, if no guilt counters, sacrifice" as separate trigger. Use "When last counter is removed, sacrifice" - cleaner and more intuitive.
5. **Dual mana abilities on lands** - {T}: Add {C} AND {T}: Add any color for artifacts = redundant. The restricted ability subsumes the unrestricted one in most cases. Cut {C} ability.
6. **Conditional within death trigger** - "if it had a spark counter" + "you may pay {1}" = two conditions on one trigger. Remove the counter check to reduce tracking.
7. **Niche can't-block restrictions** - "Can't block Mer-Ikan creatures" at common adds text for rarely relevant flavor. Cut it.
8. **Spells that rewrite REDISTRIBUTE** - If the set has a redistribute keyword, USE it. Don't spell out "remove all counters... put half back..." longhand.

## Mechanical Inconsistency Patterns
1. **Counters on tokens with no payoff on the creating card** - Academy Headmaster created tokens "with a spark counter" but nothing on the card referenced spark counters. Fix: remove the counter unless adding a payoff ability.
2. **Redundant custom counter types** - Civilian Militia used "determination counters" + "gets +1/+1 for each determination counter" which is functionally identical to just using +1/+1 counters. Fix: replace with +1/+1 counters to cut a line of text and improve set synergy.
3. **Cross-card-only counter relevance** - Barge Pilot puts cargo counters on Vehicles, which only matter if Glimmer-Barge (or similar) is in play. This is ACCEPTABLE for set design (like energy counters) but borderline at common.
4. **"Return it" on token death triggers** - Tokens cease to exist after going to graveyard (SBA). Delayed triggers saying "return it at next end step" find nothing to return. Fix: change to "create a token" instead of "return it." (Found on Put-In, the Iron Despot.)
5. **Accumulating counters with zero payoff on the card** - The Darksteel Wall accumulated construction counters every upkeep but no ability referenced them. Fix: removed all counter text. If counters only matter cross-card (Compound/Hype Cycle), they still need at least ONE on-card reference.
6. **Spark counters on created tokens with no on-card reference** - The Ledger Surfaces created Unforged tokens "with spark counters" but no chapter referenced spark counters. Fix: removed spark counters from token creation.

## Flavor Text Standards
- Should connect to set lore (Ep-Styn, En-Vidia Lattice, Mer-Ikan Foundry, etc.)
- Character quotes should match established voice
- Avoid generic fantasy flavor when set-specific options exist
