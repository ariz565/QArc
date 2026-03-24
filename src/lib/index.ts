// ═══════════════════════════════════════════════════════════════
// Central re-export — import everything from '@/lib'
// Usage: import { API, METRIC_PRESETS, HEADING, cn } from '../lib';
// ═══════════════════════════════════════════════════════════════

export { cn } from "./cn";
export {
  AGENT_COLORS,
  STATUS,
  PRIORITY,
  TEST_TYPE,
  TREND,
  CHART,
  METRIC_PRESETS,
  NAV,
  FRAMEWORK,
} from "./colors";
export { HEADING, BODY, MONO, LABEL, VALUE } from "./typography";
export { API, WS, INTEGRATIONS, FEATURES, APP, DEFAULTS } from "./config";
export {
  FRAMEWORKS,
  ENVIRONMENT_PRESETS,
  DEFAULT_ADAPTER_CONFIG,
  getAdapter,
  getActiveAdapters,
  getCapabilityLabel,
} from "./adapters";
export type {
  FrameworkAdapter,
  EnvironmentPreset,
  FrameworkCapability,
  BrowserType,
} from "./adapters";
