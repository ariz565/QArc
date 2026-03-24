import {
  FlaskConical,
  CheckCircle2,
  Bug,
  Clock,
  TrendingUp,
  Activity,
  Zap,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  Brain,
  Target,
  Layers,
  Gauge,
  Sparkles,
  GitBranch,
} from "lucide-react";
import { useState, useEffect } from "react";
import { getDashboardStats, type DashboardStatsData } from "../lib/services";
import { DASHBOARD_STATS } from "../data/mock";
import { METRIC_PRESETS, STATUS, TREND, CHART } from "../lib/colors";
import { PageHeader } from "./ui/PageHeader";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStatsData>(
    DASHBOARD_STATS as DashboardStatsData,
  );

  useEffect(() => {
    getDashboardStats().then(setStats).catch(console.error);
  }, []);

  const passRate = stats.avgPassRate;
  const executionRate = Math.round(
    (stats.totalTestsExecuted / stats.totalTestsGenerated) * 100,
  );

  return (
    <div className="h-full overflow-y-auto">
      <PageHeader
        title="Dashboard"
        subtitle="Real-time overview of AI-powered testing metrics"
        actions={
          <div className="flex items-center gap-2 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live · Sprint 23
          </div>
        }
      />

      <div className="p-6 space-y-5">
        {/* ── Row 1: Key Metrics ── */}
        <div className="grid grid-cols-6 gap-3">
          <MiniMetric
            icon={FlaskConical}
            label="Tests Generated"
            value={stats.totalTestsGenerated.toLocaleString()}
            preset="cyan"
          />
          <MiniMetric
            icon={CheckCircle2}
            label="Pass Rate"
            value={passRate + "%"}
            preset="emerald"
          />
          <MiniMetric
            icon={Bug}
            label="Bugs Found"
            value={stats.bugsFound.toString()}
            preset="rose"
          />
          <MiniMetric
            icon={Clock}
            label="Hours Saved"
            value={stats.timeSavedHours.toString()}
            preset="amber"
          />
          <MiniMetric
            icon={Target}
            label="Stories Analyzed"
            value={stats.storiesAnalyzed.toString()}
            preset="violet"
          />
          <MiniMetric
            icon={Layers}
            label="Execution Rate"
            value={executionRate + "%"}
            preset="blue"
          />
        </div>

        {/* ── Row 2: Weekly Trend + AI Health Ring ── */}
        <div className="grid grid-cols-12 gap-4">
          {/* Weekly Trend — 8 col */}
          <div className="col-span-8 bg-surface-card border border-edge rounded-xl p-5">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="text-sm font-bold text-white">
                  Weekly Test Execution
                </h3>
                <p className="text-[11px] text-slate-500">
                  Pass vs Fail trend · last 7 days
                </p>
              </div>
              <div className="flex gap-4 text-[11px]">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-emerald-400" /> Passed
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-rose-400" /> Failed
                </span>
              </div>
            </div>

            <div className="flex items-end gap-3 h-40">
              {stats.weeklyTrend.map((day) => {
                const total = day.tests;
                const passH = total > 0 ? (day.pass / total) * 140 : 0;
                const failH = total > 0 ? (day.fail / total) * 140 : 0;
                return (
                  <div
                    key={day.day}
                    className="flex-1 flex flex-col items-center gap-1 group"
                  >
                    {/* Tooltip */}
                    <div className="text-[9px] font-mono text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      {day.pass}/{total}
                    </div>
                    <div className="flex flex-col-reverse items-center gap-0.5 h-36 w-full">
                      <div
                        className={`w-full rounded-t ${CHART.passBar} transition-all duration-700`}
                        style={{ height: passH }}
                      />
                      <div
                        className={`w-full rounded-t ${CHART.failBar} transition-all duration-700`}
                        style={{ height: failH }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {day.day}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Health Gauges — 4 col */}
          <div className="col-span-4 space-y-3">
            <div className="bg-surface-card border border-edge rounded-xl p-4">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-bold text-white">AI Health</h3>
              </div>
              <div className="space-y-3">
                <GaugeBar
                  label="Test Coverage"
                  value={87}
                  color="bg-emerald-500/60"
                  textColor="text-emerald-400"
                />
                <GaugeBar
                  label="Automation Rate"
                  value={94}
                  color="bg-violet-500/60"
                  textColor="text-violet-400"
                />
                <GaugeBar
                  label="First-Run Pass"
                  value={passRate}
                  color="bg-cyan-500/60"
                  textColor="text-cyan-400"
                />
                <GaugeBar
                  label="Bug Detection"
                  value={76}
                  color="bg-amber-500/60"
                  textColor="text-amber-400"
                />
              </div>
            </div>

            <div className="bg-linear-to-br from-cyan-500/10 to-violet-500/10 border border-cyan-500/20 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold text-white">
                  Sprint 23 Highlights
                </span>
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-400 leading-relaxed">
                <li className="flex gap-2">
                  <span className="text-emerald-400">+</span> 7 agents processed
                  156 stories
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-400">+</span> 1,247 test cases
                  generated
                </li>
                <li className="flex gap-2">
                  <span className="text-emerald-400">+</span> {passRate}%
                  first-run pass rate
                </li>
                <li className="flex gap-2">
                  <span className="text-rose-400">!</span> 12 critical security
                  bugs caught
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* ── Row 3: Top Issues + Recent Runs + Agent Performance ── */}
        <div className="grid grid-cols-12 gap-4">
          {/* Top Issues — 3 col */}
          <div className="col-span-3 bg-surface-card border border-edge rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">Top Issues</h3>
              <Bug className="w-4 h-4 text-rose-400" />
            </div>
            <div className="space-y-2.5">
              {stats.topIssues.map((issue, i) => (
                <div key={i} className="flex items-center gap-2.5">
                  <span
                    className={`text-[8px] font-bold uppercase px-1.5 py-0.5 rounded ${
                      TREND[issue.trend as keyof typeof TREND]?.bg ||
                      TREND.neutral.bg
                    } ${TREND[issue.trend as keyof typeof TREND]?.text || TREND.neutral.text}`}
                  >
                    {issue.trend}
                  </span>
                  <span className="text-xs text-slate-300 flex-1 truncate">
                    {issue.type}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">
                    {issue.count}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Pipeline Runs — 5 col */}
          <div className="col-span-5 bg-surface-card border border-edge rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">Recent Runs</h3>
              <Activity className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="space-y-1.5">
              {stats.recentRuns.map((run, i) => {
                const total = run.pass + run.fail;
                const rate = Math.round((run.pass / total) * 100);
                return (
                  <div
                    key={i}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg bg-surface/50 border border-edge-light"
                  >
                    <div
                      className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                        run.fail === 0
                          ? STATUS.pass.dot
                          : run.fail <= 2
                            ? STATUS.warning.dot
                            : STATUS.fail.dot
                      }`}
                    />
                    <span className="text-[11px] font-mono text-cyan-400 w-20 shrink-0">
                      {run.storyId}
                    </span>
                    <span className="text-[11px] text-slate-300 flex-1 truncate">
                      {run.title}
                    </span>
                    {/* Mini pass/fail bar */}
                    <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden shrink-0">
                      <div
                        className="h-full bg-emerald-500/70 rounded-full"
                        style={{ width: `${rate}%` }}
                      />
                    </div>
                    <span className="text-[9px] font-mono text-slate-500 w-8 text-right">
                      {rate}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Agent Performance — 4 col */}
          <div className="col-span-4 bg-surface-card border border-edge rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">Agent Speed</h3>
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div className="space-y-2">
              {[
                { name: "Story Analyzer", time: "1.2s", color: "#22d3ee" },
                { name: "Test Strategist", time: "0.8s", color: "#fb923c" },
                { name: "Test Writer", time: "2.4s", color: "#a78bfa" },
                { name: "Automation Eng", time: "1.8s", color: "#34d399" },
                { name: "Test Executor", time: "4.2s", color: "#60a5fa" },
                { name: "Bug Detective", time: "1.5s", color: "#fb7185" },
                { name: "Coverage Analyst", time: "0.6s", color: "#fbbf24" },
              ].map((agent) => (
                <div key={agent.name} className="flex items-center gap-2.5">
                  <div
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ background: agent.color }}
                  />
                  <span className="text-[11px] text-slate-300 flex-1">
                    {agent.name}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">
                    {agent.time}
                  </span>
                  <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.min((parseFloat(agent.time) / 5) * 100, 100)}%`,
                        background: agent.color + "80",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Row 4: Framework Usage + Coverage Heatmap + Quick Actions ── */}
        <div className="grid grid-cols-12 gap-4">
          {/* Framework Usage */}
          <div className="col-span-4 bg-surface-card border border-edge rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">Framework Usage</h3>
              <GitBranch className="w-4 h-4 text-violet-400" />
            </div>
            <div className="space-y-2.5">
              {[
                { name: "Playwright", pct: 62, color: "#2EAD33" },
                { name: "Cypress", pct: 24, color: "#69D3A7" },
                { name: "Selenium", pct: 14, color: "#43B02A" },
              ].map((fw) => (
                <div key={fw.name}>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-300">{fw.name}</span>
                    <span className="font-mono" style={{ color: fw.color }}>
                      {fw.pct}%
                    </span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${fw.pct}%`,
                        background: fw.color + "90",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Test Type Distribution */}
          <div className="col-span-4 bg-surface-card border border-edge rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">
                Test Distribution
              </h3>
              <Gauge className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              {[
                {
                  label: "Functional",
                  count: 847,
                  color: "text-emerald-400",
                  bg: "bg-emerald-500/10",
                },
                {
                  label: "Security",
                  count: 186,
                  color: "text-rose-400",
                  bg: "bg-rose-500/10",
                },
                {
                  label: "Edge Cases",
                  count: 124,
                  color: "text-orange-400",
                  bg: "bg-orange-500/10",
                },
                {
                  label: "Performance",
                  count: 56,
                  color: "text-blue-400",
                  bg: "bg-blue-500/10",
                },
                {
                  label: "Accessibility",
                  count: 34,
                  color: "text-violet-400",
                  bg: "bg-violet-500/10",
                },
                {
                  label: "Visual",
                  count: 0,
                  color: "text-slate-500",
                  bg: "bg-slate-800/50",
                },
              ].map((t) => (
                <div
                  key={t.label}
                  className={`${t.bg} rounded-lg p-2.5 text-center`}
                >
                  <div className={`text-lg font-black ${t.color}`}>
                    {t.count}
                  </div>
                  <div className="text-[9px] text-slate-500 uppercase tracking-wider mt-0.5">
                    {t.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quality Score + Coverage */}
          <div className="col-span-4 space-y-3">
            <div className="bg-surface-card border border-edge rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white">Quality Score</h3>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex items-center gap-4">
                <div className="relative w-16 h-16">
                  <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      className="text-slate-800"
                    />
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeDasharray={`${87 * 0.88} ${88 - 87 * 0.88}`}
                      strokeLinecap="round"
                      className="text-emerald-400"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-black text-emerald-400">
                      A+
                    </span>
                  </div>
                </div>
                <div className="space-y-1 text-[10px]">
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-16">Coverage</span>
                    <span className="text-emerald-400 font-mono">87%</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-16">Stability</span>
                    <span className="text-cyan-400 font-mono">94%</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-16">Speed</span>
                    <span className="text-amber-400 font-mono">92%</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-16">Security</span>
                    <span className="text-violet-400 font-mono">85%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-surface-card border border-edge rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-xs font-bold text-white">
                  vs Last Sprint
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <CompareChip label="Tests" value="+18%" positive />
                <CompareChip label="Pass Rate" value="+2.3%" positive />
                <CompareChip label="Bugs" value="-31%" positive />
                <CompareChip label="Coverage" value="+5%" positive />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────

function MiniMetric({
  icon: Icon,
  label,
  value,
  preset,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  preset: keyof typeof METRIC_PRESETS;
}) {
  const p = METRIC_PRESETS[preset];
  return (
    <div
      className={`bg-surface-card border rounded-xl p-4 card-hover ${p.border}`}
    >
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 ${p.bg}`}
      >
        <Icon className={`w-4 h-4 ${p.text}`} />
      </div>
      <div className={`text-xl font-black ${p.text} mb-0.5`}>{value}</div>
      <div className="text-[10px] text-slate-500">{label}</div>
    </div>
  );
}

function GaugeBar({
  label,
  value,
  color,
  textColor,
}: {
  label: string;
  value: number;
  color: string;
  textColor: string;
}) {
  return (
    <div>
      <div className="flex justify-between text-[11px] mb-1">
        <span className="text-slate-400">{label}</span>
        <span className={`font-mono ${textColor}`}>{value}%</span>
      </div>
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-700`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function CompareChip({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive: boolean;
}) {
  return (
    <div className="flex items-center justify-between bg-surface/50 rounded-lg px-2.5 py-1.5">
      <span className="text-[10px] text-slate-500">{label}</span>
      <span
        className={`text-[10px] font-mono flex items-center gap-0.5 ${
          positive ? "text-emerald-400" : "text-rose-400"
        }`}
      >
        {positive ? (
          <ArrowUpRight className="w-2.5 h-2.5" />
        ) : (
          <ArrowDownRight className="w-2.5 h-2.5" />
        )}
        {value}
      </span>
    </div>
  );
}
