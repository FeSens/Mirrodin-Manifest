#mechanic
# Design goals

- Create **risk-based asymmetry**
    
- Reward long-term “investment” (high mana value)
    
- Punish greed _sometimes_
    
- Generate tension and table politics
    
- Be deterministic enough to be playable, not coin-flip chaos
    

---

## ✅ **Core Definition (Clean & Rules-Safe)**

### **Gamble — keyword action**

> **Gamble — Choose target opponent. You and that player reveal the top card of your libraries. The player who revealed the card with the greater mana value wins the gamble. If the mana values are equal, the active player wins the gamble.**

This wording:

- Uses only existing MTG concepts
    
- Avoids hidden information ambiguity
    
- Cleanly defines ties
    
- Works in multiplayer
    

---

## 📜 Reminder Text (for commons)

> _(To gamble, you and target opponent reveal the top card of your libraries. Whoever reveals the card with greater mana value wins.)_

---

## 🎭 Flavor Home Run

- High-cost decks = long-term investors
    
- Low-cost decks = liquidity, volatility
    
- Ties favor the active player → **timing matters**
    
- Knowledge (scry) = market manipulation
    

This _is_ the invisible hand.

---

## 🔧 How Gamble Appears on Cards

### Positive / Negative outcomes

Cards **must explicitly define win/loss effects**:

> _If you win the gamble,_ …  
> _If you lose the gamble,_ …

This keeps Gamble modular and extensible.

---

## 🔥 Example Cards

### **Gamble with the Devil**

> Gamble.  
> If you lose the gamble, this deals 6 damage to you.

### **Insider Trading**

> Gamble.  
> If you win the gamble, draw two cards.  
> If you lose the gamble, discard a card.

---

## ⚠️ Balance Notes

- Gamble should appear **mostly at common/uncommon**
    
- Loss conditions must matter, or the mechanic becomes free value
    
- Scry before Gamble is extremely strong (intentional, but controlled)