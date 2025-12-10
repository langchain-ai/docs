/**
 * Language Toggle Script
 *
 * Enables smart navigation when switching between Python and TypeScript docs.
 * When a user clicks the language dropdown, this redirects them to the equivalent
 * page in the target language (preserving the section hash) instead of the default
 * overview page.
 *
 * How it works:
 * 1. Click listener detects language toggle clicks and stores current URL+hash
 * 2. MutationObserver detects when Mintlify's client-side routing changes the path
 * 3. On path change, check if we're switching languages and redirect to equivalent page
 */

(function () {
    "use strict";

    const STORAGE_KEY = "langchain_docs_prev_url";
    const PYTHON_PREFIX = "/oss/python/";
    const JS_PREFIX = "/oss/javascript/";

    // Selector for language dropdown items (Python/TypeScript links)
    const LANGUAGE_TOGGLE_SELECTOR = '[data-dropdown-item]';

    /**
     * Convert a path from one language to another
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

    /**
     * Detect which language a path belongs to
     * Returns "python", "javascript", or null
     */
    function getPathLanguage(path) {
      if (path.startsWith(PYTHON_PREFIX)) return "python";
      if (path.startsWith(JS_PREFIX)) return "javascript";
      return null;
    }

    /**
     * Store current URL (path + hash) in session storage
     * Only stores language-specific pages
     */
    function storeCurrent() {
      const lang = getPathLanguage(location.pathname);
      if (lang) {
        try {
          sessionStorage.setItem(STORAGE_KEY, location.pathname + location.hash);
        } catch (e) {}
      }
    }

    /**
     * Check if we should redirect to an equivalent page in a different language
     * This runs after every path change detected by the MutationObserver
     */
    function checkRedirect() {
      const currentLang = getPathLanguage(location.pathname);
      if (!currentLang) return;

      // Get the previous URL we stored
      let previousUrl;
      try {
        previousUrl = sessionStorage.getItem(STORAGE_KEY);
      } catch (e) {
        storeCurrent();
        return;
      }

      if (!previousUrl) {
        storeCurrent();
        return;
      }

      // Split path and hash (e.g., "/oss/python/foo#bar" → ["/oss/python/foo", "bar"])
      const [prevPath, prevHash = ""] = previousUrl.split("#");
      const prevLang = getPathLanguage(prevPath);

      // Only redirect if we're switching between languages
      if (prevLang && prevLang !== currentLang) {
        const equivalentPath = getEquivalentPath(prevPath, currentLang);

        if (equivalentPath && equivalentPath !== location.pathname) {
          // Clear storage before redirect to prevent redirect loops
          try {
            sessionStorage.removeItem(STORAGE_KEY);
          } catch (e) {}

          // Redirect with the hash from the previous page
          location.replace(equivalentPath + (prevHash ? "#" + prevHash : ""));
          return;
        }
      }

      // If no redirect needed, store current location for next navigation
      storeCurrent();
    }

    // Store current URL when language toggle is clicked
    // This captures the hash before Mintlify's client-side routing changes the page
    document.addEventListener("click", function (e) {
      const toggle = e.target.closest(LANGUAGE_TOGGLE_SELECTOR);
      if (toggle) {
        storeCurrent();
      }
    }, true);

    // Watch for URL changes via Mintlify's client-side routing
    // MutationObserver is necessary because Mintlify changes the URL without full page reloads
    let lastPath = location.pathname;

    const observer = new MutationObserver(() => {
      if (location.pathname !== lastPath) {
        lastPath = location.pathname;
        checkRedirect();
      }
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    // Run initial check in case user landed here via language toggle
    checkRedirect();
  })();
