import type { CardData } from '../types/card';
import { getCardColorClass } from '../types/card';
import './MtgCardPixelPerfect.css';

type CardSize = 'sm' | 'md' | 'lg' | 'xl';

interface MtgCardProps {
  card: CardData;
  size?: CardSize;
  className?: string;
  style?: React.CSSProperties;
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
      if (symbol === 't') {
        return <i key={i} className="ms ms-tap ms-cost" />;
      }
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

export const MtgCardPixelPerfect: React.FC<MtgCardProps> = ({
  card,
  size = 'md',
  className = '',
  style,
}) => {
  const colorClass = getCardColorClass(card.colors);
  const manaSymbols = parseManaCost(card.manaCost);
  const isCreature = card.type.toLowerCase().includes('creature');
  const isPlaneswalker = card.type.toLowerCase().includes('planeswalker');
  const rarityClass = card.rarity?.toLowerCase() || '';

  // Calculate text size based on content length
  const getTextSizeClass = () => {
    const len = (card.rulesText || '').length;
    if (len > 400) return 'text-xs';
    if (len > 300) return 'text-sm';
    if (len > 200) return 'text-md';
    return 'text-lg';
  };

  return (
    <div
      className={`mtg-card-pp size-${size} ${colorClass} rarity-${rarityClass} ${className}`}
      style={style}
    >
      <div className="card-scale">
        {/* Black Border */}
        <div className="card-border">
          {/* Inner Frame */}
          <div className="card-frame-pp">
            {/* Title Bar */}
            <div className="title-bar-pp">
              <span className="card-name-pp">{card.name}</span>
              <span className="mana-cost-pp">
                {manaSymbols.map((symbol, i) => (
                  <i key={i} className={`ms ms-${symbol} ms-cost`} />
                ))}
              </span>
            </div>

            {/* Art Box */}
            <div className="art-box-pp">
              {card.artUrl ? (
                <img src={card.artUrl} alt={card.name} className="card-art-pp" />
              ) : (
                <div className="art-placeholder-pp">
                  <span>{card.name}</span>
                </div>
              )}
            </div>

            {/* Type Line */}
            <div className="type-bar-pp">
              <span className="type-line-pp">{card.typeLine}</span>
              <span className="set-symbol-pp">
                <i className={`ss ss-mm ss-fw ${getRarityClass(card.rarity)}`} />
              </span>
            </div>

            {/* Text Box */}
            <div className={`text-box-pp ${getTextSizeClass()}`}>
              <div className="rules-text-pp">
                {card.rulesText.split('\n').map((line, i) => (
                  <p key={i}>{parseRulesText(line)}</p>
                ))}
              </div>
              {card.flavorText && (
                <div className="flavor-text-pp">
                  <em>{card.flavorText}</em>
                </div>
              )}
            </div>

            {/* P/T Box for creatures */}
            {isCreature && card.power && card.toughness && (
              <div className="pt-box-pp">
                <div className="pt-inner" />
                <div className="pt-text-bg" />
                <span>{card.power}/{card.toughness}</span>
              </div>
            )}

            {/* Loyalty Box for planeswalkers */}
            {isPlaneswalker && card.loyalty && (
              <div className="loyalty-box-pp">
                <span>{card.loyalty}</span>
              </div>
            )}
          </div>

          {/* Bottom Info Bar (on black border) */}
          <div className="info-bar-pp">
            <span className="collector-info-pp">
              {card.collectorNumber && `${card.collectorNumber} • `}
              {card.artist && `${card.artist}`}
            </span>
          </div>

          {/* Holofoil Stamp for Rare/Mythic */}
          {(rarityClass === 'rare' || rarityClass === 'mythic') && (
            <div className="holofoil-stamp-pp" />
          )}
        </div>
      </div>
    </div>
  );
};

export default MtgCardPixelPerfect;
