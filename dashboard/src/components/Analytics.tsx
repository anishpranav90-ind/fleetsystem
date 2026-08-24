import type { Analytics as AnalyticsType } from "../types";

interface AnalyticsProps {
  data: AnalyticsType | null;
}

export default function Analytics({ data }: AnalyticsProps) {
  if (!data) {
    return (
      <div>
        <div className="panel-title">Analytics</div>
        <p style={{ color: "var(--text-muted)", fontSize: 12 }}>
          Waiting for data...
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="panel-title">Analytics</div>
      <div className="analytics-grid">
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-green)" }}>
            {data.completed_tasks}
          </div>
          <div className="analytics-label">Completed</div>
        </div>
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-yellow)" }}>
            {data.total_tasks - data.completed_tasks}
          </div>
          <div className="analytics-label">Pending</div>
        </div>
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-blue)" }}>
            {data.utilization.toFixed(0)}%
          </div>
          <div className="analytics-label">Utilization</div>
        </div>
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-cyan)" }}>
            {data.avg_battery.toFixed(0)}%
          </div>
          <div className="analytics-label">Avg Battery</div>
        </div>
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-green)" }}>
            {data.active_robots}
          </div>
          <div className="analytics-label">Active</div>
        </div>
        <div className="analytics-item">
          <div className="analytics-value" style={{ color: "var(--accent-red)" }}>
            {data.failed_robots}
          </div>
          <div className="analytics-label">Failed</div>
        </div>
      </div>
    </div>
  );
}
