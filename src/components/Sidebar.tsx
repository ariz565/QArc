import {
  LayoutDashboard,
  Workflow,
  TestTubes,
  BarChart3,
  Network,
  Hexagon,
  Clock,
  Settings,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { NAV } from "../lib/colors";
import { APP } from "../lib/config";

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "pipeline", label: "Pipeline", icon: Workflow },
  { id: "testcases", label: "Test Cases", icon: TestTubes },
  { id: "agents", label: "Agents", icon: Network },
  { id: "reports", label: "Reports", icon: BarChart3 },
  { id: "history", label: "History", icon: Clock },
  { id: "settings", label: "Settings", icon: Settings },
];

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <aside className="w-56 border-r border-edge-strong bg-surface-deep flex flex-col h-screen shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 flex items-center gap-3 border-b border-edge-strong">
        <div className="w-8 h-8 rounded-lg bg-linear-to-br from-cyan-400 to-violet-500 flex items-center justify-center">
          <Hexagon className="w-4 h-4 text-white" strokeWidth={2.5} />
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-white">
            {APP.name.toUpperCase()}
          </div>
          <div className="text-[10px] font-mono text-slate-500 tracking-wider">
            {APP.tagline}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = activePage === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                active
                  ? `${NAV.active.bg} ${NAV.active.text} border ${NAV.active.border}`
                  : `nav-item-inactive ${NAV.inactive.text} hover:${NAV.inactive.hoverText} hover:${NAV.inactive.hoverBg} border border-transparent`
              }`}
            >
              <Icon className="w-4 h-4" strokeWidth={active ? 2.5 : 2} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer: theme toggle + status */}
      <div className="px-4 py-4 border-t border-edge-strong space-y-3">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium nav-item-inactive ${NAV.inactive.text} hover:${NAV.themeToggle.hoverText} hover:${NAV.themeToggle.hoverBg} transition-all border border-transparent`}
        >
          {isDark ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-violet-400" />
          )}
          {isDark ? "Light Mode" : "Dark Mode"}
        </button>

        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px] shadow-emerald-400/50 animate-pulse" />
          <span className="text-xs text-slate-400 font-mono">
            {APP.agentCount} agents online
          </span>
        </div>
        <div className="text-[10px] text-slate-600 font-mono">
          v{APP.version} · Multi-Agent Engine
        </div>
      </div>
    </aside>
  );
}
