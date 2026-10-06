/**
 * Sortable integration download tables
 *
 * Generated snippets wrap markdown tables in
 * `<div class="integration-downloads-table">`. Cells that need numeric or
 * categorical sort expose `<span data-sort-value="...">`. This script makes
 * every header clickable and reorders tbody rows.
 *
 * Download badges (pepy / shields.io) are live images. On enhance, this script
 * fetches each badge SVG, parses the displayed count into data-sort-value, and
 * re-sorts so order matches the badges even when baked-in values have drifted.
 *
 * Mintlify auto-injects every .js file under src/, so this runs site-wide.
 * A MutationObserver re-enhances tables after client-side navigations.
 */

(function () {
  "use strict";

  const WRAPPER = ".integration-downloads-table";
  const ENHANCED = "data-sort-enhanced";
  const BADGE_IMG =
    'img[src*="pepy.tech/badge/"], img[src*="img.shields.io/"]';

  /** @type {Map<string, Promise<number|null>>} */
  const badgeCountCache = new Map();

  function parseAbbreviatedCount(raw) {
    const text = String(raw || "")
      .replace(/\/month/i, "")
      .replace(/,/g, "")
      .trim();
    const match = text.match(/^([\d.]+)\s*([kKmMbB])?$/);
    if (!match) return null;
    const n = Number(match[1]);
    if (Number.isNaN(n)) return null;
    const suffix = (match[2] || "").toLowerCase();
    if (suffix === "k") return Math.round(n * 1e3);
    if (suffix === "m") return Math.round(n * 1e6);
    if (suffix === "b") return Math.round(n * 1e9);
    return Math.round(n);
  }

  function extractCountFromPepySvg(svgText) {
    const texts = Array.from(
      String(svgText).matchAll(/<text[^>]*>([^<]+)<\/text>/g),
    ).map((match) => match[1].trim());
    for (let i = texts.length - 1; i >= 0; i -= 1) {
      if (/downloads/i.test(texts[i])) continue;
      const count = parseAbbreviatedCount(texts[i]);
      if (count !== null) return count;
    }
    return null;
  }

  function extractCountFromShields(svgOrLabel) {
    const text = String(svgOrLabel);
    const labeled =
      text.match(/aria-label="([^"]+)"/i) ||
      text.match(/<title>([^<]+)<\/title>/i);
    const source = labeled ? labeled[1] : text;
    const downloads = source.match(/downloads:\s*(.+)/i);
    if (downloads) return parseAbbreviatedCount(downloads[1]);
    return parseAbbreviatedCount(source);
  }

  function extractBadgeCount(url, body) {
    if (/pepy\.tech/i.test(url)) return extractCountFromPepySvg(body);
    if (/shields\.io/i.test(url)) return extractCountFromShields(body);
    return extractCountFromPepySvg(body) ?? extractCountFromShields(body);
  }

  function fetchBadgeCount(url) {
    if (badgeCountCache.has(url)) return badgeCountCache.get(url);

    const pending = fetch(url, { mode: "cors", credentials: "omit" })
      .then(function (response) {
        if (!response.ok) return null;
        return response.text();
      })
      .then(function (body) {
        if (!body) return null;
        return extractBadgeCount(url, body);
      })
      .catch(function () {
        return null;
      });

    badgeCountCache.set(url, pending);
    return pending;
  }

  function syncDownloadSortValues(table) {
    const images = table.querySelectorAll(BADGE_IMG);
    if (images.length === 0) return Promise.resolve(false);

    const jobs = Array.from(images).map(function (img) {
      const span = img.closest("[data-sort-value]");
      if (!span) return Promise.resolve(false);
      const url = img.currentSrc || img.getAttribute("src") || "";
      if (!url) return Promise.resolve(false);

      return fetchBadgeCount(url).then(function (count) {
        if (count === null) return false;
        const next = String(count);
        if (span.getAttribute("data-sort-value") === next) return false;
        span.setAttribute("data-sort-value", next);
        return true;
      });
    });

    return Promise.all(jobs).then(function (results) {
      return results.some(Boolean);
    });
  }

  function cellSortValue(cell) {
    if (!cell) return { kind: "empty", value: "" };

    const marked = cell.querySelector("[data-sort-value]");
    if (marked) {
      const raw = marked.getAttribute("data-sort-value");
      const asNumber = Number(raw);
      if (raw !== null && raw !== "" && !Number.isNaN(asNumber)) {
        return { kind: "number", value: asNumber };
      }
      return { kind: "string", value: (raw || "").toLowerCase() };
    }

    // Name / link column: prefer link text, fall back to cell text.
    const link = cell.querySelector("a");
    const text = (link ? link.textContent : cell.textContent) || "";
    return { kind: "string", value: text.trim().toLowerCase() };
  }

  function compareValues(a, b, direction) {
    const aMissing = a.kind === "number" && a.value < 0;
    const bMissing = b.kind === "number" && b.value < 0;
    // Keep N/A (-1) at the bottom for either downloads sort direction.
    if (aMissing !== bMissing) return aMissing ? 1 : -1;

    let result = 0;
    if (a.kind === "number" && b.kind === "number") {
      result = a.value - b.value;
    } else {
      result = String(a.value).localeCompare(String(b.value));
    }
    return direction === "asc" ? result : -result;
  }

  function sortTable(table, columnIndex, direction) {
    const tbody = table.tBodies[0];
    if (!tbody) return;

    const rows = Array.from(tbody.rows);
    rows.sort((rowA, rowB) =>
      compareValues(
        cellSortValue(rowA.cells[columnIndex]),
        cellSortValue(rowB.cells[columnIndex]),
        direction,
      ),
    );
    rows.forEach((row) => tbody.appendChild(row));
  }

  function setAriaSort(headers, activeIndex, direction) {
    headers.forEach((th, index) => {
      if (index === activeIndex) {
        th.setAttribute(
          "aria-sort",
          direction === "asc" ? "ascending" : "descending",
        );
      } else {
        th.removeAttribute("aria-sort");
      }
    });
  }

  function enhanceTable(wrapper) {
    const table = wrapper.querySelector("table");
    if (!table || table.getAttribute(ENHANCED) === "true") return;

    const headRow = table.tHead && table.tHead.rows[0];
    if (!headRow || !table.tBodies[0]) return;

    const headers = Array.from(headRow.cells);
    if (headers.length === 0) return;

    table.setAttribute(ENHANCED, "true");

    // Default: Downloads column descending when present, else first column.
    let activeColumn = Math.max(
      0,
      headers.findIndex((th) => /downloads/i.test(th.textContent || "")),
    );
    let direction = "desc";
    setAriaSort(headers, activeColumn, direction);
    sortTable(table, activeColumn, direction);

    // Prefer live badge counts over baked-in data-sort-value.
    syncDownloadSortValues(table).then(function (changed) {
      if (!changed) return;
      if (!/downloads/i.test(headers[activeColumn].textContent || "")) return;
      sortTable(table, activeColumn, direction);
    });

    headers.forEach((th, columnIndex) => {
      th.setAttribute("data-sortable", "true");
      th.setAttribute("tabindex", "0");
      th.setAttribute("role", "columnheader");
      th.title = "Sort by this column";

      const toggle = function (event) {
        // Keep markdown header links navigable.
        if (event.target && event.target.closest && event.target.closest("a")) {
          return;
        }
        event.preventDefault();

        if (activeColumn === columnIndex) {
          direction = direction === "asc" ? "desc" : "asc";
        } else {
          activeColumn = columnIndex;
          // Downloads default to high-first; other columns start ascending.
          direction = /downloads/i.test(th.textContent || "") ? "desc" : "asc";
        }
        setAriaSort(headers, activeColumn, direction);
        sortTable(table, activeColumn, direction);
      };

      th.addEventListener("click", toggle);
      th.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          toggle(event);
        }
      });
    });
  }

  function enhanceAll(root) {
    const scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll(WRAPPER).forEach(enhanceTable);
  }

  function start() {
    enhanceAll(document);

    const observer = new MutationObserver(function (mutations) {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (!node || node.nodeType !== 1) continue;
          if (node.matches && node.matches(WRAPPER)) {
            enhanceTable(node);
          } else if (node.querySelectorAll) {
            enhanceAll(node);
          }
        }
      }
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
