import { useState, useEffect, useRef, useCallback } from "react";
import {
  Play,
  Check,
  Loader2,
  Circle,
  ChevronDown,
  ChevronRight,
  Terminal,
  FileCode2,
  Bug,
  ShieldCheck,
  Zap,
  Search,
  BookOpen,
  Code2,
  FlaskConical,
  BadgeAlert,
  PieChart,
} from "lucide-react";
import {
  AGENTS as MOCK_AGENTS,
  STORIES as MOCK_STORIES,
  STORY_OUTPUTS,
  generateLogs,
  type JiraStory,
  type AgentDef,
  type TestCase,
  type LogEntry,
} from "../data/mock";
import {
  getAgents,
  getStories,
  getMockOutputs,
  getMockLogs,
  startPipeline,
  connectPipelineWs,
  isMockMode,
} from "../lib/services";

// ─── Icon map for agents ────────────────────────────────────

const AGENT_ICONS: Record<string, React.ElementType> = {
  story: Search,
  strategy: BookOpen,
  writer: FileCode2,
  automation: Code2,
  executor: FlaskConical,
  bug: Bug,
  coverage: PieChart,
};

// ─── Streaming text hook ────────────────────────────────────

function useStreamingText(
  text: string,
  active: boolean,
  wordsPerTick = 3,
  tickMs = 40,
) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!active) {
      setDisplayed("");
      setDone(false);
      return;
    }
    const words = text.split(" ");
    let idx = 0;
    const interval = setInterval(() => {
      idx += wordsPerTick;
      if (idx >= words.length) {
        setDisplayed(text);
        setDone(true);
        clearInterval(interval);
      } else {
        setDisplayed(words.slice(0, idx).join(" "));
      }
    }, tickMs);
    return () => clearInterval(interval);
  }, [text, active, wordsPerTick, tickMs]);

  return { displayed, done };
}

// ─── Agent status types ─────────────────────────────────────

type AgentStatus = "idle" | "processing" | "complete";

interface AgentState {
  status: AgentStatus;
  output: string;
  testCases?: TestCase[];
  automationCode?: string;
}

// ═════════════════════════════════════════════════════════════
// PIPELINE COMPONENT — The hero of the demo
// ═════════════════════════════════════════════════════════════

export default function Pipeline() {
  const [AGENTS, setAgents] = useState<AgentDef[]>(MOCK_AGENTS);
  const [STORIES, setStories] = useState<JiraStory[]>(MOCK_STORIES);
  const [selectedStory, setSelectedStory] = useState<JiraStory | null>(null);
  const [agentStates, setAgentStates] = useState<Record<string, AgentState>>(
    {},
  );
  const [pipelineStatus, setPipelineStatus] = useState<
    "idle" | "running" | "complete"
  >("idle");
  const [currentAgentIdx, setCurrentAgentIdx] = useState(-1);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeOutputTab, setActiveOutputTab] = useState("story");
  const [expandedStory, setExpandedStory] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [testResults, setTestResults] = useState<TestCase[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Load agents & stories from service (mock or real)
  useEffect(() => {
    getAgents().then(setAgents).catch(console.error);
    getStories().then(setStories).catch(console.error);
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Initialize agent states
  useEffect(() => {
    const initial: Record<string, AgentState> = {};
    AGENTS.forEach((a) => {
      initial[a.id] = { status: "idle", output: "" };
    });
    setAgentStates(initial);
  }, [AGENTS]);

  // Run the pipeline — mock simulation or real backend
  const runPipeline = useCallback(async () => {
    if (!selectedStory || pipelineStatus === "running") return;

    setPipelineStatus("running");
    setProgress(0);
    setLogs([]);
    setTestResults([]);
    setActiveOutputTab("story");

    // Reset all agents
    const fresh: Record<string, AgentState> = {};
    AGENTS.forEach((a) => {
      fresh[a.id] = { status: "idle", output: "" };
    });
    setAgentStates(fresh);

    if (isMockMode()) {
      // ── Mock mode: local simulation ──
      const outputs = getMockOutputs(selectedStory.id);
      const allLogs = getMockLogs(selectedStory.id);

      for (let i = 0; i < AGENTS.length; i++) {
        const agent = AGENTS[i];
        const agentOutput = outputs[i];
        const agentLogs = allLogs[i] || [];

        setCurrentAgentIdx(i);
        setActiveOutputTab(agent.id);
        setProgress(Math.round((i / AGENTS.length) * 100));

        setAgentStates((prev) => ({
          ...prev,
          [agent.id]: { ...prev[agent.id], status: "processing" },
        }));

        for (let j = 0; j < agentLogs.length; j++) {
          await sleep(350);
          setLogs((prev) => [...prev, agentLogs[j]]);
        }

        if (agentOutput) {
          setAgentStates((prev) => ({
            ...prev,
            [agent.id]: {
              status: "processing",
              output: agentOutput.content,
              testCases: agentOutput.testCases,
              automationCode: agentOutput.automationCode,
            },
          }));

          if (agent.id === "executor" && agentOutput.executionResults) {
            const cases = outputs.find((o) => o.testCases)?.testCases || [];
            const results = agentOutput.executionResults;
            const updatedCases: TestCase[] = [];
            let executorLog =
              "▶ Launching Chromium browser context...\n▶ Configuring parallel workers...\n\n";
            setAgentStates((prev) => ({
              ...prev,
              executor: { ...prev.executor, output: executorLog },
            }));

            for (const result of results) {
              await sleep(400);
              const tc = cases.find((c) => c.id === result.id);
              const icon = result.status === "pass" ? "✓" : "✗";
              executorLog += `  ${icon} ${result.id}: ${tc?.name || "Test"} (${result.duration})\n`;
              if (result.error) {
                executorLog += `    └─ ${result.error}\n`;
              }
              const updatedTc: TestCase = {
                ...(tc || {
                  id: result.id,
                  name: "Test",
                  type: "functional",
                  priority: "P1",
                  scenario: "",
                  steps: [],
                  expected: "",
                }),
                status: result.status,
                duration: result.duration,
              };
              updatedCases.push(updatedTc);
              setTestResults([...updatedCases]);
              setAgentStates((prev) => ({
                ...prev,
                executor: { ...prev.executor, output: executorLog },
              }));
            }

            const passCount = results.filter((r) => r.status === "pass").length;
            executorLog += `\n━━━ Results: ${passCount}/${results.length} passed ━━━`;
            setAgentStates((prev) => ({
              ...prev,
              executor: { ...prev.executor, output: executorLog },
            }));
          }
        }

        await sleep(agent.id === "executor" ? 200 : 800);

        setAgentStates((prev) => ({
          ...prev,
          [agent.id]: { ...prev[agent.id], status: "complete" },
        }));

        setProgress(Math.round(((i + 1) / AGENTS.length) * 100));
      }
    } else {
      // ── Real mode: call backend API + WebSocket stream ──
      try {
        const status = await startPipeline({
          storyId: selectedStory.id,
          framework: "playwright",
        });

        const ws = connectPipelineWs(status.executionId);

        await new Promise<void>((resolve, reject) => {
          ws.onmessage = (evt) => {
            const msg = JSON.parse(evt.data);
            if (msg.type === "agent_start") {
              const idx = AGENTS.findIndex((a) => a.id === msg.agentId);
              if (idx >= 0) setCurrentAgentIdx(idx);
              setActiveOutputTab(msg.agentId);
              setAgentStates((prev) => ({
                ...prev,
                [msg.agentId]: { ...prev[msg.agentId], status: "processing" },
              }));
            } else if (msg.type === "log") {
              setLogs((prev) => [
                ...prev,
                {
                  time: msg.timestamp ?? new Date().toISOString(),
                  agentId: msg.agentId ?? "system",
                  message: msg.message,
                  type: msg.level ?? "info",
                } as LogEntry,
              ]);
            } else if (msg.type === "agent_output") {
              setAgentStates((prev) => ({
                ...prev,
                [msg.agentId]: {
                  status: "processing",
                  output: msg.content ?? "",
                  testCases: msg.testCases,
                  automationCode: msg.automationCode,
                },
              }));
            } else if (msg.type === "agent_complete") {
              setAgentStates((prev) => ({
                ...prev,
                [msg.agentId]: { ...prev[msg.agentId], status: "complete" },
              }));
            } else if (msg.type === "progress") {
              setProgress(msg.percent ?? 0);
            } else if (msg.type === "complete") {
              setPipelineStatus("complete");
              setCurrentAgentIdx(-1);
              setProgress(100);
              ws.close();
              resolve();
            } else if (msg.type === "error") {
              console.error("Pipeline error:", msg.message);
              ws.close();
              reject(new Error(msg.message));
            }
          };
          ws.onerror = () => {
            reject(new Error("WebSocket connection failed"));
            ws.close();
          };
        });
      } catch (err) {
        console.error("Pipeline run failed:", err);
      }
    }

    setPipelineStatus("complete");
    setCurrentAgentIdx(-1);
  }, [selectedStory, pipelineStatus, AGENTS]);

  // Active agent output for streaming
  const activeOutput = agentStates[activeOutputTab];
  const isActiveStreaming = activeOutput?.status === "processing";
  const { displayed: streamedText } = useStreamingText(
    activeOutput?.output || "",
    isActiveStreaming,
    4,
    30,
  );

  const displayText =
    activeOutput?.status === "complete" ? activeOutput.output : streamedText;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 bg-surface-deep/80 backdrop-blur flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-lg font-bold text-white">AI Test Pipeline</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Select a Jira story → Run the multi-agent pipeline → Get results
          </p>
        </div>
        <div className="flex items-center gap-3">
          {pipelineStatus === "running" && (
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Processing... {progress}%
            </div>
          )}
          {pipelineStatus === "complete" && (
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
              <Check className="w-3.5 h-3.5" />
              Pipeline complete
            </div>
          )}
          <button
            onClick={runPipeline}
            disabled={!selectedStory || pipelineStatus === "running"}
            className={`pipeline-run-btn flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all ${
              pipelineStatus === "running"
                ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 cursor-wait"
                : selectedStory
                  ? "bg-linear-to-r from-cyan-500/20 to-violet-500/20 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400/50 hover:shadow-lg hover:shadow-cyan-500/10 cursor-pointer"
                  : "bg-slate-800/50 text-slate-600 border border-slate-700/50 cursor-not-allowed"
            }`}
          >
            {pipelineStatus === "running" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" fill="currentColor" />
            )}
            {pipelineStatus === "running" ? "Running..." : "Run AI Pipeline"}
          </button>
        </div>
      </div>

      {/* Progress bar */}
      {pipelineStatus !== "idle" && (
        <div className="h-0.5 bg-slate-800 shrink-0">
          <div
            className="h-full bg-linear-to-r from-cyan-400 to-violet-400 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {/* ── Left: Story Selector ── */}
        <div className="w-72 border-r border-slate-800/80 bg-surface overflow-y-auto shrink-0">
          <div className="px-4 py-3 border-b border-slate-800/60 flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
              Jira Stories
            </span>
            <span className="text-[10px] font-mono text-cyan-500 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              LIVE
            </span>
          </div>

          {STORIES.map((story) => (
            <div key={story.id}>
              <div
                onClick={() => {
                  setSelectedStory(story);
                  setExpandedStory(
                    expandedStory === story.id ? null : story.id,
                  );
                  if (pipelineStatus === "complete") {
                    setPipelineStatus("idle");
                    setProgress(0);
                  }
                }}
                className={`px-4 py-3.5 border-b border-slate-800/40 cursor-pointer transition-all ${
                  selectedStory?.id === story.id
                    ? "bg-cyan-500/5 border-l-2 border-l-cyan-400"
                    : "hover:bg-slate-800/40 border-l-2 border-l-transparent"
                }`}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-[11px] font-mono text-cyan-400">
                    {story.id}
                  </span>
                  <span
                    className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                      story.priority === "Critical"
                        ? "bg-rose-500/20 text-rose-400"
                        : story.priority === "High"
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-emerald-500/20 text-emerald-400"
                    }`}
                  >
                    {story.priority}
                  </span>
                  <span className="text-[10px] font-mono text-slate-600 ml-auto">
                    {story.storyPoints} SP
                  </span>
                </div>
                <div className="text-[13px] font-semibold text-slate-200 leading-snug mb-2">
                  {story.title}
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {story.labels.map((l) => (
                    <span
                      key={l}
                      className="text-[10px] font-mono text-slate-500 bg-slate-800/80 border border-slate-700/50 px-1.5 py-0.5 rounded"
                    >
                      {l}
                    </span>
                  ))}
                </div>
              </div>

              {/* Expanded story detail */}
              {expandedStory === story.id && (
                <div className="px-4 py-3 bg-slate-900/50 border-b border-slate-800/40 animate-slide-up">
                  <p className="text-xs text-slate-400 leading-relaxed mb-3">
                    {story.description}
                  </p>
                  <div className="text-[10px] font-bold uppercase tracking-widest text-slate-600 mb-2">
                    Acceptance Criteria
                  </div>
                  {story.acceptance.map((a, i) => (
                    <div
                      key={i}
                      className="flex gap-2 mb-1.5 text-xs text-slate-300"
                    >
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-500 mt-0.5 shrink-0" />
                      <span>{a}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* ── Center: Agent Pipeline + Output ── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {!selectedStory ? (
            <WelcomeScreen />
          ) : (
            <>
              {/* Agent chain */}
              <div className="px-6 py-4 border-b border-slate-800/60 bg-surface/50 shrink-0">
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  {AGENTS.map((agent, idx) => {
                    const state = agentStates[agent.id];
                    const Icon = AGENT_ICONS[agent.id] || Circle;
                    return (
                      <div
                        key={agent.id}
                        className="flex items-center gap-2 shrink-0"
                      >
                        {idx > 0 && (
                          <div className="flex items-center">
                            <svg width="24" height="2" className="shrink-0">
                              <line
                                x1="0"
                                y1="1"
                                x2="24"
                                y2="1"
                                stroke={
                                  state?.status === "complete"
                                    ? "#34d399"
                                    : state?.status === "processing"
                                      ? "#22d3ee"
                                      : "#334155"
                                }
                                strokeWidth="2"
                                className={
                                  state?.status === "processing"
                                    ? "connector-animate"
                                    : ""
                                }
                              />
                            </svg>
                          </div>
                        )}
                        <button
                          onClick={() =>
                            state?.status !== "idle" &&
                            setActiveOutputTab(agent.id)
                          }
                          className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-medium transition-all whitespace-nowrap ${
                            state?.status === "complete"
                              ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
                              : state?.status === "processing"
                                ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-300 agent-active"
                                : "border-slate-700/50 bg-slate-800/30 text-slate-500"
                          } ${
                            activeOutputTab === agent.id &&
                            state?.status !== "idle"
                              ? "ring-1 ring-cyan-500/30"
                              : ""
                          }`}
                          style={
                            {
                              "--glow-color": agent.color + "40",
                            } as React.CSSProperties
                          }
                        >
                          {state?.status === "complete" ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : state?.status === "processing" ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Icon className="w-3.5 h-3.5" />
                          )}
                          {agent.name}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Main output area */}
              <div className="flex-1 flex overflow-hidden">
                {/* Agent output */}
                <div className="flex-1 overflow-y-auto p-6">
                  {/* Agent info header */}
                  <div className="flex items-center gap-3 mb-4">
                    {(() => {
                      const agent = AGENTS.find(
                        (a) => a.id === activeOutputTab,
                      );
                      const Icon = AGENT_ICONS[activeOutputTab] || Circle;
                      const state = agentStates[activeOutputTab];
                      if (!agent) return null;
                      return (
                        <>
                          <div
                            className="w-9 h-9 rounded-lg flex items-center justify-center"
                            style={{
                              background: agent.color + "18",
                              border: `1px solid ${agent.color}30`,
                            }}
                          >
                            <Icon
                              className="w-4.5 h-4.5"
                              style={{ color: agent.color }}
                            />
                          </div>
                          <div>
                            <div className="text-sm font-bold text-white">
                              {agent.name}
                            </div>
                            <div className="text-[11px] text-slate-500 font-mono">
                              {agent.role} · {agent.model}
                            </div>
                          </div>
                          <div className="ml-auto">
                            <span
                              className={`text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded ${
                                state?.status === "complete"
                                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                  : state?.status === "processing"
                                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                                    : "bg-slate-800/50 text-slate-600 border border-slate-700/50"
                              }`}
                            >
                              {state?.status || "idle"}
                            </span>
                          </div>
                        </>
                      );
                    })()}
                  </div>

                  {/* Output content */}
                  {activeOutput?.status === "idle" ? (
                    <div className="text-sm text-slate-600 italic">
                      Waiting for pipeline to reach this agent...
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Text output (with streaming effect) */}
                      {displayText && (
                        <div className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-4">
                          <pre className="text-[12px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
                            {displayText}
                            {isActiveStreaming && (
                              <span className="stream-cursor" />
                            )}
                          </pre>
                        </div>
                      )}

                      {/* Test cases (if writer agent) */}
                      {activeOutputTab === "writer" &&
                        activeOutput?.testCases &&
                        activeOutput.status === "complete" && (
                          <TestCaseCards cases={activeOutput.testCases} />
                        )}

                      {/* Automation code (if automation agent) */}
                      {activeOutputTab === "automation" &&
                        activeOutput?.automationCode &&
                        activeOutput.status === "complete" && (
                          <div className="bg-slate-900/80 border border-slate-800/60 rounded-lg overflow-hidden">
                            <div className="px-4 py-2 border-b border-slate-800/60 flex items-center gap-2">
                              <FileCode2 className="w-3.5 h-3.5 text-emerald-400" />
                              <span className="text-xs font-mono text-slate-400">
                                oauth2.spec.ts — Playwright
                              </span>
                            </div>
                            <pre className="p-4 text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                              {activeOutput.automationCode}
                            </pre>
                          </div>
                        )}

                      {/* Execution results (if executor) */}
                      {activeOutputTab === "executor" &&
                        testResults.length > 0 && (
                          <div className="space-y-2 mt-4">
                            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
                              Execution Results
                            </div>
                            {testResults.map((tc) => (
                              <div
                                key={tc.id}
                                className={`flex items-center gap-3 px-3 py-2 rounded-lg border text-xs animate-slide-up ${
                                  tc.status === "pass"
                                    ? "bg-emerald-500/5 border-emerald-500/20"
                                    : "bg-rose-500/5 border-rose-500/20"
                                }`}
                              >
                                {tc.status === "pass" ? (
                                  <Check className="w-4 h-4 text-emerald-400" />
                                ) : (
                                  <BadgeAlert className="w-4 h-4 text-rose-400" />
                                )}
                                <span className="font-mono text-slate-400">
                                  {tc.id}
                                </span>
                                <span className="text-slate-300 font-medium">
                                  {tc.name}
                                </span>
                                <span className="ml-auto font-mono text-slate-500">
                                  {tc.duration}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                    </div>
                  )}
                </div>

                {/* Right sidebar — metrics summary */}
                {pipelineStatus !== "idle" && (
                  <div className="w-64 border-l border-slate-800/60 bg-surface/30 overflow-y-auto shrink-0">
                    <div className="px-4 py-3 border-b border-slate-800/60">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                        Pipeline Metrics
                      </span>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-2 p-3">
                      <MetricBox
                        label="Tests"
                        value={testResults.length || "—"}
                        color="text-cyan-400"
                      />
                      <MetricBox
                        label="Passed"
                        value={
                          testResults.filter((t) => t.status === "pass")
                            .length || "—"
                        }
                        color="text-emerald-400"
                      />
                      <MetricBox
                        label="Failed"
                        value={
                          testResults.filter((t) => t.status === "fail")
                            .length || "—"
                        }
                        color="text-rose-400"
                      />
                      <MetricBox
                        label="Pass Rate"
                        value={
                          testResults.length > 0
                            ? Math.round(
                                (testResults.filter((t) => t.status === "pass")
                                  .length /
                                  testResults.length) *
                                  100,
                              ) + "%"
                            : "—"
                        }
                        color="text-amber-400"
                      />
                    </div>

                    {/* Active agents */}
                    <div className="px-4 py-3 border-t border-slate-800/60">
                      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-3">
                        Agent Status
                      </div>
                      {AGENTS.map((agent) => {
                        const state = agentStates[agent.id];
                        return (
                          <div
                            key={agent.id}
                            className="flex items-center gap-2 mb-2 text-xs"
                          >
                            <div
                              className={`w-2 h-2 rounded-full ${
                                state?.status === "complete"
                                  ? "bg-emerald-400"
                                  : state?.status === "processing"
                                    ? "bg-cyan-400 animate-pulse"
                                    : "bg-slate-700"
                              }`}
                            />
                            <span
                              className={
                                state?.status !== "idle"
                                  ? "text-slate-300"
                                  : "text-slate-600"
                              }
                            >
                              {agent.name}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* ── Bottom: Live Console ── */}
              {pipelineStatus !== "idle" && (
                <ConsolePanel
                  logs={logs}
                  logEndRef={logEndRef}
                  agents={AGENTS}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────

function WelcomeScreen() {
  return (
    <div className="flex-1 flex items-center justify-center p-12">
      <div className="max-w-xl text-center">
        <div className="text-[11px] font-mono text-cyan-500 tracking-widest uppercase mb-4 flex items-center justify-center gap-2">
          <Zap className="w-3.5 h-3.5" />
          AI-Powered Multi-Agent System
        </div>
        <h2 className="text-3xl font-black text-white tracking-tight mb-3">
          Test smarter.{" "}
          <span className="bg-linear-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
            Ship faster.
          </span>
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mb-8 max-w-md mx-auto">
          Select a Jira story from the left panel. 7 specialized AI agents will
          analyze requirements, generate test cases, write automation code,
          execute tests, detect bugs, and deliver coverage insights —
          automatically.
        </p>
        <div className="grid grid-cols-3 gap-3 max-w-lg mx-auto">
          {[
            { icon: Search, label: "Analyze", desc: "Parse requirements" },
            { icon: FileCode2, label: "Generate", desc: "Write test cases" },
            { icon: Code2, label: "Automate", desc: "Playwright code" },
            { icon: FlaskConical, label: "Execute", desc: "Run in parallel" },
            { icon: Bug, label: "Detect", desc: "Find root causes" },
            { icon: PieChart, label: "Report", desc: "Coverage insights" },
          ].map((f) => (
            <div
              key={f.label}
              className="bg-surface-card border border-slate-800/60 rounded-lg p-3 text-center card-hover"
            >
              <f.icon className="w-5 h-5 text-slate-400 mx-auto mb-2" />
              <div className="text-xs font-semibold text-slate-300">
                {f.label}
              </div>
              <div className="text-[10px] text-slate-500">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TestCaseCards({ cases }: { cases: TestCase[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  return (
    <div className="space-y-2">
      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
        Generated Test Cases ({cases.length})
      </div>
      {cases.map((tc) => (
        <div
          key={tc.id}
          className="bg-slate-900/50 border border-slate-800/50 rounded-lg overflow-hidden animate-slide-up"
        >
          <div
            className="flex items-center gap-3 px-3 py-2.5 cursor-pointer hover:bg-slate-800/30"
            onClick={() => setExpanded(expanded === tc.id ? null : tc.id)}
          >
            {expanded === tc.id ? (
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
            )}
            <span className="text-[11px] font-mono text-violet-400">
              {tc.id}
            </span>
            <span className="text-xs font-medium text-slate-300">
              {tc.name}
            </span>
            <span
              className={`ml-auto text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                tc.priority === "P0"
                  ? "bg-rose-500/10 text-rose-400"
                  : tc.priority === "P1"
                    ? "bg-amber-500/10 text-amber-400"
                    : "bg-slate-700/50 text-slate-400"
              }`}
            >
              {tc.priority}
            </span>
            <span
              className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                tc.type === "security"
                  ? "bg-red-500/10 text-red-400"
                  : tc.type === "edge"
                    ? "bg-orange-500/10 text-orange-400"
                    : tc.type === "performance"
                      ? "bg-blue-500/10 text-blue-400"
                      : "bg-emerald-500/10 text-emerald-400"
              }`}
            >
              {tc.type}
            </span>
          </div>
          {expanded === tc.id && (
            <div className="px-4 py-3 border-t border-slate-800/40 text-xs animate-slide-up">
              <pre className="text-slate-400 whitespace-pre-wrap font-mono leading-relaxed">
                {tc.scenario}
              </pre>
              <div className="mt-3 space-y-1">
                {tc.steps.map((step, i) => (
                  <div key={i} className="flex gap-2 text-slate-400">
                    <span className="text-slate-600">{i + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 text-emerald-400/80">
                <span className="text-slate-500">Expected: </span>
                {tc.expected}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ConsolePanel({
  logs,
  logEndRef,
  agents,
}: {
  logs: LogEntry[];
  logEndRef: React.RefObject<HTMLDivElement | null>;
  agents: AgentDef[];
}) {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className="border-t border-slate-800/80 bg-surface-deep shrink-0">
      <div
        className="px-4 py-2 flex items-center gap-2 cursor-pointer hover:bg-slate-800/20"
        onClick={() => setCollapsed(!collapsed)}
      >
        <Terminal className="w-3.5 h-3.5 text-slate-500" />
        <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
          Live Console
        </span>
        <span className="text-[10px] font-mono text-slate-600 ml-1">
          {logs.length} events
        </span>
        {collapsed ? (
          <ChevronRight className="w-3 h-3 text-slate-600 ml-auto" />
        ) : (
          <ChevronDown className="w-3 h-3 text-slate-600 ml-auto" />
        )}
      </div>
      {!collapsed && (
        <div className="h-36 overflow-y-auto px-4 pb-3 font-mono text-[11px] leading-relaxed">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-slate-600 shrink-0">[{log.time}]</span>
              <span
                className="shrink-0"
                style={{
                  color:
                    agents.find((a: AgentDef) => a.id === log.agentId)?.color ||
                    "#64748b",
                }}
              >
                {agents.find((a: AgentDef) => a.id === log.agentId)?.name ||
                  log.agentId}
              </span>
              <span className="text-slate-500">→</span>
              <span
                className={
                  log.type === "success"
                    ? "text-emerald-400"
                    : log.type === "error"
                      ? "text-rose-400"
                      : log.type === "warning"
                        ? "text-amber-400"
                        : "text-slate-400"
                }
              >
                {log.message}
              </span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      )}
    </div>
  );
}

function MetricBox({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="bg-surface-card border border-slate-800/50 rounded-lg p-2.5 text-center">
      <div className={`text-lg font-black ${color}`}>{value}</div>
      <div className="text-[9px] font-mono text-slate-500 uppercase tracking-wider">
        {label}
      </div>
    </div>
  );
}

// ─── Util ───────────────────────────────────────────────────

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
