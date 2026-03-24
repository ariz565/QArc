// ═══════════════════════════════════════════════════════════════
// Data Service — single gate for all data access.
//
// FEATURES.useMockData === true  → returns local mock data
// FEATURES.useMockData === false → makes real backend API calls
//
// Components import from here, never from mock.ts directly.
// ═══════════════════════════════════════════════════════════════

import { API, FEATURES, WS } from "./config";
import { http } from "./http";
import {
  AGENTS,
  STORIES,
  STORY_OUTPUTS,
  DASHBOARD_STATS,
  generateLogs,
  type JiraStory,
  type AgentDef,
  type AgentOutput,
  type TestCase,
  type LogEntry,
} from "../data/mock";

// Re-export types so components import from one place
export type { JiraStory, AgentDef, AgentOutput, TestCase, LogEntry };

// ─── Stories ─────────────────────────────────────────────────

// Backend uses snake_case (story_points), frontend uses camelCase (storyPoints)
interface BackendStory {
  id: string;
  title: string;
  description: string;
  priority: "Critical" | "High" | "Medium";
  labels: string[];
  acceptance: string[];
  story_points: number;
  sprint: string;
}

function mapStory(s: BackendStory): JiraStory {
  return {
    id: s.id,
    title: s.title,
    description: s.description,
    priority: s.priority,
    labels: s.labels,
    acceptance: s.acceptance,
    storyPoints: s.story_points,
    sprint: s.sprint,
  };
}

export async function getStories(): Promise<JiraStory[]> {
  if (FEATURES.useMockData) return STORIES;
  const raw = await http.get<BackendStory[]>(API.endpoints.stories);
  return raw.map(mapStory);
}

export async function getStory(id: string): Promise<JiraStory | undefined> {
  if (FEATURES.useMockData) return STORIES.find((s) => s.id === id);
  return http.get<JiraStory>(API.endpoints.storyDetail(id));
}

// ─── Agents ──────────────────────────────────────────────────

export async function getAgents(): Promise<AgentDef[]> {
  if (FEATURES.useMockData) return AGENTS;
  return http.get<AgentDef[]>(API.endpoints.agents);
}

// ─── Pipeline ────────────────────────────────────────────────

export interface PipelineRunRequest {
  storyId: string;
  framework: string;
}

export interface PipelineStatus {
  executionId: string;
  storyId: string;
  status: string;
  phase: string;
  agentsCompleted: string[];
  currentAgent: string | null;
}

/** Start a real pipeline run. Returns execution ID + initial status. */
export async function startPipeline(
  req: PipelineRunRequest,
): Promise<PipelineStatus> {
  return http.post<PipelineStatus>(API.endpoints.runPipeline, {
    story_id: req.storyId,
    framework: req.framework,
  });
}

/** Get pipeline status by execution ID. */
export async function getPipelineStatus(
  executionId: string,
): Promise<PipelineStatus> {
  return http.get<PipelineStatus>(
    `${API.endpoints.pipelineStatus}/${executionId}`,
  );
}

/** Get mock agent outputs for a story (mock-only path). */
export function getMockOutputs(storyId: string): AgentOutput[] {
  return STORY_OUTPUTS[storyId] ?? [];
}

/** Get mock streaming logs for a story (mock-only path). */
export function getMockLogs(storyId: string): LogEntry[][] {
  return generateLogs(storyId);
}

/** Open a WebSocket to stream real pipeline events. */
export function connectPipelineWs(executionId: string): WebSocket {
  const url = `${WS.baseUrl}${API.version}${WS.endpoints.pipelineStream}/${executionId}`;
  return new WebSocket(url);
}

// ─── Dashboard ───────────────────────────────────────────────

export interface DashboardStatsData {
  totalTestsGenerated: number;
  totalTestsExecuted: number;
  bugsFound: number;
  avgPassRate: number;
  storiesAnalyzed: number;
  timeSavedHours: number;
  topIssues: { type: string; count: number; trend: string }[];
  recentRuns: {
    storyId: string;
    title: string;
    pass: number;
    fail: number;
    time: string;
    date: string;
  }[];
  weeklyTrend: { day: string; tests: number; pass: number; fail: number }[];
}

export async function getDashboardStats(): Promise<DashboardStatsData> {
  if (FEATURES.useMockData) return DASHBOARD_STATS as DashboardStatsData;

  // Backend returns a different shape — map it to the frontend model
  const raw = await http.get<{
    total_tests: number;
    passed: number;
    failed: number;
    coverage: number;
    avg_duration_ms: number;
    active_pipelines: number;
  }>(API.endpoints.dashboardStats);

  return {
    totalTestsGenerated: raw.total_tests,
    totalTestsExecuted: raw.passed + raw.failed,
    bugsFound: raw.failed,
    avgPassRate:
      raw.total_tests > 0
        ? Math.round((raw.passed / raw.total_tests) * 100)
        : 0,
    storiesAnalyzed: raw.active_pipelines,
    timeSavedHours: Math.round(
      (raw.total_tests * raw.avg_duration_ms) / 3_600_000,
    ),
    topIssues: [],
    recentRuns: [],
    weeklyTrend: [],
  };
}

// ─── Test Cases ──────────────────────────────────────────────

export async function getAllTestCases(): Promise<
  { storyId: string; storyTitle: string; tests: TestCase[] }[]
> {
  if (FEATURES.useMockData) {
    return STORIES.map((story) => {
      const outputs = STORY_OUTPUTS[story.id] ?? [];
      const tests = outputs.flatMap((o) => o.testCases ?? []);
      return { storyId: story.id, storyTitle: story.title, tests };
    });
  }
  // Backend returns flat list — group client-side if needed
  return http.get(API.endpoints.testCases);
}

// ─── Executions / History ────────────────────────────────────

export interface ExecutionRun {
  id: string;
  storyId: string;
  storyTitle: string;
  framework: string;
  trigger: "manual" | "ci" | "scheduled";
  timestamp: string;
  duration: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  environment?: string;
  coveragePercent?: number;
}

// Backend execution model uses snake_case + different field names
interface BackendExecution {
  id: string;
  story_id: string;
  story_title: string;
  framework: string;
  trigger: "manual" | "ci" | "scheduled";
  status: string;
  started_at: string;
  completed_at: string | null;
  duration_ms: number;
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  coverage: number;
  verdict: string | null;
}

function mapExecution(e: BackendExecution): ExecutionRun {
  const durationSec = e.duration_ms / 1000;
  return {
    id: e.id,
    storyId: e.story_id,
    storyTitle: e.story_title,
    framework: e.framework,
    trigger: e.trigger,
    timestamp: e.started_at,
    duration:
      durationSec >= 1 ? `${durationSec.toFixed(1)}s` : `${e.duration_ms}ms`,
    total: e.total_tests,
    passed: e.passed,
    failed: e.failed,
    skipped: e.skipped,
    coveragePercent: Math.round(e.coverage),
  };
}

export async function getExecutions(): Promise<ExecutionRun[]> {
  if (FEATURES.useMockData) return []; // ExecutionHistory has its own inline mock
  const res = await http.get<{ items: BackendExecution[] }>(
    API.endpoints.executions,
  );
  return res.items.map(mapExecution);
}

// ─── Reports ─────────────────────────────────────────────────

export async function getReportData() {
  if (FEATURES.useMockData) {
    return {
      stats: DASHBOARD_STATS as DashboardStatsData,
      stories: STORIES,
      storyOutputs: STORY_OUTPUTS,
      agents: AGENTS,
    };
  }
  // Parallel fetch — reuse mapped functions so shapes match
  const [stats, stories, agents] = await Promise.all([
    getDashboardStats(),
    getStories(),
    getAgents(),
  ]);
  return {
    stats,
    stories,
    storyOutputs: {} as Record<string, AgentOutput[]>,
    agents,
  };
}

// ─── Utility: check if we're in mock mode ────────────────────

export const isMockMode = () => FEATURES.useMockData;
