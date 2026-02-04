import { useMemo, useRef, useState } from 'react';
import { MtgCard } from './components/MtgCard';
import { MtgCardPixelPerfect } from './components/MtgCardPixelPerfect';
import type { CardData } from './types/card';
import cardsData from './data/cards.json';
import './App.css';
import { toPng } from 'html-to-image';

type SortOption = 'name' | 'cmc' | 'color' | 'rarity' | 'type';
type FilterColor = 'all' | 'W' | 'U' | 'B' | 'R' | 'G' | 'C' | 'M';

const RARITY_ORDER = ['Common', 'Uncommon', 'Rare', 'Mythic'];
const COLOR_ORDER = ['White', 'Blue', 'Black', 'Red', 'Green'];

function App() {
  const cards = cardsData as CardData[];

  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('name');
  const [filterColor, setFilterColor] = useState<FilterColor>('all');
  const [filterRarity, setFilterRarity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedCard, setSelectedCard] = useState<CardData | null>(null);
  const [usePixelPerfect, setUsePixelPerfect] = useState(true);
  const [calibrationMode, setCalibrationMode] = useState(false);
  const [refOpacity, setRefOpacity] = useState(0.55);
  const [cardOpacity, setCardOpacity] = useState(1);
  const [exporting, setExporting] = useState(false);
  const [exportPng, setExportPng] = useState<string | null>(null);
  const [diffPng, setDiffPng] = useState<string | null>(null);
  const [diffStats, setDiffStats] = useState<{ avg: number; nearPct: number } | null>(null);
  const [ignoreArt, setIgnoreArt] = useState(true);
  const [ignoreText, setIgnoreText] = useState(true);
  const [referenceUrl, setReferenceUrl] = useState('/reference/goal-mtg.jpg');
  const [offsets, setOffsets] = useState({
    frameX: 0,
    frameY: 0,
    titleX: 0,
    titleY: 0,
    artX: 0,
    artY: 0,
    typeX: 0,
    typeY: 0,
    textX: 0,
    textY: 0,
    infoX: 0,
    infoY: 0,
    stampX: 0,
    stampY: 0,
    ptX: 0,
    ptY: 0,
    loyaltyX: 0,
    loyaltyY: 0,
  });
  const cardCaptureRef = useRef<HTMLDivElement | null>(null);

  const EXPORT_W = 672;
  const EXPORT_H = 936;

  const calibrationStyle = {
    '--frame-dx': `${offsets.frameX}px`,
    '--frame-dy': `${offsets.frameY}px`,
    '--title-dx': `${offsets.titleX}px`,
    '--title-dy': `${offsets.titleY}px`,
    '--art-dx': `${offsets.artX}px`,
    '--art-dy': `${offsets.artY}px`,
    '--type-dx': `${offsets.typeX}px`,
    '--type-dy': `${offsets.typeY}px`,
    '--text-dx': `${offsets.textX}px`,
    '--text-dy': `${offsets.textY}px`,
    '--info-dx': `${offsets.infoX}px`,
    '--info-dy': `${offsets.infoY}px`,
    '--stamp-dx': `${offsets.stampX}px`,
    '--stamp-dy': `${offsets.stampY}px`,
    '--pt-dx': `${offsets.ptX}px`,
    '--pt-dy': `${offsets.ptY}px`,
    '--loyalty-dx': `${offsets.loyaltyX}px`,
    '--loyalty-dy': `${offsets.loyaltyY}px`,
  } as React.CSSProperties;

  const calibrationFields = [
    { label: 'Frame', x: 'frameX', y: 'frameY' },
    { label: 'Title', x: 'titleX', y: 'titleY' },
    { label: 'Art', x: 'artX', y: 'artY' },
    { label: 'Type', x: 'typeX', y: 'typeY' },
    { label: 'Text', x: 'textX', y: 'textY' },
    { label: 'Info', x: 'infoX', y: 'infoY' },
    { label: 'Stamp', x: 'stampX', y: 'stampY' },
    { label: 'P/T', x: 'ptX', y: 'ptY' },
    { label: 'Loyalty', x: 'loyaltyX', y: 'loyaltyY' },
  ] as const;

  const calibrationCard = useMemo(() => {
    const whiteCreature = cards.find(
      c => c.power && c.toughness && c.colors?.length === 1 && c.colors[0] === 'White'
    );
    return whiteCreature ?? cards.find(c => c.power && c.toughness) ?? cards[0];
  }, [cards]);

  const calibrationDisplayCard =
    selectedCard && selectedCard.power && selectedCard.toughness ? selectedCard : calibrationCard;

  const loadImage = (src: string) =>
    new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });

  const buildDiff = async (generatedUrl: string) => {
    const [refImg, genImg] = await Promise.all([loadImage(referenceUrl), loadImage(generatedUrl)]);
    const root = cardCaptureRef.current;
    const rootRect = root?.getBoundingClientRect();

    const rectFrom = (selector: string) => {
      if (!root || !rootRect) return null;
      const el = root.querySelector(selector) as HTMLElement | null;
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {
        x: r.left - rootRect.left,
        y: r.top - rootRect.top,
        w: r.width,
        h: r.height,
      };
    };

    const insetRect = (rect: { x: number; y: number; w: number; h: number }, padX: number, padY?: number) => {
      const py = padY ?? padX;
      return {
        x: rect.x + padX,
        y: rect.y + py,
        w: rect.w - padX * 2,
        h: rect.h - py * 2,
      };
    };

    const expandRect = (rect: { x: number; y: number; w: number; h: number }, padX: number, padY?: number) => {
      const py = padY ?? padX;
      return {
        x: rect.x - padX,
        y: rect.y - py,
        w: rect.w + padX * 2,
        h: rect.h + py * 2,
      };
    };

    const masks: { x: number; y: number; w: number; h: number }[] = [];
    if (ignoreArt) {
      const art = rectFrom('.art-box-pp');
      if (art) masks.push(insetRect(art, 6));
    }
    if (ignoreText) {
      const text = rectFrom('.text-box-pp');
      if (text) masks.push(insetRect(text, 10));

      const title = rectFrom('.title-bar-pp');
      if (title) masks.push(insetRect(title, 14, 10));

      const type = rectFrom('.type-bar-pp');
      if (type) masks.push(insetRect(type, 14, 10));

      const info = rectFrom('.info-bar-pp');
      if (info) masks.push(expandRect(info, 6, 4));
    }

    const inMask = (x: number, y: number) => {
      for (const m of masks) {
        if (x >= m.x && x <= m.x + m.w && y >= m.y && y <= m.y + m.h) {
          return true;
        }
      }
      return false;
    };

    const canvas = document.createElement('canvas');
    canvas.width = EXPORT_W;
    canvas.height = EXPORT_H;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.clearRect(0, 0, EXPORT_W, EXPORT_H);
    ctx.drawImage(refImg, 0, 0, EXPORT_W, EXPORT_H);
    const refData = ctx.getImageData(0, 0, EXPORT_W, EXPORT_H).data;

    ctx.clearRect(0, 0, EXPORT_W, EXPORT_H);
    ctx.drawImage(genImg, 0, 0, EXPORT_W, EXPORT_H);
    const genData = ctx.getImageData(0, 0, EXPORT_W, EXPORT_H).data;

    const out = ctx.createImageData(EXPORT_W, EXPORT_H);
    let totalDiff = 0;
    let near = 0;
    let considered = 0;
    const pxCount = EXPORT_W * EXPORT_H;

    for (let i = 0; i < refData.length; i += 4) {
      const p = i / 4;
      const x = p % EXPORT_W;
      const y = Math.floor(p / EXPORT_W);

      if (inMask(x, y)) {
        out.data[i] = 0;
        out.data[i + 1] = 0;
        out.data[i + 2] = 0;
        out.data[i + 3] = 0;
        continue;
      }

      const dr = Math.abs(genData[i] - refData[i]);
      const dg = Math.abs(genData[i + 1] - refData[i + 1]);
      const db = Math.abs(genData[i + 2] - refData[i + 2]);
      const diff = (dr + dg + db) / 3;

      out.data[i] = dr;
      out.data[i + 1] = dg;
      out.data[i + 2] = db;
      out.data[i + 3] = 255;

      totalDiff += diff;
      if (diff < 8) near += 1;
      considered += 1;
    }

    ctx.putImageData(out, 0, 0);
    const denom = considered || 1;
    const avg = totalDiff / denom;
    const nearPct = (near / denom) * 100;
    setDiffStats({ avg: Number(avg.toFixed(2)), nearPct: Number(nearPct.toFixed(2)) });
    return canvas.toDataURL('image/png');
  };

  const exportCardPng = async () => {
    if (!cardCaptureRef.current || exporting) return;
    setExporting(true);
    try {
      if (document.fonts?.ready) {
        await document.fonts.ready;
      }
      const dataUrl = await toPng(cardCaptureRef.current, {
        cacheBust: true,
        pixelRatio: 1,
        width: EXPORT_W,
        height: EXPORT_H,
        filter: node => {
          if (!(node instanceof HTMLElement)) return true;
          if (ignoreArt && node.classList.contains('card-art-pp')) return false;
          if (ignoreArt && node.classList.contains('art-box-pp')) return false;
          return true;
        },
      });
      setExportPng(dataUrl);
      const diff = await buildDiff(dataUrl);
      setDiffPng(diff);
    } catch (err) {
      console.error('Export failed', err);
    } finally {
      setExporting(false);
    }
  };

  // Get unique types for filter
  const cardTypes = useMemo(() => {
    const types = new Set<string>();
    cards.forEach(c => types.add(c.type));
    return Array.from(types).sort();
  }, [cards]);

  // Filter and sort cards
  const filteredCards = useMemo(() => {
    let result = [...cards];

    // Search filter
    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter(c =>
        c.name.toLowerCase().includes(searchLower) ||
        c.rulesText.toLowerCase().includes(searchLower) ||
        c.typeLine.toLowerCase().includes(searchLower)
      );
    }

    // Color filter
    if (filterColor !== 'all') {
      if (filterColor === 'M') {
        result = result.filter(c => c.colors.length > 1);
      } else if (filterColor === 'C') {
        result = result.filter(c => c.colors.length === 0);
      } else {
        const colorMap: Record<string, string> = {
          'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'
        };
        result = result.filter(c => c.colors.includes(colorMap[filterColor]));
      }
    }

    // Rarity filter
    if (filterRarity !== 'all') {
      result = result.filter(c => c.rarity === filterRarity);
    }

    // Type filter
    if (filterType !== 'all') {
      result = result.filter(c => c.type === filterType);
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'cmc':
          return a.cmc - b.cmc || a.name.localeCompare(b.name);
        case 'color':
          const aColorIdx = a.colors.length > 1 ? 10 : a.colors.length === 0 ? 11 : COLOR_ORDER.indexOf(a.colors[0]);
          const bColorIdx = b.colors.length > 1 ? 10 : b.colors.length === 0 ? 11 : COLOR_ORDER.indexOf(b.colors[0]);
          return aColorIdx - bColorIdx || a.name.localeCompare(b.name);
        case 'rarity':
          return RARITY_ORDER.indexOf(b.rarity) - RARITY_ORDER.indexOf(a.rarity) || a.name.localeCompare(b.name);
        case 'type':
          return a.type.localeCompare(b.type) || a.name.localeCompare(b.name);
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return result;
  }, [cards, search, sortBy, filterColor, filterRarity, filterType]);

  return (
    <div className="app">
      <header className="header">
        <h1>Mirrodin Manifest</h1>
        <p className="subtitle">Card Gallery — {cards.length} Cards</p>
      </header>

      <div className="controls">
        <input
          type="text"
          placeholder="Search cards..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="search-input"
        />

        <select value={sortBy} onChange={e => setSortBy(e.target.value as SortOption)}>
          <option value="name">Sort by Name</option>
          <option value="cmc">Sort by Mana Value</option>
          <option value="color">Sort by Color</option>
          <option value="rarity">Sort by Rarity</option>
          <option value="type">Sort by Type</option>
        </select>

        <select value={filterColor} onChange={e => setFilterColor(e.target.value as FilterColor)}>
          <option value="all">All Colors</option>
          <option value="W">White</option>
          <option value="U">Blue</option>
          <option value="B">Black</option>
          <option value="R">Red</option>
          <option value="G">Green</option>
          <option value="M">Multicolor</option>
          <option value="C">Colorless</option>
        </select>

        <select value={filterRarity} onChange={e => setFilterRarity(e.target.value)}>
          <option value="all">All Rarities</option>
          <option value="Common">Common</option>
          <option value="Uncommon">Uncommon</option>
          <option value="Rare">Rare</option>
          <option value="Mythic">Mythic</option>
        </select>

        <select value={filterType} onChange={e => setFilterType(e.target.value)}>
          <option value="all">All Types</option>
          {cardTypes.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <label className="toggle-label">
          <input
            type="checkbox"
            checked={usePixelPerfect}
            onChange={e => setUsePixelPerfect(e.target.checked)}
          />
          Pixel Perfect
        </label>

        <label className="toggle-label">
          <input
            type="checkbox"
            checked={calibrationMode}
            onChange={e => setCalibrationMode(e.target.checked)}
          />
          Calibration
        </label>
      </div>

      {calibrationMode && (
        <section className="calibration">
          <div className="calibration-controls">
            <div className="calibration-row">
              <label>
                Reference Opacity
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={refOpacity}
                  onChange={e => setRefOpacity(Number(e.target.value))}
                />
              </label>
              <label>
                Card Opacity
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={cardOpacity}
                  onChange={e => setCardOpacity(Number(e.target.value))}
                />
              </label>
              <label>
                Ignore Art
                <input
                  type="checkbox"
                  checked={ignoreArt}
                  onChange={e => setIgnoreArt(e.target.checked)}
                />
              </label>
              <label>
                Ignore Text
                <input
                  type="checkbox"
                  checked={ignoreText}
                  onChange={e => setIgnoreText(e.target.checked)}
                />
              </label>
            </div>

            <div className="calibration-actions">
              <button type="button" onClick={exportCardPng} disabled={exporting}>
                {exporting ? 'Exporting…' : 'Export PNG + Diff'}
              </button>
              {exportPng && (
                <a className="calibration-download" href={exportPng} download="card.png">
                  Download PNG
                </a>
              )}
              <label className="calibration-upload">
                Reference Image
                <input
                  type="file"
                  accept="image/*"
                  onChange={e => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const url = URL.createObjectURL(file);
                      setReferenceUrl(url);
                    }
                  }}
                />
              </label>
            </div>

            <div className="calibration-grid">
              {calibrationFields.map(field => (
                <div key={field.label} className="calibration-field">
                  <span>{field.label}</span>
                  <label>
                    X
                    <input
                      type="number"
                      step={0.5}
                      value={offsets[field.x]}
                      onChange={e =>
                        setOffsets(prev => ({ ...prev, [field.x]: Number(e.target.value) }))
                      }
                    />
                  </label>
                  <label>
                    Y
                    <input
                      type="number"
                      step={0.5}
                      value={offsets[field.y]}
                      onChange={e =>
                        setOffsets(prev => ({ ...prev, [field.y]: Number(e.target.value) }))
                      }
                    />
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="calibration-stage">
            <img
              className="calibration-ref"
              src={referenceUrl}
              alt="Reference MTG card"
              style={{ opacity: refOpacity }}
            />
            <div className="calibration-card" style={{ opacity: cardOpacity }}>
              <div className="calibration-capture" ref={cardCaptureRef}>
                <MtgCardPixelPerfect
                  card={calibrationDisplayCard}
                  size="xl"
                  className="calibration-card-inner"
                  style={calibrationStyle}
                />
              </div>
            </div>
          </div>

          <pre className="calibration-readout">{JSON.stringify(offsets, null, 2)}</pre>

          {(exportPng || diffPng) && (
            <div className="calibration-results">
              {exportPng && (
                <div className="calibration-result">
                  <span>Exported PNG</span>
                  <img src={exportPng} alt="Exported card" />
                </div>
              )}
              {diffPng && (
                <div className="calibration-result">
                  <span>Diff (absolute)</span>
                  <img src={diffPng} alt="Diff image" />
                </div>
              )}
              {diffStats && (
                <div className="calibration-metrics">
                  <div>Avg diff: {diffStats.avg}</div>
                  <div>Pixels within 8: {diffStats.nearPct}%</div>
                </div>
              )}
            </div>
          )}
        </section>
      )}

      <div className="results-info">
        Showing {filteredCards.length} of {cards.length} cards
      </div>

      <div className="card-grid">
        {filteredCards.map(card => (
          <div
            key={card.name}
            className="card-wrapper"
            onClick={() => setSelectedCard(card)}
          >
            {usePixelPerfect ? (
              <MtgCardPixelPerfect card={card} size="md" />
            ) : (
              <MtgCard card={card} />
            )}
          </div>
        ))}
      </div>

      {/* Modal for selected card */}
      {selectedCard && (
        <div className="modal-overlay" onClick={() => setSelectedCard(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            {usePixelPerfect ? (
              <MtgCardPixelPerfect card={selectedCard} size="lg" />
            ) : (
              <MtgCard card={selectedCard} />
            )}
            <button className="modal-close" onClick={() => setSelectedCard(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
