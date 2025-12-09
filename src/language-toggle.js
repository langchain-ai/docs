/**
 * Language Toggle Script
 *
 * Enables smart navigation when switching between Python and TypeScript
 * documentation. When a user clicks the language dropdown to switch languages,
 * this script redirects them to the equivalent page in the target language
 * instead of the default overview page.
 */

(function () {
  "use strict";

  var STORAGE_KEY = "langchain_docs_prev_path";
  var STORAGE_KEY_HASH = "langchain_docs_prev_hash";
  var PYTHON_PREFIX = "/oss/python/";
  var JS_PREFIX = "/oss/javascript/";

  // Overview/landing pages for each tab - these are where the dropdown navigates to
  var LANDING_PAGES = [
    // LangChain tab
    "langchain/overview",
    // LangGraph tab
    "langgraph/overview",
    // Deep Agents tab
    "deepagents/overview",
    // Integrations tab
    "integrations/providers/overview",
    // Learn tab
    "learn",
    // Reference tab
    "reference/overview",
    // Contribute tab
    "contributing/overview",
  ];

  /**
   * Get the equivalent path in the target language
   */
  function getEquivalentPath(sourcePath, targetLang) {
    var sourcePrefix = targetLang === "python" ? JS_PREFIX : PYTHON_PREFIX;
    var targetPrefix = targetLang === "python" ? PYTHON_PREFIX : JS_PREFIX;

    if (sourcePath.startsWith(sourcePrefix)) {
      return targetPrefix + sourcePath.substring(sourcePrefix.length);
    }
    return null;
  }

  /**
   * Check if a path is a landing/overview page (where dropdown navigates to)
   */
  function isLandingPage(path) {
    // Remove trailing slash for comparison
    var normalizedPath = path.replace(/\/$/, "");

    return LANDING_PAGES.some(function (landing) {
      return (
        normalizedPath === PYTHON_PREFIX + landing ||
        normalizedPath === JS_PREFIX + landing ||
        normalizedPath === (PYTHON_PREFIX + landing).replace(/\/$/, "") ||
        normalizedPath === (JS_PREFIX + landing).replace(/\/$/, "")
      );
    });
  }

  /**
   * Detect which language a path belongs to
   */
  function getPathLanguage(path) {
    if (path.startsWith(PYTHON_PREFIX)) return "python";
    if (path.startsWith(JS_PREFIX)) return "javascript";
    return null;
  }

  /**
   * Store current path and hash for later comparison
   */
  function storeCurrentPath() {
    var path = window.location.pathname;
    var hash = window.location.hash;
    // Only store if it's a language-specific page
    if (getPathLanguage(path)) {
      try {
        sessionStorage.setItem(STORAGE_KEY, path);
        sessionStorage.setItem(STORAGE_KEY_HASH, hash || "");
      } catch (e) {
        // sessionStorage not available
      }
    }
  }

  /**
   * Get the previously stored path
   */
  function getPreviousPath() {
    try {
      return sessionStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  /**
   * Get the previously stored hash
   */
  function getPreviousHash() {
    try {
      return sessionStorage.getItem(STORAGE_KEY_HASH) || "";
    } catch (e) {
      return "";
    }
  }

  /**
   * Main logic to check and redirect if needed
   */
  function checkAndRedirect() {
    var currentPath = window.location.pathname;
    var currentLang = getPathLanguage(currentPath);

    // Only proceed if we're on a language-specific page
    if (!currentLang) {
      return;
    }

    // Only redirect if we're on a landing page (indicates dropdown navigation)
    if (!isLandingPage(currentPath)) {
      // We're on a regular page, just store it
      storeCurrentPath();
      return;
    }

    // Check if we have a previous path from the other language
    var previousPath = getPreviousPath();
    if (!previousPath) {
      storeCurrentPath();
      return;
    }

    var previousLang = getPathLanguage(previousPath);

    // Only redirect if we came from the other language
    if (!previousLang || previousLang === currentLang) {
      storeCurrentPath();
      return;
    }

    // Don't redirect if the previous page was also a landing page
    // (user was intentionally navigating between overview pages)
    if (isLandingPage(previousPath)) {
      storeCurrentPath();
      return;
    }

    // Calculate the equivalent page in the new language
    var equivalentPath = getEquivalentPath(previousPath, currentLang);

    if (!equivalentPath || equivalentPath === currentPath) {
      storeCurrentPath();
      return;
    }

    // Get the hash from the previous page to preserve section navigation
    var previousHash = getPreviousHash();

    // Redirect to the equivalent page with the hash if present
    // Clear the stored path to prevent redirect loops
    try {
      sessionStorage.removeItem(STORAGE_KEY);
      sessionStorage.removeItem(STORAGE_KEY_HASH);
    } catch (e) {
      // Ignore
    }

    // Use replace to avoid polluting browser history
    window.location.replace(equivalentPath + previousHash);
  }

  /**
   * Set up event listeners for path tracking
   */
  function setupPathTracking() {
    // Track clicks on links to store path before navigation
    document.addEventListener(
      "click",
      function (event) {
        var link = event.target.closest("a");
        if (link && link.href && link.href.startsWith(window.location.origin)) {
          storeCurrentPath();
        }
      },
      true
    );

    // For SPAs, also monitor popstate (back/forward navigation)
    window.addEventListener("popstate", function () {
      // Small delay to let the URL update
      setTimeout(checkAndRedirect, 0);
    });

    // Monitor for client-side navigation via MutationObserver
    // Mintlify may update the URL without full page loads
    var lastPath = window.location.pathname;

    if (window.MutationObserver) {
      var observer = new MutationObserver(function () {
        var newPath = window.location.pathname;
        if (newPath !== lastPath) {
          lastPath = newPath;
          checkAndRedirect();
        }
      });

      // Observe changes to document title (usually changes with navigation)
      // and body (content changes)
      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    }

    // Also use a periodic check as a fallback for missed navigations
    setInterval(function () {
      var newPath = window.location.pathname;
      if (newPath !== lastPath) {
        lastPath = newPath;
        checkAndRedirect();
      }
    }, 500);
  }

  // Initialize
  function init() {
    checkAndRedirect();
    setupPathTracking();
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
