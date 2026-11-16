import type { Summary } from "./api";
import { ActivationsChart } from "./components/ActivationsChart";
import { KpiCard } from "./components/KpiCard";
import { useFetch } from "./hooks/useFetch";
import "./App.css";

function App() {
  const summary = useFetch<Summary>("/api/stats/summary");

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <h1>Device Activations</h1>
        <p className="subtitle">Calendar periods · Israel time</p>
      </header>

      {summary.error && (
        <p className="error">Could not load summary: {summary.error}</p>
      )}

      <section className="kpi-grid">
        <KpiCard label="Today" value={summary.data?.today} />
        <KpiCard label="This week" value={summary.data?.week} />
        <KpiCard label="This month" value={summary.data?.month} />
        <KpiCard label="This year" value={summary.data?.year} />
      </section>

      <ActivationsChart />
    </main>
  );
}

export default App;
