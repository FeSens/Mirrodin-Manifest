export interface CardData {
  name: string;
  manaCost: string;
  cmc: number;
  type: string;
  subtype?: string;
  supertype?: string;
  typeLine: string;
  rulesText: string;
  flavorText?: string;
  power?: string;
  toughness?: string;
  loyalty?: string;
  colors: string[];
  rarity: 'Common' | 'Uncommon' | 'Rare' | 'Mythic';
  set: string;
  artUrl?: string;
  artist?: string;
  collectorNumber?: string;
}

export type CardColor = 'W' | 'U' | 'B' | 'R' | 'G' | 'C' | 'M' | 'Land';

export const COLOR_MAP: Record<string, CardColor> = {
  'White': 'W',
  'Blue': 'U',
  'Black': 'B',
  'Red': 'R',
  'Green': 'G',
  'Colorless': 'C',
};

export const getCardColorClass = (colors: string[]): string => {
  if (colors.length === 0) return 'colorless';
  if (colors.length > 1) return 'multicolor';

  const colorMap: Record<string, string> = {
    'White': 'white',
    'Blue': 'blue',
    'Black': 'black',
    'Red': 'red',
    'Green': 'green',
  };

  return colorMap[colors[0]] || 'colorless';
};
