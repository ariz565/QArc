// ═══════════════════════════════════════════════════════════════
// Centralized Color Tokens — Single source of truth for all colors.
// Import from here instead of hardcoding hex/tailwind classes.
// ═══════════════════════════════════════════════════════════════

// ─── Agent Identity Colors ───────────────────────────────────
// Used across Pipeline, Dashboard, AgentNetwork, Settings

export const AGENT_COLORS = {
  story: "#22d3ee",
  strategy: "#fb923c",
  writer: "#a78bfa",
  automation: "#34d399",
  executor: "#60a5fa",
  bug: "#fb7185",
  coverage: "#fbbf24",
} as const;

// ─── Semantic Status Colors ──────────────────────────────────
// For badges, dots, borders — Tailwind class fragments

export const STATUS = {
  pass: {
    text: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    dot: "bg-emerald-400",
    hex: "#34d399",
  },
  fail: {
    text: "text-rose-400",
    bg: "bg-rose-500/10",
    border: "border-rose-500/20",
    dot: "bg-rose-400",
    hex: "#fb7185",
  },
  running: {
    text: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
    dot: "bg-cyan-400",
    hex: "#22d3ee",
  },
  warning: {
    text: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
    dot: "bg-amber-400",
    hex: "#fbbf24",
  },
  idle: {
    text: "text-slate-500",
    bg: "bg-slate-800/50",
    border: "border-slate-700/50",
    dot: "bg-slate-600",
    hex: "#64748b",
  },
} as const;

// ─── Priority Colors ─────────────────────────────────────────

export const PRIORITY = {
  P0: { text: "text-rose-400", bg: "bg-rose-500/15", label: "Critical" },
  P1: { text: "text-amber-400", bg: "bg-amber-500/15", label: "High" },
  P2: { text: "text-blue-400", bg: "bg-blue-500/15", label: "Medium" },
  P3: { text: "text-slate-400", bg: "bg-slate-700/50", label: "Low" },
} as const;

// ─── Test Type Colors ────────────────────────────────────────

export const TEST_TYPE = {
  functional: {
    text: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  security: {
    text: "text-rose-400",
    bg: "bg-rose-500/10",
    border: "border-rose-500/20",
  },
  edge: {
    text: "text-orange-400",
    bg: "bg-orange-500/10",
    border: "border-orange-500/20",
  },
  performance: {
    text: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  accessibility: {
    text: "text-violet-400",
    bg: "bg-violet-500/10",
    border: "border-violet-500/20",
  },
} as const;

// ─── Trend Colors ────────────────────────────────────────────

export const TREND = {
  up: { text: "text-emerald-400", bg: "bg-emerald-500/15" },
  down: { text: "text-rose-400", bg: "bg-rose-500/15" },
  stable: { text: "text-amber-400", bg: "bg-amber-500/15" },
  neutral: { text: "text-blue-400", bg: "bg-blue-500/15" },
} as const;

// ─── Chart / Visualization Colors ────────────────────────────

export const CHART = {
  passBar: "bg-emerald-500/70",
  failBar: "bg-rose-500/60",
  progressTrack: "bg-slate-800",
  cyan: "bg-cyan-500/60",
  emerald: "bg-emerald-500/60",
  violet: "bg-violet-500/60",
  amber: "bg-amber-500/60",
} as const;

// ─── Metric Card Presets ─────────────────────────────────────
// Pre-built color combos for stat/metric cards

export const METRIC_PRESETS = {
  cyan: {
    text: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
  },
  emerald: {
    text: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  rose: {
    text: "text-rose-400",
    bg: "bg-rose-500/10",
    border: "border-rose-500/20",
  },
  amber: {
    text: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  violet: {
    text: "text-violet-400",
    bg: "bg-violet-500/10",
    border: "border-violet-500/20",
  },
  blue: {
    text: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
} as const;

// ─── Sidebar / Navigation ────────────────────────────────────
// Constant colors that work in BOTH light and dark modes

export const NAV = {
  active: {
    bg: "bg-cyan-500/10",
    text: "text-cyan-400",
    border: "border-cyan-500/20",
  },
  inactive: {
    text: "text-slate-400",
    hoverText: "text-cyan-300",
    hoverBg: "bg-cyan-500/5",
  },
  themeToggle: {
    hoverBg: "bg-cyan-500/5",
    hoverText: "text-cyan-300",
  },
} as const;

// ─── Framework Colors (from adapters) ────────────────────────

export const FRAMEWORK = {
  playwright: "#2EAD33",
  selenium: "#43B02A",
  cypress: "#69D3A7",
  appium: "#662D91",
  k6: "#7D64FF",
  axe: "#FF4D6A",
} as const;
