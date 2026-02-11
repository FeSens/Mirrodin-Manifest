import { useState, useEffect, useRef, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { toPng } from 'html-to-image';
import { MtgCard } from 'mtg-card';
import type { CardData } from './types/card';
import cardsData from './data/cards.json';

function cardDataToProps(card: CardData) {
  const manaCost = (card.manaCost.match(/\{([^}]+)\}/g) || [])
    .map(m => m.slice(1, -1));

  const isLegendary = card.typeLine.toLowerCase().startsWith('legendary');
  const isPlaneswalker = card.type.toLowerCase().includes('planeswalker');

  const rarityMap: Record<string, string> = {
    Common: 'C', Uncommon: 'U', Rare: 'R', Mythic: 'M',
  };

  const base = {
    cardName: card.name,
    manaCost,
    typeLine: card.typeLine,
    cardArt: card.artUrl,
    legendary: isLegendary || undefined,
    rarity: rarityMap[card.rarity] || 'C',
    cardNumber: card.collectorNumber,
    totalCards: card.totalCards,
    artist: card.artist,
    year: '2025 — NOT FOR SALE',
    language: 'EN',
    setSymbolUrl: '/set-symbol.svg',
  };

  if (isPlaneswalker && card.loyalty) {
    const loyaltyAbilities = card.rulesText
      .split('\n')
      .filter(line => /^[+\-−]?\d+:/.test(line.trim()))
      .map(line => {
        const match = line.trim().match(/^([+\-−]?\d+):\s*(.+)$/);
        return match
          ? { cost: match[1].replace('−', '-'), text: match[2] }
          : { cost: '0', text: line.trim() };
      });

    return {
      ...base,
      frame: 'planeswalker' as const,
      loyaltyAbilities: loyaltyAbilities.length > 0
        ? loyaltyAbilities
        : [{ cost: '0', text: card.rulesText }],
      startingLoyalty: card.loyalty,
    };
  }

  return {
    ...base,
    rulesText: card.rulesText,
    flavorText: card.flavorText,
    power: card.power,
    toughness: card.toughness,
  };
}

// Extend window for ready signal
declare global {
  interface Window {
    __CARD_READY: boolean;
    __EXPORTED_PNG: string | null;
  }
}

// Parse URL params
const params = new URLSearchParams(window.location.search);
const cardName = params.get('card');
const cardIndex = params.get('index');
const refImagePath = params.get('ref') || './reference/goal-mtg.jpg';
const showCompare = params.get('compare') !== 'false'; // default true

// Find the requested card
const cards = cardsData as CardData[];
let selectedCard: CardData | undefined;

if (cardName) {
  selectedCard = cards.find(c => c.name.toLowerCase() === cardName.toLowerCase());
} else if (cardIndex) {
  selectedCard = cards[parseInt(cardIndex, 10)];
}

// Default: find first green enchantment (similar to Oath of Nissa reference)
if (!selectedCard) {
  selectedCard = cards.find(c =>
    c.colors.includes('Green') && c.type.toLowerCase().includes('enchantment')
  ) || cards.find(c => c.colors.includes('Green')) || cards[0];
}

// ── Pixel Diff Logic ────────────────────────────────────────────
function computeDiff(
  img1Data: ImageData,
  img2Data: ImageData,
  width: number,
  height: number,
  options: { ignoreArt: boolean; ignoreText: boolean }
): { diffCanvas: HTMLCanvasElement; stats: DiffStats } {
  const diffCanvas = document.createElement('canvas');
  diffCanvas.width = width;
  diffCanvas.height = height;
  const ctx = diffCanvas.getContext('2d')!;
  const diffImageData = ctx.createImageData(width, height);

  // Card element regions (normalized to 0-1)
  const artRegion = { x: 50/672, y: 104/936, w: 572/672, h: 417/936 };
  const textRegion = { x: 49/672, y: 585/936, w: 573/672, h: 284/936 };

  let totalDiff = 0;
  let mismatchCount = 0;
  let comparedPixels = 0;

  for (let i = 0; i < width * height; i++) {
    const x = i % width;
    const y = Math.floor(i / width);
    const nx = x / width;
    const ny = y / height;

    // Check if in ignore region
    const inArt = options.ignoreArt &&
      nx >= artRegion.x && nx <= artRegion.x + artRegion.w &&
      ny >= artRegion.y && ny <= artRegion.y + artRegion.h;
    const inText = options.ignoreText &&
      nx >= textRegion.x && nx <= textRegion.x + textRegion.w &&
      ny >= textRegion.y && ny <= textRegion.y + textRegion.h;

    const idx = i * 4;
    if (inArt || inText) {
      // Gray out ignored regions
      diffImageData.data[idx] = 80;
      diffImageData.data[idx + 1] = 80;
      diffImageData.data[idx + 2] = 80;
      diffImageData.data[idx + 3] = 255;
      continue;
    }

    const dr = Math.abs(img1Data.data[idx] - img2Data.data[idx]);
    const dg = Math.abs(img1Data.data[idx + 1] - img2Data.data[idx + 1]);
    const db = Math.abs(img1Data.data[idx + 2] - img2Data.data[idx + 2]);
    const diff = (dr + dg + db) / 3;

    totalDiff += diff;
    comparedPixels++;
    if (diff > 20) mismatchCount++;

    // Color the diff: green = match, red = mismatch, intensity = magnitude
    if (diff < 10) {
      diffImageData.data[idx] = 0;
      diffImageData.data[idx + 1] = 60;
      diffImageData.data[idx + 2] = 0;
    } else if (diff < 30) {
      diffImageData.data[idx] = Math.round(diff * 4);
      diffImageData.data[idx + 1] = Math.round(diff * 2);
      diffImageData.data[idx + 2] = 0;
    } else {
      diffImageData.data[idx] = Math.min(255, Math.round(diff * 3));
      diffImageData.data[idx + 1] = 0;
      diffImageData.data[idx + 2] = Math.min(255, Math.round(diff));
    }
    diffImageData.data[idx + 3] = 255;
  }

  ctx.putImageData(diffImageData, 0, 0);

  return {
    diffCanvas,
    stats: {
      avgDiff: comparedPixels > 0 ? totalDiff / comparedPixels : 0,
      matchPercent: comparedPixels > 0
        ? ((comparedPixels - mismatchCount) / comparedPixels) * 100
        : 100,
      mismatchPixels: mismatchCount,
      totalPixels: comparedPixels,
    },
  };
}

interface DiffStats {
  avgDiff: number;
  matchPercent: number;
  mismatchPixels: number;
  totalPixels: number;
}

// ── Main Render Component ───────────────────────────────────────
function RenderApp() {
  const cardRef = useRef<HTMLDivElement>(null);
  const [exported, setExported] = useState<string | null>(null);
  const [diffImage, setDiffImage] = useState<string | null>(null);
  const [stats, setStats] = useState<DiffStats | null>(null);
  const [ignoreArt, setIgnoreArt] = useState(true);
  const [ignoreText, setIgnoreText] = useState(true);
  const [refLoaded, setRefLoaded] = useState(false);
  const refImgRef = useRef<HTMLImageElement | null>(null);

  const card = selectedCard!;

  const exportCard = useCallback(async () => {
    if (!cardRef.current) return;
    await document.fonts.ready;
    // Wait for render
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));

    const dataUrl = await toPng(cardRef.current, {
      cacheBust: true,
      pixelRatio: 1,
      width: 672,
      height: 936,
    });
    setExported(dataUrl);
    window.__EXPORTED_PNG = dataUrl;
    return dataUrl;
  }, []);

  const runComparison = useCallback(async () => {
    const pngUrl = exported || await exportCard();
    if (!pngUrl || !refImgRef.current) return;

    // Draw both images to canvas for comparison
    const W = 672, H = 936;
    const canvas1 = document.createElement('canvas');
    canvas1.width = W; canvas1.height = H;
    const ctx1 = canvas1.getContext('2d')!;

    const canvas2 = document.createElement('canvas');
    canvas2.width = W; canvas2.height = H;
    const ctx2 = canvas2.getContext('2d')!;

    // Draw reference
    ctx1.drawImage(refImgRef.current, 0, 0, W, H);
    const refData = ctx1.getImageData(0, 0, W, H);

    // Draw rendered
    const img = new Image();
    img.crossOrigin = 'anonymous';
    await new Promise<void>((resolve) => {
      img.onload = () => resolve();
      img.src = pngUrl;
    });
    ctx2.drawImage(img, 0, 0, W, H);
    const renderedData = ctx2.getImageData(0, 0, W, H);

    // Compute diff
    const { diffCanvas, stats: diffStats } = computeDiff(
      refData, renderedData, W, H,
      { ignoreArt, ignoreText }
    );

    setDiffImage(diffCanvas.toDataURL());
    setStats(diffStats);
  }, [exported, exportCard, ignoreArt, ignoreText]);

  // Auto-export on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      exportCard().then(() => {
        window.__CARD_READY = true;
        console.log(`[render] Card "${card.name}" exported at 672x936`);
      });
    }, 1000);
    return () => clearTimeout(timer);
  }, [exportCard, card.name]);

  // Load reference image
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => { refImgRef.current = img; setRefLoaded(true); };
    img.src = refImagePath;
  }, []);

  return (
    <div style={{ background: '#1a1a2e', minHeight: '100vh', padding: 20 }}>
      {/* Card render area */}
      <div
        ref={cardRef}
        id="card-capture"
        style={{ width: 672, height: 936, margin: '0 auto' }}
      >
        <MtgCard {...cardDataToProps(card)} />
      </div>

      {/* Comparison controls */}
      {showCompare && (
        <div style={{ maxWidth: 2100, margin: '30px auto', color: '#ddd', fontFamily: 'sans-serif' }}>
          <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center', flexWrap: 'wrap' }}>
            <button onClick={exportCard} style={btnStyle}>
              Export PNG
            </button>
            <button onClick={runComparison} disabled={!refLoaded} style={btnStyle}>
              Compare vs Reference
            </button>
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <input type="checkbox" checked={ignoreArt} onChange={e => setIgnoreArt(e.target.checked)} />
              Ignore Art
            </label>
            <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <input type="checkbox" checked={ignoreText} onChange={e => setIgnoreText(e.target.checked)} />
              Ignore Text
            </label>
            {exported && (
              <a href={exported} download={`${card.name.replace(/\s+/g, '_')}.png`} style={{ color: '#ffd700' }}>
                Download PNG
              </a>
            )}
          </div>

          {stats && (
            <div style={{ marginBottom: 20, padding: 16, background: 'rgba(0,0,0,0.4)', borderRadius: 8 }}>
              <h3 style={{ margin: '0 0 10px', color: '#ffd700' }}>Comparison Stats</h3>
              <div>Match: <strong>{stats.matchPercent.toFixed(1)}%</strong></div>
              <div>Avg diff: <strong>{stats.avgDiff.toFixed(2)}</strong></div>
              <div>Mismatched pixels: <strong>{stats.mismatchPixels.toLocaleString()}</strong> / {stats.totalPixels.toLocaleString()}</div>
            </div>
          )}

          {/* Side by side comparison */}
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            <div>
              <h4 style={{ color: '#aaa', margin: '0 0 8px' }}>Reference</h4>
              <img src={refImagePath} style={{ width: 336, height: 468, objectFit: 'contain', borderRadius: 8 }} />
            </div>
            {exported && (
              <div>
                <h4 style={{ color: '#aaa', margin: '0 0 8px' }}>Rendered</h4>
                <img src={exported} style={{ width: 336, height: 468, objectFit: 'contain', borderRadius: 8 }} />
              </div>
            )}
            {diffImage && (
              <div>
                <h4 style={{ color: '#aaa', margin: '0 0 8px' }}>Diff (green=match, red=mismatch)</h4>
                <img src={diffImage} style={{ width: 336, height: 468, objectFit: 'contain', borderRadius: 8 }} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: '10px 20px',
  background: '#ffd700',
  color: '#111',
  border: 'none',
  borderRadius: 8,
  fontWeight: 'bold',
  cursor: 'pointer',
};

// Mount
const root = createRoot(document.getElementById('render-root')!);
root.render(<RenderApp />);
