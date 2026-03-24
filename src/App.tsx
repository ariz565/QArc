import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import Pipeline from "./components/Pipeline";
import TestCases from "./components/TestCases";
import AgentNetwork from "./components/AgentNetwork";
import Reports from "./components/Reports";
import Settings from "./components/Settings";
import ExecutionHistory from "./components/ExecutionHistory";

export default function App() {
  const [activePage, setActivePage] = useState("pipeline");

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return <Dashboard />;
      case "pipeline":
        return <Pipeline />;
      case "testcases":
        return <TestCases />;
      case "agents":
        return <AgentNetwork />;
      case "reports":
        return <Reports />;
      case "history":
        return <ExecutionHistory />;
      case "settings":
        return <Settings />;
      default:
        return <Pipeline />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-surface-deep">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="flex-1 overflow-y-auto">{renderPage()}</main>
    </div>
  );
}
