import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'yaml';

interface CardData {
  name: string;
  manaCost: string;
  cmc: number;
  type: string;
  subtype?: string;
  typeLine: string;
  rulesText: string;
  flavorText?: string;
  power?: string;
  toughness?: string;
  colors: string[];
  rarity: string;
  set: string;
  artUrl: string;
}

const CARDS_DIR = path.join(__dirname, '../../cards');
const OUTPUT_FILE = path.join(__dirname, '../src/data/cards.json');
const IMAGES_DIR = path.join(__dirname, '../../images');

function parseCard(content: string, filename: string): CardData | null {
  // Extract frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) return null;

  try {
    const frontmatter = yaml.parse(frontmatterMatch[1]);
    const body = content.slice(frontmatterMatch[0].length);

    // Check if it's a card
    if (!frontmatter.tags?.includes('card')) return null;

    // Extract name from H1
    const nameMatch = body.match(/^#\s+(.+)$/m);
    const name = nameMatch ? nameMatch[1].trim() : filename.replace('.md', '');

    // Extract type line
    const typeLineMatch = body.match(/## Card Type Line\n(.+)/);
    const typeLine = typeLineMatch ? typeLineMatch[1].trim() : frontmatter.type || '';

    // Extract rules text (blockquote content)
    const rulesMatch = body.match(/## Rules Text\n([\s\S]*?)(?=\n##|$)/);
    let rulesText = '';
    if (rulesMatch) {
      const lines = rulesMatch[1].split('\n')
        .filter((l: string) => l.startsWith('>'))
        .map((l: string) => l.replace(/^>\s*/, ''))
        .filter((l: string) => !l.startsWith('*')); // Remove flavor text lines
      rulesText = lines.join('\n').trim();
    }

    // Extract flavor text from Rules Text section (italic lines)
    let flavorText: string | undefined;
    if (rulesMatch) {
      const flavorLines = rulesMatch[1].split('\n')
        .filter((l: string) => l.startsWith('>'))
        .map((l: string) => l.replace(/^>\s*/, ''))
        .filter((l: string) => l.startsWith('*') && l.endsWith('*'));
      if (flavorLines.length > 0) {
        flavorText = flavorLines.map((l: string) => l.replace(/^\*|\*$/g, '')).join(' ');
      }
    }

    // Also check dedicated Flavor Text section
    const flavorMatch = body.match(/## Flavor Text\n>\s*\*(.+)\*/);
    if (flavorMatch) {
      flavorText = flavorMatch[1];
    }

    // Sanitize filename for image path
    const imageName = name.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_');

    // Check if image exists
    const imagePath = path.join(IMAGES_DIR, `${imageName}.png`);
    const hasImage = fs.existsSync(imagePath);

    return {
      name,
      manaCost: frontmatter.mana_cost || '',
      cmc: frontmatter.cmc || 0,
      type: frontmatter.type || '',
      subtype: frontmatter.subtype,
      typeLine,
      rulesText,
      flavorText,
      power: frontmatter.power?.toString(),
      toughness: frontmatter.toughness?.toString(),
      colors: frontmatter.color || [],
      rarity: frontmatter.rarity || 'Common',
      set: frontmatter.set || 'Mirrodin Manifest',
      artUrl: hasImage ? `./images/${imageName}.png` : '',
    };
  } catch (e) {
    console.error(`Error parsing ${filename}:`, e);
    return null;
  }
}

function main() {
  const cards: CardData[] = [];

  // Read all card files
  const files = fs.readdirSync(CARDS_DIR).filter(f => f.endsWith('.md'));

  for (const file of files) {
    const content = fs.readFileSync(path.join(CARDS_DIR, file), 'utf-8');
    const card = parseCard(content, file);
    if (card) {
      cards.push(card);
    }
  }

  // Sort by name
  cards.sort((a, b) => a.name.localeCompare(b.name));

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write output
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(cards, null, 2));

  console.log(`Generated ${cards.length} cards to ${OUTPUT_FILE}`);

  // Stats
  const withArt = cards.filter(c => c.artUrl).length;
  console.log(`Cards with art: ${withArt}/${cards.length}`);
}

main();
