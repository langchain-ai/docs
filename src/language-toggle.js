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

  var LANDING_PAGES = [
    "langchain/overview",
    "langgraph/overview",
    "deepagents/overview",
    "integrations/providers/overview",
    "learn",
    "reference/overview",
    "contributing/overview",
  ];

  function getPathLanguage(path) {
    if (path.startsWith(PYTHON_PREFIX)) return "python";
    if (path.startsWith(JS_PREFIX)) return "javascript";
    return null;
  }

  function isLandingPage(path) {
    var normalized = path.replace(/\/$/, "");
    return LANDING_PAGES.some(function (landing) {
      return (
        normalized === PYTHON_PREFIX + landing ||
        normalized === JS_PREFIX + landing
      );
    });
  }

  function getEquivalentPath(sourcePath, targetLang) {
    var sourcePrefix = targetLang === "python" ? JS_PREFIX : PYTHON_PREFIX;
    var targetPrefix = targetLang === "python" ? PYTHON_PREFIX : JS_PREFIX;
    if (sourcePath.startsWith(sourcePrefix)) {
      return targetPrefix + sourcePath.substring(sourcePrefix.length);
    }
    return null;
  }

  function getStorage(key, fallback) {
    try {
      return sessionStorage.getItem(key) || fallback;
    } catch (e) {
      return fallback;
    }
  }

  function setStorage(key, value) {
    try {
      sessionStorage.setItem(key, value);
    } catch (e) {}
  }

  function clearStorage() {
    try {
      sessionStorage.removeItem(STORAGE_KEY);
      sessionStorage.removeItem(STORAGE_KEY_HASH);
    } catch (e) {}
  }

  function storeCurrentPath() {
    var path = window.location.pathname;
    if (getPathLanguage(path)) {
      setStorage(STORAGE_KEY, path);
      setStorage(STORAGE_KEY_HASH, window.location.hash || "");
    }
  }

  function checkAndRedirect() {
    var currentPath = window.location.pathname;
    var currentLang = getPathLanguage(currentPath);

    if (!currentLang || !isLandingPage(currentPath)) {
      storeCurrentPath();
      return;
    }

    var previousPath = getStorage(STORAGE_KEY, null);
    var previousLang = previousPath && getPathLanguage(previousPath);

    // Redirect only if coming from a non-landing page in the other language
    if (!previousLang || previousLang === currentLang || isLandingPage(previousPath)) {
      storeCurrentPath();
      return;
    }

    var equivalentPath = getEquivalentPath(previousPath, currentLang);
    if (!equivalentPath || equivalentPath === currentPath) {
      storeCurrentPath();
      return;
    }

    clearStorage();
    window.location.replace(equivalentPath + getStorage(STORAGE_KEY_HASH, ""));
  }

  function setupPathTracking() {
    var lastPath = window.location.pathname;

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

    window.addEventListener("popstate", function () {
      setTimeout(checkAndRedirect, 0);
    });

    // Poll for URL changes (handles SPA navigation)
    setInterval(function () {
      if (window.location.pathname !== lastPath) {
        lastPath = window.location.pathname;
        checkAndRedirect();
      }
    }, 500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      checkAndRedirect();
      setupPathTracking();
    });
  } else {
    checkAndRedirect();
    setupPathTracking();
  }
})();
