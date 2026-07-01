/**
 * Language Toggle Script
 *
 * Enables smart navigation when switching between Python and TypeScript docs.
 * When a user picks the other language from the dropdown, this redirects them to
 * the equivalent page (preserving the section hash) instead of the default
 * overview/landing page for that language.
 *
 * Notes on the implementation:
 * - Mintlify auto-injects every .js file in the repo as custom JS, so this runs
 *   on every page without a <script> tag in docs.json.
 * - Switching the language dropdown can trigger a full page reload, which wipes
 *   in-memory state. The "page we came from" is therefore persisted in
 *   sessionStorage so it survives the navigation.
 * - The dropdown items render as `<p class="nav-dropdown-item-title">Python</p>`
 *   inside `nav-dropdown-item-*` containers.
 */

(function () {
  "use strict";

  const PYTHON_PREFIX = "/oss/python/";
  const JS_PREFIX = "/oss/javascript/";

  // sessionStorage key holding the last language-specific page (path + hash).
  const STORAGE_KEY = "lc-language-toggle-prev";

  // Matches any part of a language dropdown item (icon, text, or title).
  const LANGUAGE_TOGGLE_SELECTOR = '[class*="nav-dropdown-item"]';

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
   * e.g., /oss/javascript/foo → /oss/python/foo
   */
  function getEquivalentPath(sourcePath, targetLang) {
    const sourcePrefix = targetLang === "python" ? JS_PREFIX : PYTHON_PREFIX;
    const targetPrefix = targetLang === "python" ? PYTHON_PREFIX : JS_PREFIX;

    if (sourcePath.startsWith(sourcePrefix)) {
      return targetPrefix + sourcePath.substring(sourcePrefix.length);
    }
    return null;
  }

  function readPrevious() {
    try {
      return sessionStorage.getItem(STORAGE_KEY);
    } catch (e) {
      // sessionStorage can throw in private-mode Safari; degrade gracefully.
      return null;
    }
  }

  function writePrevious(value) {
    try {
      sessionStorage.setItem(STORAGE_KEY, value);
    } catch (e) {
      /* ignore */
    }
  }

  /**
   * Persist the current page (path + hash) when it is a language-specific page.
   * Stored so a later language switch can find its equivalent, even across a
   * full page reload.
   */
  function storeCurrent() {
    if (getPathLanguage(location.pathname)) {
      writePrevious(location.pathname + location.hash);
    }
  }

  /**
   * If we just landed on a language page whose language differs from the stored
   * page, redirect to the equivalent page in the current language.
   */
  function checkRedirect() {
    const currentLang = getPathLanguage(location.pathname);
    if (!currentLang) return;

    const previous = readPrevious();
    if (!previous) {
      storeCurrent();
      return;
    }

    // Split path and hash (e.g. "/oss/python/foo#bar" → "/oss/python/foo", "bar")
    const hashIndex = previous.indexOf("#");
    const prevPath = hashIndex === -1 ? previous : previous.slice(0, hashIndex);
    const prevHash = hashIndex === -1 ? "" : previous.slice(hashIndex + 1);
    const prevLang = getPathLanguage(prevPath);

    // Only redirect if we are switching between languages.
    if (prevLang && prevLang !== currentLang) {
      const equivalentPath = getEquivalentPath(prevPath, currentLang);

      if (equivalentPath && equivalentPath !== location.pathname) {
        const target = equivalentPath + (prevHash ? "#" + prevHash : "");
        // Store the destination first so the post-redirect load does not loop.
        writePrevious(target);
        location.replace(target);
        return;
      }
    }

    // No redirect needed: remember the current page for the next switch.
    storeCurrent();
  }

  // Capture the page we are leaving the instant a language dropdown item is
  // clicked, before Mintlify navigates (which may be a full page reload).
  document.addEventListener(
    "click",
    function (e) {
      if (e.target.closest && e.target.closest(LANGUAGE_TOGGLE_SELECTOR)) {
        storeCurrent();
      }
    },
    true,
  );

  // Watch for URL changes from Mintlify's client-side routing.
  let lastPath = location.pathname;

  function onPathChange() {
    if (location.pathname !== lastPath) {
      lastPath = location.pathname;
      checkRedirect();
    }
  }

  // Handle back/forward navigation.
  window.addEventListener("popstate", onPathChange);

  // Keep the stored hash fresh as the reader scrolls through sections.
  window.addEventListener("hashchange", function () {
    storeCurrent();
    onPathChange();
  });

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

  // Run an initial check in case the reader arrived here via a language switch.
  checkRedirect();
})();
