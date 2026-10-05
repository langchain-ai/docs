(function () {
  "use strict";

  const PAGE = "/langsmith/self-hosted-changelog";
  const CHAPTER = /^langsmith-\d+-\d+-0$/;
  let scheduled = false;

  function updateIndex(nav, headings) {
    const signature = headings.map((heading) => heading.id).join(",");
    if (nav.dataset.chapters === signature) return;
    nav.dataset.chapters = signature;

    const title = document.createElement("strong");
    title.textContent = "Minor releases";
    const links = document.createElement("div");
    links.className = "changelog-chapter-links";
    for (const heading of headings) {
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent.replace(/\u200b/g, "").trim();
      links.appendChild(link);
    }
    nav.replaceChildren(title, links);
  }

  function mountIndex(parent, id, headings, before) {
    let nav = document.getElementById(id);
    if (!nav) {
      nav = document.createElement("nav");
      nav.id = id;
      nav.className = "changelog-chapter-index";
      nav.setAttribute("aria-label", "Minor releases");
      parent.insertBefore(nav, before || null);
    }
    updateIndex(nav, headings);
    return nav;
  }

  function enhance() {
    scheduled = false;
    if (document.documentElement.dataset.currentPath !== PAGE) {
      document.querySelectorAll(".changelog-chapter-index").forEach((nav) => nav.remove());
      document.querySelectorAll(".changelog-chapter-heading").forEach((heading) => {
        heading.classList.remove("changelog-chapter-heading");
      });
      return;
    }

    const headings = Array.from(document.querySelectorAll("h2[id]")).filter(
      (heading) => CHAPTER.test(heading.id) && heading.getClientRects().length,
    );
    if (!headings.length) {
      document.querySelectorAll(".changelog-chapter-index").forEach((nav) => nav.remove());
      return;
    }
    headings.forEach((heading) => heading.classList.add("changelog-chapter-heading"));

    const side = document.getElementById("content-side-layout");
    const content = document.getElementById("content");
    if (content) {
      const inline = mountIndex(content, "changelog-chapters-inline", headings, content.firstChild);
      inline.classList.toggle("changelog-chapter-index-fallback", !side);
    }
    if (side) mountIndex(side, "changelog-chapters-sidebar", headings);
  }

  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(enhance);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", schedule, { once: true });
  } else {
    schedule();
  }
  new MutationObserver(schedule).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-current-path"],
    childList: true,
    subtree: true,
  });
})();
