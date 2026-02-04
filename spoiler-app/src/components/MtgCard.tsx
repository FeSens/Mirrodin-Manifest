import type { CardData } from '../types/card';
import { getCardColorClass } from '../types/card';
import './MtgCard.css';

interface MtgCardProps {
  card: CardData;
}

// Parse mana cost string like "{2}{W}{U}" into symbols
const parseManaCost = (cost: string): string[] => {
  if (!cost) return [];
  const matches = cost.match(/\{([^}]+)\}/g) || [];
  return matches.map(m => m.slice(1, -1).toLowerCase());
};

// Parse rules text and convert {X} symbols to mana icons
const parseRulesText = (text: string): React.ReactNode[] => {
  if (!text) return [];

  const parts = text.split(/(\{[^}]+\})/g);
  return parts.map((part, i) => {
    const match = part.match(/\{([^}]+)\}/);
    if (match) {
      const symbol = match[1].toLowerCase();
      // Handle tap symbol
      if (symbol === 't') {
        return <i key={i} className="ms ms-tap ms-cost" />;
      }
      // Handle hybrid mana
      if (symbol.includes('/')) {
        const [a, b] = symbol.split('/');
        return <i key={i} className={`ms ms-${a}${b} ms-cost ms-split`} />;
      }
      return <i key={i} className={`ms ms-${symbol} ms-cost`} />;
    }
    return <span key={i}>{part}</span>;
  });
};

// Get rarity class for set symbol
const getRarityClass = (rarity: string): string => {
  const rarityMap: Record<string, string> = {
    'Common': 'ss-common',
    'Uncommon': 'ss-uncommon',
    'Rare': 'ss-rare',
    'Mythic': 'ss-mythic',
  };
  return rarityMap[rarity] || 'ss-common';
};

export const MtgCard: React.FC<MtgCardProps> = ({ card }) => {
  const colorClass = getCardColorClass(card.colors);
  const manaSymbols = parseManaCost(card.manaCost);
  const isCreature = card.type.toLowerCase().includes('creature');
  const isPlaneswalker = card.type.toLowerCase().includes('planeswalker');
  const rarityClass = card.rarity?.toLowerCase() || '';

  // Determine text size based on rules text length
  const getTextSizeClass = () => {
    const len = (card.rulesText || '').length;
    if (len > 400) return 'text-tiny';
    if (len > 300) return 'text-small';
    if (len > 200) return 'text-medium';
    return 'text-normal';
  };

  return (
    <div className={`mtg-card ${colorClass} ${rarityClass}`}>
      {/* Card Frame */}
      <div className="card-frame">
        {/* Title Bar */}
        <div className="title-bar">
          <span className="card-name">{card.name}</span>
          <span className="mana-cost">
            {manaSymbols.map((symbol, i) => (
              <i key={i} className={`ms ms-${symbol} ms-cost`} />
            ))}
          </span>
        </div>

        {/* Art Box */}
        <div className="art-box">
          {card.artUrl ? (
            <img src={card.artUrl} alt={card.name} className="card-art" />
          ) : (
            <div className="art-placeholder">
              <span>{card.name}</span>
            </div>
          )}
        </div>

        {/* Type Bar */}
        <div className="type-bar">
          <span className="type-line">{card.typeLine}</span>
          <span className="set-symbol">
            <i className={`ss ss-mm ss-fw ${getRarityClass(card.rarity)}`} />
          </span>
        </div>

        {/* Text Box */}
        <div className={`text-box ${getTextSizeClass()}`}>
          <div className="rules-text">
            {card.rulesText.split('\n').map((line, i) => (
              <p key={i}>{parseRulesText(line)}</p>
            ))}
          </div>
          {card.flavorText && (
            <div className="flavor-text">
              <em>{card.flavorText}</em>
            </div>
          )}
        </div>

        {/* Info Bar */}
        <div className="info-bar">
          <span className="artist">
            {card.collectorNumber && `${card.collectorNumber} `}
            {card.artist && `Illus. ${card.artist}`}
          </span>
          {/* P/T Box for creatures */}
          {isCreature && card.power && card.toughness && (
            <div className="pt-box">
              {card.power}/{card.toughness}
            </div>
          )}
          {/* Loyalty for planeswalkers */}
          {isPlaneswalker && card.loyalty && (
            <div className="loyalty-box">{card.loyalty}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MtgCard;
