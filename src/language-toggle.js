/**
 * Language Toggle Script
 *
 * Enables smart navigation when switching between Python and TypeScript docs.
 * When a reader picks the other language from the dropdown, this redirects them
 * to the equivalent page (preserving the section hash) instead of the default
 * overview/landing page for that language.
 *
 * Why this is needed:
 * - Both language options in the switcher link to the same, language-agnostic
 *   landing page (e.g. /build-overview), so the target language cannot be read
 *   from the destination URL. It is read from the clicked item's label instead.
 * - Switching languages can trigger a full page reload, so the intended switch
 *   is persisted in sessionStorage to survive the navigation.
 *
 * Mintlify auto-injects every .js file in the repo as custom JS, so this runs on
 * every page without needing a <script> tag in docs.json. The dropdown items
 * render as `<p class="nav-dropdown-item-title">Python</p>` inside
 * `nav-dropdown-item-*` containers.
 */

(function () {
  "use strict";

  const PYTHON_PREFIX = "/oss/python/";
  const JS_PREFIX = "/oss/javascript/";

  // sessionStorage key holding a pending language switch (survives a reload).
  const PENDING_KEY = "lc-language-toggle-pending";

  // A pending switch older than this (ms) is ignored, so a stored record can
  // never trigger a stray redirect on some later, unrelated navigation.
  const PENDING_TTL_MS = 8000;

  /**
   * Detect which language a path belongs to.
   * Returns "python", "javascript", or null.
   */
  function getPathLanguage(path) {
    if (path.startsWith(PYTHON_PREFIX)) return "python";
    if (path.startsWith(JS_PREFIX)) return "javascript";
    return null;
  }

  /**
   * Convert a path from one language to another.
   * e.g., getEquivalentPath("/oss/python/foo", "javascript") → "/oss/javascript/foo"
   */
  function getEquivalentPath(sourcePath, targetLang) {
    const sourcePrefix = targetLang === "python" ? JS_PREFIX : PYTHON_PREFIX;
    const targetPrefix = targetLang === "python" ? PYTHON_PREFIX : JS_PREFIX;

    if (sourcePath.startsWith(sourcePrefix)) {
      return targetPrefix + sourcePath.substring(sourcePrefix.length);
    }
    return null;
  }

  /**
   * Map a dropdown item label to a language, or null if it is not a language
   * item. The docs use "Python" and "TypeScript" as the dropdown labels.
   */
  function labelToLanguage(text) {
    const label = (text || "").trim().toLowerCase();
    if (label === "python") return "python";
    if (label === "typescript" || label === "javascript") return "javascript";
    return null;
  }

  /**
   * Given the clicked element, find the language a dropdown item would switch
   * to, tolerating clicks on the item's icon, text container, or title.
   */
  function clickTargetLanguage(startEl) {
    for (let node = startEl, depth = 0; node && depth < 5; node = node.parentElement, depth++) {
      if (!node.classList) continue;

      let titleEl = null;
      if (node.classList.contains("nav-dropdown-item-title")) {
        titleEl = node;
      } else if (node.querySelector) {
        titleEl = node.querySelector(".nav-dropdown-item-title");
      }

      if (titleEl) {
        return labelToLanguage(titleEl.textContent);
      }
    }
    return null;
  }

  function readPending() {
    try {
      return sessionStorage.getItem(PENDING_KEY);
    } catch (e) {
      // sessionStorage can throw in private-mode Safari; degrade gracefully.
      return null;
    }
  }

  function writePending(value) {
    try {
      sessionStorage.setItem(PENDING_KEY, value);
    } catch (e) {
      /* ignore */
    }
  }

  function clearPending() {
    try {
      sessionStorage.removeItem(PENDING_KEY);
    } catch (e) {
      /* ignore */
    }
  }

  /**
   * If a fresh language switch is pending, redirect to the equivalent of the
   * page it started from, in the newly selected language. Consumed once.
   * Returns true if a redirect was triggered.
   */
  function applyPendingSwitch() {
    const raw = readPending();
    if (!raw) return false;

    // Consume once: a switch is acted on at most a single time.
    clearPending();

    let pending;
    try {
      pending = JSON.parse(raw);
    } catch (e) {
      return false;
    }

    if (
      !pending ||
      !pending.src ||
      !pending.lang ||
      typeof pending.ts !== "number" ||
      Date.now() - pending.ts > PENDING_TTL_MS
    ) {
      return false;
    }

    // Split the source into path and hash.
    const hashIndex = pending.src.indexOf("#");
    const srcPath = hashIndex === -1 ? pending.src : pending.src.slice(0, hashIndex);
    const srcHash = hashIndex === -1 ? "" : pending.src.slice(hashIndex);

    const srcLang = getPathLanguage(srcPath);
    // A shared, language-agnostic source page (e.g. /build-overview) has no
    // per-language equivalent to preserve.
    if (!srcLang || srcLang === pending.lang) return false;

    const equivalent = getEquivalentPath(srcPath, pending.lang);
    if (!equivalent || equivalent === location.pathname) return false;

    location.replace(equivalent + srcHash);
    return true;
  }

  // Handle a language dropdown click the instant it happens, before Mintlify
  // navigates (the destination URL does not encode the target language, and the
  // navigation may be a full page reload).
  document.addEventListener(
    "click",
    function (e) {
      const targetLang = e.target && clickTargetLanguage(e.target);
      if (!targetLang) return;

      // Record the intended switch as a fallback: this survives a full page
      // reload and is applied on the next load if the fast path below does not
      // run (e.g. the source is the shared, language-agnostic landing page).
      writePending(
        JSON.stringify({
          src: location.pathname + location.hash,
          lang: targetLang,
          ts: Date.now(),
        }),
      );

      // Fast path: if the current page has a resolvable equivalent, go straight
      // there and skip the intermediate landing-page load (avoids a visible
      // flash). The capture-phase listener runs before Mintlify's own click
      // handler, so suppressing propagation prevents its navigation.
      const srcLang = getPathLanguage(location.pathname);
      if (srcLang && srcLang !== targetLang) {
        const equivalent = getEquivalentPath(location.pathname, targetLang);
        if (equivalent && equivalent !== location.pathname) {
          e.preventDefault();
          e.stopImmediatePropagation();
          location.assign(equivalent + location.hash);
        }
      }
    },
    true,
  );

  // Watch for URL changes from Mintlify's client-side routing.
  let lastPath = location.pathname;

  function onPathChange() {
    if (location.pathname !== lastPath) {
      lastPath = location.pathname;
      applyPendingSwitch();
    }
  }

  window.addEventListener("popstate", onPathChange);
  window.addEventListener("hashchange", onPathChange);

  // Intercept History API calls used by client-side routing.
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  history.pushState = function () {
    originalPushState.apply(this, arguments);
    onPathChange();
  };

  history.replaceState = function () {
    originalReplaceState.apply(this, arguments);
    onPathChange();
  };

  // Handle the full-page-reload case: apply any pending switch on initial load.
  applyPendingSwitch();
})();
