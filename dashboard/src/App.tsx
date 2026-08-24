import { useState, useEffect, useCallback } from "react";
import { fleetSocket } from "./services/websocket";
import type { FleetState, RobotState } from "./types";
import FleetPanel from "./components/FleetPanel";
import WarehouseMap from "./components/WarehouseMap";
import RobotDetail from "./components/RobotDetail";
import TaskList from "./components/TaskList";
import Analytics from "./components/Analytics";
import EdgeAIEvents from "./components/EdgeAIEvents";

export default function App() {
  const [fleet, setFleet] = useState<FleetState | null>(null);
  const [connected, setConnected] = useState(false);
  const [selectedRobot, setSelectedRobot] = useState<string | null>(null);

  const handleFleetState = useCallback((state: FleetState) => {
    setFleet(state);
  }, []);

  const handleStatus = useCallback((isConnected: boolean) => {
    setConnected(isConnected);
  }, []);

  useEffect(() => {
    fleetSocket.onFleetState(handleFleetState);
    fleetSocket.onStatusChange(handleStatus);
    fleetSocket.connect();

    return () => {
      fleetSocket.disconnect();
    };
  }, [handleFleetState, handleStatus]);

  const selectedRobotData: RobotState | undefined = fleet?.robots.find(
    (r) => r.robot_id === selectedRobot
  );

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="header">
        <div className="header-logo">
          🤖 <span>EDGE</span>FLEET
        </div>
        <div className="header-status">
          <span>
            <span
              className={`status-dot ${connected ? "live" : "offline"}`}
            />
            {connected ? "LIVE" : "OFFLINE"}
          </span>
          <span>
            {fleet?.robots.length ?? 0} robots
          </span>
          <span>
            {fleet?.analytics.completed_tasks ?? 0} completed
          </span>
        </div>
      </div>

      {/* Fleet panel — left sidebar */}
      <div className="fleet-panel">
        <FleetPanel
          robots={fleet?.robots ?? []}
          selectedRobot={selectedRobot}
          onSelect={setSelectedRobot}
        />
      </div>

      {/* Warehouse map — center */}
      <div className="map-area">
        <WarehouseMap
          robots={fleet?.robots ?? []}
          tasks={fleet?.tasks ?? []}
          selectedRobot={selectedRobot}
          onSelectRobot={setSelectedRobot}
        />
      </div>

      {/* Robot detail — right sidebar */}
      <div className="robot-detail">
        <RobotDetail robot={selectedRobotData ?? null} />
      </div>

      {/* Bottom panel — tasks, analytics, events */}
      <div className="bottom-panel">
        <div className="bottom-section">
          <TaskList tasks={fleet?.tasks ?? []} />
        </div>
        <div className="bottom-section">
          <Analytics data={fleet?.analytics ?? null} />
        </div>
        <div className="bottom-section">
          <EdgeAIEvents events={fleet?.events ?? []} />
        </div>
      </div>
    </div>
  );
}
