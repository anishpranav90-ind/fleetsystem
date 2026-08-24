import type { FleetEvent } from "../types";

interface EdgeAIEventsProps {
  events: FleetEvent[];
}

const EVENT_ICONS: Record<string, string> = {
  STOP: "🛑",
  SLOW: "⚠️",
  REROUTE: "🔄",
  GO_CHARGE: "🔋",
  CONTINUE: "✅",
  COMMAND: "📨",
};

function formatTime(timestamp: number): string {
  const d = new Date(timestamp * 1000);
  return d.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function EdgeAIEvents({ events }: EdgeAIEventsProps) {
  const recent = events.slice(-15).reverse();

  return (
    <div>
      <div className="panel-title">
        Edge AI Events ({events.length})
      </div>
      {recent.length === 0 && (
        <p style={{ color: "var(--text-muted)", fontSize: 12 }}>
          No events yet.
        </p>
      )}
      {recent.map((event, i) => {
        const icon = EVENT_ICONS[event.event.split(":")[0]] ?? "❓";
        return (
          <div key={i} className="event-row">
            <span className="event-icon">{icon}</span>
            <span className="event-robot">
              {event.robot.toUpperCase()}
            </span>
            <span className="event-action">{event.event}</span>
            <span
              style={{
                marginLeft: "auto",
                color: "var(--text-muted)",
                fontSize: 10,
              }}
            >
              {formatTime(event.time)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
