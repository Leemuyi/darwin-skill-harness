#!/usr/bin/env node
/**
 * Darwin Skill - cross-platform high-resolution screenshot helper
 *
 * Usage: node scripts/screenshot.mjs [html-file] [output-png] [--open]
 *
 * Features:
 * - Resolves Playwright from the project/local/global Node module path instead of
 *   a user-specific absolute path.
 * - Works on macOS, Linux and Windows file URL/path handling.
 * - Captures only the .card element at 2x deviceScaleFactor.
 * - Opens the generated image only when --open is passed.
 */

import { createRequire } from 'module';
import { existsSync } from 'fs';
import { resolve } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { spawn } from 'child_process';

const require = createRequire(import.meta.url);

function resolvePath(input, fallbackUrl) {
  return resolve(input || fileURLToPath(fallbackUrl));
}

async function loadPlaywright() {
  const candidates = ['playwright', 'playwright-core'];

  for (const name of candidates) {
    try {
      return await import(name);
    } catch {
      // ESM package import failed; try CommonJS resolution below.
    }

    try {
      return require(name);
    } catch {
      // Keep looking.
    }
  }

  throw new Error(
    'Playwright is not installed. Install it with `npm install -D playwright`, ' +
    '`npm install -D playwright-core`, or run through an environment that provides Playwright.'
  );
}

function openImageIfRequested(outputPath) {
  if (!process.argv.includes('--open')) return;

  const opener = process.platform === 'darwin'
    ? 'open'
    : process.platform === 'win32'
      ? 'cmd'
      : 'xdg-open';
  const args = process.platform === 'win32'
    ? ['/c', 'start', '', outputPath]
    : [outputPath];

  const child = spawn(opener, args, { stdio: 'ignore', detached: true });
  child.on('error', (err) => {
    console.warn(`Unable to open image automatically: ${err.message}`);
  });
  child.unref();
}

const htmlPath = resolvePath(process.argv[2], new URL('../templates/result-card.html', import.meta.url));
const outputPath = resolvePath(process.argv[3], new URL('../templates/result-card.png', import.meta.url));

async function screenshot() {
  if (!existsSync(htmlPath)) {
    throw new Error(`HTML file does not exist: ${htmlPath}`);
  }

  const pw = await loadPlaywright();
  const browser = await pw.chromium.launch();

  try {
    const context = await browser.newContext({
      viewport: { width: 920, height: 1600 },
      deviceScaleFactor: 2,
    });

    const page = await context.newPage();
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });

    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(2000);

    const card = page.locator('.card').first();
    await card.waitFor({ state: 'visible', timeout: 5000 });
    await card.screenshot({
      path: outputPath,
      type: 'png',
    });

    const box = await card.boundingBox();
    if (box) {
      console.log(`Card size: ${Math.round(box.width)}x${Math.round(box.height)}px (CSS)`);
      console.log(`Output size: ${Math.round(box.width * 2)}x${Math.round(box.height * 2)}px (2x)`);
    }
    console.log(`Screenshot saved: ${outputPath}`);
  } finally {
    await browser.close();
  }

  openImageIfRequested(outputPath);
}

screenshot().catch((err) => {
  console.error('Screenshot failed:', err.message);
  process.exit(1);
});
