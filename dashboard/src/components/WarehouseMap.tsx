import { useRef, useEffect } from "react";
import type { RobotState, TaskInfo } from "../types";

interface WarehouseMapProps {
  robots: RobotState[];
  tasks: TaskInfo[];
  selectedRobot: string | null;
  onSelectRobot: (robotId: string) => void;
}

// Warehouse bounds (matching Gazebo world: 30m x 20m)
const WORLD = { x: -15, y: -10, w: 30, h: 20 };
const PADDING = 30;

// Warehouse obstacles (shelves, packing stations, walls)
const OBSTACLES = [
  // Shelves
  { x: -6, y: 3, w: 2, h: 0.8, color: "#4a3520", label: "Shelf A" },
  { x: -6, y: -3, w: 2, h: 0.8, color: "#4a3520", label: "Shelf A" },
  { x: 0, y: 3, w: 2, h: 0.8, color: "#4a3520", label: "Shelf B" },
  { x: 0, y: -3, w: 2, h: 0.8, color: "#4a3520", label: "Shelf B" },
  // Packing stations
  { x: 10, y: 5, w: 1.5, h: 1.5, color: "#1a5a1a", label: "Pack 1" },
  { x: 10, y: 0, w: 1.5, h: 1.5, color: "#1a5a1a", label: "Pack 2" },
  { x: 10, y: -5, w: 1.5, h: 1.5, color: "#1a5a1a", label: "Pack 3" },
  // Charging station
  { x: -12, y: 7, w: 1, h: 0.6, color: "#1a2a6a", label: "Charge" },
  // Walls
  { x: 0, y: 10, w: 30, h: 0.2, color: "#333" },
  { x: 0, y: -10, w: 30, h: 0.2, color: "#333" },
];

function worldToSvg(
  wx: number,
  wy: number,
  svgW: number,
  svgH: number
): { x: number; y: number } {
  const scaleX = (svgW - PADDING * 2) / WORLD.w;
  const scaleY = (svgH - PADDING * 2) / WORLD.h;
  const scale = Math.min(scaleX, scaleY);
  const offsetX = (svgW - WORLD.w * scale) / 2;
  const offsetY = (svgH - WORLD.h * scale) / 2;
  return {
    x: (wx - WORLD.x) * scale + offsetX,
    y: (wy - WORLD.y) * scale + offsetY,
  };
}

const STATUS_COLORS: Record<string, string> = {
  IDLE: "#22c55e",
  BUSY: "#eab308",
  CHARGING: "#3b82f6",
  FAILED: "#ef4444",
};

export default function WarehouseMap({
  robots,
  tasks,
  selectedRobot,
  onSelectRobot,
}: WarehouseMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    // Resize handler
    const resize = () => svg.classList.add("resized");
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  return (
    <svg
      ref={svgRef}
      className="warehouse-canvas"
      viewBox="0 0 1200 700"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Grid lines */}
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path
            d="M 40 0 L 0 0 0 40"
            fill="none"
            stroke="#1a2236"
            strokeWidth="1"
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="var(--bg-primary)" />
      <rect width="100%" height="100%" fill="url(#grid)" />

      {/* Warehouse label */}
      <text
        x="600"
        y="30"
        textAnchor="middle"
        fill="var(--text-muted)"
        fontSize="14"
        fontWeight="600"
        letterSpacing="0.1em"
      >
        WAREHOUSE
      </text>

      {/* Obstacles */}
      {OBSTACLES.map((obs, i) => {
        const p1 = worldToSvg(obs.x - obs.w / 2, obs.y - obs.h / 2, 1200, 700);
        const p2 = worldToSvg(
          obs.x - obs.w / 2 + obs.w,
          obs.y - obs.h / 2 + obs.h,
          1200,
          700
        );
        return (
          <g key={i}>
            <rect
              x={p1.x}
              y={p1.y}
              width={p2.x - p1.x}
              height={p2.y - p1.y}
              fill={obs.color}
              stroke="#333"
              strokeWidth="1"
              rx="3"
            />
            <text
              x={(p1.x + p2.x) / 2}
              y={(p1.y + p2.y) / 2 + 4}
              textAnchor="middle"
              fill="rgba(255,255,255,0.5)"
              fontSize="9"
            >
              {obs.label}
            </text>
          </g>
        );
      })}

      {/* Robots */}
      {robots.map((robot) => {
        const pos = worldToSvg(robot.x, robot.y, 1200, 700);
        const color = STATUS_COLORS[robot.status] || "#888";
        const isSelected = robot.robot_id === selectedRobot;
        const r = isSelected ? 14 : 10;

        return (
          <g
            key={robot.robot_id}
            style={{ cursor: "pointer" }}
            onClick={() => onSelectRobot(robot.robot_id)}
          >
            {/* Selection ring */}
            {isSelected && (
              <circle
                cx={pos.x}
                cy={pos.y}
                r={r + 6}
                fill="none"
                stroke={color}
                strokeWidth="2"
                opacity="0.4"
              />
            )}

            {/* Battery ring */}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={r + 2}
              fill="none"
              stroke={color}
              strokeWidth="1"
              strokeDasharray={`${(robot.battery / 100) * (2 * Math.PI * (r + 2))} ${2 * Math.PI * (r + 2)}`}
              opacity="0.3"
            />

            {/* Robot body */}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={r}
              fill={color}
              stroke={isSelected ? "#fff" : "#333"}
              strokeWidth={isSelected ? 2 : 1}
            />

            {/* Robot label */}
            <text
              x={pos.x}
              y={pos.y + r + 14}
              textAnchor="middle"
              fill="var(--text-primary)"
              fontSize="10"
              fontWeight="600"
            >
              {robot.robot_id.toUpperCase()}
            </text>

            {/* Battery text */}
            <text
              x={pos.x}
              y={pos.y + 4}
              textAnchor="middle"
              fill="#000"
              fontSize="9"
              fontWeight="700"
            >
              {robot.battery.toFixed(0)}
            </text>

            {/* Edge AI indicator */}
            {robot.edge_ai_decision !== "CONTINUE" && (
              <text
                x={pos.x}
                y={pos.y - r - 6}
                textAnchor="middle"
                fill={
                  robot.edge_ai_decision === "STOP"
                    ? "var(--accent-red)"
                    : "var(--accent-yellow)"
                }
                fontSize="10"
                fontWeight="700"
              >
                ⚠ {robot.edge_ai_decision}
              </text>
            )}
          </g>
        );
      })}

      {/* Task indicators */}
      {tasks
        .filter((t) => t.status !== "COMPLETED")
        .map((task) => {
          const pickup = worldToSvg(task.pickup.x, task.pickup.y, 1200, 700);
          const dropoff = worldToSvg(task.dropoff.x, task.dropoff.y, 1200, 700);

          return (
            <g key={task.task_id}>
              {/* Pickup marker */}
              <rect
                x={pickup.x - 5}
                y={pickup.y - 5}
                width="10"
                height="10"
                fill="var(--accent-purple)"
                opacity="0.7"
                transform={`rotate(45 ${pickup.x} ${pickup.y})`}
              />
              <text
                x={pickup.x}
                y={pickup.y - 10}
                textAnchor="middle"
                fill="var(--accent-purple)"
                fontSize="8"
              >
                📦
              </text>

              {/* Dropoff marker */}
              <rect
                x={dropoff.x - 5}
                y={dropoff.y - 5}
                width="10"
                height="10"
                fill="var(--accent-cyan)"
                opacity="0.7"
                transform={`rotate(45 ${dropoff.x} ${dropoff.y})`}
              />
              <text
                x={dropoff.x}
                y={dropoff.y - 10}
                textAnchor="middle"
                fill="var(--accent-cyan)"
                fontSize="8"
              >
                📍
              </text>
            </g>
          );
        })}
    </svg>
  );
}
