// ═══════════════════════════════════════════════════════════════
// Centralized App Config — API base URLs, feature flags, constants.
// All backend connection points and runtime config live here.
// ═══════════════════════════════════════════════════════════════

// ─── API Configuration ───────────────────────────────────────

export const API = {
  /** Backend base URL — point this to your FastAPI / Express server */
  baseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",

  /** API version prefix */
  version: "/api/v1",

  /** Full API root (baseUrl + version) */
  get root() {
    return `${this.baseUrl}${this.version}`;
  },

  /** Individual endpoint paths */
  endpoints: {
    // Pipeline
    runPipeline: "/pipeline/run",
    pipelineStatus: "/pipeline/status",

    // Stories / Jira
    stories: "/stories",
    storyDetail: (id: string) => `/stories/${id}`,

    // Test cases
    testCases: "/test-cases",
    testCasesByStory: (storyId: string) => `/test-cases/story/${storyId}`,

    // Agents
    agents: "/agents",
    agentHealth: "/agents/health",

    // Execution / History
    executions: "/executions",
    executionDetail: (id: string) => `/executions/${id}`,

    // Dashboard
    dashboardStats: "/dashboard/stats",
    weeklyTrend: "/dashboard/weekly-trend",

    // Reports
    reports: "/reports",
    coverageReport: "/reports/coverage",

    // Settings
    frameworks: "/settings/frameworks",
    environments: "/settings/environments",
    connections: "/settings/connections",

    // Auth (future)
    login: "/auth/login",
    logout: "/auth/logout",
    me: "/auth/me",
  },
} as const;

// ─── WebSocket Configuration ─────────────────────────────────

export const WS = {
  /** WebSocket base URL for real-time pipeline events */
  baseUrl: import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000",
  endpoints: {
    pipelineStream: "/ws/pipeline",
    agentLogs: "/ws/logs",
  },
} as const;

// ─── External Integrations ───────────────────────────────────

export const INTEGRATIONS = {
  jira: {
    baseUrl: import.meta.env.VITE_JIRA_BASE_URL || "",
    projectKey: import.meta.env.VITE_JIRA_PROJECT_KEY || "PROJ",
  },
  github: {
    repoUrl: import.meta.env.VITE_GITHUB_REPO_URL || "",
  },
  slack: {
    webhookUrl: import.meta.env.VITE_SLACK_WEBHOOK_URL || "",
  },
} as const;

// ─── Feature Flags ───────────────────────────────────────────

export const FEATURES = {
  /** Use mock data instead of real API calls (override with VITE_USE_MOCK_DATA=false) */
  useMockData: import.meta.env.VITE_USE_MOCK_DATA !== "false",

  /** Enable WebSocket streaming for pipeline logs */
  enableWsStreaming: import.meta.env.VITE_ENABLE_WS_STREAMING === "true",

  /** Show experimental A11y and performance testing tabs */
  showExperimentalAdapters: true,

  /** Enable parallel test execution in UI */
  enableParallelExecution: true,
} as const;

// ─── App Metadata ────────────────────────────────────────────

export const APP = {
  name: "QA Nexus",
  tagline: "AI TESTING",
  version: "2.0.0",
  description: "AI-Powered Multi-Agent Testing Platform",
  agentCount: 7,
  localStorageKeys: {
    theme: "qa-nexus-theme",
    activeFrameworks: "qa-nexus-frameworks",
    lastStoryId: "qa-nexus-last-story",
  },
} as const;

// ─── Default Execution Settings ──────────────────────────────

export const DEFAULTS = {
  parallelWorkers: 4,
  timeoutMs: 30000,
  retries: 2,
  headless: true,
  screenshotsOnFailure: true,
  videoOnFailure: false,
} as const;
