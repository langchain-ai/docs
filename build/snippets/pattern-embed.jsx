"use client";
import { useEffect, useRef, useState, useCallback } from "react";

export const PatternEmbed = ({
  pattern,
  id,
  theme,
  height,
  minHeight = 400,
  maxHeight = 700,
  className,
  defaultView = "preview",
  defaultSdk = "react",
  defaultLanguage = "js",
  showCodeTab = true,
  agentServer = "prod",
  onError,
  onReady
}) => {
// src/PatternEmbed.tsx

// zod-shim.ts
var VALID_GUEST_TYPES = /* @__PURE__ */ new Set([
  "READY",
  "RESIZE",
  "ERROR",
  "RUN_STARTED",
  "TRACE_URL",
  "THREAD_CLEARED"
]);
function stub() {
  return {
    safeParse: (data) => ({ success: true, data }),
    optional: () => stub(),
    min: () => stub(),
    url: () => stub()
  };
}
var z = {
  object: (_shape) => stub(),
  literal: (_value) => stub(),
  string: () => stub(),
  number: () => stub(),
  boolean: () => stub(),
  enum: (_values) => stub(),
  array: (_el) => stub(),
  union: (_schemas) => stub(),
  record: (_key, _value) => stub(),
  discriminatedUnion: (_key, _schemas) => ({
    safeParse(data) {
      if (
        // oxlint-disable-next-line eqeqeq
        data != null && typeof data === "object" && "type" in data && typeof data.type === "string" && VALID_GUEST_TYPES.has(data.type)
      ) {
        return { success: true, data };
      }
      return { success: false };
    },
    optional: () => stub(),
    min: () => stub(),
    url: () => stub()
  })
};

// ../preview-protocol/src/types.ts
var SetThemeMessageSchema = z.object({
  type: z.literal("SET_THEME"),
  theme: z.enum(["light", "dark"])
});
var SetPatternMessageSchema = z.object({
  type: z.literal("SET_PATTERN"),
  slug: z.string()
});
var ResetMessageSchema = z.object({
  type: z.literal("RESET")
});
var SetViewMessageSchema = z.object({
  type: z.literal("SET_VIEW"),
  view: z.enum(["preview", "code"])
});
var SetLanguageMessageSchema = z.object({
  type: z.literal("SET_LANGUAGE"),
  language: z.enum(["js", "python"])
});
var CodeFileSchema = z.object({
  filename: z.string(),
  content: z.string()
});
var UpdateCodeMessageSchema = z.object({
  type: z.literal("UPDATE_CODE"),
  files: z.array(CodeFileSchema).min(1),
  entryFile: z.string()
});
var TrackEventMessageSchema = z.object({
  type: z.literal("TRACK_EVENT"),
  name: z.string(),
  properties: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).optional()
});
var HostToGuestMessageSchema = z.discriminatedUnion("type", [
  SetThemeMessageSchema,
  SetPatternMessageSchema,
  ResetMessageSchema,
  UpdateCodeMessageSchema,
  SetViewMessageSchema,
  SetLanguageMessageSchema,
  TrackEventMessageSchema
]);
var ReadyMessageSchema = z.object({
  type: z.literal("READY"),
  framework: z.enum(["react", "vue", "angular", "svelte"])
});
var ResizeMessageSchema = z.object({
  type: z.literal("RESIZE"),
  height: z.number()
});
var ErrorMessageSchema = z.object({
  type: z.literal("ERROR"),
  message: z.string(),
  stack: z.string().optional()
});
var RunStartedMessageSchema = z.object({
  type: z.literal("RUN_STARTED"),
  runId: z.string()
});
var TraceUrlMessageSchema = z.object({
  type: z.literal("TRACE_URL"),
  url: z.string().url(),
  runId: z.string()
});
var ThreadClearedMessageSchema = z.object({
  type: z.literal("THREAD_CLEARED")
});
var GuestToHostMessageSchema = z.discriminatedUnion("type", [
  ReadyMessageSchema,
  ResizeMessageSchema,
  ErrorMessageSchema,
  RunStartedMessageSchema,
  TraceUrlMessageSchema,
  ThreadClearedMessageSchema
]);
var PreviewMessageSchema = z.union([HostToGuestMessageSchema, GuestToHostMessageSchema]);

// ../preview-protocol/src/host.ts
function isOriginAllowed(origin, allowedOrigins) {
  return allowedOrigins.includes("*") || allowedOrigins.includes(origin);
}
function createPreviewHost(iframe, options) {
  const { allowedOrigins } = options;
  const targetOrigins = options.targetOrigins ?? allowedOrigins;
  const listeners = /* @__PURE__ */ new Map();
  function postToGuest(message) {
    if (!iframe.contentWindow) return;
    for (const origin of targetOrigins) {
      iframe.contentWindow.postMessage(message, origin);
    }
  }
  function addListener(type, callback) {
    if (!listeners.has(type)) {
      listeners.set(type, /* @__PURE__ */ new Set());
    }
    listeners.get(type).add(callback);
    return () => {
      listeners.get(type)?.delete(callback);
    };
  }
  function handleMessage(event) {
    if (!isOriginAllowed(event.origin, allowedOrigins)) return;
    const result = GuestToHostMessageSchema.safeParse(event.data);
    if (!result.success) return;
    const msg = result.data;
    const cbs = listeners.get(msg.type);
    if (!cbs) return;
    for (const cb of cbs) {
      switch (msg.type) {
        case "READY":
          cb(msg.framework);
          break;
        case "RESIZE":
          cb(msg.height);
          break;
        case "ERROR":
          cb(msg.message, msg.stack);
          break;
        case "RUN_STARTED":
          cb(msg.runId);
          break;
        case "TRACE_URL":
          cb(msg.url, msg.runId);
          break;
        case "THREAD_CLEARED":
          cb();
          break;
      }
    }
  }
  window.addEventListener("message", handleMessage);
  return {
    setTheme(theme) {
      postToGuest({ type: "SET_THEME", theme });
    },
    setPattern(slug) {
      postToGuest({ type: "SET_PATTERN", slug });
    },
    setView(view) {
      postToGuest({ type: "SET_VIEW", view });
    },
    setLanguage(language) {
      postToGuest({ type: "SET_LANGUAGE", language });
    },
    updateCode(files, entryFile) {
      postToGuest({ type: "UPDATE_CODE", files, entryFile });
    },
    reset() {
      postToGuest({ type: "RESET" });
    },
    trackEvent(name, properties) {
      postToGuest({ type: "TRACK_EVENT", name, properties });
    },
    onReady(callback) {
      return addListener("READY", callback);
    },
    onResize(callback) {
      return addListener("RESIZE", callback);
    },
    onError(callback) {
      return addListener("ERROR", callback);
    },
    onRunStarted(callback) {
      return addListener("RUN_STARTED", callback);
    },
    onTraceUrl(callback) {
      return addListener("TRACE_URL", callback);
    },
    onThreadCleared(callback) {
      return addListener("THREAD_CLEARED", callback);
    },
    destroy() {
      window.removeEventListener("message", handleMessage);
      listeners.clear();
    }
  };
}

// src/constants.ts
var PROD_BASE = "https://ui-patterns.langchain.com";

// src/PatternEmbed.tsx
var SDK_LABELS = {
  react: "React",
  vue: "Vue",
  svelte: "Svelte",
  angular: "Angular"
};
var SDK_LOCAL_HOSTS = {
  react: "http://localhost:4100",
  vue: "http://localhost:4200",
  svelte: "http://localhost:4300",
  angular: "http://localhost:4400"
};
var SDK_PROD_HOSTS = {
  react: `${PROD_BASE}/react`,
  vue: `${PROD_BASE}/vue`,
  svelte: `${PROD_BASE}/svelte`,
  angular: `${PROD_BASE}/angular`
};
var SDK_LOGOS = {
  react: `<svg width="14" height="14" viewBox="0 -14 256 256" xmlns="http://www.w3.org/2000/svg"><path d="M210.483381,73.8236374 C207.827698,72.9095503 205.075867,72.0446761 202.24247,71.2267368 C202.708172,69.3261098 203.135596,67.4500894 203.515631,65.6059664 C209.753843,35.3248922 205.675082,10.9302478 191.747328,2.89849283 C178.392359,-4.80289661 156.551327,3.22703567 134.492936,22.4237776 C132.371761,24.2697233 130.244662,26.2241201 128.118477,28.2723861 C126.701777,26.917204 125.287358,25.6075897 123.876584,24.3549348 C100.758745,3.82852863 77.5866802,-4.82157937 63.6725966,3.23341515 C50.3303869,10.9571328 46.3792156,33.8904224 51.9945178,62.5880206 C52.5367729,65.3599011 53.1706189,68.1905639 53.8873982,71.068617 C50.6078941,71.9995641 47.4418534,72.9920277 44.4125156,74.0478303 C17.3093297,83.497195 0,98.3066828 0,113.667995 C0,129.533287 18.5815786,145.446423 46.8116526,155.095373 C49.0394553,155.856809 51.3511025,156.576778 53.7333796,157.260293 C52.9600965,160.37302 52.2875179,163.423318 51.7229345,166.398431 C46.3687351,194.597975 50.5500231,216.989464 63.8566899,224.664425 C77.6012619,232.590464 100.66852,224.443422 123.130185,204.809231 C124.905501,203.257196 126.687196,201.611293 128.472081,199.886102 C130.785552,202.113904 133.095375,204.222319 135.392897,206.199955 C157.14963,224.922338 178.637969,232.482469 191.932332,224.786092 C205.663234,216.837268 210.125675,192.78347 204.332202,163.5181 C203.88974,161.283006 203.374826,158.99961 202.796573,156.675661 C204.416503,156.196743 206.006814,155.702335 207.557482,155.188332 C236.905331,145.46465 256,129.745175 256,113.667995 C256,98.2510906 238.132466,83.3418093 210.483381,73.8236374 Z M204.118035,144.807565 C202.718197,145.270987 201.281904,145.718918 199.818271,146.153177 C196.578411,135.896354 192.205739,124.989735 186.854729,113.72131 C191.961041,102.721277 196.164656,91.9540963 199.313837,81.7638014 C201.93261,82.5215915 204.474374,83.3208483 206.923636,84.1643056 C230.613348,92.3195488 245.063763,104.377206 245.063763,113.667995 C245.063763,123.564379 229.457753,136.411268 204.118035,144.807565 Z M193.603754,165.642007 C196.165567,178.582766 196.531475,190.282717 194.834536,199.429057 C193.309843,207.64764 190.243595,213.12715 186.452366,215.321689 C178.384612,219.991462 161.131788,213.921395 142.525146,197.909832 C140.392124,196.074366 138.243609,194.114502 136.088259,192.040261 C143.301619,184.151133 150.510878,174.979732 157.54698,164.793993 C169.922699,163.695814 181.614905,161.900447 192.218042,159.449363 C192.740247,161.555956 193.204126,163.621993 193.603754,165.642007 Z M87.2761866,214.514686 C79.3938934,217.298414 73.1160375,217.378157 69.3211631,215.189998 C61.2461189,210.532528 57.8891498,192.554265 62.4682434,168.438039 C62.9927272,165.676183 63.6170041,162.839142 64.3365173,159.939216 C74.8234575,162.258154 86.4299951,163.926841 98.8353334,164.932519 C105.918826,174.899534 113.336329,184.06091 120.811247,192.08264 C119.178102,193.65928 117.551336,195.16028 115.933685,196.574699 C106.001303,205.256705 96.0479605,211.41654 87.2761866,214.514686 Z M50.3486141,144.746959 C37.8658105,140.48046 27.5570398,134.935332 20.4908634,128.884403 C14.1414664,123.446815 10.9357817,118.048415 10.9357817,113.667995 C10.9357817,104.34622 24.8334611,92.4562517 48.0123604,84.3748281 C50.8247961,83.3942121 53.7689223,82.4701001 56.8242337,81.6020363 C60.0276398,92.0224477 64.229889,102.917218 69.3011135,113.93411 C64.1642716,125.11459 59.9023288,136.182975 56.6674809,146.725506 C54.489347,146.099407 52.3791089,145.440499 50.3486141,144.746959 Z M62.7270678,60.4878073 C57.9160346,35.9004118 61.1112387,17.3525532 69.1516515,12.6982729 C77.7160924,7.74005624 96.6544653,14.8094222 116.614922,32.5329619 C117.890816,33.6657739 119.171723,34.8514442 120.456275,36.0781256 C113.018267,44.0647686 105.66866,53.1573386 98.6480514,63.0655695 C86.6081646,64.1815215 75.0831931,65.9741531 64.4868907,68.3746571 C63.8206914,65.6948233 63.2305903,63.0619242 62.7270678,60.4878073 Z M173.153901,87.7550367 C170.620796,83.3796304 168.020249,79.1076627 165.369124,74.9523483 C173.537126,75.9849113 181.362914,77.3555864 188.712066,79.0329319 C186.505679,86.1041206 183.755673,93.4974728 180.518546,101.076741 C178.196419,96.6680702 175.740322,92.2229454 173.153901,87.7550367 Z M128.122121,43.8938899 C133.166461,49.3588189 138.218091,55.4603279 143.186789,62.0803968 C138.179814,61.8439007 133.110868,61.720868 128.000001,61.720868 C122.937434,61.720868 117.905854,61.8411667 112.929865,62.0735617 C117.903575,55.515009 122.99895,49.4217021 128.122121,43.8938899 Z M82.8018984,87.830679 C80.2715265,92.2183886 77.8609975,96.6393627 75.5753239,101.068539 C72.3906004,93.5156998 69.6661103,86.0886276 67.440586,78.9171899 C74.7446255,77.2826781 82.5335049,75.9461789 90.6495601,74.9332099 C87.9610684,79.1268011 85.3391054,83.4302106 82.8018984,87.8297677 Z M90.8833221,153.182899 C82.4979621,152.247395 74.5919739,150.979704 67.289757,149.390303 C69.5508242,142.09082 72.3354636,134.505173 75.5876271,126.789657 C77.8792246,131.215644 80.2993228,135.638441 82.8451877,140.03572 C85.4388987,144.515476 88.1255676,148.90364 90.8833221,153.182899 Z M128.424691,184.213105 C123.24137,178.620587 118.071264,172.434323 113.021912,165.780078 C117.923624,165.972373 122.921029,166.0708 128.000001,166.0708 C133.217953,166.0708 138.376211,165.953235 143.45336,165.727219 C138.468257,172.501308 133.434855,178.697141 128.424691,184.213105 Z M180.622896,126.396409 C184.044571,134.195313 186.929004,141.741317 189.219234,148.9164 C181.796719,150.609693 173.782736,151.973534 165.339049,152.986959 C167.996555,148.775595 170.619884,144.430263 173.197646,139.960532 C175.805484,135.438399 178.28163,130.90943 180.622896,126.396409 Z M163.724586,134.496971 C159.722835,141.435557 155.614455,148.059271 151.443648,154.311611 C143.847063,154.854776 135.998946,155.134562 128.000001,155.134562 C120.033408,155.134562 112.284171,154.887129 104.822013,154.402745 C100.48306,148.068386 96.285368,141.425078 92.3091341,134.556664 C88.3442923,127.706935 84.6943232,120.799333 81.3870228,113.930466 C84.6934118,107.045648 88.3338117,100.130301 92.276781,93.292874 C96.2293193,86.4385872 100.390102,79.8276317 104.688954,73.5329157 C112.302398,72.9573964 120.109505,72.6571055 127.999545,72.6571055 C135.925583,72.6571055 143.742714,72.9596746 151.353879,73.5402067 C155.587114,79.7888993 159.719645,86.3784378 163.688588,93.2350031 C167.702644,100.168578 171.389978,107.037901 174.724618,113.77508 C171.400003,120.627999 167.720871,127.566587 163.724586,134.496971 Z M186.284677,12.3729198 C194.857321,17.3165548 198.191049,37.2542268 192.804953,63.3986692 C192.461372,65.0669011 192.074504,66.7661189 191.654369,68.4881206 C181.03346,66.0374921 169.500286,64.2138746 157.425315,63.0810626 C150.391035,53.0639249 143.101577,43.9572289 135.784778,36.073113 C137.751934,34.1806885 139.716356,32.3762092 141.672575,30.673346 C160.572216,14.2257007 178.236518,7.73185406 186.284677,12.3729198 Z M128.000001,90.8080696 C140.624975,90.8080696 150.859926,101.042565 150.859926,113.667995 C150.859926,126.292969 140.624975,136.527922 128.000001,136.527922 C115.375026,136.527922 105.140075,126.292969 105.140075,113.667995 C105.140075,101.042565 115.375026,90.8080696 128.000001,90.8080696 Z" fill="#00D8FF"/></svg>`,
  vue: `<svg width="14" height="14" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 4L16 28L30 4H24.5L16 18.5L7.5 4H2Z" fill="#41B883"/><path d="M7.5 4L16 18.5L24.5 4H19.5L16.0653 10.0126L12.5 4H7.5Z" fill="#35495E"/></svg>`,
  svelte: `<svg width="14" height="14" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><path d="M26.47,5.7A8.973,8.973,0,0,0,14.677,3.246L7.96,7.4a7.461,7.461,0,0,0-3.481,5.009,7.686,7.686,0,0,0,.8,5.058,7.358,7.358,0,0,0-1.151,2.8,7.789,7.789,0,0,0,1.4,6.028,8.977,8.977,0,0,0,11.794,2.458L24.04,24.6a7.468,7.468,0,0,0,3.481-5.009,7.673,7.673,0,0,0-.8-5.062,7.348,7.348,0,0,0,1.152-2.8A7.785,7.785,0,0,0,26.47,5.7" fill="#ff3e00"/><path d="M14.022,26.64A5.413,5.413,0,0,1,8.3,24.581a4.678,4.678,0,0,1-.848-3.625,4.307,4.307,0,0,1,.159-.61l.127-.375.344.238a8.76,8.76,0,0,0,2.628,1.274l.245.073-.025.237a1.441,1.441,0,0,0,.271.968,1.63,1.63,0,0,0,1.743.636,1.512,1.512,0,0,0,.411-.175l6.7-4.154a1.366,1.366,0,0,0,.633-.909,1.407,1.407,0,0,0-.244-1.091,1.634,1.634,0,0,0-1.726-.622,1.509,1.509,0,0,0-.413.176l-2.572,1.584a4.934,4.934,0,0,1-1.364.582,5.415,5.415,0,0,1-5.727-2.06A4.678,4.678,0,0,1,7.811,13.1,4.507,4.507,0,0,1,9.9,10.09l6.708-4.154a4.932,4.932,0,0,1,1.364-.581A5.413,5.413,0,0,1,23.7,7.414a4.679,4.679,0,0,1,.848,3.625,4.272,4.272,0,0,1-.159.61l-.127.375-.344-.237a8.713,8.713,0,0,0-2.628-1.274l-.245-.074.025-.237a1.438,1.438,0,0,0-.272-.968,1.629,1.629,0,0,0-1.725-.622,1.484,1.484,0,0,0-.411.176l-6.722,4.14a1.353,1.353,0,0,0-.631.908,1.394,1.394,0,0,0,.244,1.092,1.634,1.634,0,0,0,1.726.621,1.538,1.538,0,0,0,.413-.175l2.562-1.585a4.9,4.9,0,0,1,1.364-.581,5.417,5.417,0,0,1,5.728,2.059,4.681,4.681,0,0,1,.843,3.625A4.5,4.5,0,0,1,22.1,21.905l-6.707,4.154a4.9,4.9,0,0,1-1.364.581" fill="#fff"/></svg>`,
  angular: `<svg width="14" height="14" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#a-clip)"><mask id="a-mask" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="14" y="0" width="484" height="512"><path d="M14 0h484v512H14V0z" fill="#fff"/></mask><g mask="url(#a-mask)"><path d="M496 86l-18 272L312 0l184 86zM380 438l-124 72-126-72 24-62h202l24 62zM256 136l64 160H190l66-160zM32 358L14 86 198 0 32 358z" fill="url(#a-grad1)"/><path d="M496 86l-18 272L312 0l184 86zM380 438l-124 72-126-72 24-62h202l24 62zM256 136l64 160H190l66-160zM32 358L14 86 198 0 32 358z" fill="url(#a-grad2)"/></g></g><defs><linearGradient id="a-grad1" x1="120.4" y1="463.8" x2="504" y2="281.4" gradientUnits="userSpaceOnUse"><stop stop-color="#E40035"/><stop offset=".2" stop-color="#F60A48"/><stop offset=".4" stop-color="#F20755"/><stop offset=".5" stop-color="#DC087D"/><stop offset=".7" stop-color="#9717E7"/><stop offset="1" stop-color="#6C00F5"/></linearGradient><linearGradient id="a-grad2" x1="103" y1="61.4" x2="354" y2="348" gradientUnits="userSpaceOnUse"><stop stop-color="#FF31D9"/><stop offset="1" stop-color="#FF5BE1" stop-opacity="0"/></linearGradient><clipPath id="a-clip"><path fill="#fff" transform="translate(14)" d="M0 0h484v512H0z"/></clipPath></defs></svg>`
};
var PROD_AGENT_API_BASE = `${PROD_BASE}/api/langgraph`;
function normalizeAgentServerBase(agentServer, useLocalPreview) {
  const trimmed = agentServer.trim();
  if (useLocalPreview) {
    return "http://127.0.0.1:2024";
  }
  if (trimmed === "prod") {
    return PROD_AGENT_API_BASE;
  }
  if (trimmed === "local") {
    return PROD_AGENT_API_BASE;
  }
  return PROD_AGENT_API_BASE;
}
function isLocalhost() {
  if (typeof window === "undefined") return false;
  const { hostname } = window.location;
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "[::]";
}
function detectPageTheme() {
  if (typeof document === "undefined") return "light";
  const el = document.documentElement;
  if (el.classList.contains("dark")) return "dark";
  if (el.getAttribute("data-theme") === "dark") return "dark";
  if (el.style.colorScheme === "dark") return "dark";
  return "light";
}
var CACHE_KEY = "__lcPlaygroundIframeCache";
var iframeCache = globalThis[CACHE_KEY] ?? (() => {
  const m = /* @__PURE__ */ new Map();
  globalThis[CACHE_KEY] = m;
  return m;
})();
var SDK_CACHE_KEY = "__lcPlaygroundSdkCache";
var sdkCache = globalThis[SDK_CACHE_KEY] ?? (() => {
  const m = /* @__PURE__ */ new Map();
  globalThis[SDK_CACHE_KEY] = m;
  return m;
})();
var LANG_CACHE_KEY = "__lcPlaygroundLangCache";
var langCache = globalThis[LANG_CACHE_KEY] ?? (() => {
  const m = /* @__PURE__ */ new Map();
  globalThis[LANG_CACHE_KEY] = m;
  return m;
})();
var INSTANCE_COUNTER_KEY = "__lcPlaygroundInstanceCounter";
function nextAutoInstanceIndex() {
  const g = globalThis;
  const state = g[INSTANCE_COUNTER_KEY] ?? (() => {
    const s = { n: 0, resetScheduled: false };
    g[INSTANCE_COUNTER_KEY] = s;
    return s;
  })();
  const index = state.n++;
  if (!state.resetScheduled) {
    state.resetScheduled = true;
    queueMicrotask(() => {
      state.n = 0;
      state.resetScheduled = false;
    });
  }
  return index;
}
var VIEW_EYE_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
var VIEW_CODE_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;
var CHEVRON_DOWN_SVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`;
var TRACE_ICON_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`;
var TRACE_SPINNER_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="animate-spin"><circle cx="12" cy="12" r="10" opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/></svg>`;
var EXTERNAL_LINK_SVG = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`;
var DOWNLOAD_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`;
var EXPAND_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`;
var CLOSE_SVG = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
var LANG_TS_SVG = `<svg fill="none" height="18" viewBox="0 0 512 512" width="18" xmlns="http://www.w3.org/2000/svg"><rect fill="#3178c6" height="512" rx="50" width="512"/><rect fill="#3178c6" height="512" rx="50" width="512"/><path clip-rule="evenodd" d="m316.939 407.424v50.061c8.138 4.172 17.763 7.3 28.875 9.386s22.823 3.129 35.135 3.129c11.999 0 23.397-1.147 34.196-3.442 10.799-2.294 20.268-6.075 28.406-11.342 8.138-5.266 14.581-12.15 19.328-20.65s7.121-19.007 7.121-31.522c0-9.074-1.356-17.026-4.069-23.857s-6.625-12.906-11.738-18.225c-5.112-5.319-11.242-10.091-18.389-14.315s-15.207-8.213-24.18-11.967c-6.573-2.712-12.468-5.345-17.685-7.9-5.217-2.556-9.651-5.163-13.303-7.822-3.652-2.66-6.469-5.476-8.451-8.448-1.982-2.973-2.974-6.336-2.974-10.091 0-3.441.887-6.544 2.661-9.308s4.278-5.136 7.512-7.118c3.235-1.981 7.199-3.52 11.894-4.615 4.696-1.095 9.912-1.642 15.651-1.642 4.173 0 8.581.313 13.224.938 4.643.626 9.312 1.591 14.008 2.894 4.695 1.304 9.259 2.947 13.694 4.928 4.434 1.982 8.529 4.276 12.285 6.884v-46.776c-7.616-2.92-15.937-5.084-24.962-6.492s-19.381-2.112-31.066-2.112c-11.895 0-23.163 1.278-33.805 3.833s-20.006 6.544-28.093 11.967c-8.086 5.424-14.476 12.333-19.171 20.729-4.695 8.395-7.043 18.433-7.043 30.114 0 14.914 4.304 27.638 12.912 38.172 8.607 10.533 21.675 19.45 39.204 26.751 6.886 2.816 13.303 5.579 19.25 8.291s11.086 5.528 15.415 8.448c4.33 2.92 7.747 6.101 10.252 9.543 2.504 3.441 3.756 7.352 3.756 11.733 0 3.233-.783 6.231-2.348 8.995s-3.939 5.162-7.121 7.196-7.147 3.624-11.894 4.771c-4.748 1.148-10.303 1.721-16.668 1.721-10.851 0-21.597-1.903-32.24-5.71-10.642-3.806-20.502-9.516-29.579-17.13zm-84.159-123.342h64.22v-41.082h-179v41.082h63.906v182.918h50.874z" fill="#fff" fill-rule="evenodd"/></svg>`;
var LANG_PYTHON_SVG = `<svg version="1.1" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://web.resource.org/cc/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="18px" height="18px" viewBox="0.21 -0.077 110 110" enable-background="new 0.21 -0.077 110 110" xml:space="preserve"><linearGradient id="SVGID_1_" gradientUnits="userSpaceOnUse" x1="63.8159" y1="56.6829" x2="118.4934" y2="1.8225" gradientTransform="matrix(1 0 0 -1 -53.2974 66.4321)"> <stop offset="0" style="stop-color:#387EB8"/> <stop offset="1" style="stop-color:#366994"/></linearGradient><path fill="url(#SVGID_1_)" d="M55.023-0.077c-25.971,0-26.25,10.081-26.25,12.156c0,3.148,0,12.594,0,12.594h26.75v3.781 c0,0-27.852,0-37.375,0c-7.949,0-17.938,4.833-17.938,26.25c0,19.673,7.792,27.281,15.656,27.281c2.335,0,9.344,0,9.344,0 s0-9.765,0-13.125c0-5.491,2.721-15.656,15.406-15.656c15.91,0,19.971,0,26.531,0c3.902,0,14.906-1.696,14.906-14.406 c0-13.452,0-17.89,0-24.219C82.054,11.426,81.515-0.077,55.023-0.077z M40.273,8.392c2.662,0,4.813,2.15,4.813,4.813 c0,2.661-2.151,4.813-4.813,4.813s-4.813-2.151-4.813-4.813C35.46,10.542,37.611,8.392,40.273,8.392z"/><linearGradient id="SVGID_2_" gradientUnits="userSpaceOnUse" x1="97.0444" y1="21.6321" x2="155.6665" y2="-34.5308" gradientTransform="matrix(1 0 0 -1 -53.2974 66.4321)"> <stop offset="0" style="stop-color:#FFE052"/> <stop offset="1" style="stop-color:#FFC331"/></linearGradient><path fill="url(#SVGID_2_)" d="M55.397,109.923c25.959,0,26.282-10.271,26.282-12.156c0-3.148,0-12.594,0-12.594H54.897v-3.781 c0,0,28.032,0,37.375,0c8.009,0,17.938-4.954,17.938-26.25c0-23.322-10.538-27.281-15.656-27.281c-2.336,0-9.344,0-9.344,0 s0,10.216,0,13.125c0,5.491-2.631,15.656-15.406,15.656c-15.91,0-19.476,0-26.532,0c-3.892,0-14.906,1.896-14.906,14.406 c0,14.475,0,18.265,0,24.219C28.366,100.497,31.562,109.923,55.397,109.923z M70.148,101.454c-2.662,0-4.813-2.151-4.813-4.813 s2.15-4.813,4.813-4.813c2.661,0,4.813,2.151,4.813,4.813S72.809,101.454,70.148,101.454z"/></svg>`;
var SDK_OPTIONS = Object.keys(SDK_LABELS).map((k) => [k, SDK_LABELS[k]]);
var EMBED_CSS = `
[data-lc-pe] .lc-tab{font-size:13px;font-family:inherit}
[data-lc-pe] .lc-sdk-option{font-size:13px}
[data-lc-pe] .lc-border{border-color:#B8DFFF}
[data-lc-pe].dark .lc-border{border-color:#1A2740}
[data-lc-pe] .lc-bg-surface{background-color:white}
[data-lc-pe].dark .lc-bg-surface{background-color:#0B1120}
[data-lc-pe] .lc-bg-wash{background-color:#F2FAFF}
[data-lc-pe].dark .lc-bg-wash{background-color:#030710}
[data-lc-pe] .lc-tab-active{background-color:#7FC8FF;color:#030710}
[data-lc-pe] .lc-tab-inactive{background-color:transparent;color:#6B8299}
[data-lc-pe] .lc-tab-inactive:hover{background-color:#E5F4FF;color:#030710}
[data-lc-pe].dark .lc-tab-inactive:hover{background-color:#1A2740;color:#C8DDF0}
[data-lc-pe] .lc-tab-trace{background-color:#FFF3E0;color:#E65100}
[data-lc-pe].dark .lc-tab-trace{background-color:#3E2723;color:#FFB74D}
[data-lc-pe] .lc-tab-trace:hover{background-color:#FFE0B2}
[data-lc-pe].dark .lc-tab-trace:hover{background-color:#4E342E}
[data-lc-pe] .lc-tab-trace-loading{background-color:transparent;color:#6B8299;cursor:not-allowed}
[data-lc-pe] .lc-sdk-btn{border-color:#B8DFFF;background-color:white;font-size:13px;color:#030710}
[data-lc-pe].dark .lc-sdk-btn{border-color:#1A2740;background-color:#0B1120;color:#C8DDF0}
[data-lc-pe] .lc-sdk-btn:hover{background-color:#E5F4FF}
[data-lc-pe].dark .lc-sdk-btn:hover{background-color:#1A2740}
[data-lc-pe] .lc-dropdown{border-color:#B8DFFF;background-color:white;min-width:120px}
[data-lc-pe].dark .lc-dropdown{border-color:#1A2740;background-color:#0B1120}
[data-lc-pe] .lc-sdk-selected{background-color:#E5F4FF;color:#030710}
[data-lc-pe].dark .lc-sdk-selected{background-color:#1A2740;color:#C8DDF0}
[data-lc-pe] .lc-sdk-unselected{color:#6B8299}
[data-lc-pe] .lc-sdk-unselected:hover{background-color:#F2FAFF;color:#030710}
[data-lc-pe].dark .lc-sdk-unselected:hover{background-color:#1A2740;color:#C8DDF0}
[data-lc-pe] .lc-spinner{border-color:#B8DFFF;border-top-color:#7FC8FF}
[data-lc-pe].dark .lc-spinner{border-color:#1A2740;border-top-color:#7FC8FF}
[data-lc-pe] .lc-error{background-color:rgb(178 125 117/0.1);border-color:rgb(178 125 117/0.3);color:#B27D75}
[data-lc-pe] .lc-error-btn{border-color:rgb(178 125 117/0.3);background-color:white;color:#B27D75}
[data-lc-pe].dark .lc-error-btn{background-color:#0B1120}
[data-lc-pe] .lc-lang-switcher .lc-tab{padding:4px 8px}
@media(max-width:639px){
[data-lc-pe] .lc-toolbar{flex-wrap:wrap;gap:8px}
[data-lc-pe] .lc-tab-label{display:none}
[data-lc-pe] .lc-tab{padding-left:10px;padding-right:10px}
[data-lc-pe] .lc-sdk-btn{margin-left:auto}
}
[data-lc-pe] .lc-expand-btn{border:none;background:transparent;cursor:pointer;padding:6px;border-radius:6px;display:inline-flex;align-items:center;justify-content:center;color:#6B8299;transition:background-color 0.15s,color 0.15s}
[data-lc-pe] .lc-expand-btn:hover{background-color:#E5F4FF;color:#030710}
[data-lc-pe].dark .lc-expand-btn:hover{background-color:#1A2740;color:#C8DDF0}
.lc-pe-backdrop{position:fixed;inset:0;z-index:9998;background:rgba(0,0,0,0.4);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
`;

  const slotRef = useRef(null);
  const cardRef = useRef(null);
  const placeholderRef = useRef(null);
  const cachedRef = useRef(null);
  const autoInstanceRef = useRef(null);
  if (!id && autoInstanceRef.current === null) {
    autoInstanceRef.current = `auto-${nextAutoInstanceIndex()}`;
  }
  const instanceKey = id ?? autoInstanceRef.current;
  const useLocalPreview = agentServer === "local" || agentServer === "prod" && isLocalhost();
  const agentQuery = agentServer !== "local" && agentServer !== "prod" ? `?agentServer=${encodeURIComponent(agentServer)}` : "";
  const sdkCacheKey = `${agentServer}|${pattern}|${instanceKey}`;
  const [sdk, setSdkRaw] = useState(() => {
    const fromCache = sdkCache.get(sdkCacheKey);
    if (fromCache) return fromCache;
    const hosts = useLocalPreview ? SDK_LOCAL_HOSTS : SDK_PROD_HOSTS;
    let best = null;
    for (const [s, url] of Object.entries(hosts)) {
      const entry = iframeCache.get(`${url}|${agentQuery}|${instanceKey}`);
      if (entry?.lastActiveAt && (!best || entry.lastActiveAt > best.at)) {
        best = { sdk: s, at: entry.lastActiveAt };
      }
    }
    if (best) return best.sdk;
    return defaultSdk;
  });
  const setSdk = useCallback(
    (s) => {
      sdkCache.set(sdkCacheKey, s);
      setSdkRaw(s);
    },
    [sdkCacheKey]
  );
  const [sdkDropdownOpen, setSdkDropdownOpen] = useState(false);
  const langCacheKey = `${agentServer}|${pattern}|${instanceKey}`;
  const [agentLang, setAgentLangRaw] = useState(
    () => langCache.get(langCacheKey) ?? defaultLanguage
  );
  const setAgentLang = useCallback(
    (l) => {
      langCache.set(langCacheKey, l);
      setAgentLangRaw(l);
    },
    [langCacheKey]
  );
  const previewUrl = useLocalPreview ? SDK_LOCAL_HOSTS[sdk] : SDK_PROD_HOSTS[sdk];
  const cacheKey = `${previewUrl}|${agentQuery}|${instanceKey}`;
  const [ready, setReady] = useState(() => iframeCache.get(cacheKey)?.ready ?? false);
  const [iframeHeight, setIframeHeight] = useState(
    () => iframeCache.get(cacheKey)?.lastHeight ?? minHeight
  );
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState(
    () => iframeCache.get(cacheKey)?.lastView ?? defaultView
  );
  const [traceUrl, setTraceUrl] = useState(null);
  const [traceLoading, setTraceLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const expandedRef = useRef(false);
  expandedRef.current = expanded;
  const [pageTheme, setPageTheme] = useState(detectPageTheme);
  useEffect(() => {
    setPageTheme(detectPageTheme());
    const observer = new MutationObserver(() => setPageTheme(detectPageTheme()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-theme", "style"]
    });
    return () => observer.disconnect();
  }, []);
  const effectiveTheme = theme ?? pageTheme;
  useEffect(() => {
    if (document.getElementById("lc-pe-css")) return;
    const style = document.createElement("style");
    style.id = "lc-pe-css";
    style.textContent = EMBED_CSS;
    document.head.appendChild(style);
  }, []);
  const onErrorRef = useRef(onError);
  onErrorRef.current = onError;
  const onReadyRef = useRef(onReady);
  onReadyRef.current = onReady;
  const patternRef = useRef(pattern);
  patternRef.current = pattern;
  const themeRef = useRef(effectiveTheme);
  themeRef.current = effectiveTheme;
  const activeViewRef = useRef(activeView);
  activeViewRef.current = activeView;
  const agentLangRef = useRef(agentLang);
  agentLangRef.current = agentLang;
  useEffect(() => {
    let cached = iframeCache.get(cacheKey);
    if (cached?.hideTimer) {
      clearTimeout(cached.hideTimer);
      cached.hideTimer = void 0;
    }
    if (!cached) {
      const iframe2 = document.createElement("iframe");
      iframe2.src = `${previewUrl}/${agentQuery}#/${patternRef.current}`;
      iframe2.setAttribute("sandbox", "allow-scripts allow-same-origin allow-forms");
      iframe2.setAttribute("allow", "clipboard-write");
      iframe2.title = `${patternRef.current} pattern`;
      iframe2.setAttribute("data-cache-key", cacheKey);
      Object.assign(iframe2.style, {
        position: "fixed",
        border: "none",
        visibility: "hidden",
        pointerEvents: "auto",
        zIndex: "1",
        borderRadius: "0 0 15px 15px"
      });
      document.body.appendChild(iframe2);
      let iframeOrigin;
      try {
        iframeOrigin = new URL(previewUrl).origin;
      } catch {
        iframeOrigin = previewUrl;
      }
      const host2 = createPreviewHost(iframe2, { allowedOrigins: [iframeOrigin] });
      cached = {
        iframe: iframe2,
        host: host2,
        ready: false,
        lastHeight: minHeight,
        lastView: defaultView,
        lastActiveAt: 0
      };
      iframeCache.set(cacheKey, cached);
    }
    cachedRef.current = cached;
    const { iframe, host } = cached;
    if (cached.ready) {
      setReady(true);
      setIframeHeight(cached.lastHeight);
      host.setTheme(themeRef.current);
      host.setPattern(patternRef.current);
      host.setLanguage(agentLangRef.current);
      if (activeViewRef.current !== "preview") {
        host.setView(activeViewRef.current);
      }
      cached.lastActiveAt = Date.now();
      iframe.style.visibility = "visible";
    }
    const unsubReady = host.onReady(() => {
      cached.ready = true;
      cached.lastActiveAt = Date.now();
      setReady(true);
      host.setTheme(themeRef.current);
      host.setPattern(patternRef.current);
      host.setLanguage(agentLangRef.current);
      if (activeViewRef.current !== "preview") {
        host.setView(activeViewRef.current);
      }
      iframe.style.visibility = "visible";
      onReadyRef.current?.();
    });
    const unsubResize = host.onResize((h) => {
      if (expandedRef.current) return;
      const clamped = Math.min(maxHeight, Math.max(minHeight, h));
      cached.lastHeight = clamped;
      setIframeHeight(clamped);
    });
    const unsubError = host.onError((message, stack) => {
      setError(message);
      iframe.style.visibility = "hidden";
      onErrorRef.current?.(message, stack);
    });
    const unsubRunStarted = host.onRunStarted(() => {
      setTraceUrl(null);
      setTraceLoading(true);
    });
    const unsubTraceUrl = host.onTraceUrl((url, _runId) => {
      setTraceUrl(url);
      setTraceLoading(false);
    });
    const unsubThreadCleared = host.onThreadCleared(() => {
      setTraceUrl(null);
      setTraceLoading(false);
    });
    function syncPosition() {
      const slot2 = slotRef.current;
      if (!slot2) return;
      const rect = slot2.getBoundingClientRect();
      const { style } = iframe;
      style.top = `${rect.top}px`;
      style.left = `${rect.left}px`;
      style.width = `${rect.width}px`;
      style.setProperty("height", `${rect.height}px`, "important");
      if (expandedRef.current) {
        style.zIndex = "10000";
      } else {
        style.zIndex = "1";
      }
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
      unsubReady();
      unsubResize();
      unsubError();
      unsubRunStarted();
      unsubTraceUrl();
      unsubThreadCleared();
      cachedRef.current = null;
      cached.hideTimer = setTimeout(() => {
        iframe.style.visibility = "hidden";
      }, 200);
    };
  }, [cacheKey, previewUrl, agentQuery, defaultView, minHeight, maxHeight]);
  useEffect(() => {
    requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
    if (!expanded) return;
    const card = cardRef.current;
    const placeholder = placeholderRef.current;
    if (!card || !placeholder) return;
    const wrapper = document.createElement("div");
    wrapper.setAttribute("data-lc-pe", "");
    wrapper.className = `${effectiveTheme === "dark" ? "dark" : ""}`;
    document.body.appendChild(wrapper);
    const backdrop = document.createElement("div");
    backdrop.className = "lc-pe-backdrop";
    backdrop.addEventListener("click", () => setExpanded(false));
    wrapper.appendChild(backdrop);
    wrapper.appendChild(card);
    Object.assign(card.style, {
      position: "fixed",
      zIndex: "9999",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      width: "min(70vw, calc(100vw - 48px))",
      height: "85vh",
      display: "flex",
      flexDirection: "column"
    });
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setExpanded(false);
    };
    document.addEventListener("keydown", handleKeyDown);
    const pageWrapper = document.body.children[0];
    const savedFilter = pageWrapper?.style.filter ?? "";
    const savedPointerEvents = pageWrapper?.style.pointerEvents ?? "";
    if (pageWrapper && pageWrapper !== wrapper) {
      pageWrapper.style.filter = "blur(4px)";
      pageWrapper.style.pointerEvents = "none";
    }
    requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      if (pageWrapper && pageWrapper !== wrapper) {
        pageWrapper.style.filter = savedFilter;
        pageWrapper.style.pointerEvents = savedPointerEvents;
      }
      card.style.cssText = "";
      placeholder.appendChild(card);
      wrapper.remove();
      requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
    };
  }, [expanded, effectiveTheme]);
  useEffect(() => {
    if (!ready || !cachedRef.current) return;
    setError(null);
    cachedRef.current.host.setPattern(pattern);
  }, [pattern, ready]);
  useEffect(() => {
    if (!ready || !cachedRef.current) return;
    cachedRef.current.host.setTheme(effectiveTheme);
  }, [effectiveTheme, ready]);
  useEffect(() => {
    if (!ready || !cachedRef.current) return;
    cachedRef.current.host.setLanguage(agentLang);
  }, [agentLang, ready]);
  const switchView = useCallback(
    (view) => {
      setActiveView(view);
      if (cachedRef.current) {
        cachedRef.current.lastView = view;
        if (cachedRef.current.ready) {
          cachedRef.current.host.setView(view);
          if (view === "code") {
            cachedRef.current.host.trackEvent("code_tab_clicked", { pattern });
          }
        }
      }
    },
    [pattern]
  );
  const sdkButtonRef = useRef(null);
  useEffect(() => {
    if (!sdkDropdownOpen || !sdkButtonRef.current) return;
    const isDark = effectiveTheme === "dark";
    const rect = sdkButtonRef.current.getBoundingClientRect();
    const dropdown = document.createElement("div");
    Object.assign(dropdown.style, {
      position: "fixed",
      top: `${rect.bottom + 4}px`,
      right: `${window.innerWidth - rect.right}px`,
      zIndex: expandedRef.current ? "10001" : "10",
      minWidth: "120px",
      borderRadius: "8px",
      border: `1px solid ${isDark ? "#1A2740" : "#B8DFFF"}`,
      backgroundColor: isDark ? "#0B1120" : "white",
      boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
      padding: "4px 0"
    });
    for (const [value, label] of SDK_OPTIONS) {
      const isSelected = value === sdk;
      const btn = document.createElement("button");
      btn.type = "button";
      Object.assign(btn.style, {
        display: "flex",
        alignItems: "center",
        gap: "6px",
        width: "100%",
        textAlign: "left",
        padding: "6px 12px",
        fontSize: "13px",
        cursor: "pointer",
        border: "none",
        fontWeight: isSelected ? "500" : "normal",
        backgroundColor: isSelected ? isDark ? "#1A2740" : "#E5F4FF" : "transparent",
        color: isSelected ? isDark ? "#C8DDF0" : "#030710" : "#6B8299"
      });
      btn.innerHTML = `<span>${SDK_LOGOS[value]}</span>${label}`;
      btn.addEventListener("mouseenter", () => {
        if (!isSelected) {
          btn.style.backgroundColor = isDark ? "#1A2740" : "#F2FAFF";
          btn.style.color = isDark ? "#C8DDF0" : "#030710";
        }
      });
      btn.addEventListener("mouseleave", () => {
        if (!isSelected) {
          btn.style.backgroundColor = "transparent";
          btn.style.color = "#6B8299";
        }
      });
      btn.addEventListener("click", () => {
        setSdk(value);
        setSdkDropdownOpen(false);
        cachedRef.current?.host.trackEvent("sdk_switched", { sdk: value, pattern });
      });
      dropdown.appendChild(btn);
    }
    document.body.appendChild(dropdown);
    const handleClose = (e) => {
      if (!dropdown.contains(e.target) && !sdkButtonRef.current?.contains(e.target)) {
        setSdkDropdownOpen(false);
      }
    };
    const timer = setTimeout(() => document.addEventListener("mousedown", handleClose), 0);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClose);
      dropdown.remove();
    };
  }, [sdkDropdownOpen, sdk, effectiveTheme, setSdk, pattern]);
  const handleReset = useCallback(() => {
    cachedRef.current?.host.reset();
    if (cachedRef.current?.ready) {
      cachedRef.current.host.setPattern(pattern);
    }
  }, [pattern]);
  const resolvedHeight = height ?? Math.min(maxHeight, Math.max(minHeight, iframeHeight));
  const heightStyle = typeof resolvedHeight === "number" ? `${resolvedHeight}px` : resolvedHeight;
  useEffect(() => {
    if (!expanded) {
      slotRef.current?.style.setProperty("height", heightStyle, "important");
    } else {
      slotRef.current?.style.removeProperty("height");
    }
  }, [heightStyle, expanded]);
  const tabBase = "lc-tab inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border-none font-medium cursor-pointer transition-all duration-150";
  const tabActiveClass = `${tabBase} lc-tab-active shadow-sm`;
  const tabInactiveClass = `${tabBase} lc-tab-inactive`;
  const tabTraceActiveClass = `${tabBase} lc-tab-trace`;
  const tabTraceLoadingClass = `${tabBase} lc-tab-trace-loading`;
  const toolbar = showCodeTab && <div className="lc-toolbar flex items-stretch justify-between px-3 py-2 border-b lc-border lc-bg-wash">
      <div
    className="inline-flex items-stretch gap-0.5 rounded-lg border lc-border lc-bg-surface"
    style={{ padding: 3 }}
  >
        <button
    type="button"
    aria-label="Preview"
    onClick={() => switchView("preview")}
    className={activeView === "preview" ? tabActiveClass : tabInactiveClass}
  >
          <span dangerouslySetInnerHTML={{ __html: VIEW_EYE_SVG }} />
          <span className="lc-tab-label">Preview</span>
        </button>
        <button
    type="button"
    aria-label="Code"
    onClick={() => switchView("code")}
    className={activeView === "code" ? tabActiveClass : tabInactiveClass}
  >
          <span dangerouslySetInnerHTML={{ __html: VIEW_CODE_SVG }} />
          <span className="lc-tab-label">Code</span>
        </button>
        {(traceUrl || traceLoading) && !useLocalPreview && <a
    href={traceUrl ?? "#"}
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Trace"
    onClick={(e) => {
      if (!traceUrl) e.preventDefault();
      else cachedRef.current?.host.trackEvent("trace_tab_clicked", { pattern });
    }}
    className={traceUrl ? tabTraceActiveClass : tabTraceLoadingClass}
    aria-disabled={!traceUrl}
  >
            <span
    dangerouslySetInnerHTML={{
      __html: traceUrl ? TRACE_ICON_SVG : TRACE_SPINNER_SVG
    }}
  />
            <span className="lc-tab-label">Trace</span>
            {traceUrl && <span className="ml-0.5" dangerouslySetInnerHTML={{ __html: EXTERNAL_LINK_SVG }} />}
          </a>}
      </div>

      {activeView === "code" && <div
    className="lc-lang-switcher inline-flex items-stretch gap-0.5 rounded-lg border lc-border lc-bg-surface"
    style={{ padding: 3 }}
  >
          <button
    type="button"
    aria-label="TypeScript"
    onClick={() => setAgentLang("js")}
    className={agentLang === "js" ? tabActiveClass : tabInactiveClass}
    title="TypeScript / JavaScript"
  >
            <span dangerouslySetInnerHTML={{ __html: LANG_TS_SVG }} />
          </button>
          <button
    type="button"
    aria-label="Python"
    onClick={() => setAgentLang("python")}
    className={agentLang === "python" ? tabActiveClass : tabInactiveClass}
    title="Python"
  >
            <span dangerouslySetInnerHTML={{ __html: LANG_PYTHON_SVG }} />
          </button>
        </div>}

      <div className="inline-flex items-center gap-1.5">
        <button
    type="button"
    aria-label={expanded ? "Collapse" : "Expand"}
    onClick={() => setExpanded((v) => !v)}
    className="lc-expand-btn"
    title={expanded ? "Collapse" : "Expand"}
  >
          <span dangerouslySetInnerHTML={{ __html: expanded ? CLOSE_SVG : EXPAND_SVG }} />
        </button>

        {
    /* Download button */
  }
        <button
    type="button"
    aria-label="Download project"
    title="Download project to run locally"
    onClick={() => {
      const base = normalizeAgentServerBase(agentServer, useLocalPreview);
      const params = new URLSearchParams({ sdk, lang: agentLang });
      const url = `${base}/download/${encodeURIComponent(pattern)}?${params}`;
      const a = document.createElement("a");
      a.href = url;
      a.download = `${pattern}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      cachedRef.current?.host.trackEvent("download_clicked", {
        pattern,
        sdk,
        lang: agentLang
      });
    }}
    className="lc-expand-btn"
  >
          <span dangerouslySetInnerHTML={{ __html: DOWNLOAD_SVG }} />
        </button>

        {
    /* SDK selector — dropdown is appended to document.body via effect */
  }
        <button
    ref={sdkButtonRef}
    type="button"
    onClick={() => setSdkDropdownOpen((o) => !o)}
    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border lc-sdk-btn font-medium cursor-pointer transition-colors"
  >
          <span dangerouslySetInnerHTML={{ __html: SDK_LOGOS[sdk] }} />
          {SDK_LABELS[sdk]}
          <span dangerouslySetInnerHTML={{ __html: CHEVRON_DOWN_SVG }} />
        </button>
      </div>
    </div>;
  const slot = <div
    ref={slotRef}
    className="relative w-full"
    style={expanded ? { flex: 1, minHeight: 0 } : { height: heightStyle }}
  >
      {!ready && !error && <div className="absolute inset-0 flex items-center justify-center z-10 lc-bg-wash">
          <div className="size-6 border-2 lc-spinner rounded-full animate-spin" />
        </div>}

      {error && <div className="absolute top-3 inset-x-3 z-10 px-4 py-3 rounded-2xl border lc-error text-sm">
          <strong>Preview Error</strong>
          <p className="mt-1 opacity-80" style={{ fontSize: 13 }}>
            {error}
          </p>
          <button
    type="button"
    onClick={handleReset}
    className="mt-2 px-3 py-1 text-xs rounded-lg border lc-error-btn cursor-pointer"
  >
            Retry
          </button>
        </div>}
    </div>;
  return <div
    data-lc-pe
    ref={placeholderRef}
    className={`${effectiveTheme === "dark" ? "dark" : ""} ${className ?? ""}`}
  >
      <div ref={cardRef} className="rounded-2xl border lc-border overflow-hidden lc-bg-surface">
        {toolbar}
        {slot}
      </div>
    </div>;

};
