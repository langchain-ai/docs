"use client";
import { useEffect, useRef, useState } from "react";

export const ExampleEmbed = ({
  example,
  theme,
  minHeight = 500,
  maxHeight = 700
}) => {
// src/ExampleEmbed.tsx

// src/constants.ts
var PROD_BASE = "https://ui-patterns.langchain.com";

// src/ExampleEmbed.tsx
var iframeCache = (() => {
  const g = globalThis;
  if (!g.__lcExampleIframeCache) {
    g.__lcExampleIframeCache = /* @__PURE__ */ new Map();
  }
  return g.__lcExampleIframeCache;
})();
function detectPageTheme() {
  if (typeof document === "undefined") return "light";
  const root = document.documentElement;
  if (root.classList.contains("dark") || root.getAttribute("data-theme") === "dark" || root.style.colorScheme === "dark") {
    return "dark";
  }
  return "light";
}
var LOCAL_BASE = "http://localhost";
var LOCAL_PORTS = {
  "ai-elements": 4600,
  "assistant-ui": 4500
};
function isLocalhost() {
  return typeof location !== "undefined" && (location.hostname === "localhost" || location.hostname === "127.0.0.1");
}
var EMBED_CSS = `
[data-lc-ee] .lc-border{border-color:#B8DFFF}
[data-lc-ee].dark .lc-border{border-color:#1A2740}
[data-lc-ee] .lc-bg-surface{background-color:white}
[data-lc-ee].dark .lc-bg-surface{background-color:#0B1120}
[data-lc-ee] .lc-bg-wash{background-color:#F2FAFF}
[data-lc-ee].dark .lc-bg-wash{background-color:#030710}
[data-lc-ee] .lc-spinner{border-color:#B8DFFF;border-top-color:#7FC8FF}
[data-lc-ee].dark .lc-spinner{border-color:#1A2740;border-top-color:#7FC8FF}
`;

  const slotRef = useRef(null);
  const [ready, setReady] = useState(() => Boolean(iframeCache.get(example)?.iframe));
  const [iframeHeight, setIframeHeight] = useState(minHeight);
  const [pageTheme, setPageTheme] = useState(detectPageTheme);
  const effectiveTheme = theme ?? pageTheme;
  const effectiveThemeRef = useRef(effectiveTheme);
  effectiveThemeRef.current = effectiveTheme;
  useEffect(() => {
    if (document.getElementById("lc-ee-css")) return;
    const style = document.createElement("style");
    style.id = "lc-ee-css";
    style.textContent = EMBED_CSS;
    document.head.appendChild(style);
  }, []);
  useEffect(() => {
    setPageTheme(detectPageTheme());
    const observer = new MutationObserver(() => setPageTheme(detectPageTheme()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"]
    });
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const useLocal = isLocalhost();
    const localPort = LOCAL_PORTS[example];
    const src = useLocal && localPort ? `${LOCAL_BASE}:${localPort}/` : `${PROD_BASE}/${example}/`;
    let cached = iframeCache.get(example);
    if (cached?.hideTimer) {
      clearTimeout(cached.hideTimer);
      cached.hideTimer = void 0;
    }
    if (!cached) {
      const iframe = document.createElement("iframe");
      iframe.src = src;
      iframe.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms");
      iframe.setAttribute("allow", "clipboard-write");
      iframe.title = `${example} example`;
      Object.assign(iframe.style, {
        position: "fixed",
        border: "none",
        visibility: "hidden",
        pointerEvents: "auto",
        zIndex: "1",
        borderRadius: "15px"
      });
      document.body.appendChild(iframe);
      cached = { iframe };
      iframeCache.set(example, cached);
      window.addEventListener("message", (e) => {
        if (e.data?.type === "RESIZE" && iframeCache.get(example)?.iframe === iframe) {
          const h = Math.min(maxHeight, Math.max(minHeight, e.data.height));
          setIframeHeight(h);
        }
      });
      iframe.addEventListener("load", () => {
        iframe.style.visibility = "visible";
        setReady(true);
        try {
          iframe.contentWindow?.postMessage(
            { type: "CHAT_LC_SET_THEME", theme: effectiveThemeRef.current },
            "*"
          );
        } catch {
        }
      });
    } else {
      cached.iframe.style.visibility = "visible";
      setReady(true);
    }
    function syncPosition() {
      const slot = slotRef.current;
      if (!slot) return;
      const rect = slot.getBoundingClientRect();
      const { style } = cached.iframe;
      style.top = `${rect.top}px`;
      style.left = `${rect.left}px`;
      style.width = `${rect.width}px`;
      style.setProperty("height", `${rect.height}px`, "important");
    }
    syncPosition();
    const ro = new ResizeObserver(syncPosition);
    if (slotRef.current) ro.observe(slotRef.current);
    document.addEventListener("scroll", syncPosition, { passive: true, capture: true });
    window.addEventListener("resize", syncPosition, { passive: true });
    let frameCount = 0;
    let rafId = 0;
    function initialSync() {
      syncPosition();
      if (++frameCount < 5) rafId = requestAnimationFrame(initialSync);
    }
    rafId = requestAnimationFrame(initialSync);
    return () => {
      cancelAnimationFrame(rafId);
      ro.disconnect();
      document.removeEventListener("scroll", syncPosition, { capture: true });
      window.removeEventListener("resize", syncPosition);
      cached.hideTimer = setTimeout(() => {
        if (cached?.iframe) cached.iframe.style.visibility = "hidden";
      }, 200);
    };
  }, [example, minHeight, maxHeight]);
  useEffect(() => {
    const cached = iframeCache.get(example);
    if (!cached?.iframe || !ready) return;
    try {
      cached.iframe.contentWindow?.postMessage(
        { type: "CHAT_LC_SET_THEME", theme: effectiveTheme },
        "*"
      );
    } catch {
    }
  }, [effectiveTheme, ready, example]);
  return <div
    data-lc-ee=""
    className={effectiveTheme === "dark" ? "dark" : ""}
    style={{ position: "relative", fontFamily: "inherit" }}
  >
      <div
    className="lc-border lc-bg-surface"
    style={{
      border: "1px solid",
      borderRadius: "16px",
      overflow: "hidden"
    }}
  >
        {
    /* Slot — the fixed iframe is positioned over this */
  }
        <div
    ref={slotRef}
    className="lc-bg-wash"
    style={{ height: iframeHeight, position: "relative" }}
  >
          {!ready && <div
    style={{
      position: "absolute",
      inset: 0,
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }}
  >
              <div
    className="lc-spinner"
    style={{
      width: 24,
      height: 24,
      border: "3px solid",
      borderRadius: "50%",
      animation: "spin 0.8s linear infinite"
    }}
  />
              <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
            </div>}
        </div>
      </div>
    </div>;

};
