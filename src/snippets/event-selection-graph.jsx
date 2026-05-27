"use client";

import { useEffect, useState } from "react";

export const EventSelectionGraph = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    function detectDarkMode() {
      const root = document.documentElement;
      return (
        root.classList.contains("dark") ||
        root.getAttribute("data-theme") === "dark" ||
        root.style.colorScheme === "dark"
      );
    }

    setIsDarkMode(detectDarkMode());

    const observer = new MutationObserver(() => setIsDarkMode(detectDarkMode()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"],
    });

    return () => observer.disconnect();
  }, []);

  const palette = isDarkMode
    ? {
        edge: "#94a3b8",
        checkFill: "#e2e8f0",
        checkText: "#0f172a",
        graph: {
          root: {
            fill: "#111827",
            selectedFill: "#1f2937",
            stroke: "#94a3b8",
            text: "#cbd5e1",
          },
          amber: {
            fill: "#2b2111",
            selectedFill: "#3a2d14",
            stroke: "#f59e0b",
            text: "#fbbf24",
          },
          green: {
            fill: "#102a1c",
            selectedFill: "#163b27",
            stroke: "#22c55e",
            text: "#86efac",
          },
        },
        node: {
          amber: {
            fill: "#3a2d14",
            stroke: "#f59e0b",
            text: "#fde68a",
            selectedFill: "#4a3817",
          },
          blue: {
            fill: "#172554",
            stroke: "#60a5fa",
            text: "#bfdbfe",
            selectedFill: "#1e3a8a",
          },
          green: {
            fill: "#14532d",
            stroke: "#4ade80",
            text: "#bbf7d0",
            selectedFill: "#166534",
          },
          slate: {
            fill: "#1e293b",
            stroke: "#94a3b8",
            text: "#e2e8f0",
            selectedFill: "#334155",
          },
        },
      }
    : {
        edge: "#64748b",
        checkFill: "#111827",
        checkText: "#ffffff",
        graph: {
          root: {
            fill: "#ffffff",
            selectedFill: "#f1f5f9",
            stroke: "#94a3b8",
            text: "#334155",
          },
          amber: {
            fill: "#fffbeb",
            selectedFill: "#fef3c7",
            stroke: "#d97706",
            text: "#92400e",
          },
          green: {
            fill: "#f0fdf4",
            selectedFill: "#dcfce7",
            stroke: "#16a34a",
            text: "#166534",
          },
        },
        node: {
          amber: {
            fill: "#fef3c7",
            stroke: "#d97706",
            text: "#92400e",
            selectedFill: "#fde68a",
          },
          blue: {
            fill: "#eff6ff",
            stroke: "#2563eb",
            text: "#1e40af",
            selectedFill: "#dbeafe",
          },
          green: {
            fill: "#f0fdf4",
            stroke: "#16a34a",
            text: "#166534",
            selectedFill: "#dcfce7",
          },
          slate: {
            fill: "#f8fafc",
            stroke: "#94a3b8",
            text: "#334155",
            selectedFill: "#e2e8f0",
          },
        },
      };

  const graphRegions = [
    {
      id: "graph:root",
      label: "Root graph",
      namespace: [],
      color: "root",
      x: 10,
      y: 5,
      width: 600,
      height: 610,
    },
    {
      id: "graph:researcher",
      label: "Researcher graph",
      namespace: ["researcher"],
      color: "amber",
      x: 40,
      y: 115,
      width: 540,
      height: 255,
    },
    {
      id: "graph:write",
      label: "Write graph",
      namespace: ["researcher", "c"],
      color: "green",
      x: 50,
      y: 365,
      width: 310,
      height: 130,
    },
  ];

  const graphNodes = [
    {
      id: "start",
      label: "__start__",
      namespace: [],
      selectable: false,
      x: 255,
      y: 25,
      width: 110,
      height: 52,
      color: "slate",
    },
    {
      id: "a",
      label: "A",
      namespace: ["researcher", "a"],
      x: 65,
      y: 185,
      width: 90,
      height: 52,
      color: "amber",
    },
    {
      id: "b",
      label: "B",
      namespace: ["researcher", "b"],
      x: 285,
      y: 150,
      width: 90,
      height: 52,
      color: "amber",
    },
    {
      id: "c",
      label: "C",
      namespace: ["researcher", "c"],
      x: 285,
      y: 275,
      width: 90,
      height: 52,
      color: "amber",
    },
    {
      id: "d",
      label: "D",
      namespace: ["researcher", "d"],
      x: 460,
      y: 215,
      width: 90,
      height: 52,
      color: "amber",
    },
    {
      id: "e1",
      label: "E",
      namespace: ["researcher", "c", "e:02be..."],
      runtimeId: "02be...",
      x: 105,
      y: 420,
      width: 90,
      height: 56,
      color: "green",
    },
    {
      id: "e2",
      label: "E",
      namespace: ["researcher", "c", "e:91ac..."],
      runtimeId: "91ac...",
      x: 245,
      y: 420,
      width: 90,
      height: 56,
      color: "green",
    },
    {
      id: "end",
      label: "__end__",
      namespace: [],
      selectable: false,
      x: 460,
      y: 535,
      width: 110,
      height: 52,
      color: "slate",
    },
  ];

  const graphEdges = [
    { from: "start", to: "a" },
    { from: "a", to: "b", dashed: true },
    { from: "a", to: "c", dashed: true },
    { from: "b", to: "d" },
    { from: "d", to: "end" },
    { from: "c", to: "e1" },
    { from: "c", to: "e2" },
    { from: "e1", to: "end" },
    { from: "e2", to: "end" },
  ];

  function getNode(id) {
    return graphNodes.find((node) => node.id === id);
  }

  function getSelectableItem(id) {
    return (
      graphRegions.find((graphRegion) => graphRegion.id === id) ??
      graphNodes.find((node) => node.id === id)
    );
  }

  function edgePath(edge) {
    const from = getNode(edge.from);
    const to = getNode(edge.to);

    if (!from || !to) {
      return "";
    }

    const startX = from.x + from.width / 2;
    const startY = from.y + from.height;
    const endX = to.x + to.width / 2;
    const endY = to.y;
    const midY = (startY + endY) / 2;

    return `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`;
  }

  function formatNamespace(namespace) {
    return JSON.stringify(namespace);
  }

  function formatNamespacesFilter(namespaces) {
    return JSON.stringify(namespaces);
  }

  function isSameNamespace(left, right) {
    return left.length === right.length && left.every((segment, index) => segment === right[index]);
  }

  function isNamespacePrefix(prefix, namespace) {
    return prefix.length < namespace.length && prefix.every((segment, index) => segment === namespace[index]);
  }

  function isGraphItem(item) {
    return item.id.startsWith("graph:");
  }

  function collapseSelectedItems(items) {
    return items.filter(
      (item) =>
        !items.some((other) => {
          if (other.id === item.id) {
            return false;
          }

          if (other.namespace.length > 0 && isNamespacePrefix(other.namespace, item.namespace)) {
            return true;
          }

          return isSameNamespace(other.namespace, item.namespace) && isGraphItem(other) && !isGraphItem(item);
        }),
    );
  }

  function toggleSelected(id) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((selectedId) => selectedId !== id)
        : [...current, id],
    );
  }

  const [selectedIds, setSelectedIds] = useState(["graph:root"]);
  const selectedItems = selectedIds.map(getSelectableItem).filter(Boolean);
  const displayedItems = collapseSelectedItems(selectedItems);
  const selectedNamespaces = displayedItems.map((item) => item.namespace);

  function formatList(labels) {
    if (labels.length === 1) {
      return labels[0];
    }

    if (labels.length === 2) {
      return `${labels[0]} or ${labels[1]}`;
    }

    return `${labels.slice(0, -1).join(", ")}, or ${labels[labels.length - 1]}`;
  }

  function describeSelectedItem(item) {
    if (item.id.startsWith("graph:")) {
      return `the ${item.label}`;
    }

    return `node ${item.label}`;
  }

  function formatSelectedTargets(items) {
    const runtimeGroups = new Map();
    const labels = [];

    for (const item of items) {
      if (item.runtimeId) {
        const current = runtimeGroups.get(item.label) ?? [];
        runtimeGroups.set(item.label, [...current, item.runtimeId]);
      } else {
        labels.push(describeSelectedItem(item));
      }
    }

    for (const [nodeLabel, runtimeIds] of runtimeGroups) {
      const execution = runtimeIds.length === 1 ? "execution" : "executions";
      labels.push(`the specific task ${execution} ${formatList(runtimeIds)} of node ${nodeLabel}`);
    }

    return formatList(labels);
  }

  function describeSelection(items) {
    const targetDescription = formatSelectedTargets(items);
    const alternatives =
      items.length > 1 ? " Their namespaces are combined as alternatives (OR)." : "";

    return `This subscription matches events from ${targetDescription}.${alternatives}`;
  }

  return (
    <div className="my-3 rounded-xl border bg-gray-50 p-4 dark:bg-gray-900">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Select a graph or node
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-300">
            Click graphs or nodes to select namespace alternatives. Multiple selections are combined with OR.
          </div>
        </div>
        <button
          className="rounded-md border border-gray-300 px-2.5 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
          onClick={() => setSelectedIds([])}
          type="button"
        >
          Clear
        </button>
      </div>

      <div className="mt-6 overflow-x-auto">
        <svg
          aria-label="Selectable graph showing namespaces for selected nodes"
          className="h-auto w-full"
          role="img"
          viewBox="0 0 620 640"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <marker id="event-selection-graph-arrow" markerHeight="8" markerWidth="8" orient="auto" refX="7" refY="4">
              <path d="M0,0 L8,4 L0,8 Z" fill={palette.edge} />
            </marker>
          </defs>

          {graphRegions.map((graphRegion) => {
            const colors = palette.graph[graphRegion.color];
            const isSelected = selectedIds.includes(graphRegion.id);

            return (
              <g
                key={graphRegion.id}
                onClick={() => toggleSelected(graphRegion.id)}
                role="button"
                style={{ outline: "none" }}
                tabIndex={0}
              >
                <rect
                  fill={isSelected ? colors.selectedFill : colors.fill}
                  height={graphRegion.height}
                  rx="18"
                  stroke={colors.stroke}
                  strokeDasharray="8 8"
                  strokeWidth="1.5"
                  width={graphRegion.width}
                  x={graphRegion.x}
                  y={graphRegion.y}
                />
                <text
                  fill={colors.text}
                  fontSize="14"
                  fontWeight="700"
                  pointerEvents="none"
                  x={graphRegion.x + 18}
                  y={graphRegion.y + 28}
                >
                  {graphRegion.label}
                </text>
                {isSelected && (
                  <g pointerEvents="none">
                    <circle cx={graphRegion.x + graphRegion.width - 18} cy={graphRegion.y + 18} fill={palette.checkFill} r="8" />
                    <text
                      fill={palette.checkText}
                      fontSize="11"
                      fontWeight="700"
                      textAnchor="middle"
                      x={graphRegion.x + graphRegion.width - 18}
                      y={graphRegion.y + 22}
                    >
                      ✓
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {graphEdges.map((edge) => (
            <path
              d={edgePath(edge)}
              fill="none"
              key={`${edge.from}-${edge.to}`}
              markerEnd="url(#event-selection-graph-arrow)"
              stroke={palette.edge}
              strokeDasharray={edge.dashed ? "7 7" : undefined}
              strokeWidth="2"
            />
          ))}

          {graphNodes.map((node) => {
            const colors = palette.node[node.color];
            const isSelectable = node.selectable !== false;
            const isSelected = selectedIds.includes(node.id);

            return (
              <g
                key={node.id}
                onClick={isSelectable ? () => toggleSelected(node.id) : undefined}
                role={isSelectable ? "button" : undefined}
                style={{ outline: "none" }}
                tabIndex={isSelectable ? 0 : undefined}
              >
                <rect
                  fill={isSelected ? colors.selectedFill : colors.fill}
                  height={node.height}
                  rx="14"
                  stroke={colors.stroke}
                  strokeWidth="2"
                  width={node.width}
                  x={node.x}
                  y={node.y}
                />
                <text
                  fill={colors.text}
                  fontSize="18"
                  fontWeight="700"
                  pointerEvents="none"
                  textAnchor="middle"
                  x={node.x + node.width / 2}
                  y={node.y + (node.runtimeId ? 30 : 36)}
                >
                  {node.label}
                </text>
                {node.runtimeId && (
                  <text
                    fill={colors.text}
                    fontSize="11"
                    pointerEvents="none"
                    textAnchor="middle"
                    x={node.x + node.width / 2}
                    y={node.y + 45}
                  >
                    {node.runtimeId}
                  </text>
                )}
                {isSelected && (
                  <g pointerEvents="none">
                    <circle cx={node.x + node.width - 12} cy={node.y + 12} fill={palette.checkFill} r="8" />
                    <text
                      fill={palette.checkText}
                      fontSize="11"
                      fontWeight="700"
                      textAnchor="middle"
                      x={node.x + node.width - 12}
                      y={node.y + 16}
                    >
                      ✓
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="rounded-lg border bg-white p-3 dark:border-gray-700 dark:bg-gray-950">
        {displayedItems.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              {describeSelection(displayedItems)}
            </p>
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                Namespaces
              </div>
              <code className="mt-1 block text-sm text-gray-800 dark:text-gray-200">
                {formatNamespace(selectedNamespaces)}
              </code>
            </div>
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                Subscription filter
              </div>
              <code className="mt-1 block text-sm text-gray-800 dark:text-gray-200">
                {`{ "namespaces": ${formatNamespacesFilter(selectedNamespaces)}, "depth": 0 }`}
              </code>
            </div>
          </div>
        ) : (
          <div className="text-sm text-gray-600 dark:text-gray-300">
            No node selected. Select a node to show its namespace filter.
          </div>
        )}
      </div>
    </div>
  );
}
