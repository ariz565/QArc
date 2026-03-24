import { useState, useEffect } from "react";
import {
  Filter,
  ChevronDown,
  ChevronRight,
  Check,
  X,
  Clock,
  AlertTriangle,
  ShieldCheck,
  Gauge,
  FlaskConical,
} from "lucide-react";
import {
  getAllTestCases,
  getStories,
  type TestCase,
  type JiraStory,
} from "../lib/services";
import { STORY_OUTPUTS, STORIES as MOCK_STORIES } from "../data/mock";

const TYPE_ICONS: Record<string, React.ElementType> = {
  functional: FlaskConical,
  security: ShieldCheck,
  edge: AlertTriangle,
  performance: Gauge,
};

const TYPE_COLORS: Record<string, string> = {
  functional: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  security: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  edge: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  performance: "text-blue-400 bg-blue-500/10 border-blue-500/20",
};

const PRIORITY_COLORS: Record<string, string> = {
  P0: "text-rose-400 bg-rose-500/10",
  P1: "text-amber-400 bg-amber-500/10",
  P2: "text-blue-400 bg-blue-500/10",
  P3: "text-slate-400 bg-slate-700/50",
};

export default function TestCases() {
  const [filterType, setFilterType] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [filterStory, setFilterStory] = useState<string>("all");
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [stories, setStories] = useState<JiraStory[]>(MOCK_STORIES);

  // Collect all test cases from all stories — initialised from mock, then overwritten
  const buildCasesFromMock = (): (TestCase & { storyId: string })[] => {
    const cases: (TestCase & { storyId: string })[] = [];
    Object.entries(STORY_OUTPUTS).forEach(([storyId, outputs]) => {
      const writerOutput = outputs.find((o) => o.testCases);
      if (writerOutput?.testCases) {
        writerOutput.testCases.forEach((tc) => {
          cases.push({ ...tc, storyId });
        });
      }
    });
    return cases;
  };

  const [allCases, setAllCases] =
    useState<(TestCase & { storyId: string })[]>(buildCasesFromMock);

  useEffect(() => {
    getAllTestCases()
      .then((groups) => {
        const flat: (TestCase & { storyId: string })[] = [];
        groups.forEach((g) =>
          g.tests.forEach((tc) => flat.push({ ...tc, storyId: g.storyId })),
        );
        setAllCases(flat);
      })
      .catch(console.error);

    getStories().then(setStories).catch(console.error);
  }, []);

  // Apply filters
  const filtered = allCases.filter((tc) => {
    if (filterType !== "all" && tc.type !== filterType) return false;
    if (filterPriority !== "all" && tc.priority !== filterPriority)
      return false;
    if (filterStory !== "all" && tc.storyId !== filterStory) return false;
    return true;
  });

  const typeCount = (t: string) => allCases.filter((c) => c.type === t).length;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 bg-surface-deep/80 backdrop-blur shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">Test Cases</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {allCases.length} test cases generated across{" "}
              {new Set(allCases.map((c) => c.storyId)).size} stories
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Filter sidebar */}
        <div className="w-56 border-r border-slate-800/60 bg-surface overflow-y-auto shrink-0">
          <div className="px-4 py-3 border-b border-slate-800/40">
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-500">
              <Filter className="w-3 h-3" /> Filters
            </div>
          </div>

          {/* Filter: Story */}
          <div className="px-4 py-3 border-b border-slate-800/40">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
              Story
            </div>
            <button
              onClick={() => setFilterStory("all")}
              className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 ${
                filterStory === "all"
                  ? "bg-cyan-500/10 text-cyan-400"
                  : "text-slate-400 hover:bg-slate-800/40"
              }`}
            >
              All Stories
            </button>
            {stories.map((s) => (
              <button
                key={s.id}
                onClick={() => setFilterStory(s.id)}
                className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 truncate ${
                  filterStory === s.id
                    ? "bg-cyan-500/10 text-cyan-400"
                    : "text-slate-400 hover:bg-slate-800/40"
                }`}
              >
                {s.id}
              </button>
            ))}
          </div>

          {/* Filter: Type */}
          <div className="px-4 py-3 border-b border-slate-800/40">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
              Type
            </div>
            <button
              onClick={() => setFilterType("all")}
              className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 ${
                filterType === "all"
                  ? "bg-cyan-500/10 text-cyan-400"
                  : "text-slate-400 hover:bg-slate-800/40"
              }`}
            >
              All Types ({allCases.length})
            </button>
            {["functional", "security", "edge", "performance"].map((t) => {
              const Icon = TYPE_ICONS[t] || FlaskConical;
              return (
                <button
                  key={t}
                  onClick={() => setFilterType(t)}
                  className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 flex items-center gap-2 ${
                    filterType === t
                      ? "bg-cyan-500/10 text-cyan-400"
                      : "text-slate-400 hover:bg-slate-800/40"
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  <span className="capitalize">{t}</span>
                  <span className="ml-auto text-[10px] font-mono text-slate-600">
                    {typeCount(t)}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Filter: Priority */}
          <div className="px-4 py-3">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
              Priority
            </div>
            <button
              onClick={() => setFilterPriority("all")}
              className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 ${
                filterPriority === "all"
                  ? "bg-cyan-500/10 text-cyan-400"
                  : "text-slate-400 hover:bg-slate-800/40"
              }`}
            >
              All Priorities
            </button>
            {["P0", "P1", "P2", "P3"].map((p) => (
              <button
                key={p}
                onClick={() => setFilterPriority(p)}
                className={`w-full text-left text-xs px-2 py-1.5 rounded mb-1 flex items-center gap-2 ${
                  filterPriority === p
                    ? "bg-cyan-500/10 text-cyan-400"
                    : "text-slate-400 hover:bg-slate-800/40"
                }`}
              >
                <span
                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${PRIORITY_COLORS[p]}`}
                >
                  {p}
                </span>
                <span className="ml-auto text-[10px] font-mono text-slate-600">
                  {allCases.filter((c) => c.priority === p).length}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Main content — test case list */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="text-xs text-slate-500 mb-4">
            Showing {filtered.length} of {allCases.length} test cases
          </div>

          <div className="space-y-2">
            {filtered.map((tc) => {
              const Icon = TYPE_ICONS[tc.type] || FlaskConical;
              const typeCol = TYPE_COLORS[tc.type] || TYPE_COLORS.functional;
              const isExpanded = expandedCase === tc.id + tc.storyId;

              return (
                <div
                  key={tc.id + tc.storyId}
                  className="bg-surface-card border border-slate-800/50 rounded-lg overflow-hidden"
                >
                  <div
                    className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-slate-800/20 transition"
                    onClick={() =>
                      setExpandedCase(isExpanded ? null : tc.id + tc.storyId)
                    }
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-500 shrink-0" />
                    )}

                    <div
                      className={`w-7 h-7 rounded flex items-center justify-center border ${typeCol} shrink-0`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-slate-200 truncate">
                        {tc.name}
                      </div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                        {tc.id} · {tc.storyId}
                      </div>
                    </div>

                    <span
                      className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded ${PRIORITY_COLORS[tc.priority]}`}
                    >
                      {tc.priority}
                    </span>

                    <span
                      className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${typeCol}`}
                    >
                      {tc.type}
                    </span>

                    {tc.status === "pass" && (
                      <Check className="w-4 h-4 text-emerald-400" />
                    )}
                    {tc.status === "fail" && (
                      <X className="w-4 h-4 text-rose-400" />
                    )}
                    {tc.status === "pending" && (
                      <Clock className="w-4 h-4 text-slate-600" />
                    )}
                  </div>

                  {isExpanded && (
                    <div className="px-4 py-4 border-t border-slate-800/40 animate-slide-up">
                      {/* Scenario */}
                      <div className="mb-4">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
                          BDD Scenario
                        </div>
                        <pre className="text-xs font-mono text-violet-300/80 whitespace-pre-wrap bg-violet-500/5 border border-violet-500/10 rounded-lg p-3 leading-relaxed">
                          {tc.scenario}
                        </pre>
                      </div>

                      {/* Steps */}
                      <div className="mb-4">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
                          Steps
                        </div>
                        <div className="space-y-1.5">
                          {tc.steps.map((step, i) => (
                            <div
                              key={i}
                              className="flex gap-2 text-xs text-slate-300"
                            >
                              <span className="text-slate-600 font-mono w-5 text-right shrink-0">
                                {i + 1}.
                              </span>
                              <span>{step}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Expected */}
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
                          Expected Result
                        </div>
                        <div className="text-xs text-emerald-400/70 bg-emerald-500/5 border border-emerald-500/10 rounded-lg p-3">
                          {tc.expected}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
