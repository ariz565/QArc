import {
  Search,
  BookOpen,
  FileCode2,
  Code2,
  FlaskConical,
  Bug,
  PieChart,
  ArrowRight,
  Cpu,
  Brain,
  Sparkles,
} from "lucide-react";
import { useState, useEffect } from "react";
import { getAgents, type AgentDef } from "../lib/services";
import { AGENTS as MOCK_AGENTS } from "../data/mock";

const AGENT_ICONS: Record<string, React.ElementType> = {
  story: Search,
  strategy: BookOpen,
  writer: FileCode2,
  automation: Code2,
  executor: FlaskConical,
  bug: Bug,
  coverage: PieChart,
};

const CONNECTIONS: [string, string][] = [
  ["story", "strategy"],
  ["strategy", "writer"],
  ["writer", "automation"],
  ["automation", "executor"],
  ["executor", "bug"],
  ["bug", "coverage"],
];

export default function AgentNetwork() {
  const [AGENTS, setAgents] = useState<AgentDef[]>(MOCK_AGENTS);

  useEffect(() => {
    getAgents().then(setAgents).catch(console.error);
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 bg-surface-deep/80 backdrop-blur shrink-0">
        <h1 className="text-lg font-bold text-white">Agent Network</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          7 specialized AI agents working in orchestrated pipeline
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Pipeline Flow */}
        <div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <Sparkles className="w-3 h-3 text-cyan-400" /> Pipeline Architecture
          </div>

          <div className="flex items-center gap-3 overflow-x-auto pb-4">
            {AGENTS.map((agent, idx) => {
              const Icon = AGENT_ICONS[agent.id] || Cpu;
              return (
                <div
                  key={agent.id}
                  className="flex items-center gap-3 shrink-0"
                >
                  <div
                    className="w-40 rounded-xl border p-4 card-hover"
                    style={{
                      borderColor: agent.color + "30",
                      background: agent.color + "08",
                    }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ background: agent.color + "20" }}
                      >
                        <Icon
                          className="w-4 h-4"
                          style={{ color: agent.color }}
                        />
                      </div>
                      <span
                        className="text-[10px] font-mono font-bold"
                        style={{ color: agent.color }}
                      >
                        #{idx + 1}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-slate-200 mb-1">
                      {agent.name}
                    </div>
                    <div className="text-[10px] text-slate-500">
                      {agent.role}
                    </div>
                    <div className="mt-2 text-[10px] font-mono text-slate-600 bg-slate-900/50 rounded px-2 py-1">
                      {agent.model}
                    </div>
                  </div>
                  {idx < AGENTS.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-slate-600 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Agent Details */}
        <div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <Brain className="w-3 h-3 text-violet-400" /> Agent Capabilities
          </div>

          <div className="grid grid-cols-2 gap-4">
            {AGENTS.map((agent) => {
              const Icon = AGENT_ICONS[agent.id] || Cpu;
              return (
                <div
                  key={agent.id}
                  className="bg-surface-card border border-slate-800/50 rounded-xl p-5 card-hover"
                >
                  <div className="flex items-start gap-3 mb-4">
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{
                        background: agent.color + "15",
                        border: `1px solid ${agent.color}25`,
                      }}
                    >
                      <Icon
                        className="w-5 h-5"
                        style={{ color: agent.color }}
                      />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">
                        {agent.name}
                      </h3>
                      <p className="text-[11px] text-slate-500">{agent.role}</p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed mb-4">
                    {agent.description}
                  </p>

                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-600 bg-slate-800/50 border border-slate-700/50 px-2 py-0.5 rounded">
                      {agent.model}
                    </span>
                    <span
                      className="text-[10px] font-mono px-2 py-0.5 rounded"
                      style={{
                        color: agent.color,
                        background: agent.color + "10",
                        border: `1px solid ${agent.color}20`,
                      }}
                    >
                      {agent.icon}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Data Flow */}
        <div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <Cpu className="w-3 h-3 text-emerald-400" /> Data Flow
          </div>

          <div className="bg-surface-card border border-slate-800/50 rounded-xl p-6">
            <div className="space-y-3">
              {CONNECTIONS.map(([from, to], i) => {
                const fromAgent = AGENTS.find((a) => a.id === from)!;
                const toAgent = AGENTS.find((a) => a.id === to)!;
                const FromIcon = AGENT_ICONS[from] || Cpu;
                const ToIcon = AGENT_ICONS[to] || Cpu;

                return (
                  <div key={i} className="flex items-center gap-3">
                    <div className="flex items-center gap-2 w-44 shrink-0">
                      <FromIcon
                        className="w-3.5 h-3.5"
                        style={{ color: fromAgent.color }}
                      />
                      <span className="text-xs font-medium text-slate-300">
                        {fromAgent.name}
                      </span>
                    </div>
                    <div className="flex-1 h-px bg-linear-to-r from-slate-700 via-slate-600 to-slate-700 relative">
                      <ArrowRight className="w-3 h-3 text-slate-500 absolute right-0 -translate-y-1/2 top-1/2" />
                    </div>
                    <div className="flex items-center gap-2 w-44 shrink-0">
                      <ToIcon
                        className="w-3.5 h-3.5"
                        style={{ color: toAgent.color }}
                      />
                      <span className="text-xs font-medium text-slate-300">
                        {toAgent.name}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-600 w-32 shrink-0 text-right">
                      {
                        [
                          "Requirements JSON",
                          "Test Strategy",
                          "BDD Scenarios",
                          "Playwright Code",
                          "Execution Results",
                          "Bug Reports",
                        ][i]
                      }
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
