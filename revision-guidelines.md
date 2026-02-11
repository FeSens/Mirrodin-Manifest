# Revision Guidelines - Mirrodin Manifest

Rules text problems found during set review. Use this as a checklist when evaluating cards.

## Redundant Restrictions

1. **"Activate only once each turn" on tap abilities** - A {T} ability already can only be used once per turn because the creature is tapped. Adding "once each turn" is redundant text. Exception: abilities that DON'T require tapping (e.g., "{2}: Do something. Activate only once each turn.") legitimately need this restriction.

2. **"As a sorcery" on tap abilities for creatures** - Creatures with summoning sickness can't use tap abilities until your next turn anyway. "Activate only as a sorcery" on a tap ability is almost always redundant. Exception: artifacts with tap abilities CAN be used the turn they enter, so "as a sorcery" may matter there.

3. **"Once each turn" on triggers that naturally can't trigger more than once** - E.g., "At the beginning of your upkeep" already only triggers once per turn. Adding "this ability triggers only once each turn" is redundant.

## Nonsensical Rules Text

4. **Effects that can't resolve** - E.g., "Return this token from the graveyard to the battlefield" - tokens cease to exist in the graveyard and can't be returned. Use "create a new token" instead.

5. **Counters that do nothing on the card** - If a card creates tokens "with a spark counter" but no ability on the card references spark counters, the counter is dead text. Either remove the counter or add an ability that uses it.

6. **Redundant custom counter types** - If a custom counter (e.g., "determination counter") just gives +1/+1 via a separate line ("gets +1/+1 for each determination counter"), replace with standard +1/+1 counters. Saves text, better synergy.

7. **Conditions that compare all permanents on the board** - E.g., "if a permanent has three or more counters than another permanent" requires scanning every pair of permanents. Replace with fixed thresholds or targeted triggers.

8. **Tracking requirements across the entire turn** - E.g., "if no counters were put on permanents this turn" requires memorizing all counter placements for the whole turn. Unworkable in paper Magic.

## Redundant Drawbacks

9. **Stacking drawbacks that cancel out** - If mana "can only be spent on artifacts" AND you "lose life unless you cast an artifact," the life loss almost never triggers. Pick ONE drawback.

10. **Negligible penalties** - "If you lose the gamble, lose 1 life" on a card where the gamble's natural variance is already the punishment. Don't add text for meaningless penalties.

11. **"Can't attack or block" on 1/1 tokens** - A 1/1 is already weak. Adding restrictions just adds text without meaningful gameplay impact.

## Complexity Budget

12. **Too many abilities for rarity** - Commons: 1-2 abilities. Uncommons: 2-3. Rares: 2-4. Mythics: 3-4 max. Cut the weakest or most disconnected ability.

13. **Flavor text in rules text** - Italic flavor quotes should ONLY appear in the dedicated Flavor Text section, never inside the Rules Text blockquote.

14. **Wiki-links in rules text** - `[[Card Name]]` is for Obsidian navigation only, never in rules text.

## Templating Errors

15. **Replacement effects on keyword actions** - "If you would gamble" is wrong. Gamble is a keyword action, not an event. Use triggered abilities: "Whenever you gamble" instead.

16. **"Its owner" instead of "you"** - In rules text, use second person ("you") since the controller is reading the card. "Its owner may pay 2 life" should be "you may pay 2 life."

17. **Wrong targeting** - "Target non-Myr creature" on a mana ability makes it NOT a mana ability (mana abilities can't target). Use "choose" instead of "target" for mana-producing abilities.
