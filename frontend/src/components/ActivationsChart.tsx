import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Granularity, Timeseries } from "../api";
import { useFetch } from "../hooks/useFetch";

const RANGES: Record<
  Granularity,
  { buckets: number; name: string; description: string }
> = {
  day: { buckets: 30, name: "Daily", description: "Last 30 days" },
  week: { buckets: 12, name: "Weekly", description: "Last 12 weeks" },
  month: { buckets: 12, name: "Monthly", description: "Last 12 months" },
  year: { buckets: 3, name: "Yearly", description: "Last 3 years" },
};

const GRANULARITIES: Granularity[] = ["day", "week", "month", "year"];

// "2026-11-16" -> a local Date. new Date("2026-11-16") would parse it as UTC midnight,
// which can show the previous day in timezones behind UTC.
function parseLocalDate(isoDate: string): Date {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function formatAxisLabel(isoDate: string, granularity: Granularity): string {
  const date = parseLocalDate(isoDate);
  if (granularity === "year") {
    return String(date.getFullYear());
  }
  if (granularity === "month") {
    return date.toLocaleDateString("en-US", {
      month: "short",
      year: "2-digit",
    });
  }
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatTooltipLabel(isoDate: string, granularity: Granularity): string {
  const label = formatAxisLabel(isoDate, granularity);
  return granularity === "week" ? `Week of ${label}` : label;
}

export function ActivationsChart() {
  const [granularity, setGranularity] = useState<Granularity>("day");
  const range = RANGES[granularity];

  const { data, error, loading } = useFetch<Timeseries>(
    `/api/stats/timeseries?granularity=${granularity}&buckets=${range.buckets}`,
  );

  const points = data?.points ?? [];
  const lastIndex = points.length - 1;
  const total = points.reduce((sum, point) => sum + point.count, 0);

  return (
    <section className="chart-card">
      <div className="chart-header">
        <div>
          <h2>Activations over time</h2>
          <p className="subtitle">
            {range.description} · {total.toLocaleString("en-US")} total · the
            lighter bar is still in progress
          </p>
        </div>

        <div className="toggle" role="group" aria-label="Chart resolution">
          {GRANULARITIES.map((option) => (
            <button
              key={option}
              type="button"
              className={option === granularity ? "active" : ""}
              onClick={() => setGranularity(option)}
            >
              {RANGES[option].name}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="error">Could not load chart: {error}</p>}

      <div className={loading ? "chart-body is-loading" : "chart-body"}>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart
            data={points}
            margin={{ top: 8, right: 8, bottom: 0, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="bucket_start"
              tickFormatter={(value: string) =>
                formatAxisLabel(value, granularity)
              }
              minTickGap={16}
            />
            <YAxis allowDecimals={false} width={40} />
            <Tooltip
              labelFormatter={(value) =>
                formatTooltipLabel(String(value), granularity)
              }
              formatter={(value) => [value, "Activations"]}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {points.map((point, index) => (
                <Cell
                  key={point.bucket_start}
                  fill={index === lastIndex ? "#93c5fd" : "#2563eb"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
