import type { RobotState } from "../types";

interface FleetPanelProps {
  robots: RobotState[];
  selectedRobot: string | null;
  onSelect: (robotId: string) => void;
}

function batteryColor(percent: number): string {
  if (percent > 60) return "var(--accent-green)";
  if (percent > 30) return "var(--accent-yellow)";
  return "var(--accent-red)";
}

export default function FleetPanel({
  robots,
  selectedRobot,
  onSelect,
}: FleetPanelProps) {
  const sorted = [...robots].sort((a, b) => {
    const order = { FAILED: 0, BUSY: 1, CHARGING: 2, IDLE: 3 };
    return (order[a.status] ?? 4) - (order[b.status] ?? 4);
  });

  return (
    <div>
      <div className="panel-title">
        Fleet ({robots.length})
      </div>
      {sorted.map((robot) => (
        <div
          key={robot.robot_id}
          className={`robot-card ${
            selectedRobot === robot.robot_id ? "selected" : ""
          }`}
          onClick={() => onSelect(robot.robot_id)}
        >
          <div className="robot-card-header">
            <div className="robot-id">
              <span
                className={`status-dot ${
                  robot.status === "FAILED" ? "offline" : "live"
                }`}
              />
              {robot.robot_id.toUpperCase()}
            </div>
            <span className={`status-badge ${robot.status}`}>
              {robot.status}
            </span>
          </div>

          <div className="battery-bar">
            <div
              className="battery-fill"
              style={{
                width: `${robot.battery}%`,
                backgroundColor: batteryColor(robot.battery),
              }}
            />
          </div>
          <div className="battery-label">
            🔋 {robot.battery.toFixed(0)}%
            {robot.task && ` · ${robot.task}`}
          </div>
        </div>
      ))}
    </div>
  );
}
