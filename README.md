# 🤖 EdgeFleet

**Multi-Robot Fleet Management System for Warehouse AMRs**

EdgeFleet is an autonomous multi-robot fleet management platform built for warehouse environments. It coordinates multiple Autonomous Mobile Robots (AMRs) using ROS 2 + Gazebo simulation, with a centralized Fleet Manager, A* path planning, collision avoidance, battery management, failure recovery, and edge-AI local decision-making — all visualized through a real-time React dashboard.

## Architecture

```
┌──────────────────────┐
│   Fleet Dashboard    │  React / Web UI
└──────────┬───────────┘
           │ WebSocket
           ▼
┌──────────────────────┐
│   Fleet Manager      │  Python / FastAPI
└──────────┬───────────┘
           │
  ┌────────┼────────┐
  ▼        ▼        ▼
Task    Global    Fleet
Alloc   Planner   State
  │        │
  └────┬───┘
       ▼
┌───────────────────┐
│   AMR Instances   │
└───────────────────┘
  │       │       │
AMR01   AMR02   AMR03
  │       │       │
Edge    Edge    Edge
  AI      AI      AI
  │       │       │
  └───────┼───────┘
          ▼
      Gazebo
```

## Project Structure

```
EdgeFleet/
├── ros2_ws/                    # ROS 2 workspace
│   └── src/
│       ├── fleet_manager/      # Central fleet coordination
│       ├── task_allocator/     # Task assignment (nearest robot + battery check)
│       ├── path_planner/       # A* global path planning
│       ├── collision_manager/  # Multi-robot collision avoidance
│       ├── battery_manager/    # Battery simulation & charging
│       └── edge_ai/            # Local edge-AI decision engine
│
├── simulation/                 # Gazebo simulation assets
│   ├── worlds/                 # Warehouse SDF world
│   ├── models/                 # AMR robot model
│   ├── launch/                 # Single & multi-AMR launch files
│   └── config/                 # Nav2 parameters
│
├── backend/                    # FastAPI WebSocket bridge
│   ├── main.py
│   ├── websocket.py
│   └── fleet_state.py
│
└── dashboard/                  # React + TypeScript frontend
    └── src/
        ├── components/
        ├── services/
        └── types/
```

## Build Order

| Stage | Component | Status |
|-------|-----------|--------|
| 1 | ROS 2 + Gazebo (single AMR) | 🔲 |
| 2 | One AMR navigates warehouse | 🔲 |
| 3 | 5 AMRs navigate simultaneously | 🔲 |
| 4 | Task allocation | 🔲 |
| 5 | A* global path planning | 🔲 |
| 6 | Collision avoidance | 🔲 |
| 7 | Battery simulation | 🔲 |
| 8 | Failure detection + task reassignment | 🔲 |
| 9 | Edge-AI local decisions | 🔲 |
| 10 | FastAPI + WebSocket | 🔲 |
| 11 | React dashboard | 🔲 |
| 12 | Optional ML model | 🔲 |

## Quick Start

### Prerequisites

- **ROS 2 Humble** (or later)
- **Gazebo** (Ignition or Fortress)
- **Nav2** stack
- **Python 3.10+**
- **Node.js 18+**
- **pnpm** (or npm/yarn)

### 1. Build ROS 2 Workspace

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

### 2. Launch Simulation

```bash
# Single AMR
ros2 launch simulation single_amr.launch.py

# Multi-AMR fleet
ros2 launch simulation multi_amr.launch.py
```

### 3. Start Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 4. Start Dashboard

```bash
cd dashboard
pnpm install
pnpm dev
```

## ROS 2 Namespaces

Each robot is namespaced to avoid topic conflicts:

```
/amr01/odom, /amr01/scan, /amr01/cmd_vel
/amr02/odom, /amr02/scan, /amr02/cmd_vel
/amr03/odom, /amr03/scan, /amr03/cmd_vel
/amr04/odom, /amr04/scan, /amr04/cmd_vel
/amr05/odom, /amr05/scan, /amr05/cmd_vel
```

## License

MIT
