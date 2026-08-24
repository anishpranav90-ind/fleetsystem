"""EdgeFleet Backend — FastAPI + WebSocket bridge.

Architecture:
    ROS 2 → Fleet Manager → FastAPI → WebSocket → React Dashboard

This server:
1. Subscribes to ROS 2 fleet state topics (via bridge or direct)
2. Aggregates robot states into a unified fleet state
3. Serves it over WebSocket to the React dashboard
4. Provides REST endpoints for task submission
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fleet_state import FleetState, RobotState, TaskInfo


# --- Global fleet state ---

fleet_state = FleetState()

# Connected WebSocket clients
connected_clients: Set[WebSocket] = set()


# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background tasks on startup."""
    task = asyncio.create_task(fleet_state_simulator())
    yield
    task.cancel()


app = FastAPI(
    title="EdgeFleet API",
    description="Fleet management backend for EdgeFleet warehouse AMR system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REST Endpoints ---


@app.get("/")
async def root():
    return {
        "service": "EdgeFleet Backend",
        "version": "0.1.0",
        "status": "running",
        "robots": len(fleet_state.robots),
    }


@app.get("/api/fleet")
async def get_fleet_state():
    """Get complete fleet state."""
    return fleet_state.to_dict()


@app.get("/api/fleet/{robot_id}")
async def get_robot_state(robot_id: str):
    """Get state of a specific robot."""
    robot = fleet_state.get_robot(robot_id)
    if robot is None:
        return {"error": f"Robot {robot_id} not found"}
    return robot.to_dict()


@app.post("/api/tasks")
async def create_task(task: TaskInfo):
    """Submit a new task to the fleet."""
    fleet_state.add_task(task)
    await broadcast_state()
    return {"status": "accepted", "task_id": task.task_id}


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    return [t.to_dict() for t in fleet_state.tasks]


@app.get("/api/analytics")
async def get_analytics():
    """Get fleet analytics."""
    return fleet_state.get_analytics()


# --- WebSocket ---


@app.websocket("/ws/fleet")
async def websocket_fleet(websocket: WebSocket):
    """WebSocket endpoint for real-time fleet updates."""
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        # Send initial state
        await websocket.send_json(fleet_state.to_dict())

        # Keep connection alive, handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=30.0
                )
                message = json.loads(data)
                await handle_ws_message(message, websocket)
            except asyncio.TimeoutError:
                # Send heartbeat/ping
                await websocket.send_json({"type": "ping"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception:
        connected_clients.discard(websocket)


async def handle_ws_message(message: dict, websocket: WebSocket):
    """Handle incoming WebSocket messages from dashboard."""
    msg_type = message.get("type")

    if msg_type == "command":
        # Dashboard sends commands to robots
        robot_id = message.get("robot_id")
        command = message.get("command")
        fleet_state.send_command(robot_id, command)
        await broadcast_state()

    elif msg_type == "task_request":
        # Dashboard submits a task
        task = TaskInfo(**message.get("task", {}))
        fleet_state.add_task(task)
        await broadcast_state()

    elif msg_type == "pause_simulation":
        fleet_state.paused = True

    elif msg_type == "resume_simulation":
        fleet_state.paused = False


async def broadcast_state():
    """Send current fleet state to all connected clients."""
    state_json = fleet_state.to_dict()
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send_json(state_json)
        except Exception:
            disconnected.add(client)

    connected_clients.difference_update(disconnected)


# --- Simulation (for demo without ROS 2) ---


async def fleet_state_simulator():
    """Simulate fleet state for dashboard development without ROS 2."""
    import random

    robot_ids = ["amr01", "amr02", "amr03", "amr04", "amr05"]

    # Initialize robots
    for i, rid in enumerate(robot_ids):
        fleet_state.robots[rid] = RobotState(
            robot_id=rid,
            x=-10.0 + (i * 5.0),
            y=random.uniform(-5.0, 5.0),
            battery=100.0 - random.uniform(0, 40),
            status="IDLE",
            task=None,
            edge_ai_decision="CONTINUE",
        )

    # Initialize some tasks
    tasks = [
        TaskInfo(task_id="TASK-001", pickup_x=-6.0, pickup_y=3.0, dropoff_x=10.0, dropoff_y=5.0),
        TaskInfo(task_id="TASK-002", pickup_x=0.0, pickup_y=-3.0, dropoff_x=10.0, dropoff_y=0.0),
        TaskInfo(task_id="TASK-003", pickup_x=-6.0, pickup_y=-3.0, dropoff_x=10.0, dropoff_y=-5.0),
    ]
    for t in tasks:
        fleet_state.tasks.append(t)

    frame = 0
    while True:
        if not fleet_state.paused:
            frame += 1

            for rid, robot in fleet_state.robots.items():
                if robot.status == "IDLE":
                    # Wander slightly
                    robot.x += random.uniform(-0.1, 0.1)
                    robot.y += random.uniform(-0.1, 0.1)
                    robot.battery = max(0, robot.battery - 0.05)

                elif robot.status == "BUSY":
                    # Move toward task
                    if robot.task:
                        task = next(
                            (t for t in fleet_state.tasks if t.task_id == robot.task),
                            None,
                        )
                        if task:
                            dx = task.dropoff_x - robot.x
                            dy = task.dropoff_y - robot.y
                            dist = (dx**2 + dy**2) ** 0.5
                            if dist > 0.3:
                                speed = 0.3
                                robot.x += (dx / dist) * speed
                                robot.y += (dy / dist) * speed
                                robot.battery = max(0, robot.battery - 0.15)
                            else:
                                robot.status = "IDLE"
                                robot.task = None
                                task.status = "COMPLETED"
                                fleet_state.completed_tasks += 1

                elif robot.status == "CHARGING":
                    robot.battery = min(100, robot.battery + 0.5)
                    if robot.battery >= 95:
                        robot.status = "IDLE"

                # Randomly assign tasks
                if robot.status == "IDLE" and random.random() < 0.01:
                    available = [t for t in fleet_state.tasks if t.status == "PENDING"]
                    if available:
                        task = available[0]
                        task.status = "ASSIGNED"
                        robot.status = "BUSY"
                        robot.task = task.task_id
                        robot.edge_ai_decision = "CONTINUE"

                # Randomly trigger edge AI events
                if random.random() < 0.005:
                    robot.edge_ai_decision = random.choice(
                        ["STOP", "SLOW", "REROUTE", "CONTINUE", "GO_CHARGE"]
                    )
                    fleet_state.events.append({
                        "time": time.time(),
                        "robot": rid,
                        "event": robot.edge_ai_decision,
                    })

                # Randomly generate new tasks
                if random.random() < 0.002:
                    new_task = TaskInfo(
                        task_id=f"TASK-{len(fleet_state.tasks)+1:03d}",
                        pickup_x=random.uniform(-8, 5),
                        pickup_y=random.uniform(-5, 5),
                        dropoff_x=random.uniform(8, 12),
                        dropoff_y=random.uniform(-5, 5),
                    )
                    fleet_state.tasks.append(new_task)

            # Keep last 50 events
            fleet_state.events = fleet_state.events[-50:]

            await broadcast_state()

        await asyncio.sleep(0.5)


# --- Entry point ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
