/**
 * compareCard.mjs - Compare rendered MTG card against reference images
 *
 * Usage:
 *   node scripts/compareCard.mjs [--rendered <path>] [--ref <path>] [--threshold <0-1>]
 *                                 [--ignore-art] [--ignore-text] [--output <dir>]
 *
 * Prerequisites:
 *   1. Screenshot your rendered card at 672x936 and save as rendered.png
 *      (use the render.html page + browser screenshot)
 *   2. Have reference images in public/reference/
 *
 * Example:
 *   node scripts/compareCard.mjs --rendered compare-output/rendered.png --ref public/reference/goal-mtg.jpg
 */

import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import sharp from 'sharp';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

// ── Parse CLI arguments ─────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    rendered: path.join(ROOT, 'compare-output', 'rendered.png'),
    ref: path.join(ROOT, 'public', 'reference', 'goal-mtg.jpg'),
    output: path.join(ROOT, 'compare-output'),
    threshold: 0.15,
    ignoreArt: false,
    ignoreText: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--rendered': opts.rendered = path.resolve(args[++i]); break;
      case '--ref': opts.ref = path.resolve(args[++i]); break;
      case '--output': opts.output = path.resolve(args[++i]); break;
      case '--threshold': opts.threshold = parseFloat(args[++i]); break;
      case '--ignore-art': opts.ignoreArt = true; break;
      case '--ignore-text': opts.ignoreText = true; break;
    }
  }
  return opts;
}

// ── Card element regions (at 672x936) ──────────────────────────────
const REGIONS = {
  card:    { x: 0,   y: 0,   w: 672, h: 936 },
  border:  { x: 0,   y: 0,   w: 672, h: 936 },
  frame:   { x: 27,  y: 27,  w: 618, h: 860 },
  title:   { x: 49,  y: 45,  w: 575, h: 54 },
  art:     { x: 50,  y: 104, w: 572, h: 417 },
  type:    { x: 49,  y: 526, w: 573, h: 54 },
  text:    { x: 49,  y: 585, w: 573, h: 284 },
  pt:      { x: 543, y: 837, w: 102, h: 48 },
};

// ── Load image as 672x936 RGBA PNG ──────────────────────────────────
async function loadImage(filePath, targetW = 672, targetH = 936) {
  const ext = path.extname(filePath).toLowerCase();

  // Use sharp to read any format and resize to target dimensions
  const buffer = await sharp(filePath)
    .resize(targetW, targetH, { fit: 'fill' })
    .ensureAlpha()
    .raw()
    .toBuffer();

  const png = new PNG({ width: targetW, height: targetH });
  png.data = buffer;
  return png;
}

// ── Create a mask for regions to ignore ─────────────────────────────
function createMask(width, height, ignoreRegions) {
  // Returns Uint8Array where 0 = compare, 255 = ignore
  const mask = new Uint8Array(width * height);
  for (const region of ignoreRegions) {
    for (let y = region.y; y < Math.min(region.y + region.h, height); y++) {
      for (let x = region.x; x < Math.min(region.x + region.w, width); x++) {
        mask[y * width + x] = 255;
      }
    }
  }
  return mask;
}

// ── Compute per-region stats ────────────────────────────────────────
function regionStats(img1, img2, region, threshold) {
  const { x: rx, y: ry, w: rw, h: rh } = region;
  let totalDiff = 0;
  let pixelCount = 0;
  let mismatchCount = 0;

  for (let y = ry; y < Math.min(ry + rh, 936); y++) {
    for (let x = rx; x < Math.min(rx + rw, 672); x++) {
      const idx = (y * 672 + x) * 4;
      const dr = Math.abs(img1.data[idx] - img2.data[idx]);
      const dg = Math.abs(img1.data[idx + 1] - img2.data[idx + 1]);
      const db = Math.abs(img1.data[idx + 2] - img2.data[idx + 2]);
      const diff = (dr + dg + db) / 3;

      totalDiff += diff;
      pixelCount++;
      if (diff > threshold * 255) mismatchCount++;
    }
  }

  const avgDiff = pixelCount > 0 ? totalDiff / pixelCount : 0;
  const matchPct = pixelCount > 0
    ? ((pixelCount - mismatchCount) / pixelCount * 100).toFixed(1)
    : '100.0';

  return { avgDiff: avgDiff.toFixed(2), matchPct, mismatchCount, pixelCount };
}

// ── Create annotated composite image ────────────────────────────────
async function createComposite(refPath, renderedPath, diffPath, outputPath) {
  const W = 672;
  const H = 936;
  const GAP = 20;
  const LABEL_H = 40;
  const totalW = W * 3 + GAP * 2;
  const totalH = H + LABEL_H;

  // Create composite with sharp
  const refBuf = await sharp(refPath).resize(W, H).toBuffer();
  const rendBuf = await sharp(renderedPath).resize(W, H).toBuffer();
  const diffBuf = await sharp(diffPath).resize(W, H).toBuffer();

  await sharp({
    create: {
      width: totalW,
      height: totalH,
      channels: 3,
      background: { r: 40, g: 40, b: 40 },
    },
  })
    .composite([
      { input: refBuf, left: 0, top: LABEL_H },
      { input: rendBuf, left: W + GAP, top: LABEL_H },
      { input: diffBuf, left: (W + GAP) * 2, top: LABEL_H },
    ])
    .jpeg({ quality: 95 })
    .toFile(outputPath);
}

// ── MAIN ────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();
  console.log('\n🃏 MTG Card Comparison Tool');
  console.log('═'.repeat(50));
  console.log(`  Rendered: ${opts.rendered}`);
  console.log(`  Reference: ${opts.ref}`);
  console.log(`  Threshold: ${opts.threshold}`);
  console.log(`  Ignore art: ${opts.ignoreArt}`);
  console.log(`  Ignore text: ${opts.ignoreText}`);
  console.log('');

  // Ensure output dir
  fs.mkdirSync(opts.output, { recursive: true });

  // Check files exist
  if (!fs.existsSync(opts.rendered)) {
    console.error(`❌ Rendered image not found: ${opts.rendered}`);
    console.log('\nTo create a rendered image:');
    console.log('  1. Run: npm run dev');
    console.log('  2. Open: http://localhost:5173/render.html?card=CardName');
    console.log('  3. Screenshot the card at 672x936');
    console.log('  4. Save to compare-output/rendered.png');
    process.exit(1);
  }
  if (!fs.existsSync(opts.ref)) {
    console.error(`❌ Reference image not found: ${opts.ref}`);
    process.exit(1);
  }

  // Load both images at 672x936
  console.log('Loading images...');
  const rendered = await loadImage(opts.rendered);
  const reference = await loadImage(opts.ref);

  // Build ignore regions
  const ignoreRegions = [];
  if (opts.ignoreArt) ignoreRegions.push(REGIONS.art);
  if (opts.ignoreText) ignoreRegions.push(REGIONS.text);

  // If ignoring regions, zero out those pixels in both images for diff
  if (ignoreRegions.length > 0) {
    const mask = createMask(672, 936, ignoreRegions);
    for (let i = 0; i < mask.length; i++) {
      if (mask[i] === 255) {
        const idx = i * 4;
        // Set both to same color so diff shows no mismatch
        rendered.data[idx] = reference.data[idx] = 128;
        rendered.data[idx + 1] = reference.data[idx + 1] = 128;
        rendered.data[idx + 2] = reference.data[idx + 2] = 128;
        rendered.data[idx + 3] = reference.data[idx + 3] = 255;
      }
    }
  }

  // Run pixelmatch
  console.log('Running pixel comparison...');
  const diff = new PNG({ width: 672, height: 936 });
  const mismatchPixels = pixelmatch(
    rendered.data,
    reference.data,
    diff.data,
    672,
    936,
    {
      threshold: opts.threshold,
      alpha: 0.1,
      diffColor: [255, 50, 50],
      diffColorAlt: [50, 50, 255],
    }
  );

  const totalPixels = 672 * 936;
  const matchPct = ((totalPixels - mismatchPixels) / totalPixels * 100).toFixed(2);

  // Save diff image
  const diffPath = path.join(opts.output, 'diff.png');
  const diffBuffer = PNG.sync.write(diff);
  fs.writeFileSync(diffPath, diffBuffer);
  console.log(`  Saved diff: ${diffPath}`);

  // Save normalized reference
  const refNormPath = path.join(opts.output, 'reference.png');
  await sharp(opts.ref).resize(672, 936, { fit: 'fill' }).toFile(refNormPath);

  // Per-region analysis (reload originals for unmasked analysis)
  console.log('\n📊 Overall Results');
  console.log('─'.repeat(50));
  console.log(`  Total pixels:    ${totalPixels.toLocaleString()}`);
  console.log(`  Mismatched:      ${mismatchPixels.toLocaleString()}`);
  console.log(`  Match:           ${matchPct}%`);

  // Region-by-region analysis (using original unmasked images)
  const origRendered = await loadImage(opts.rendered);
  const origReference = await loadImage(opts.ref);

  console.log('\n📐 Per-Region Analysis');
  console.log('─'.repeat(50));
  for (const [name, region] of Object.entries(REGIONS)) {
    if (name === 'card' || name === 'border') continue;
    if (opts.ignoreArt && name === 'art') {
      console.log(`  ${name.padEnd(10)} [IGNORED]`);
      continue;
    }
    if (opts.ignoreText && name === 'text') {
      console.log(`  ${name.padEnd(10)} [IGNORED]`);
      continue;
    }
    const stats = regionStats(origRendered, origReference, region, opts.threshold);
    const bar = '█'.repeat(Math.round(parseFloat(stats.matchPct) / 5));
    console.log(`  ${name.padEnd(10)} ${stats.matchPct.padStart(6)}% match  avgΔ=${stats.avgDiff.padStart(6)}  ${bar}`);
  }

  // Create composite
  console.log('\nCreating composite image...');
  const compositePath = path.join(opts.output, 'composite.jpg');
  try {
    await createComposite(refNormPath, opts.rendered, diffPath, compositePath);
    console.log(`  Saved composite: ${compositePath}`);
  } catch (e) {
    console.log(`  (composite creation skipped: ${e.message})`);
  }

  // Save stats JSON
  const stats = {
    matchPercent: parseFloat(matchPct),
    mismatchPixels,
    totalPixels,
    threshold: opts.threshold,
    ignoreArt: opts.ignoreArt,
    ignoreText: opts.ignoreText,
    reference: opts.ref,
    rendered: opts.rendered,
    timestamp: new Date().toISOString(),
  };
  fs.writeFileSync(
    path.join(opts.output, 'stats.json'),
    JSON.stringify(stats, null, 2)
  );

  console.log('\n✅ Done! Check compare-output/ for results.');
  console.log('');
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
