import { useState, useEffect } from "react";
import {
  Check,
  ExternalLink,
  Monitor,
  Smartphone,
  Tablet,
  Globe,
  Cpu,
  ToggleLeft,
  ToggleRight,
  ChevronDown,
  ChevronRight,
  Link2,
} from "lucide-react";
import { PageHeader } from "./ui/PageHeader";
import { Card } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import {
  FRAMEWORKS,
  ENVIRONMENT_PRESETS,
  DEFAULT_ADAPTER_CONFIG,
  getCapabilityLabel,
  type FrameworkAdapter,
  type EnvironmentPreset,
} from "../lib/adapters";
import { getAgents, type AgentDef } from "../lib/services";
import { AGENTS as MOCK_AGENTS } from "../data/mock";

export default function Settings() {
  const [AGENTS, setAgents] = useState<AgentDef[]>(MOCK_AGENTS);
  const [activeFrameworks, setActiveFrameworks] = useState<Set<string>>(
    () =>
      new Set(FRAMEWORKS.filter((f) => f.status === "active").map((f) => f.id)),
  );
  const [environments, setEnvironments] =
    useState<EnvironmentPreset[]>(ENVIRONMENT_PRESETS);
  const [expandedAdapter, setExpandedAdapter] = useState<string | null>(
    "playwright",
  );
  const [config, setConfig] = useState(DEFAULT_ADAPTER_CONFIG);

  useEffect(() => {
    getAgents().then(setAgents).catch(console.error);
  }, []);

  const toggleFramework = (id: string) => {
    setActiveFrameworks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleEnv = (id: string) => {
    setEnvironments((prev) =>
      prev.map((e) => (e.id === id ? { ...e, enabled: !e.enabled } : e)),
    );
  };

  return (
    <div className="h-full flex flex-col">
      <PageHeader
        title="Settings"
        subtitle="Configure framework adapters, environments, and AI models"
      />

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* ═══ Framework Adapters ═══ */}
        <section>
          <SectionLabel
            icon={<Cpu className="w-3.5 h-3.5 text-cyan-400" />}
            label="Framework Adapters"
          />
          <p className="text-xs text-slate-500 mb-4">
            Select which testing frameworks to use. The Automation Engineer
            agent generates code in the active framework's style.
          </p>

          <div className="grid grid-cols-2 gap-3">
            {FRAMEWORKS.map((fw) => (
              <FrameworkCard
                key={fw.id}
                framework={fw}
                active={activeFrameworks.has(fw.id)}
                expanded={expandedAdapter === fw.id}
                onToggle={() => toggleFramework(fw.id)}
                onExpand={() =>
                  setExpandedAdapter(expandedAdapter === fw.id ? null : fw.id)
                }
              />
            ))}
          </div>
        </section>

        {/* ═══ Environment Matrix ═══ */}
        <section>
          <SectionLabel
            icon={<Globe className="w-3.5 h-3.5 text-violet-400" />}
            label="Environment Matrix"
          />
          <p className="text-xs text-slate-500 mb-4">
            Configure browser and device targets for test execution. Tests run
            in parallel across enabled environments.
          </p>

          <div className="grid grid-cols-3 gap-3">
            {environments.map((env) => {
              const DeviceIcon =
                env.viewport.width >= 1024
                  ? Monitor
                  : env.viewport.width >= 768
                    ? Tablet
                    : Smartphone;
              return (
                <button
                  key={env.id}
                  onClick={() => toggleEnv(env.id)}
                  className={`flex items-center gap-3 p-4 rounded-xl border text-left transition-all ${
                    env.enabled
                      ? "bg-cyan-500/5 border-cyan-500/20"
                      : "bg-surface-card border-edge hover:border-edge-strong"
                  }`}
                >
                  <div
                    className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                      env.enabled ? "bg-cyan-500/10" : "bg-slate-800/50"
                    }`}
                  >
                    <DeviceIcon
                      className={`w-4 h-4 ${env.enabled ? "text-cyan-400" : "text-slate-500"}`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div
                      className={`text-xs font-semibold ${env.enabled ? "text-white" : "text-slate-400"}`}
                    >
                      {env.label}
                    </div>
                    <div className="text-[10px] font-mono text-slate-600 mt-0.5">
                      {env.viewport.width}×{env.viewport.height} ·{" "}
                      {env.platform}
                    </div>
                  </div>
                  {env.enabled ? (
                    <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded border border-slate-700 shrink-0" />
                  )}
                </button>
              );
            })}
          </div>
        </section>

        {/* ═══ Execution Config ═══ */}
        <section>
          <SectionLabel
            icon={<ToggleRight className="w-3.5 h-3.5 text-emerald-400" />}
            label="Execution Config"
          />

          <div className="grid grid-cols-2 gap-4">
            <Card>
              <div className="space-y-4">
                <ConfigRow
                  label="Parallel Workers"
                  value={String(config.parallelWorkers)}
                />
                <ConfigRow
                  label="Timeout (ms)"
                  value={String(config.timeout)}
                />
                <ConfigRow label="Retries" value={String(config.retries)} />
                <ConfigRow label="Base URL" value={config.baseUrl} />
                <ConfigToggle
                  label="Headless Mode"
                  enabled={config.headless}
                  onToggle={() =>
                    setConfig({ ...config, headless: !config.headless })
                  }
                />
                <ConfigToggle
                  label="Screenshots on Failure"
                  enabled={config.screenshotsOnFailure}
                  onToggle={() =>
                    setConfig({
                      ...config,
                      screenshotsOnFailure: !config.screenshotsOnFailure,
                    })
                  }
                />
                <ConfigToggle
                  label="Video on Failure"
                  enabled={config.videoOnFailure}
                  onToggle={() =>
                    setConfig({
                      ...config,
                      videoOnFailure: !config.videoOnFailure,
                    })
                  }
                />
              </div>
            </Card>

            {/* AI Models */}
            <Card>
              <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-4">
                AI Model Assignment
              </div>
              <div className="space-y-3">
                {AGENTS.map((agent) => (
                  <div key={agent.id} className="flex items-center gap-3">
                    <div
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ background: agent.color }}
                    />
                    <span className="text-xs text-slate-300 w-36 shrink-0">
                      {agent.name}
                    </span>
                    <div className="flex-1 text-[10px] font-mono text-slate-500 bg-surface-hover border border-edge rounded px-3 py-1.5">
                      {agent.model}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </section>

        {/* ═══ Connections ═══ */}
        <section>
          <SectionLabel
            icon={<Link2 className="w-3.5 h-3.5 text-amber-400" />}
            label="Connections"
          />

          <div className="grid grid-cols-3 gap-3">
            <ConnectionCard
              name="Jira"
              status="connected"
              detail="company.atlassian.net · PROJ"
            />
            <ConnectionCard
              name="GitHub Actions"
              status="available"
              detail="CI/CD pipeline triggers"
            />
            <ConnectionCard
              name="Slack"
              status="available"
              detail="Test result notifications"
            />
          </div>
        </section>
      </div>
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────

function SectionLabel({
  icon,
  label,
}: {
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
      {icon} {label}
    </div>
  );
}

function FrameworkCard({
  framework: fw,
  active,
  expanded,
  onToggle,
  onExpand,
}: {
  framework: FrameworkAdapter;
  active: boolean;
  expanded: boolean;
  onToggle: () => void;
  onExpand: () => void;
}) {
  return (
    <div
      className={`rounded-xl border overflow-hidden transition-all ${
        active
          ? "border-emerald-500/20 bg-surface-card"
          : "border-edge bg-surface-card/50 opacity-70"
      }`}
    >
      <div className="flex items-center gap-3 px-4 py-3.5">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-black"
          style={{
            background: fw.color + "15",
            color: fw.color,
            border: `1px solid ${fw.color}30`,
          }}
        >
          {fw.shortName}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-white">{fw.name}</div>
          <div className="text-[10px] text-slate-500 font-mono">
            {fw.language}
          </div>
        </div>
        <Badge variant="status">
          {fw.status === "coming-soon"
            ? "coming-soon"
            : active
              ? "active"
              : "available"}
        </Badge>
        <button
          onClick={onToggle}
          className="p-1"
          title={active ? "Deactivate" : "Activate"}
        >
          {active ? (
            <ToggleRight className="w-5 h-5 text-emerald-400" />
          ) : (
            <ToggleLeft className="w-5 h-5 text-slate-600" />
          )}
        </button>
        <button onClick={onExpand} className="p-1">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-slate-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-500" />
          )}
        </button>
      </div>

      {expanded && (
        <div className="px-4 pb-4 border-t border-edge animate-slide-up">
          <p className="text-xs text-slate-400 leading-relaxed my-3">
            {fw.description}
          </p>

          <div className="flex flex-wrap gap-1.5 mb-3">
            {fw.capabilities.map((cap) => (
              <span
                key={cap}
                className="text-[9px] font-mono text-slate-500 bg-slate-800/60 border border-slate-700/40 px-2 py-0.5 rounded"
              >
                {getCapabilityLabel(cap)}
              </span>
            ))}
          </div>

          {fw.browserSupport.length > 0 && (
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[10px] text-slate-600">Browsers:</span>
              {fw.browserSupport.map((b) => (
                <span
                  key={b}
                  className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.5 rounded"
                >
                  {b}
                </span>
              ))}
            </div>
          )}

          <div className="bg-surface-deep border border-edge rounded-lg overflow-hidden">
            <div className="px-3 py-1.5 border-b border-edge flex items-center gap-2">
              <span className="text-[10px] font-mono text-slate-500">
                Sample generated code · {fw.language}
              </span>
            </div>
            <pre className="p-3 text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed overflow-x-auto">
              {fw.sampleCode}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs font-mono text-slate-300 bg-surface-hover border border-edge rounded px-2.5 py-1">
        {value}
      </span>
    </div>
  );
}

function ConfigToggle({
  label,
  enabled,
  onToggle,
}: {
  label: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-400">{label}</span>
      <button onClick={onToggle} className="p-0.5">
        {enabled ? (
          <ToggleRight className="w-5 h-5 text-cyan-400" />
        ) : (
          <ToggleLeft className="w-5 h-5 text-slate-600" />
        )}
      </button>
    </div>
  );
}

function ConnectionCard({
  name,
  status,
  detail,
}: {
  name: string;
  status: "connected" | "available";
  detail: string;
}) {
  return (
    <div
      className={`flex items-center gap-3 p-4 rounded-xl border transition-colors ${
        status === "connected"
          ? "bg-emerald-500/5 border-emerald-500/20"
          : "bg-surface-card border-edge hover:border-edge-strong card-hover"
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className="text-xs font-semibold text-white">{name}</div>
        <div className="text-[10px] text-slate-500 mt-0.5">{detail}</div>
      </div>
      {status === "connected" ? (
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-emerald-400">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Live
        </div>
      ) : (
        <Button variant="ghost" size="sm">
          <ExternalLink className="w-3 h-3" /> Connect
        </Button>
      )}
    </div>
  );
}
