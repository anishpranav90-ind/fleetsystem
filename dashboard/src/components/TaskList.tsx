import type { TaskInfo } from "../types";

interface TaskListProps {
  tasks: TaskInfo[];
}

const STATUS_LABELS: Record<string, string> = {
  PENDING: "⏳ PENDING",
  ASSIGNED: "🔧 ASSIGNED",
  IN_PROGRESS: "🏃 IN PROGRESS",
  COMPLETED: "✅ DONE",
  FAILED: "❌ FAILED",
};

export default function TaskList({ tasks }: TaskListProps) {
  const sorted = [...tasks].sort((a, b) => {
    const order = { FAILED: 0, PENDING: 1, ASSIGNED: 2, IN_PROGRESS: 3, COMPLETED: 4 };
    return (order[a.status] ?? 5) - (order[b.status] ?? 5);
  });

  const visible = sorted.slice(0, 15);

  return (
    <div>
      <div className="panel-title">
        Tasks ({tasks.length})
      </div>
      {visible.length === 0 && (
        <p style={{ color: "var(--text-muted)", fontSize: 12 }}>
          No tasks yet.
        </p>
      )}
      {visible.map((task) => (
        <div key={task.task_id} className="task-row">
          <span className="task-id">{task.task_id}</span>
          {task.assigned_robot && (
            <span style={{ color: "var(--accent-cyan)", fontSize: 11 }}>
              → {task.assigned_robot.toUpperCase()}
            </span>
          )}
          <span className={`task-status ${task.status}`}>
            {STATUS_LABELS[task.status] ?? task.status}
          </span>
        </div>
      ))}
    </div>
  );
}
