const fs = require('fs');
const path = require('path');

const CARDS_DIR = path.join(__dirname, '../../cards');
const OUTPUT_FILE = path.join(__dirname, '../src/data/cards.json');
const IMAGES_DIR = path.join(__dirname, '../../images');

function parseYamlValue(content, key) {
  const match = content.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
  if (!match) return '';
  const value = match[1].trim().replace(/^["']|["']$/g, '');
  // Guard against capturing the next YAML key (e.g. empty "color:" followed by "mana_cost: ...")
  if (/^[a-z_]+:/.test(value)) return '';
  return value;
}

function parseYamlArray(content, key) {
  // First try array format: key:\n  - value1\n  - value2
  const arrayRegex = new RegExp(`^${key}:\\s*\\n((?:\\s+-\\s+.+\\n?)*)`, 'm');
  const arrayMatch = content.match(arrayRegex);
  if (arrayMatch && arrayMatch[1].trim()) {
    const items = arrayMatch[1].match(/-\s+(.+)/g);
    return items ? items.map(m => m.replace(/^-\s+/, '').trim()) : [];
  }

  // Then try single value format: key: value
  const singleRegex = new RegExp(`^${key}:\\s*(.+)$`, 'm');
  const singleMatch = content.match(singleRegex);
  if (singleMatch) {
    const value = singleMatch[1].trim();
    // Skip if it looks like an empty/invalid value or captures the next key
    if (value && value !== '[]' && !value.startsWith('-') && !/^[a-z_]+:/.test(value)) {
      return [value];
    }
  }

  return [];
}

function parseCard(content, filename) {
  // Extract frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) return null;

  const frontmatter = frontmatterMatch[1];
  const body = content.slice(frontmatterMatch[0].length);

  // Check if it's a card
  if (!frontmatter.includes('- card')) return null;

  // Extract name from H1
  const nameMatch = body.match(/^#\s+(.+)$/m);
  const name = nameMatch ? nameMatch[1].trim() : filename.replace('.md', '');

  // Extract type line
  const typeLineMatch = body.match(/## Card Type Line\n(.+)/);
  const typeLine = typeLineMatch ? typeLineMatch[1].trim() : parseYamlValue(frontmatter, 'type');

  // Detect supertype from type line
  const supertype = typeLine.toLowerCase().startsWith('legendary') ? 'Legendary' : undefined;

  // Extract rules text (blockquote content, excluding flavor text)
  const rulesMatch = body.match(/## Rules Text\n([\s\S]*?)(?=\n##|$)/);
  let rulesText = '';
  if (rulesMatch) {
    const lines = rulesMatch[1].split('\n')
      .filter(l => l.startsWith('>'))
      .map(l => l.replace(/^>\s*/, ''))
      .filter(l => !(l.startsWith('*') && l.endsWith('*'))); // Filter full-line italics (flavor)

    rulesText = lines.join('\n').trim();

    // Strip inline italic reminder text like *(It's an artifact...)*
    rulesText = rulesText.replace(/\s*\*\([^)]*\)\*/g, '');
  }

  // Extract flavor text
  let flavorText;
  const flavorSectionMatch = body.match(/## Flavor Text\n>\s*\*(.+)\*/);
  if (flavorSectionMatch) {
    flavorText = flavorSectionMatch[1];
  } else if (rulesMatch) {
    // Check for italic lines in rules text
    const flavorLines = rulesMatch[1].split('\n')
      .filter(l => l.startsWith('>'))
      .map(l => l.replace(/^>\s*/, ''))
      .filter(l => l.startsWith('*') && l.endsWith('*'));
    if (flavorLines.length > 0) {
      flavorText = flavorLines.map(l => l.replace(/^\*|\*$/g, '')).join(' ');
    }
  }

  // Sanitize filename for image path
  const imageName = name.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_');

  // Check if image exists
  const imagePath = path.join(IMAGES_DIR, `${imageName}.png`);
  const hasImage = fs.existsSync(imagePath);

  const power = parseYamlValue(frontmatter, 'power');
  const toughness = parseYamlValue(frontmatter, 'toughness');
  const loyalty = parseYamlValue(frontmatter, 'loyalty');

  return {
    name,
    manaCost: parseYamlValue(frontmatter, 'mana_cost'),
    cmc: parseInt(parseYamlValue(frontmatter, 'cmc')) || 0,
    type: parseYamlValue(frontmatter, 'type'),
    subtype: parseYamlValue(frontmatter, 'subtype') || undefined,
    supertype: supertype,
    typeLine,
    rulesText,
    flavorText,
    power: power || undefined,
    toughness: toughness || undefined,
    loyalty: loyalty || undefined,
    colors: parseYamlArray(frontmatter, 'color'),
    rarity: parseYamlValue(frontmatter, 'rarity') || 'Common',
    set: parseYamlValue(frontmatter, 'set') || 'Mirrodin Manifest',
    artist: 'Felipe Bonetto',
    artUrl: hasImage ? `./images/${imageName}.png` : '',
  };
}

function main() {
  const cards = [];

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

  // Assign collector numbers after sorting
  const totalCards = cards.length;
  cards.forEach((card, index) => {
    card.collectorNumber = String(index + 1);
    card.totalCards = String(totalCards);
  });

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

  // Color breakdown
  const byColor = {};
  cards.forEach(c => {
    const key = c.colors.length > 1 ? 'Multicolor' : c.colors[0] || 'Colorless';
    byColor[key] = (byColor[key] || 0) + 1;
  });
  console.log('By color:', byColor);
}

main();
