import { useState, useEffect } from "react";
import {
  Clock,
  ChevronDown,
  ChevronRight,
  Check,
  X,
  Play,
  GitBranch,
  Filter,
  Calendar,
} from "lucide-react";
import { PageHeader } from "./ui/PageHeader";
import { Badge } from "./ui/Badge";
import { FRAMEWORKS } from "../lib/adapters";
import { getExecutions, type ExecutionRun } from "../lib/services";

// ─── Mock execution history ──────────────────────────────────

const MOCK_RUNS: ExecutionRun[] = [
  {
    id: "run-001",
    storyId: "PROJ-1042",
    storyTitle: "OAuth2 Authentication",
    framework: "playwright",
    trigger: "manual",
    timestamp: "Mar 24, 2026 · 10:30 AM",
    duration: "4.2s",
    total: 8,
    passed: 6,
    failed: 2,
    skipped: 0,
    environment: "Chromium · 1920×1080 · Linux",
    coveragePercent: 87,
  },
  {
    id: "run-002",
    storyId: "PROJ-1043",
    storyTitle: "Shopping Cart Checkout",
    framework: "cypress",
    trigger: "ci",
    timestamp: "Mar 24, 2026 · 09:15 AM",
    duration: "12.3s",
    total: 8,
    passed: 7,
    failed: 1,
    skipped: 0,
    environment: "Chrome · 1920×1080 · Windows",
    coveragePercent: 92,
  },
  {
    id: "run-003",
    storyId: "PROJ-1044",
    storyTitle: "Real-time Notifications",
    framework: "playwright",
    trigger: "manual",
    timestamp: "Mar 24, 2026 · 08:45 AM",
    duration: "6.7s",
    total: 8,
    passed: 8,
    failed: 0,
    skipped: 0,
    environment: "Chromium · 1920×1080 · Linux",
    coveragePercent: 95,
  },
  {
    id: "run-004",
    storyId: "PROJ-1042",
    storyTitle: "OAuth2 Authentication",
    framework: "selenium",
    trigger: "scheduled",
    timestamp: "Mar 23, 2026 · 11:00 PM",
    duration: "8.1s",
    total: 8,
    passed: 5,
    failed: 3,
    skipped: 0,
    environment: "Firefox · 1920×1080 · Linux",
    coveragePercent: 78,
  },
  {
    id: "run-005",
    storyId: "PROJ-1040",
    storyTitle: "User Profile API",
    framework: "playwright",
    trigger: "ci",
    timestamp: "Mar 23, 2026 · 06:30 PM",
    duration: "3.9s",
    total: 12,
    passed: 12,
    failed: 0,
    skipped: 0,
    environment: "Chromium · 1920×1080 · Linux",
    coveragePercent: 98,
  },
  {
    id: "run-006",
    storyId: "PROJ-1038",
    storyTitle: "File Upload Service",
    framework: "cypress",
    trigger: "manual",
    timestamp: "Mar 23, 2026 · 03:15 PM",
    duration: "15.4s",
    total: 10,
    passed: 8,
    failed: 1,
    skipped: 1,
    environment: "Chrome · 1920×1080 · macOS",
    coveragePercent: 85,
  },
  {
    id: "run-007",
    storyId: "PROJ-1035",
    storyTitle: "Search Filters",
    framework: "playwright",
    trigger: "ci",
    timestamp: "Mar 23, 2026 · 12:00 PM",
    duration: "5.2s",
    total: 15,
    passed: 15,
    failed: 0,
    skipped: 0,
    environment: "Chromium + Firefox · 1920×1080",
    coveragePercent: 96,
  },
  {
    id: "run-008",
    storyId: "PROJ-1043",
    storyTitle: "Shopping Cart Checkout",
    framework: "selenium",
    trigger: "scheduled",
    timestamp: "Mar 22, 2026 · 11:00 PM",
    duration: "18.7s",
    total: 8,
    passed: 6,
    failed: 2,
    skipped: 0,
    environment: "Firefox + Edge · 1920×1080 · Windows",
    coveragePercent: 82,
  },
];

// ─── Trigger icons ───────────────────────────────────────────

const TRIGGER_ICONS: Record<string, React.ElementType> = {
  manual: Play,
  ci: GitBranch,
  scheduled: Clock,
};

const TRIGGER_LABELS: Record<string, string> = {
  manual: "Manual",
  ci: "CI/CD",
  scheduled: "Scheduled",
};

// ═════════════════════════════════════════════════════════════

export default function ExecutionHistory() {
  const [runs, setRuns] = useState<ExecutionRun[]>(MOCK_RUNS);
  const [expandedRun, setExpandedRun] = useState<string | null>(null);
  const [filterFramework, setFilterFramework] = useState<string>("all");

  useEffect(() => {
    getExecutions()
      .then((data) => {
        if (data.length > 0) setRuns(data);
      })
      .catch(console.error);
  }, []);

  const filtered =
    filterFramework === "all"
      ? runs
      : runs.filter((r) => r.framework === filterFramework);

  // Aggregate stats
  const totalRuns = runs.length;
  const avgPassRate =
    runs.length > 0
      ? Math.round(
          runs.reduce((sum, r) => sum + (r.passed / r.total) * 100, 0) /
            runs.length,
        )
      : 0;
  const totalTests = runs.reduce((sum, r) => sum + r.total, 0);
  const totalPassed = runs.reduce((sum, r) => sum + r.passed, 0);

  return (
    <div className="h-full flex flex-col">
      <PageHeader
        title="Execution History"
        subtitle={`${totalRuns} pipeline runs · ${totalTests} total tests · ${avgPassRate}% avg pass rate`}
        actions={
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={filterFramework}
              onChange={(e) => setFilterFramework(e.target.value)}
              className="bg-surface-card border border-edge rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none"
            >
              <option value="all">All Frameworks</option>
              {FRAMEWORKS.filter((f) => f.status !== "coming-soon").map(
                (fw) => (
                  <option key={fw.id} value={fw.id}>
                    {fw.name}
                  </option>
                ),
              )}
            </select>
          </div>
        }
      />

      <div className="flex-1 overflow-y-auto">
        {/* Stats bar */}
        <div className="grid grid-cols-4 gap-3 px-6 py-4 border-b border-edge">
          <MiniStat
            label="Total Runs"
            value={totalRuns}
            color="text-cyan-400"
          />
          <MiniStat
            label="Tests Executed"
            value={totalTests}
            color="text-violet-400"
          />
          <MiniStat
            label="Tests Passed"
            value={totalPassed}
            color="text-emerald-400"
          />
          <MiniStat
            label="Avg Pass Rate"
            value={`${avgPassRate}%`}
            color="text-amber-400"
          />
        </div>

        {/* Run list */}
        <div className="p-6 space-y-2">
          {filtered.map((run) => {
            const isExpanded = expandedRun === run.id;
            const passRate = Math.round((run.passed / run.total) * 100);
            const fw = FRAMEWORKS.find((f) => f.id === run.framework);
            const TriggerIcon = TRIGGER_ICONS[run.trigger] || Clock;

            return (
              <div
                key={run.id}
                className="bg-surface-card border border-edge rounded-xl overflow-hidden"
              >
                {/* Run row */}
                <div
                  className="flex items-center gap-4 px-5 py-3.5 cursor-pointer hover:bg-surface-hover transition-colors"
                  onClick={() => setExpandedRun(isExpanded ? null : run.id)}
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-500 shrink-0" />
                  )}

                  {/* Status dot */}
                  <div
                    className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                      run.failed === 0
                        ? "bg-emerald-400"
                        : run.failed <= 1
                          ? "bg-amber-400"
                          : "bg-rose-400"
                    }`}
                  />

                  {/* Story */}
                  <div className="w-48 shrink-0">
                    <div className="text-xs font-mono text-cyan-400">
                      {run.storyId}
                    </div>
                    <div className="text-xs text-slate-300 truncate">
                      {run.storyTitle}
                    </div>
                  </div>

                  {/* Framework badge */}
                  <div
                    className="text-[10px] font-bold font-mono px-2 py-0.5 rounded shrink-0"
                    style={{
                      color: fw?.color,
                      background: (fw?.color || "#666") + "15",
                      border: `1px solid ${fw?.color || "#666"}30`,
                    }}
                  >
                    {fw?.shortName || run.framework}
                  </div>

                  {/* Trigger */}
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-500 w-20 shrink-0">
                    <TriggerIcon className="w-3 h-3" />
                    {TRIGGER_LABELS[run.trigger]}
                  </div>

                  {/* Results */}
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                      <Check className="w-3 h-3" /> {run.passed}
                    </span>
                    {run.failed > 0 && (
                      <span className="text-[11px] font-mono text-rose-400 flex items-center gap-1">
                        <X className="w-3 h-3" /> {run.failed}
                      </span>
                    )}
                    {run.skipped > 0 && (
                      <span className="text-[11px] font-mono text-slate-500">
                        ~{run.skipped}
                      </span>
                    )}
                  </div>

                  {/* Pass rate bar */}
                  <div className="flex-1 flex items-center gap-2 min-w-0">
                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          passRate >= 90
                            ? "bg-emerald-500"
                            : passRate >= 70
                              ? "bg-amber-500"
                              : "bg-rose-500"
                        }`}
                        style={{ width: `${passRate}%`, opacity: 0.7 }}
                      />
                    </div>
                    <span
                      className={`text-[11px] font-mono font-bold w-10 text-right ${
                        passRate >= 90
                          ? "text-emerald-400"
                          : passRate >= 70
                            ? "text-amber-400"
                            : "text-rose-400"
                      }`}
                    >
                      {passRate}%
                    </span>
                  </div>

                  {/* Metadata */}
                  <div className="text-right shrink-0">
                    <div className="text-[10px] font-mono text-slate-500">
                      {run.duration}
                    </div>
                    <div className="text-[10px] text-slate-600">
                      {run.timestamp.split("·")[0]}
                    </div>
                  </div>
                </div>

                {/* Expanded detail */}
                {isExpanded && (
                  <div className="px-5 py-4 border-t border-edge bg-surface/50 animate-slide-up">
                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <DetailItem
                        label="Framework"
                        value={fw?.name || run.framework}
                      />
                      <DetailItem label="Environment" value={run.environment} />
                      <DetailItem
                        label="Trigger"
                        value={TRIGGER_LABELS[run.trigger]}
                      />
                      <DetailItem
                        label="Coverage"
                        value={`${run.coveragePercent}%`}
                      />
                    </div>
                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <DetailItem
                        label="Total Tests"
                        value={String(run.total)}
                      />
                      <DetailItem label="Passed" value={String(run.passed)} />
                      <DetailItem label="Failed" value={String(run.failed)} />
                      <DetailItem label="Duration" value={run.duration} />
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3 h-3 text-slate-600" />
                      <span className="text-[11px] text-slate-500">
                        {run.timestamp}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────

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
    <div className="bg-surface-card border border-edge rounded-lg p-3 text-center">
      <div className={`text-xl font-black ${color}`}>{value}</div>
      <div className="text-[10px] text-slate-500 mt-0.5">{label}</div>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] font-mono text-slate-600 uppercase">
        {label}
      </div>
      <div className="text-xs text-slate-300 mt-0.5">{value}</div>
    </div>
  );
}
