/**
 * Sortable integration download tables
 *
 * Generated snippets wrap markdown tables in
 * `<div class="integration-downloads-table">`. Cells that need numeric or
 * categorical sort expose `<span data-sort-value="...">`. This script makes
 * every header clickable and reorders tbody rows.
 *
 * Mintlify auto-injects every .js file under src/, so this runs site-wide.
 * A MutationObserver re-enhances tables after client-side navigations.
 */

(function () {
  "use strict";

  const WRAPPER = ".integration-downloads-table";
  const ENHANCED = "data-sort-enhanced";

  function cellSortValue(cell, columnIndex) {
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
        cellSortValue(rowA.cells[columnIndex], columnIndex),
        cellSortValue(rowB.cells[columnIndex], columnIndex),
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
