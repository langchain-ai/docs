"use strict";
(() => {
  // src/constants.ts
  var PROD_BASE = "https://ui-patterns.langchain.com";

  // src/ChatLangChainEmbed.ts
  var MOBILE_BREAKPOINT = 768;
  var ROOT_OPEN_CLASS = "lc-chat-widget-open";
  var LOCAL_EMBED_BASE_URL = "http://localhost:4100";
  var PROD_EMBED_BASE_URL = `${PROD_BASE}/react`;
  var CHAT_APP_URL = "https://chat.langchain.com/";
  var PANEL_TRANSITION = "300ms cubic-bezier(0.22, 1, 0.36, 1)";
  var WIDGET_STYLE_ID = "lc-chat-widget-style";
  var WIDGET_INIT_KEY = "__lcChatWidgetInitialized";
  var MIN_PANEL_WIDTH = 280;
  var MAX_PANEL_WIDTH_RATIO = 0.7;
  function lcIsLocalhost() {
    if (typeof window === "undefined") return false;
    var h = window.location.hostname;
    return h === "localhost" || h === "127.0.0.1" || h === "[::1]";
  }
  function lcDetectPageTheme() {
    if (typeof document === "undefined") return "light";
    var el = document.documentElement;
    if (el.classList.contains("dark")) return "dark";
    if (el.getAttribute("data-theme") === "dark") return "dark";
    if (el.style.colorScheme === "dark") return "dark";
    return "light";
  }
  function lcGetEmbedSrc(apiUrl, assistantId, sessionBust) {
    var baseUrl = lcIsLocalhost() ? LOCAL_EMBED_BASE_URL : PROD_EMBED_BASE_URL;
    var params = [];
    if (apiUrl) params.push("apiUrl=" + encodeURIComponent(apiUrl));
    if (assistantId) params.push("assistantId=" + encodeURIComponent(assistantId));
    if (sessionBust !== void 0) {
      params.push("_lcSession=" + encodeURIComponent(String(sessionBust)));
    }
    var query = params.length ? "?" + params.join("&") : "";
    return baseUrl + "/" + query + "#/chat-langchain";
  }
  function lcGetPanelWidth() {
    if (window.innerWidth <= MOBILE_BREAKPOINT) return 0;
    return Math.round(Math.max(360, Math.min(window.innerWidth * 0.3, 480)));
  }
  var WIDGET_CSS = (
    /*css*/
    `
:root {
  --lc-chat-panel-width: 420px;
  --lc-chat-widget-bg-light: #161F34;
  --lc-chat-widget-bg-dark: #006DDD;
  --lc-chat-widget-surface-light: #ffffff;
  --lc-chat-widget-surface-dark: #030710;
  --lc-chat-widget-border-light: #dde4ef;
  --lc-chat-widget-border-dark: rgb(38, 38, 38);
  --lc-chat-widget-shadow-light: 0 20px 60px rgba(3, 7, 16, 0.15);
  --lc-chat-widget-shadow-dark: 0 20px 60px rgba(0, 0, 0, 0.5);
}
#lc-chat-widget-close:focus-visible,
#lc-chat-widget-open-link:focus-visible,
#lc-chat-widget-new-thread:focus-visible,
#lc-chat-widget-history:focus-visible {
  outline: 2px solid #7fc8ff;
  outline-offset: 3px;
}
#lc-chat-widget-close svg,
#lc-chat-widget-open-link svg,
#lc-chat-widget-new-thread svg,
#lc-chat-widget-history svg {
  width: 18px;
  height: 18px;
}
#lc-chat-widget-panel {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9998;
  width: var(--lc-chat-panel-width);
  height: 100vh;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform ${PANEL_TRANSITION};
  background: var(--lc-chat-widget-surface-light);
  border-left: 1px solid var(--lc-chat-widget-border-light);
}
/* Mintlify (and similar) top banner \u2014 keep panel below fixed banner */
#lc-chat-widget-panel[data-lc-banner-offset="true"] {
  margin-top: 40px;
  height: calc(100vh - 40px);
}
html.${ROOT_OPEN_CLASS} #lc-chat-widget-panel { transform: translateX(0); }
#lc-chat-widget-panel[data-theme='dark'] {
  background: var(--lc-chat-widget-surface-dark);
  border-left-color: var(--lc-chat-widget-border-dark);
}
#lc-chat-widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px 13px;
  border-bottom: 1px solid var(--lc-chat-widget-border-light);
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-header {
  border-bottom-color: var(--lc-chat-widget-border-dark);
}
#lc-chat-widget-title {
  margin: 0;
  font: 600 16px/1.2 'Inter', sans-serif;
  color: #030710;
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-title { color: #ffffff; }
#lc-chat-widget-actions { display: flex; align-items: center; gap: 8px; }
#lc-chat-widget-open-link,
#lc-chat-widget-close,
#lc-chat-widget-new-thread,
#lc-chat-widget-history {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #161F34;
  background: transparent;
  text-decoration: none;
  cursor: pointer;
  transition: background 150ms ease, color 150ms ease;
}
#lc-chat-widget-open-link:hover,
#lc-chat-widget-close:hover,
#lc-chat-widget-new-thread:hover,
#lc-chat-widget-history:hover {
  background: rgba(22, 31, 52, 0.08);
}
#lc-chat-widget-panel[data-theme='dark'] :is(#lc-chat-widget-open-link, #lc-chat-widget-close, #lc-chat-widget-new-thread, #lc-chat-widget-history) {
  color: #c8d4e8;
}
#lc-chat-widget-panel[data-theme='dark'] :is(#lc-chat-widget-open-link:hover, #lc-chat-widget-close:hover, #lc-chat-widget-new-thread:hover, #lc-chat-widget-history:hover) {
  background: rgba(127, 200, 255, 0.08);
  color: #ffffff;
}
#lc-chat-widget-new-thread {
  display: none;
}
#lc-chat-widget-panel[data-thread-started='true'] #lc-chat-widget-new-thread {
  display: inline-flex;
}
#lc-chat-widget-history {
  display: none;
}
#lc-chat-widget-panel[data-saved-threads='true'] #lc-chat-widget-history {
  display: inline-flex;
}
#lc-chat-widget-panel[data-history-open='true'] #lc-chat-widget-history {
  background: rgba(127, 200, 255, 0.12);
  color: #006ddd;
}
#lc-chat-widget-panel[data-theme='dark'][data-history-open='true'] #lc-chat-widget-history {
  background: rgba(127, 200, 255, 0.12);
  color: #ffffff;
}
#lc-chat-widget-body { position: relative; flex: 1 1 auto; min-height: 0; }
#lc-chat-widget-iframe {
  width: 100%;
  height: 100%;
  border: 0;
  opacity: 0;
  transition: opacity 200ms ease;
  background: #ffffff;
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-iframe { background: #030710; }
#lc-chat-widget-panel[data-ready='true'] #lc-chat-widget-iframe { opacity: 1; }
#lc-chat-widget-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.92);
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-loading {
  background: rgba(3, 7, 16, 0.94);
}
#lc-chat-widget-panel[data-ready='true'] #lc-chat-widget-loading { display: none; }
#lc-chat-widget-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(22, 31, 52, 0.12);
  border-top-color: #006DDD;
  border-radius: 999px;
  animation: lc-chat-widget-spin 0.8s linear infinite;
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-spinner {
  border-color: rgba(127, 200, 255, 0.15);
  border-top-color: #7FC8FF;
}
@keyframes lc-chat-widget-spin { to { transform: rotate(360deg); } }
@media (max-width: 768px) {
  :root { --lc-chat-panel-width: 100vw; }
  #lc-chat-widget-panel { width: 100vw; }
}
#lc-chat-widget-resize-handle {
  position: absolute;
  top: 0;
  left: -4px;
  width: 8px;
  height: 100%;
  cursor: ew-resize;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
#lc-chat-widget-resize-handle::before {
  content: '';
  width: 3px;
  height: 36px;
  border-radius: 999px;
  background: transparent;
  transition: background 150ms ease;
}
#lc-chat-widget-resize-handle:hover::before,
#lc-chat-widget-resize-handle.lc-dragging::before {
  background: rgba(22, 31, 52, 0.2);
}
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-resize-handle:hover::before,
#lc-chat-widget-panel[data-theme='dark'] #lc-chat-widget-resize-handle.lc-dragging::before {
  background: rgba(127, 200, 255, 0.3);
}
@media (max-width: 768px) {
  #lc-chat-widget-resize-handle { display: none; }
}
/* Mintlify "On this page" (#content-side-layout) uses full viewport width for layout;
   hide it while the chat panel is open so the main column is not squeezed on viewports < 1800px. */
@media (max-width: 1799px) {
  html.${ROOT_OPEN_CLASS} #content-side-layout {
    display: none !important;
  }
}
`
  );
  function ChatLangChainEmbed({
    theme,
    apiUrl,
    assistantId,
    onReady
  }) {
    if (typeof window === "undefined") return null;
    if (window[WIDGET_INIT_KEY]) return null;
    window[WIDGET_INIT_KEY] = true;
    var panelReady = false;
    var panelOpen = false;
    var iframe = null;
    var fallbackTimer = 0;
    var appRoot = null;
    var currentPanelWidth = lcGetPanelWidth();
    var isDragging = false;
    var dragStartX = 0;
    var dragStartWidth = 0;
    if (!document.getElementById(WIDGET_STYLE_ID)) {
      var style = document.createElement("style");
      style.id = WIDGET_STYLE_ID;
      style.textContent = WIDGET_CSS;
      document.head.appendChild(style);
    }
    var panel = document.createElement("aside");
    panel.id = "lc-chat-widget-panel";
    panel.setAttribute("aria-label", "Chat LangChain");
    panel.setAttribute("data-ready", "false");
    panel.setAttribute("data-theme", lcDetectPageTheme());
    panel.innerHTML = /*html*/
    `
    <div id="lc-chat-widget-resize-handle" aria-hidden="true"></div>
    <div id="lc-chat-widget-header">
      <h2 id="lc-chat-widget-title">Chat LangChain</h2>
      <div id="lc-chat-widget-actions">
        <button id="lc-chat-widget-history" type="button" aria-label="Past chats" title="Past chats" aria-pressed="false">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button id="lc-chat-widget-new-thread" type="button" aria-label="Start a new thread" title="Start a new thread">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L12 14l-4 1 1-4 7.5-7.5z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <a id="lc-chat-widget-open-link" href="${CHAT_APP_URL}" target="_blank" rel="noreferrer" aria-label="Open Chat LangChain in a new tab" title="Open chat.langchain.com in a new tab">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M14 5h5v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 14 19 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M19 14v4a1 1 0 0 1-1 1h-12a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </a>
        <button id="lc-chat-widget-close" type="button" aria-label="Close Chat LangChain" title="Close panel">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>
    <div id="lc-chat-widget-body">
      <div id="lc-chat-widget-loading" aria-hidden="true"><div id="lc-chat-widget-spinner"></div></div>
    </div>
  `;
    document.body.appendChild(panel);
    function syncBannerPanelOffset() {
      var hasBanner = !!document.getElementById("banner");
      panel.setAttribute("data-lc-banner-offset", hasBanner ? "true" : "false");
    }
    syncBannerPanelOffset();
    var bannerOffsetRaf = 0;
    var bannerObserver = new MutationObserver(function() {
      if (bannerOffsetRaf) return;
      bannerOffsetRaf = requestAnimationFrame(function() {
        bannerOffsetRaf = 0;
        syncBannerPanelOffset();
      });
    });
    bannerObserver.observe(document.body, { childList: true, subtree: true });
    var panelBody = document.getElementById("lc-chat-widget-body");
    var closeButton = document.getElementById("lc-chat-widget-close");
    var historyButton = document.getElementById("lc-chat-widget-history");
    var newThreadButton = document.getElementById("lc-chat-widget-new-thread");
    var openLink = document.getElementById("lc-chat-widget-open-link");
    var resizeHandle = document.getElementById("lc-chat-widget-resize-handle");
    function syncTheme() {
      var t = theme ?? lcDetectPageTheme();
      panel.setAttribute("data-theme", t);
      if (iframe && panelReady && iframe.contentWindow) {
        iframe.contentWindow.postMessage({ type: "CHAT_LC_SET_THEME", theme: t }, "*");
      }
    }
    function ensureAppRoot() {
      if (appRoot && document.body.contains(appRoot)) return appRoot;
      appRoot = document.querySelector("body > .antialiased") || document.querySelector("body > div.antialiased") || document.querySelector("body > div:not(#lc-chat-widget-panel)");
      return appRoot;
    }
    function clampWidth(w) {
      return Math.round(
        Math.max(MIN_PANEL_WIDTH, Math.min(window.innerWidth * MAX_PANEL_WIDTH_RATIO, w))
      );
    }
    function updatePanelWidth(w) {
      currentPanelWidth = clampWidth(w);
      document.documentElement.style.setProperty("--lc-chat-panel-width", currentPanelWidth + "px");
      var root = ensureAppRoot();
      if (root && panelOpen) root.style.marginRight = currentPanelWidth + "px";
    }
    function updateLayout() {
      var root = ensureAppRoot();
      if (window.innerWidth <= MOBILE_BREAKPOINT) {
        document.documentElement.style.setProperty("--lc-chat-panel-width", "100vw");
      } else {
        currentPanelWidth = clampWidth(currentPanelWidth);
        document.documentElement.style.setProperty("--lc-chat-panel-width", currentPanelWidth + "px");
      }
      if (root) {
        root.style.transition = "margin-right " + PANEL_TRANSITION;
        root.style.marginRight = panelOpen && window.innerWidth > MOBILE_BREAKPOINT ? currentPanelWidth + "px" : "";
      }
    }
    function ensureIframe() {
      if (iframe) return;
      iframe = document.createElement("iframe");
      iframe.id = "lc-chat-widget-iframe";
      iframe.src = lcGetEmbedSrc(apiUrl, assistantId);
      iframe.title = "Chat LangChain";
      iframe.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms allow-popups");
      iframe.setAttribute("allow", "clipboard-write");
      iframe.addEventListener("load", function handleLoad() {
        if (panelReady) return;
        fallbackTimer = window.setTimeout(setPanelReady, 1500);
      });
      panelBody.appendChild(iframe);
    }
    function sendPageContext() {
      if (iframe && panelReady && iframe.contentWindow) {
        iframe.contentWindow.postMessage(
          { type: "CHAT_LC_SET_CONTEXT", pageUrl: window.location.href },
          "*"
        );
      }
    }
    function setPanelReady() {
      if (panelReady) return;
      panelReady = true;
      panel.setAttribute("data-ready", "true");
      if (fallbackTimer) {
        window.clearTimeout(fallbackTimer);
        fallbackTimer = 0;
      }
      syncTheme();
      sendPageContext();
      if (onReady) onReady();
    }
    function updateOpenLink(threadId) {
      if (!openLink) return;
      if (threadId) {
        openLink.href = CHAT_APP_URL + "?threadId=" + encodeURIComponent(threadId);
      } else {
        openLink.href = CHAT_APP_URL;
      }
    }
    function markThreadStarted() {
      panel.setAttribute("data-thread-started", "true");
    }
    function setHistoryPanelOpen(open) {
      panel.setAttribute("data-history-open", open ? "true" : "false");
      historyButton.setAttribute("aria-pressed", open ? "true" : "false");
    }
    function setSavedThreadsIndicator(has) {
      panel.setAttribute("data-saved-threads", has ? "true" : "false");
    }
    function startNewThread() {
      panel.setAttribute("data-thread-started", "false");
      setHistoryPanelOpen(false);
      updateOpenLink(null);
      if (fallbackTimer) {
        window.clearTimeout(fallbackTimer);
        fallbackTimer = 0;
      }
      ensureIframe();
      if (!iframe) return;
      panelReady = false;
      panel.setAttribute("data-ready", "false");
      iframe.src = lcGetEmbedSrc(apiUrl, assistantId, Date.now());
    }
    function openPanel() {
      ensureIframe();
      panelOpen = true;
      document.documentElement.classList.add(ROOT_OPEN_CLASS);
      updateLayout();
      sendPageContext();
    }
    function closePanel() {
      panelOpen = false;
      document.documentElement.classList.remove(ROOT_OPEN_CLASS);
      updateLayout();
      setHistoryPanelOpen(false);
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({ type: "CHAT_LC_SET_HISTORY_VIEW", open: false }, "*");
      }
    }
    document.addEventListener(
      "click",
      function lcChatTriggerCapture(e) {
        var t = e.target;
        if (!(t instanceof Element)) return;
        var anchor = t.closest('a[href^="https://chat.langchain.com"]');
        if (!anchor || anchor.closest("#lc-chat-widget-panel")) return;
        e.preventDefault();
        openPanel();
      },
      true
    );
    var origPushState = history.pushState.bind(history);
    var origReplaceState = history.replaceState.bind(history);
    function afterDocNav() {
      queueMicrotask(sendPageContext);
    }
    history.pushState = function(data, unused, url) {
      var r = origPushState(data, unused, url);
      afterDocNav();
      return r;
    };
    history.replaceState = function(data, unused, url) {
      var r = origReplaceState(data, unused, url);
      afterDocNav();
      return r;
    };
    closeButton.addEventListener("click", closePanel);
    newThreadButton.addEventListener("click", startNewThread);
    window.addEventListener("keydown", function handleKeydown(event) {
      if (event.key === "Escape" && panelOpen) {
        closePanel();
        return;
      }
      if (event.key === "i" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        if (panelOpen) closePanel();
        else openPanel();
      }
    });
    window.addEventListener("resize", updateLayout, { passive: true });
    window.addEventListener("popstate", sendPageContext);
    window.addEventListener("hashchange", sendPageContext);
    historyButton.addEventListener("click", function() {
      ensureIframe();
      if (!iframe || !iframe.contentWindow) return;
      iframe.contentWindow.postMessage({ type: "CHAT_LC_TOGGLE_HISTORY" }, "*");
    });
    window.addEventListener("message", function handleMessages(event) {
      if (!event.data) return;
      if (event.data.type === "CHAT_LC_READY") setPanelReady();
      if (event.data.type === "CHAT_LC_PROMPT_SENT") markThreadStarted();
      if (event.data.type === "CHAT_LC_THREAD_ID") {
        updateOpenLink(event.data.threadId ?? null);
        if (event.data.threadId) markThreadStarted();
      }
      if (event.data.type === "CHAT_LC_HISTORY_VIEW" && typeof event.data.open === "boolean") {
        setHistoryPanelOpen(event.data.open);
      }
      if (event.data.type === "CHAT_LC_HAS_SAVED_THREADS" && typeof event.data.has === "boolean") {
        setSavedThreadsIndicator(event.data.has);
      }
    });
    resizeHandle.addEventListener("mousedown", function(e) {
      if (window.innerWidth <= MOBILE_BREAKPOINT) return;
      isDragging = true;
      dragStartX = e.clientX;
      dragStartWidth = currentPanelWidth;
      resizeHandle.classList.add("lc-dragging");
      document.body.style.cursor = "ew-resize";
      document.body.style.userSelect = "none";
      if (iframe) iframe.style.pointerEvents = "none";
      e.preventDefault();
    });
    document.addEventListener("mousemove", function(e) {
      if (!isDragging) return;
      updatePanelWidth(dragStartWidth + (dragStartX - e.clientX));
    });
    document.addEventListener("mouseup", function() {
      if (!isDragging) return;
      isDragging = false;
      resizeHandle.classList.remove("lc-dragging");
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      if (iframe) iframe.style.pointerEvents = "";
    });
    var themeObserver = new MutationObserver(syncTheme);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"]
    });
    syncTheme();
    updateLayout();
    return null;
  }
  ChatLangChainEmbed({});
})();
