"""Fleet State — Data models and state management for the fleet."""

import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RobotState(BaseModel):
    """State of a single AMR."""

    robot_id: str
    x: float = 0.0
    y: float = 0.0
    battery: float = 100.0
    status: str = "IDLE"  # IDLE, BUSY, CHARGING, FAILED
    task: Optional[str] = None
    edge_ai_decision: str = "CONTINUE"
    path: List[List[float]] = Field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "robot_id": self.robot_id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "battery": round(self.battery, 1),
            "status": self.status,
            "task": self.task,
            "edge_ai_decision": self.edge_ai_decision,
            "path": self.path,
        }


class TaskInfo(BaseModel):
    """A warehouse task (pickup → dropoff)."""

    task_id: str
    pickup_x: float = 0.0
    pickup_y: float = 0.0
    dropoff_x: float = 0.0
    dropoff_y: float = 0.0
    status: str = "PENDING"  # PENDING, ASSIGNED, IN_PROGRESS, COMPLETED, FAILED
    assigned_robot: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "pickup": {"x": self.pickup_x, "y": self.pickup_y},
            "dropoff": {"x": self.dropoff_x, "y": self.dropoff_y},
            "status": self.status,
            "assigned_robot": self.assigned_robot,
        }


class FleetState:
    """Central fleet state manager."""

    def __init__(self):
        self.robots: Dict[str, RobotState] = {}
        self.tasks: List[TaskInfo] = []
        self.completed_tasks: int = 0
        self.events: List[dict] = []
        self.paused: bool = False

    def get_robot(self, robot_id: str) -> Optional[RobotState]:
        return self.robots.get(robot_id)

    def update_robot(self, robot_id: str, **kwargs):
        if robot_id in self.robots:
            for k, v in kwargs.items():
                setattr(self.robots[robot_id], k, v)

    def add_task(self, task: TaskInfo):
        self.tasks.append(task)

    def send_command(self, robot_id: str, command: str):
        """Send a command to a robot (e.g., STOP, GO_CHARGE)."""
        if robot_id in self.robots:
            self.events.append({
                "time": time.time(),
                "robot": robot_id,
                "event": f"COMMAND:{command}",
            })

    def get_analytics(self) -> dict:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == "COMPLETED")
        active = sum(1 for r in self.robots.values() if r.status == "BUSY")
        failed = sum(1 for r in self.robots.values() if r.status == "FAILED")
        avg_battery = (
            sum(r.battery for r in self.robots.values()) / len(self.robots)
            if self.robots
            else 0
        )

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "active_robots": active,
            "failed_robots": failed,
            "total_robots": len(self.robots),
            "avg_battery": round(avg_battery, 1),
            "utilization": (
                round(active / len(self.robots) * 100, 1) if self.robots else 0
            ),
            "recent_events": self.events[-10:],
        }

    def to_dict(self) -> dict:
        return {
            "type": "fleet_state",
            "timestamp": time.time(),
            "robots": [r.to_dict() for r in self.robots.values()],
            "tasks": [t.to_dict() for t in self.tasks],
            "analytics": self.get_analytics(),
            "events": self.events[-20:],
            "paused": self.paused,
        }
