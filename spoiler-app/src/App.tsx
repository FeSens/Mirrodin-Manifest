import { useMemo, useState } from 'react';
import { MtgCard } from 'mtg-card';
import type { CardData } from './types/card';
import cardsData from './data/cards.json';
import './App.css';

type SortOption = 'name' | 'cmc' | 'color' | 'rarity' | 'type';
type FilterColor = 'all' | 'W' | 'U' | 'B' | 'R' | 'G' | 'C' | 'M';

const RARITY_ORDER = ['Common', 'Uncommon', 'Rare', 'Mythic'];
const COLOR_ORDER = ['White', 'Blue', 'Black', 'Red', 'Green'];

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
    // Parse loyalty abilities from rules text lines like "+1: Draw a card.\n-2: Deal 3 damage.\n-7: Ultimate."
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

function App() {
  const cards = cardsData as CardData[];

  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('name');
  const [filterColor, setFilterColor] = useState<FilterColor>('all');
  const [filterRarity, setFilterRarity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedCard, setSelectedCard] = useState<CardData | null>(null);

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
      </div>

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
            <MtgCard {...cardDataToProps(card)} />
          </div>
        ))}
      </div>

      {/* Modal for selected card */}
      {selectedCard && (
        <div className="modal-overlay" onClick={() => setSelectedCard(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <MtgCard {...cardDataToProps(selectedCard)} />
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
