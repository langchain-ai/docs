#!/usr/bin/env node
/**
 * Link checker using Playwright (headless browser).
 * Crawls docs.langchain.com, extracts links after DOMContentLoaded (avoids networkidle
 * timeouts on pages with long-lived requests), and verifies each link. Internal hash
 * links wait for heading ids after client render and try slug variants (Unicode quotes,
 * @ and / in headings).
 *
 * Usage:
 *   node check.js [options] [startUrl]
 *
 * Options:
 *   --max-pages=N    Max pages to crawl (default: 500)
 *   --timeout=N      Request timeout in ms (default: 15000)
 *   --concurrency=N  Concurrent link checks (default: 8)
 *
 * Example:
 *   node check.js https://docs.langchain.com/
 *   node check.js --max-pages=100
 *
 * Output: report (summary, broken links) goes to stdout; crawl/verify progress uses stderr.
 *   node check.js > report.txt   # captures the full report; progress still prints to terminal
 */

import { chromium } from 'playwright';

const BASE_URL = 'https://docs.langchain.com';
const DEFAULT_MAX_PAGES = 10000;
const DEFAULT_TIMEOUT = 15000;
const DEFAULT_CONCURRENCY = 8;

/** Matches real Chromium enough that many sites do not return 403 to programmatic checks. */
const BROWSER_LIKE_UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 LangChain-Docs-Link-Check/1.0';

// URLs matching these patterns are skipped (regex or substring)
const SKIP_PATTERNS = [
  'academy.langchain.com',
  'fonts.googleapis.com',
  'fonts.gstatic.com',
  'mintcdn.com',
  'mintlify-assets',
  'platform.openai.com/account/api-keys',
  'mcp.apify.com',
  'github.com',
];

// Parse args
const args = process.argv.slice(2);
let startUrl = BASE_URL + '/';
let maxPages = DEFAULT_MAX_PAGES;
let timeout = DEFAULT_TIMEOUT;
let concurrency = DEFAULT_CONCURRENCY;

for (const arg of args) {
  if (arg.startsWith('--max-pages=')) maxPages = parseInt(arg.split('=')[1], 10);
  else if (arg.startsWith('--timeout=')) timeout = parseInt(arg.split('=')[1], 10);
  else if (arg.startsWith('--concurrency=')) concurrency = parseInt(arg.split('=')[1], 10);
  else if (!arg.startsWith('--')) startUrl = arg;
}

const startOrigin = new URL(startUrl).origin;

/** Whether to skip checking this URL. */
function shouldSkip(url) {
  return SKIP_PATTERNS.some((p) => url.includes(p));
}

/** Normalize href to absolute URL. */
function resolveUrl(href, baseUrl) {
  if (!href || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) return null;
  try {
    return new URL(href, baseUrl).href;
  } catch {
    return null;
  }
}

/** Check if URL is same-origin (docs to crawl). */
function isInternal(url) {
  try {
    return new URL(url).origin === startOrigin;
  } catch {
    return false;
  }
}

/** Check if URL has a fragment. */
function hasFragment(url) {
  try {
    return new URL(url).hash.length > 1;
  } catch {
    return false;
  }
}

/**
 * Get fragment ID (without #), decoded for DOM lookup.
 * Node's URL.hash leaves percent-encoding intact; browsers decode when matching
 * document.getElementById to id="..." from HTML, so we must decode here too.
 */
function getFragment(url) {
  try {
    const hash = new URL(url).hash;
    if (!hash || hash.length <= 1) return null;
    const raw = hash.slice(1);
    try {
      return decodeURIComponent(raw);
    } catch {
      return raw;
    }
  } catch {
    return null;
  }
}

/** Get URL without fragment. */
function urlWithoutFragment(url) {
  try {
    const u = new URL(url);
    u.hash = '';
    return u.href;
  } catch {
    return url;
  }
}

/**
 * Mintlify heading ids and in-doc hash links sometimes differ (Unicode apostrophes,
 * @ and / in headings). Try several candidates after hydration.
 */
function fragmentIdCandidates(frag) {
  if (!frag) return [];
  const candidates = [];
  const seen = new Set();
  const add = (s) => {
    if (s == null || s === '' || seen.has(s)) return;
    seen.add(s);
    candidates.push(s);
  };
  add(frag);
  try {
    add(frag.normalize('NFC'));
    add(frag.normalize('NFD'));
  } catch (_e) {
    // Invalid Unicode for normalization; skip variants.
  }
  const asciiTypography = frag
    .replace(/[\u2018\u2019\u201A\u201B\u2032\u2035]/g, "'")
    .replace(/[\u201C\u201D\u201E]/g, '"');
  add(asciiTypography);
  if (frag.includes("'")) {
    add(frag.replace(/'/g, '\u2019'));
    add(frag.replace(/'/g, '\u2018'));
  }
  if (frag.includes('"')) {
    add(frag.replace(/"/g, '\u201C'));
    add(frag.replace(/"/g, '\u201D'));
  }
  const noSmartQuotes = frag.replace(/[\u2018\u2019\u201A\u201B\u2032\u2035`']/g, '');
  add(noSmartQuotes);
  add(noSmartQuotes.replace(/-+/g, '-').replace(/^-|-$/g, ''));
  const slugGuess = frag
    .replace(/@/g, '')
    .replace(/\//g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
  add(slugGuess);
  if (frag.includes('/')) {
    add(frag.replace(/\//g, ''));
    add(frag.replace(/\//g, '-'));
  }
  return candidates;
}

/**
 * Runs in the browser (serialized by Playwright). Treats :target, exact id match, and
 * NFC + curly-to-ASCII quote folding so link hashes match Mintlify heading ids.
 */
function internalFragmentExistsInDocument(idList) {
  if (document.querySelector(':target')) return true;
  for (let i = 0; i < idList.length; i++) {
    const id = idList[i];
    if (id && document.getElementById(id)) return true;
  }
  const fold = (s) => {
    try {
      return s
        .normalize('NFC')
        .replace(/[\u2018\u2019\u201A\u201B\u2032\u2035`]/g, "'")
        .replace(/[\u201C\u201D\u201E]/g, '"');
    } catch {
      return s;
    }
  };
  const wantFolded = new Set();
  for (let i = 0; i < idList.length; i++) {
    const id = idList[i];
    if (id) wantFolded.add(fold(id));
  }
  const els = document.querySelectorAll('[id]');
  for (let i = 0; i < els.length; i++) {
    const hid = els[i].getAttribute('id');
    if (hid != null && wantFolded.has(fold(hid))) return true;
  }
  return false;
}

async function main() {
  const toCrawl = [startUrl];
  const visited = new Set();
  const linksToCheck = new Map(); // url -> { sourcePage, hasFragment }
  const checked = new Map();     // url -> { ok, status?, error? }
  const broken = [];

  console.log(`Crawling ${startUrl} (max ${maxPages} pages, timeout ${timeout}ms)...\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: BROWSER_LIKE_UA,
    ignoreHTTPSErrors: true,
  });

  const request = context.request;

  try {
    // Phase 1: Crawl and collect links
    while (toCrawl.length > 0 && visited.size < maxPages) {
      const url = toCrawl.shift();
      if (visited.has(url)) continue;
      visited.add(url);

      process.stderr.write(`\rCrawled ${visited.size} pages, found ${linksToCheck.size} links...`);

      const page = await context.newPage();
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout });
        const base = page.url();

        const hrefs = await page.$$eval('a[href]', (anchors) =>
          anchors.map((a) => a.getAttribute('href')).filter(Boolean)
        );

        for (const href of hrefs) {
          const resolved = resolveUrl(href, base);
          if (!resolved || shouldSkip(resolved)) continue;

          if (!linksToCheck.has(resolved)) {
            linksToCheck.set(resolved, { sourcePage: url, hasFragment: hasFragment(resolved) });
          }

          if (isInternal(resolved)) {
            const withoutHash = urlWithoutFragment(resolved);
            if (!visited.has(withoutHash) && !toCrawl.includes(withoutHash)) {
              toCrawl.push(withoutHash);
            }
          }
        }
      } catch (err) {
        console.log(`\nFailed to load ${url}: ${err.message}`);
      } finally {
        await page.close();
      }
    }

    process.stderr.write(`\rCrawled ${visited.size} pages, found ${linksToCheck.size} links. Verifying...\n\n`);

    // Phase 2: Verify each link (batched for concurrency)
    const urls = [...linksToCheck.keys()];
    const results = [];

    async function checkOne(url) {
      const { hasFragment: hasFrag } = linksToCheck.get(url);
      const frag = hasFrag ? getFragment(url) : null;

      if (isInternal(url) && hasFrag) {
        const page = await context.newPage();
        try {
          // Navigate with hash so the browser resolves the fragment; Mintlify/Next may
          // stream body after DOMContentLoaded, so use `load` and the full timeout window.
          await page.goto(url, { waitUntil: 'load', timeout });
          const ids = fragmentIdCandidates(frag);
          const fragWait = Math.max(2000, timeout);
          await page.waitForFunction(internalFragmentExistsInDocument, ids, { timeout: fragWait }).catch(() => {});
          const exists = await page.evaluate(internalFragmentExistsInDocument, ids);
          await page.close();
          return { url, ok: exists, status: exists ? 200 : null, error: exists ? null : 'Fragment not found' };
        } catch (err) {
          await page.close();
          return { url, ok: false, status: null, error: err.message };
        }
      }

      try {
        const response = await request.get(url, { timeout });
        const ok = response.ok();
        return { url, ok, status: response.status(), error: ok ? null : `HTTP ${response.status()}` };
      } catch (err) {
        return { url, ok: false, status: null, error: err.message };
      }
    }

    for (let i = 0; i < urls.length; i += concurrency) {
      const batch = urls.slice(i, i + concurrency);
      const batchResults = await Promise.all(batch.map(checkOne));
      results.push(...batchResults);
      for (const r of batchResults) {
        if (!r.ok) {
          const { sourcePage } = linksToCheck.get(r.url) || {};
          broken.push({ url: r.url, error: r.error, status: r.status, sourcePage });
          console.log(`❌ ${r.url}`);
          console.log(`   ${r.error}${sourcePage ? ` (from ${sourcePage})` : ''}`);
        }
      }
      process.stderr.write(`\rVerified ${Math.min(i + concurrency, urls.length)}/${urls.length} links (${broken.length} broken)...`);
    }
  } finally {
    await browser.close();
  }

  // Summary
  const total = linksToCheck.size;
  const okCount = total - broken.length;
  console.log(`\n${total} links checked: ${okCount} OK, ${broken.length} broken`);

  if (broken.length > 0) {
    // stdout so `node check.js > report.txt` captures the full report (stderr is progress only)
    console.log('\n--- Broken links (URL → source page) ---');
    for (const b of broken) {
      console.log(b.url);
      console.log(`  source: ${b.sourcePage ?? '(unknown)'}`);
      console.log(`  ${b.error}${b.status != null ? ` (${b.status})` : ''}`);
    }
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
