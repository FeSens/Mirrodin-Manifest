import type { CardData } from '../types/card';

// This will be populated by the build script
export const cards: CardData[] = [];

// Function to parse card from markdown (used in build script)
export const parseCardFromMarkdown = (content: string, filename: string): CardData | null => {
  // Extract frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) return null;

  const frontmatter = frontmatterMatch[1];
  const body = content.slice(frontmatterMatch[0].length);

  // Check if it's a card
  if (!frontmatter.includes('- card')) return null;

  // Parse frontmatter fields
  const getValue = (key: string): string => {
    const match = frontmatter.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
    return match ? match[1].trim().replace(/^["']|["']$/g, '') : '';
  };

  const getArray = (key: string): string[] => {
    const regex = new RegExp(`${key}:\\s*\\n((?:\\s+-\\s+.+\\n?)*)`, 'm');
    const match = frontmatter.match(regex);
    if (!match) return [];
    return match[1].match(/-\s+(.+)/g)?.map(m => m.replace(/^-\s+/, '').trim()) || [];
  };

  // Extract name from H1
  const nameMatch = body.match(/^#\s+(.+)$/m);
  const name = nameMatch ? nameMatch[1].trim() : filename.replace('.md', '');

  // Extract type line
  const typeLineMatch = body.match(/## Card Type Line\n(.+)/);
  const typeLine = typeLineMatch ? typeLineMatch[1].trim() : getValue('type');

  // Extract rules text (blockquote content)
  const rulesMatch = body.match(/## Rules Text\n([\s\S]*?)(?=\n##|$)/);
  let rulesText = '';
  if (rulesMatch) {
    const lines = rulesMatch[1].split('\n')
      .filter(l => l.startsWith('>'))
      .map(l => l.replace(/^>\s*/, ''))
      .filter(l => !l.startsWith('*')); // Remove flavor text lines
    rulesText = lines.join('\n');
  }

  // Extract flavor text
  const flavorMatch = body.match(/## Flavor Text\n>\s*\*(.+)\*/);
  const flavorText = flavorMatch ? flavorMatch[1] : undefined;

  // Get colors
  const colors = getArray('color');

  // Get power/toughness
  const power = getValue('power');
  const toughness = getValue('toughness');

  // Sanitize filename for image path
  const imageName = name.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_');

  return {
    name,
    manaCost: getValue('mana_cost'),
    cmc: parseInt(getValue('cmc')) || 0,
    type: getValue('type'),
    subtype: getValue('subtype'),
    typeLine,
    rulesText,
    flavorText,
    power: power || undefined,
    toughness: toughness || undefined,
    colors,
    rarity: getValue('rarity') as CardData['rarity'],
    set: getValue('set') || 'Mirrodin Manifest',
    artUrl: `./images/${imageName}.png`,
  };
};
