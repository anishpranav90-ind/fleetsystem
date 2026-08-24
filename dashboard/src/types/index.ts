/** EdgeFleet TypeScript types */

export interface RobotState {
  robot_id: string;
  x: number;
  y: number;
  battery: number;
  status: "IDLE" | "BUSY" | "CHARGING" | "FAILED";
  task: string | null;
  edge_ai_decision: string;
  path: number[][];
}

export interface TaskInfo {
  task_id: string;
  pickup: { x: number; y: number };
  dropoff: { x: number; y: number };
  status: "PENDING" | "ASSIGNED" | "IN_PROGRESS" | "COMPLETED" | "FAILED";
  assigned_robot: string | null;
}

export interface FleetEvent {
  time: number;
  robot: string;
  event: string;
}

export interface Analytics {
  total_tasks: number;
  completed_tasks: number;
  active_robots: number;
  failed_robots: number;
  total_robots: number;
  avg_battery: number;
  utilization: number;
  recent_events: FleetEvent[];
}

export interface FleetState {
  type: string;
  timestamp: number;
  robots: RobotState[];
  tasks: TaskInfo[];
  analytics: Analytics;
  events: FleetEvent[];
  paused: boolean;
}
