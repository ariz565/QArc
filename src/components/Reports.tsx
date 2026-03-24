import {
  BarChart3,
  PieChart,
  TrendingUp,
  FileText,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { useState, useEffect } from "react";
import {
  getReportData,
  type DashboardStatsData,
  type AgentDef,
  type AgentOutput,
  type JiraStory,
} from "../lib/services";
import {
  DASHBOARD_STATS,
  STORY_OUTPUTS as MOCK_OUTPUTS,
  STORIES as MOCK_STORIES,
  AGENTS as MOCK_AGENTS,
} from "../data/mock";

export default function Reports() {
  const [stats, setStats] = useState(DASHBOARD_STATS as DashboardStatsData);
  const [stories, setStories] = useState<JiraStory[]>(MOCK_STORIES);
  const [storyOutputs, setStoryOutputs] =
    useState<Record<string, AgentOutput[]>>(MOCK_OUTPUTS);
  const [agents, setAgents] = useState<AgentDef[]>(MOCK_AGENTS);

  useEffect(() => {
    getReportData()
      .then((data) => {
        setStats(data.stats);
        setStories(data.stories);
        setStoryOutputs(data.storyOutputs);
        setAgents(data.agents);
      })
      .catch(console.error);
  }, []);

  // Aggregate data across stories
  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;
  const typeDistribution: Record<string, number> = {};
  const priorityDistribution: Record<string, number> = {};

  Object.values(storyOutputs).forEach((outputs) => {
    const writerOutput = outputs.find((o) => o.testCases);
    const executorOutput = outputs.find((o) => o.executionResults);

    writerOutput?.testCases?.forEach((tc) => {
      totalTests++;
      typeDistribution[tc.type] = (typeDistribution[tc.type] || 0) + 1;
      priorityDistribution[tc.priority] =
        (priorityDistribution[tc.priority] || 0) + 1;
    });

    executorOutput?.executionResults?.forEach((r) => {
      if (r.status === "pass") passedTests++;
      if (r.status === "fail") failedTests++;
    });
  });

  const passRate =
    totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 bg-surface-deep/80 backdrop-blur shrink-0">
        <h1 className="text-lg font-bold text-white">Reports & Analytics</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Comprehensive testing insights powered by AI analysis
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-5 gap-3">
          <MiniStat
            label="Total Tests"
            value={totalTests}
            color="text-cyan-400"
          />
          <MiniStat
            label="Passed"
            value={passedTests}
            color="text-emerald-400"
          />
          <MiniStat label="Failed" value={failedTests} color="text-rose-400" />
          <MiniStat
            label="Pass Rate"
            value={`${passRate}%`}
            color="text-amber-400"
          />
          <MiniStat
            label="Stories"
            value={stories.length}
            color="text-violet-400"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Test Type Distribution */}
          <div className="bg-surface-card border border-slate-800/60 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <PieChart className="w-4 h-4 text-violet-400" />
              <h3 className="text-sm font-bold text-white">
                Test Type Distribution
              </h3>
            </div>
            <div className="space-y-3">
              {Object.entries(typeDistribution).map(([type, count]) => {
                const pct = Math.round((count / totalTests) * 100);
                const colorMap: Record<string, string> = {
                  functional: "bg-emerald-500",
                  security: "bg-rose-500",
                  edge: "bg-orange-500",
                  performance: "bg-blue-500",
                };
                return (
                  <div key={type}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-slate-300 capitalize font-medium">
                        {type}
                      </span>
                      <span className="text-slate-500 font-mono">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${colorMap[type] || "bg-slate-500"} transition-all duration-700`}
                        style={{ width: `${pct}%`, opacity: 0.7 }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Priority Distribution */}
          <div className="bg-surface-card border border-slate-800/60 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white">
                Priority Distribution
              </h3>
            </div>
            <div className="space-y-3">
              {["P0", "P1", "P2", "P3"].map((p) => {
                const count = priorityDistribution[p] || 0;
                const pct =
                  totalTests > 0 ? Math.round((count / totalTests) * 100) : 0;
                const colorMap: Record<string, string> = {
                  P0: "bg-rose-500",
                  P1: "bg-amber-500",
                  P2: "bg-blue-500",
                  P3: "bg-slate-500",
                };
                return (
                  <div key={p}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-slate-300 font-medium">
                        {p} —{" "}
                        {p === "P0"
                          ? "Critical"
                          : p === "P1"
                            ? "High"
                            : p === "P2"
                              ? "Medium"
                              : "Low"}
                      </span>
                      <span className="text-slate-500 font-mono">
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${colorMap[p]} transition-all duration-700`}
                        style={{ width: `${pct}%`, opacity: 0.7 }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Per-Story Analysis */}
          <div className="bg-surface-card border border-slate-800/60 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">
                Per-Story Analysis
              </h3>
            </div>
            <div className="space-y-3">
              {stories.map((story) => {
                const outputs = storyOutputs[story.id];
                const testCases =
                  outputs?.find((o) => o.testCases)?.testCases || [];
                const execResults =
                  outputs?.find((o) => o.executionResults)?.executionResults ||
                  [];
                const passed = execResults.filter(
                  (r) => r.status === "pass",
                ).length;
                const failed = execResults.filter(
                  (r) => r.status === "fail",
                ).length;
                const rate =
                  execResults.length > 0
                    ? Math.round((passed / execResults.length) * 100)
                    : 0;

                return (
                  <div
                    key={story.id}
                    className="flex items-center gap-3 p-3 rounded-lg bg-surface/50 border border-slate-800/40"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-mono text-cyan-400">
                        {story.id}
                      </div>
                      <div className="text-xs text-slate-300 truncate mt-0.5">
                        {story.title}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs font-mono text-slate-300">
                        {testCases.length} tests
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] font-mono text-emerald-400">
                          {passed}✓
                        </span>
                        <span className="text-[10px] font-mono text-rose-400">
                          {failed}✗
                        </span>
                        <span
                          className={`text-[10px] font-bold font-mono ${
                            rate >= 80
                              ? "text-emerald-400"
                              : rate >= 60
                                ? "text-amber-400"
                                : "text-rose-400"
                          }`}
                        >
                          {rate}%
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Coverage Report */}
          <div className="bg-surface-card border border-slate-800/60 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Coverage Report</h3>
            </div>
            <div className="space-y-4">
              {[
                {
                  label: "Functional Coverage",
                  value: 94,
                  color: "bg-emerald-500",
                },
                { label: "Security Coverage", value: 78, color: "bg-rose-500" },
                {
                  label: "Edge Case Coverage",
                  value: 85,
                  color: "bg-orange-500",
                },
                {
                  label: "Performance Coverage",
                  value: 67,
                  color: "bg-blue-500",
                },
                {
                  label: "Integration Coverage",
                  value: 72,
                  color: "bg-violet-500",
                },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-slate-300 font-medium">
                      {item.label}
                    </span>
                    <span className="text-slate-400 font-mono font-bold">
                      {item.value}%
                    </span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${item.color} transition-all duration-700`}
                      style={{ width: `${item.value}%`, opacity: 0.6 }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400">
                  CONDITIONAL GO
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Overall coverage meets release threshold. Security and
                performance areas recommended for additional review before
                production deployment.
              </p>
            </div>
          </div>
        </div>

        {/* AI Agent Performance */}
        <div className="bg-surface-card border border-slate-800/60 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-5">
            <TrendingUp className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white">
              Agent Performance Metrics
            </h3>
          </div>
          <div className="grid grid-cols-7 gap-3">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="text-center p-3 rounded-lg border"
                style={{
                  borderColor: agent.color + "20",
                  background: agent.color + "05",
                }}
              >
                <div
                  className="text-lg font-black mb-1"
                  style={{ color: agent.color }}
                >
                  {
                    ["2.1s", "1.8s", "3.2s", "2.7s", "4.1s", "1.9s", "1.5s"][
                      agents.indexOf(agent)
                    ]
                  }
                </div>
                <div className="text-[10px] text-slate-400 font-medium">
                  {agent.name}
                </div>
                <div className="text-[9px] text-slate-600 font-mono mt-0.5">
                  avg latency
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function MiniStat({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="bg-surface-card border border-slate-800/50 rounded-lg p-3 text-center">
      <div className={`text-xl font-black ${color}`}>{value}</div>
      <div className="text-[10px] text-slate-500 mt-0.5">{label}</div>
    </div>
  );
}
