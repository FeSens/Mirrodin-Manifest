# React MTG Card Generator - Technical Specification

A comprehensive guide for generating pixel-perfect Magic: The Gathering cards using React.

---

## Card Specifications

### Physical Dimensions
- **Standard Size**: 2.5" × 3.5" (63.5mm × 88.9mm)
- **Corner Radius**: 3.5mm (approximately 1/8")

### Digital Resolution for Print
| DPI | Width (px) | Height (px) | Use Case |
|-----|------------|-------------|----------|
| 72  | 180 | 252 | Web preview only |
| 300 | 750 | 1050 | Standard print quality |
| 600 | 1500 | 2100 | High-quality print |

### Print Bleed & Safe Zones
- **Bleed Area**: Extend artwork 0.125" (3mm) past trim line
- **Safe Zone**: Keep text 0.125" (3mm) inside trim line
- **Minimum upload size**: 822 × 1122 pixels (for print services)

---

## Card Frame Anatomy

### Layer Structure (bottom to top)
1. **Background/Art** - Card artwork (fills art box area)
2. **Card Frame** - The colored border/frame overlay
3. **Text Boxes** - Title bar, type line, rules text box
4. **Symbols** - Mana cost, set symbol, P/T box
5. **Text Content** - All text overlays

### Key Regions
```
┌─────────────────────────────────┐
│  ┌───────────────────────────┐  │
│  │ Name                  {M} │  │ ← Title Bar
│  ├───────────────────────────┤  │
│  │                           │  │
│  │                           │  │
│  │       CARD ARTWORK        │  │ ← Art Box
│  │                           │  │
│  │                           │  │
│  ├───────────────────────────┤  │
│  │ Type Line            [S]  │  │ ← Type Bar
│  ├───────────────────────────┤  │
│  │                           │  │
│  │      Rules Text           │  │ ← Text Box
│  │      Flavor text          │  │
│  │                           │  │
│  ├───────────────────────────┤  │
│  │ Artist Info      [P/T]    │  │ ← Info Bar
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## Required Dependencies

### NPM Packages
```bash
npm install mana-font keyrune @saeris/typeface-beleren-bold
```

### Font Resources
| Resource | Purpose | NPM Package |
|----------|---------|-------------|
| **Beleren Bold** | Card titles, type lines | `@saeris/typeface-beleren-bold` |
| **mana-font** | Mana symbols ({W}, {U}, {B}, {R}, {G}, etc.) | `mana-font` |
| **keyrune** | Set/expansion symbols | `keyrune` |
| **MPlantin** | Rules text (body font) | Custom or fallback to serif |

### CDN Alternative
```html
<!-- Mana symbols -->
<link href="//cdn.jsdelivr.net/npm/mana-font@latest/css/mana.css" rel="stylesheet" />

<!-- Set symbols -->
<link href="//cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.css" rel="stylesheet" />
```

---

## Color Palette by Card Type

### Frame Colors (Modern Frame - 8th Edition+)
| Color | Primary | Accent | Text Box BG |
|-------|---------|--------|-------------|
| White | #F8F6D8 | #F0E68C | #FFFEF5 |
| Blue | #0E68AB | #1E90FF | #C6DEF1 |
| Black | #2D2D2D | #4A4A4A | #C9C5C0 |
| Red | #D32029 | #FF4444 | #F9C6B6 |
| Green | #00733E | #228B22 | #C4D9B0 |
| Gold (Multi) | #C9A227 | #FFD700 | #F5E6C8 |
| Artifact | #8E9AA0 | #B8C4C8 | #D4D8DA |
| Colorless | #C4B8A8 | #D4C8B8 | #E8E0D8 |
| Land | #8B7355 | #A08060 | #D4C8B8 |

---

## React Component Architecture

### Component Structure
```
<MtgCard>
  ├── <CardFrame>           // Border and background
  │   ├── <TitleBar>        // Name + mana cost
  │   ├── <ArtBox>          // Card artwork image
  │   ├── <TypeBar>         // Type line + set symbol
  │   ├── <TextBox>         // Rules + flavor text
  │   └── <InfoBar>         // Artist, collector number, P/T
  └── <PowerToughness>      // P/T box (creatures only)
</MtgCard>
```

### Props Interface
```typescript
interface MtgCardProps {
  // Identity
  name: string;
  manaCost: string;        // e.g., "{2}{W}{U}"

  // Type
  supertype?: string;      // "Legendary", "Basic", etc.
  type: string;            // "Creature", "Instant", etc.
  subtype?: string;        // "Human Wizard", "Aura", etc.

  // Content
  artUrl: string;
  rulesText: string;       // Supports {mana} syntax
  flavorText?: string;

  // Stats (creatures)
  power?: string;
  toughness?: string;

  // Metadata
  rarity: 'common' | 'uncommon' | 'rare' | 'mythic';
  setCode: string;         // For keyrune symbol
  collectorNumber?: string;
  artist?: string;

  // Appearance
  cardColors: string[];    // ['W'], ['U', 'B'], etc.
}
```

---

## CSS Techniques

### Card Container
```css
.mtg-card {
  position: relative;
  width: 375px;           /* 2.5" at 150 DPI (web scale) */
  height: 525px;          /* 3.5" at 150 DPI */
  border-radius: 18px;    /* Scaled corner radius */
  overflow: hidden;
  font-family: 'MPlantin', 'Palatino Linotype', serif;
}
```

### Layer Positioning
```css
.card-frame {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 4%;
}

.art-box {
  position: relative;
  z-index: 0;
  width: 92%;
  height: 44%;
  margin: 0 auto;
  overflow: hidden;
  border: 3px solid #171314;
}

.text-box {
  position: relative;
  z-index: 2;
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid #171314;
  padding: 8px;
  overflow: hidden;
}
```

### Mana Symbol Rendering
```jsx
// Parse mana cost string and render icons
const renderManaCost = (cost: string) => {
  const symbols = cost.match(/\{[^}]+\}/g) || [];
  return symbols.map((symbol, i) => {
    const code = symbol.slice(1, -1).toLowerCase();
    return <i key={i} className={`ms ms-${code} ms-cost`} />;
  });
};
```

### Text Scaling for Rules Text
```css
.rules-text {
  font-size: 14px;
  line-height: 1.3;
}

/* Scale down for long text */
.rules-text.long {
  font-size: 12px;
}

.rules-text.very-long {
  font-size: 10px;
}
```

---

## Export for Print

### html-to-image / dom-to-image
```typescript
import { toPng } from 'html-to-image';

const exportCard = async (cardElement: HTMLElement) => {
  const dataUrl = await toPng(cardElement, {
    width: 750,           // 300 DPI
    height: 1050,
    pixelRatio: 2,        // For retina quality
    quality: 1.0,
  });

  // Download or upload
  const link = document.createElement('a');
  link.download = 'card.png';
  link.href = dataUrl;
  link.click();
};
```

### Puppeteer Server-Side Rendering
```typescript
// For batch export at high resolution
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setViewport({ width: 750, height: 1050, deviceScaleFactor: 2 });
await page.goto(`http://localhost:3000/card/${cardId}`);
await page.screenshot({ path: 'card.png', type: 'png' });
```

---

## Sources & References

### Libraries
- [mana-font](https://github.com/andrewgioia/mana) - Mana symbol icon font
- [keyrune](https://github.com/andrewgioia/keyrune) - Set symbol icon font
- [typeface-beleren-bold](https://github.com/Saeris/typeface-beleren-bold) - Beleren font package
- [reactjs-mtg-card](https://github.com/germanyn/reactjs-mtg-card) - React MTG card component

### Tutorials
- [Make a Magic: The Gathering card in CSS](https://codeburst.io/make-a-magic-the-gathering-card-in-css-5e4e06a5e604) - Davide Iaiunese
- [MTG Card Size Guide](https://www.qpmarketnetwork.com/trading-card-game/mtg-card-size-guide-dimensions-matter/) - Print specifications

### Tools
- [MTGCardBuilder](https://mtgcardbuilder.com/) - Online card creator
- [Card Conjurer](https://github.com/Investigamer/cardconjurer) - Custom card creator
- [Artificer App](https://artificer.app/) - 1143+ MTG frame templates

### Design Reference
- [Card frame history - MTG Wiki](https://mtg.fandom.com/wiki/Card_frame)
- [Figma MTG Card Designer](https://www.figma.com/community/file/773439497184575668)
