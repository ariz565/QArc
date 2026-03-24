// ═══════════════════════════════════════════════════════════════
// Centralized Typography Tokens — Font sizes, weights, line-heights.
// Use these Tailwind class fragments across all components.
// ═══════════════════════════════════════════════════════════════

// ─── Headings ────────────────────────────────────────────────

export const HEADING = {
  /** Page titles — "Dashboard", "AI Test Pipeline" */
  page: "text-lg font-bold text-white",
  /** Section titles inside cards */
  section: "text-sm font-bold text-white",
  /** Card subtitles */
  subtitle: "text-xs text-slate-500 mt-0.5",
  /** Hero heading — Pipeline welcome */
  hero: "text-3xl font-black text-white tracking-tight",
} as const;

// ─── Body Text ───────────────────────────────────────────────

export const BODY = {
  /** Primary body text inside cards */
  primary: "text-xs text-slate-300",
  /** Secondary / supporting text */
  secondary: "text-xs text-slate-400",
  /** Muted label text */
  muted: "text-[11px] text-slate-500",
  /** Faint timestamps, hints */
  faint: "text-[10px] text-slate-600",
} as const;

// ─── Mono / Code ─────────────────────────────────────────────

export const MONO = {
  /** Inline mono values — story IDs, stats */
  inline: "text-xs font-mono",
  /** Tiny mono — status labels, counters */
  tiny: "text-[10px] font-mono",
  /** Code blocks */
  code: "text-[11px] font-mono leading-relaxed",
  /** Console / log entries */
  console: "text-[11px] font-mono leading-relaxed",
} as const;

// ─── Labels ──────────────────────────────────────────────────

export const LABEL = {
  /** Section dividers — "FRAMEWORK ADAPTERS", "JIRA STORIES" */
  section: "text-[10px] font-bold uppercase tracking-widest text-slate-500",
  /** Badge / tag text */
  badge: "text-[9px] font-bold uppercase",
  /** Metric card labels */
  metric: "text-[11px] text-slate-500",
  /** Metric card change text */
  change: "text-[10px] text-slate-600",
} as const;

// ─── Values / Numbers ────────────────────────────────────────

export const VALUE = {
  /** Large stat numbers — "1,247", "89%" */
  stat: "text-2xl font-black",
  /** Medium metric — pass rate bars */
  medium: "text-lg font-black",
  /** Small inline values */
  small: "text-sm font-semibold",
} as const;
