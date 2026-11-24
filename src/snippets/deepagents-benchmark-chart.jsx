"use client";

import { useEffect, useState } from "react";

export const DeepAgentsBenchmarkChart = () => {
  const [isDark, setIsDark] = useState(false);
  const [hover, setHover] = useState(null);

  useEffect(() => {
    const detect = () => {
      const root = document.documentElement;
      return (
        root.classList.contains("dark") ||
        root.getAttribute("data-theme") === "dark" ||
        root.style.colorScheme === "dark"
      );
    };
    setIsDark(detect());
    const observer = new MutationObserver(() => setIsDark(detect()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"],
    });
    return () => observer.disconnect();
  }, []);

  const theme = isDark
    ? { ink: "#ffffff", ink2: "#c3c2b7", muted: "#898781", grid: "#2c2c2a", surface: "#1a1a19" }
    : { ink: "#0b0b0b", ink2: "#52514e", muted: "#898781", grid: "#e1e0d9", surface: "#ffffff" };

  // Score is the mean pass rate over tasks; cost is the median task's mean
  // estimated cost over its trials, in US dollars. `se` is one standard error.
  const BENCHMARKS = [
    {
      id: "tb4",
      group: "coding",
      title: "Terminal-Bench 4.0",
      tasks: { opus: 57, sol: 60, kimi: 57 },
      runs: [
        { model: "opus", harness: "deepagents", score: 0.5175, scoreSe: 0.0218, cost: 1.414, costSe: 0.064 },
        { model: "opus", harness: "claude-code", score: 0.5263, scoreSe: 0.0226, cost: 1.565, costSe: 0.109 },
        { model: "opus", harness: "pi", score: 0.4942, scoreSe: 0.0224, cost: 1.301, costSe: 0.057 },
        { model: "sol", harness: "deepagents", score: 0.4472, scoreSe: 0.0237, cost: 0.364, costSe: 0.015 },
        { model: "sol", harness: "codex", score: 0.475, scoreSe: 0.0231, cost: 0.438, costSe: 0.013 },
        { model: "sol", harness: "pi", score: 0.3667, scoreSe: 0.0235, cost: 0.164, costSe: 0.005 },
        { model: "kimi", harness: "claude-code", score: 0.5848, scoreSe: 0.0306, cost: 2.441, costSe: 0.177 },
        { model: "kimi", harness: "codex", score: 0.5936, scoreSe: 0.029, cost: 1.261, costSe: 0.033 },
        { model: "kimi", harness: "pi", score: 0.5029, scoreSe: 0.0274, cost: 1.419, costSe: 0.086 },
      ],
    },
    {
      id: "tbs",
      group: "coding",
      title: "Terminal-Bench Science 0.1",
      tasks: { opus: 59, sol: 59 },
      runs: [
        { model: "opus", harness: "deepagents", score: 0.4379, scoreSe: 0.0314, cost: 6.336, costSe: 0.296 },
        { model: "opus", harness: "claude-code", score: 0.4407, scoreSe: 0.029, cost: 6.767, costSe: 0.364 },
        { model: "opus", harness: "pi", score: 0.3531, scoreSe: 0.0293, cost: 3.628, costSe: 0.179 },
        { model: "sol", harness: "deepagents", score: 0.4718, scoreSe: 0.0287, cost: 1.617, costSe: 0.075 },
        { model: "sol", harness: "codex", score: 0.5028, scoreSe: 0.0211, cost: 1.293, costSe: 0.047 },
        { model: "sol", harness: "pi", score: 0.2514, scoreSe: 0.0233, cost: 0.228, costSe: 0.009 },
      ],
    },
    {
      id: "apex",
      group: "work",
      title: "APEX-Agents 1.1",
      tasks: { opus: 38, sol: 39 },
      runs: [
        { model: "opus", harness: "deepagents", score: 0.4912, scoreSe: 0.0274, cost: 0.241, costSe: 0.007 },
        { model: "opus", harness: "claude-code", score: 0.4737, scoreSe: 0.0258, cost: 0.253, costSe: 0.007 },
        { model: "opus", harness: "pi", score: 0.4912, scoreSe: 0.0196, cost: 0.226, costSe: 0.005 },
        { model: "sol", harness: "deepagents", score: 0.547, scoreSe: 0.014, cost: 0.068, costSe: 0.004 },
        { model: "sol", harness: "codex", score: 0.5385, scoreSe: 0.0217, cost: 0.148, costSe: 0.005 },
        { model: "sol", harness: "pi", score: 0.5684, scoreSe: 0.0173, cost: 0.057, costSe: 0.002 },
      ],
    },
  ];

  const GROUPS = {
    coding: "Coding",
    work: "Professional work",
  };

  const MODELS = {
    opus: { label: "Claude Opus 5.5 (med)", light: "#2a78d6", dark: "#3987e5" },
    sol: { label: "GPT-6.1 Sol (med)", light: "#eb6834", dark: "#d95926" },
    kimi: { label: "Kimi K3.1 Pro (med)", light: "#1f9d6b", dark: "#2bb07c" },
  };

  // Deep Agents is the only filled mark; competing harnesses are outlined.
  const HARNESSES = {
    deepagents: { label: "Deep Agents", shape: "circle" },
    "claude-code": { label: "Claude Code", shape: "square" },
    codex: { label: "Codex", shape: "diamond" },
    pi: { label: "Pi", shape: "triangle" },
  };

  const pct = (v) => `${(v * 100).toFixed(1)}%`;
  const colorOf = (model) => MODELS[model][isDark ? "dark" : "light"];
  const isFilled = (harness) => harness === "deepagents";

  const marker = (harness, cx, cy, color, size = 6) => {
    // Hollow marks take the surface color so whiskers don't show through.
    const fill = isFilled(harness) ? color : theme.surface;
    const common = { fill, stroke: color, strokeWidth: 2 };
    switch (HARNESSES[harness].shape) {
      case "square":
        return <rect x={cx - size + 0.5} y={cy - size + 0.5} width={2 * size - 1} height={2 * size - 1} rx={1.5} {...common} />;
      case "diamond":
        return <path d={`M${cx} ${cy - size - 1}L${cx + size + 1} ${cy}L${cx} ${cy + size + 1}L${cx - size - 1} ${cy}Z`} {...common} />;
      case "triangle":
        return <path d={`M${cx} ${cy - size - 1}L${cx + size + 1} ${cy + size}L${cx - size - 1} ${cy + size}Z`} {...common} />;
      default:
        return <circle cx={cx} cy={cy} r={size} {...common} />;
    }
  };

  const legend = (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 20px", fontSize: 13, color: theme.ink2, marginBottom: 12 }}>
      {Object.entries(MODELS).map(([k, m]) => (
        <span key={k} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: 3, background: colorOf(k) }} />
          {m.label}
        </span>
      ))}
      {Object.entries(HARNESSES).map(([k, h]) => (
        <span key={k} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <svg width={16} height={16} aria-hidden="true">
            {marker(k, 8, 8, theme.ink2, 5)}
          </svg>
          {h.label}
        </span>
      ))}
    </div>
  );

  const tooltipStyle = (left, top, flip) => ({
    position: "absolute",
    left,
    top,
    transform: flip ? "translate(calc(-100% - 14px), -50%)" : "translate(14px, -50%)",
    background: theme.surface,
    color: theme.ink,
    border: `1px solid ${theme.grid}`,
    borderRadius: 8,
    padding: "6px 10px",
    fontSize: 12,
    lineHeight: 1.5,
    whiteSpace: "nowrap",
    pointerEvents: "none",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
    zIndex: 2,
  });

  // Scatter plot: score against median cost per task, linear x from zero.
  // Round x tick steps (1, 2, 2.5, or 5 times a power of 10), about four per axis.
  const niceTicks = (v) => {
    const raw = v / 4;
    const p = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].find((m) => m * p >= raw) * p;
    const n = Math.ceil(v / step - 1e-9);
    return Array.from({ length: n + 1 }, (_, i) => Math.round(i * step * 1000) / 1000);
  };
  const SW = 460;
  const SH = 340;
  const PAD = { left: 44, right: 12, top: 10, bottom: 40 };

  // Greedy direct-label placement: of the spots right, left, above, and
  // below each point that fit in the plot, take the one that least overlaps
  // the other points, their whiskers, and labels already placed.
  const placeLabels = (points) => {
    const obstacles = points.map((p) => [
      { x0: p.cx - 8, x1: p.cx + 8, y0: p.cy - 8, y1: p.cy + 8 },
      { x0: p.wx0, x1: p.wx1, y0: p.cy - 2, y1: p.cy + 2 },
      { x0: p.cx - 2, x1: p.cx + 2, y0: p.wy0, y1: p.wy1 },
    ]);
    const placed = [];
    const overlaps = (a, b) => a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1;
    const area = (a, b) =>
      overlaps(a, b) ? (Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0)) * (Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0)) : 0;
    const inside = (b) => b.x0 >= PAD.left && b.x1 <= SW - PAD.right && b.y0 >= PAD.top && b.y1 <= SH - PAD.bottom;
    return points.map((p, i) => {
      const w = p.text.length * 6.6;
      const { cx, cy } = p;
      const above = { y: cy - 13, y0: cy - 25, y1: cy - 9 };
      const below = { y: cy + 23, y0: cy + 9, y1: cy + 27 };
      const candidates = [
        { x: cx + 11, y: cy + 4, anchor: "start", box: { x0: cx + 9, x1: cx + 13 + w, y0: cy - 8, y1: cy + 8 } },
        { x: cx - 11, y: cy + 4, anchor: "end", box: { x0: cx - 13 - w, x1: cx - 9, y0: cy - 8, y1: cy + 8 } },
        ...[above, below].flatMap((v) => [
          { x: cx, y: v.y, anchor: "middle", box: { x0: cx - w / 2, x1: cx + w / 2, y0: v.y0, y1: v.y1 } },
          { x: cx + 6, y: v.y, anchor: "end", box: { x0: cx + 6 - w, x1: cx + 6, y0: v.y0, y1: v.y1 } },
          { x: cx - 6, y: v.y, anchor: "start", box: { x0: cx - 6, x1: cx - 6 + w, y0: v.y0, y1: v.y1 } },
        ]),
      ];
      // Covering a marker or label costs far more than crossing a whisker.
      const penalty = (c) =>
        obstacles.reduce(
          (sum, [mark, ...whiskers], j) =>
            j === i ? sum : sum + 20 * area(c.box, mark) + whiskers.reduce((t, b) => t + area(c.box, b), 0),
          0,
        ) + placed.reduce((sum, b) => sum + 20 * area(c.box, b), 0);
      const fits = candidates.filter((c) => inside(c.box));
      const pick = (fits.length ? fits : candidates).reduce((best, c) => (penalty(c) < penalty(best) ? c : best));
      placed.push(pick.box);
      return pick;
    });
  };

  const scatter = (bench) => {
    const runs = bench.runs;
    const xTicks = niceTicks(Math.max(...runs.map((r) => r.cost + r.costSe)));
    const xmax = xTicks[xTicks.length - 1];
    const ymin = Math.floor((Math.min(...runs.map((r) => r.score - r.scoreSe)) - 0.02) * 20) / 20;
    const ymax = Math.ceil((Math.max(...runs.map((r) => r.score + r.scoreSe)) + 0.02) * 20) / 20;
    const X = (v) => PAD.left + ((SW - PAD.left - PAD.right) * v) / xmax;
    const Y = (v) => PAD.top + (SH - PAD.top - PAD.bottom) * (1 - (v - ymin) / (ymax - ymin));
    const yTicks = [];
    for (let v = ymin; v <= ymax + 1e-9; v += 0.05) yTicks.push(Math.round(v * 100) / 100);
    const points = runs.map((r) => ({
      r,
      cx: X(r.cost),
      cy: Y(r.score),
      wx0: X(r.cost - r.costSe),
      wx1: X(r.cost + r.costSe),
      wy0: Y(r.score + r.scoreSe),
      wy1: Y(r.score - r.scoreSe),
      text: HARNESSES[r.harness].label,
    }));
    const labels = placeLabels(points);
    const active =
      hover && hover.bench === bench.id
        ? points.find((p) => p.r.model === hover.model && p.r.harness === hover.harness)
        : null;

    return (
      <figure key={bench.id} style={{ margin: 0, minWidth: 0 }}>
        <figcaption style={{ fontWeight: 600, fontSize: 15, marginBottom: 4, color: theme.ink }}>{bench.title}</figcaption>
        <div style={{ position: "relative" }}>
          <svg
            viewBox={`0 0 ${SW} ${SH}`}
            width="100%"
            role="img"
            aria-label={`${bench.title}: score versus median cost per task for each harness and model`}
            style={{ display: "block", overflow: "visible" }}
          >
            {xTicks.map((t) => (
              <g key={`x${t}`}>
                <line x1={X(t)} x2={X(t)} y1={PAD.top} y2={SH - PAD.bottom} stroke={theme.grid} />
                <text x={X(t)} y={SH - PAD.bottom + 16} textAnchor="middle" fontSize={11} fill={theme.muted}>
                  {`$${t % 1 ? t.toFixed(2) : t}`}
                </text>
              </g>
            ))}
            {yTicks.map((t) => (
              <g key={`y${t}`}>
                <line x1={PAD.left} x2={SW - PAD.right} y1={Y(t)} y2={Y(t)} stroke={theme.grid} />
                <text x={PAD.left - 6} y={Y(t) + 4} textAnchor="end" fontSize={11} fill={theme.muted}>
                  {`${Math.round(t * 100)}%`}
                </text>
              </g>
            ))}
            <text x={(PAD.left + SW - PAD.right) / 2} y={SH - 4} textAnchor="middle" fontSize={11} fill={theme.ink2}>
              Median estimated cost per task (USD)
            </text>
            <text
              transform={`translate(10 ${(PAD.top + SH - PAD.bottom) / 2}) rotate(-90)`}
              textAnchor="middle"
              fontSize={11}
              fill={theme.ink2}
            >
              Score
            </text>
            {points.map(({ r, cx, cy, wx0, wx1, wy0, wy1, text }, i) => {
              const color = colorOf(r.model);
              const key = { bench: bench.id, model: r.model, harness: r.harness };
              const dim = active && active.r !== r;
              return (
                <g
                  key={`${r.model}-${r.harness}`}
                  opacity={dim ? 0.35 : 1}
                  onMouseEnter={() => setHover(key)}
                  onMouseLeave={() => setHover(null)}
                  onFocus={() => setHover(key)}
                  onBlur={() => setHover(null)}
                  tabIndex={0}
                  aria-label={`${text} with ${MODELS[r.model].label}: score ${pct(r.score)}, $${r.cost.toFixed(2)} median cost per task`}
                  style={{ cursor: "default", outline: "none" }}
                >
                  <line x1={wx0} x2={wx1} y1={cy} y2={cy} stroke={color} strokeWidth={1.5} />
                  <line x1={cx} x2={cx} y1={wy0} y2={wy1} stroke={color} strokeWidth={1.5} />
                  {marker(r.harness, cx, cy, color)}
                  <text
                    x={labels[i].x}
                    y={labels[i].y}
                    textAnchor={labels[i].anchor}
                    fontSize={12}
                    fontWeight={isFilled(r.harness) ? 600 : 400}
                    fill={isFilled(r.harness) ? theme.ink : theme.ink2}
                    stroke={theme.surface}
                    strokeWidth={3}
                    paintOrder="stroke"
                  >
                    {text}
                  </text>
                  <circle cx={cx} cy={cy} r={14} fill="transparent" />
                </g>
              );
            })}
          </svg>
          {active && (
            <div role="status" style={tooltipStyle(`${(active.cx / SW) * 100}%`, `${(active.cy / SH) * 100}%`, active.cx > SW * 0.55)}>
              <div style={{ fontWeight: 600 }}>
                {HARNESSES[active.r.harness].label} · {MODELS[active.r.model].label}
              </div>
              <div>
                Score {pct(active.r.score)} <span style={{ color: theme.muted }}>± {pct(active.r.scoreSe)}</span>
              </div>
              <div>
                Median cost ${active.r.cost.toFixed(2)}{" "}
                <span style={{ color: theme.muted }}>± ${active.r.costSe.toFixed(2)}</span>
              </div>
              <div style={{ color: theme.muted }}>{bench.tasks[active.r.model]} tasks, 3 trials each</div>
            </div>
          )}
        </div>
      </figure>
    );
  };

  const grid = { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 420px), 1fr))", gap: 28 };

  return (
    <div className="deepagents-benchmark-chart" style={{ margin: "16px 0" }}>
      {legend}
      {Object.entries(GROUPS).map(([g, label]) => (
        <section key={g} style={{ marginTop: 20 }}>
          <div style={{ fontWeight: 600, fontSize: 13, letterSpacing: 0.4, textTransform: "uppercase", color: theme.muted, marginBottom: 10 }}>
            {label}
          </div>
          <div style={grid}>{BENCHMARKS.filter((b) => b.group === g).map(scatter)}</div>
        </section>
      ))}
    </div>
  );
};
