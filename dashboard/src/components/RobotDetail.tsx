import type { RobotState } from "../types";

interface RobotDetailProps {
  robot: RobotState | null;
}

function batteryColor(percent: number): string {
  if (percent > 60) return "var(--accent-green)";
  if (percent > 30) return "var(--accent-yellow)";
  return "var(--accent-red)";
}

const DECISION_ICONS: Record<string, string> = {
  STOP: "🛑",
  SLOW: "⚠️",
  REROUTE: "🔄",
  GO_CHARGE: "🔋",
  CONTINUE: "✅",
};

export default function RobotDetail({ robot }: RobotDetailProps) {
  if (!robot) {
    return (
      <div>
        <div className="panel-title">Robot Detail</div>
        <div className="detail-section">
          <p style={{ color: "var(--text-muted)", fontSize: 13 }}>
            Select a robot from the fleet panel or warehouse map.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="panel-title">Robot Detail</div>

      {/* Robot header */}
      <div className="detail-section">
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            className={`status-dot ${
              robot.status === "FAILED" ? "offline" : "live"
            }`}
            style={{ width: 10, height: 10 }}
          />
          <span style={{ fontWeight: 700, fontSize: 16 }}>
            {robot.robot_id.toUpperCase()}
          </span>
          <span className={`status-badge ${robot.status}`} style={{ marginLeft: "auto" }}>
            {robot.status}
          </span>
        </div>
      </div>

      {/* Battery */}
      <div className="detail-section">
        <div className="detail-row">
          <span className="detail-label">Battery</span>
          <span
            className="detail-value"
            style={{ color: batteryColor(robot.battery) }}
          >
            {robot.battery.toFixed(1)}%
          </span>
        </div>
        <div className="battery-bar" style={{ marginTop: 6, height: 6 }}>
          <div
            className="battery-fill"
            style={{
              width: `${robot.battery}%`,
              backgroundColor: batteryColor(robot.battery),
            }}
          />
        </div>
      </div>

      {/* Position */}
      <div className="detail-section">
        <div className="detail-row">
          <span className="detail-label">Position X</span>
          <span className="detail-value">{robot.x.toFixed(2)}m</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Position Y</span>
          <span className="detail-value">{robot.y.toFixed(2)}m</span>
        </div>
      </div>

      {/* Task */}
      <div className="detail-section">
        <div className="detail-row">
          <span className="detail-label">Current Task</span>
          <span className="detail-value">
            {robot.task ?? "—"}
          </span>
        </div>
      </div>

      {/* Edge AI */}
      <div className="detail-section">
        <div className="detail-row">
          <span className="detail-label">Edge AI</span>
          <span className="detail-value">
            {DECISION_ICONS[robot.edge_ai_decision] ?? "❓"}{" "}
            {robot.edge_ai_decision}
          </span>
        </div>
      </div>

      {/* Commands */}
      {robot.status !== "FAILED" && (
        <div className="detail-section">
          <div className="panel-title" style={{ marginBottom: 6 }}>
            Commands
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {["STOP", "GO_CHARGE"].map((cmd) => (
              <button
                key={cmd}
                onClick={() => {
                  // TODO: Send via WebSocket
                  console.log(`Command: ${cmd} → ${robot.robot_id}`);
                }}
                style={{
                  padding: "4px 10px",
                  borderRadius: 4,
                  border: "1px solid var(--border)",
                  background: "var(--bg-card)",
                  color: "var(--text-primary)",
                  cursor: "pointer",
                  fontSize: 11,
                  fontWeight: 600,
                }}
              >
                {cmd}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
