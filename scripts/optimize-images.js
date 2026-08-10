const fs = require('fs').promises;
const path = require('path');

async function ensureDir(dir) {
  try { await fs.mkdir(dir, { recursive: true }); } catch (e) {}
}

async function optimizeImage(filePath) {
  const sharp = require('sharp');
  const ext = path.extname(filePath);
  const basename = path.basename(filePath, ext);
  const outDir = path.join(path.dirname(filePath), 'optimized');
  await ensureDir(outDir);
  const sizes = [800, 1200];

  for (const w of sizes) {
    const outJpeg = path.join(outDir, `${basename}-${w}.jpg`);
    const outWebp = path.join(outDir, `${basename}-${w}.webp`);
    try {
      await sharp(filePath)
        .rotate()
        .resize({ width: w, withoutEnlargement: true })
        .jpeg({ quality: 70, mozjpeg: true })
        .toFile(outJpeg);
      await sharp(filePath)
        .rotate()
        .resize({ width: w, withoutEnlargement: true })
        .webp({ quality: 70 })
        .toFile(outWebp);
      console.log('wrote', outJpeg, outWebp);
    } catch (err) {
      console.error('failed optimizing', filePath, err.message);
    }
  }
}

async function collectImageFiles(rootDir) {
  const entries = await fs.readdir(rootDir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'optimized' || entry.name === 'node_modules') continue;
      files.push(...await collectImageFiles(fullPath));
    } else if (entry.isFile()) {
      const lower = entry.name.toLowerCase();
      if (['.jpg', '.jpeg', '.png', '.webp'].some(ext => lower.endsWith(ext))) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

async function main() {
  const roots = [
    path.join(__dirname, '..', 'archive', 'unsorted'),
    path.join(__dirname, '..', 'portfolio'),
    path.join(__dirname, '..', 'public', 'external')
  ];

  for (const srcDir of roots) {
    const imageFiles = await collectImageFiles(srcDir);
    for (const full of imageFiles) {
      await optimizeImage(full);
    }
  }

  console.log('done');
}

main().catch(err => {
  console.error(err);
  process.exitCode = 1;
});
