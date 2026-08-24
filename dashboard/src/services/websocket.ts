/**
 * WebSocket service — connects to FastAPI backend for real-time fleet updates.
 *
 * Auto-reconnects on disconnect. Provides typed callbacks for fleet state changes.
 */

import type { FleetState } from "../types";

type FleetCallback = (state: FleetState) => void;
type StatusCallback = (connected: boolean) => void;

class FleetWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private fleetCallback: FleetCallback | null = null;
  private statusCallback: StatusCallback | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private _connected = false;

  constructor(url: string = "ws://localhost:8000/ws/fleet") {
    this.url = url;
  }

  get connected(): boolean {
    return this._connected;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this._connected = true;
        this.statusCallback?.(true);
        console.log("🔌 EdgeFleet WebSocket connected");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "fleet_state") {
            this.fleetCallback?.(data as FleetState);
          }
        } catch (e) {
          console.warn("Invalid WS message:", e);
        }
      };

      this.ws.onclose = () => {
        this._connected = false;
        this.statusCallback?.(false);
        console.log("🔌 WebSocket disconnected, reconnecting in 2s...");
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this._connected = false;
        this.ws?.close();
      };
    } catch {
      this.scheduleReconnect();
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
    this.ws = null;
  }

  send(data: Record<string, unknown>) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  onFleetState(callback: FleetCallback) {
    this.fleetCallback = callback;
  }

  onStatusChange(callback: StatusCallback) {
    this.statusCallback = callback;
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 2000);
  }
}

export const fleetSocket = new FleetWebSocket();
