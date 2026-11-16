type KpiCardProps = {
  label: string;
  value: number | undefined;
};

export function KpiCard({ label, value }: KpiCardProps) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">
        {value === undefined ? "–" : value.toLocaleString("en-US")}
      </div>
    </div>
  );
}
