(function () {
  "use strict";

  const CHANGELOG_PATH = "/langsmith/self-hosted-changelog";
  let wasOnChangelog = false;

  function applyDefaultFilter() {
    const currentPath = document.documentElement.dataset.currentPath;
    const isOnChangelog = currentPath === CHANGELOG_PATH;

    if (!isOnChangelog) {
      wasOnChangelog = false;
      return;
    }

    if (wasOnChangelog) return;
    wasOnChangelog = true;

    const params = new URLSearchParams(location.search);
    if (params.has("tags")) return;

    params.set("tags", "Stable");
    location.replace(`${location.pathname}?${params}${location.hash}`);
  }

  applyDefaultFilter();

  new MutationObserver(applyDefaultFilter).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-current-path"],
  });
})();
