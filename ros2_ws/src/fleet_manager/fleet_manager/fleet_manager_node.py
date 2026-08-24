"""Fleet Manager — Central coordination node for EdgeFleet."""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import String
import time
import math


class FleetManager(Node):
    """Central fleet coordinator. Subscribes to all AMR states, assigns tasks,
    detects failures, and publishes fleet-wide state."""

    def __init__(self):
        super().__init__("fleet_manager")

        # Parameters
        self.declare_parameter("robot_ids", ["amr01", "amr02", "amr03"])
        self.declare_parameter("heartbeat_timeout", 10.0)
        self.declare_parameter("battery_threshold", 20.0)

        self.robot_ids = (
            self.get_parameter("robot_ids").get_parameter_value().string_array_value
        )
        self.heartbeat_timeout = (
            self.get_parameter("heartbeat_timeout").get_parameter_value().double_value
        )
        self.battery_threshold = (
            self.get_parameter("battery_threshold").get_parameter_value().double_value
        )

        # Fleet state storage
        self.robot_states = {}
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = 0

        # Subscribers — one per robot (namespaced)
        for robot_id in self.robot_ids:
            ns = f"/{robot_id}"

            self.create_subscription(
                Pose,
                f"{ns}/odom_pose",
                lambda msg, rid=robot_id: self._odom_callback(rid, msg),
                10,
            )

            self.create_subscription(
                String,
                f"{ns}/status",
                lambda msg, rid=robot_id: self._status_callback(rid, msg),
                10,
            )

        # Publishers
        self.fleet_state_pub = self.create_publisher(String, "/fleet/state", 10)
        self.task_pub = self.create_publisher(String, "/fleet/task_assign", 10)
        self.conflict_pub = self.create_publisher(String, "/fleet/conflict", 10)

        # Heartbeat checker timer
        self.create_timer(1.0, self._check_heartbeats)

        # Fleet state publisher timer
        self.create_timer(0.5, self._publish_fleet_state)

        self.get_logger().info(
            f"Fleet Manager started. Monitoring {len(self.robot_ids)} robots: "
            f"{', '.join(self.robot_ids)}"
        )

    # --- Callbacks ---

    def _odom_callback(self, robot_id: str, msg: Pose):
        """Update robot position from odometry."""
        if robot_id not in self.robot_states:
            self.robot_states[robot_id] = {
                "x": 0.0,
                "y": 0.0,
                "battery": 100.0,
                "status": "IDLE",
                "task": None,
                "last_heartbeat": time.time(),
            }

        self.robot_states[robot_id]["x"] = msg.position.x
        self.robot_states[robot_id]["y"] = msg.position.y
        self.robot_states[robot_id]["last_heartbeat"] = time.time()

    def _status_callback(self, robot_id: str, msg: String):
        """Update robot status."""
        if robot_id not in self.robot_states:
            self.robot_states[robot_id] = {
                "x": 0.0,
                "y": 0.0,
                "battery": 100.0,
                "status": msg.data,
                "task": None,
                "last_heartbeat": time.time(),
            }
        self.robot_states[robot_id]["status"] = msg.data
        self.robot_states[robot_id]["last_heartbeat"] = time.time()

    # --- Task Allocation ---

    def assign_task(self, task_id: str, pickup: Pose, dropoff: Pose):
        """Assign a task to the nearest available robot with sufficient battery."""
        best_robot = None
        best_distance = float("inf")

        for robot_id, state in self.robot_states.items():
            if state["status"] != "IDLE":
                continue
            if state["battery"] < self.battery_threshold:
                self.get_logger().warn(
                    f"{robot_id} battery too low ({state['battery']:.0f}%), skipping"
                )
                continue

            dist = math.sqrt(
                (state["x"] - pickup.position.x) ** 2
                + (state["y"] - pickup.position.y) ** 2
            )

            if dist < best_distance:
                best_distance = dist
                best_robot = robot_id

        if best_robot is None:
            self.get_logger().warn(f"No robot available for task {task_id}")
            self.task_queue.append((task_id, pickup, dropoff))
            return

        self.robot_states[best_robot]["status"] = "BUSY"
        self.robot_states[best_robot]["task"] = task_id
        self.active_tasks[task_id] = best_robot

        self.get_logger().info(
            f"Assigned {task_id} → {best_robot} (distance: {best_distance:.1f}m)"
        )

        # Publish assignment
        msg = String()
        msg.data = f"ASSIGN:{task_id}:{best_robot}"
        self.task_pub.publish(msg)

    def recover_task(self, failed_robot: str):
        """Reassign tasks from a failed robot to the nearest available one."""
        tasks_to_reassign = [
            tid for tid, rid in self.active_tasks.items() if rid == failed_robot
        ]
        for task_id in tasks_to_reassign:
            del self.active_tasks[task_id]
            self.get_logger().warn(f"Recovering task {task_id} from {failed_robot}")
            # TODO: Store pickup/dropoff for reassignment
            # For now, log the recovery

    # --- Heartbeat / Failure Detection ---

    def _check_heartbeats(self):
        now = time.time()
        for robot_id, state in self.robot_states.items():
            elapsed = now - state["last_heartbeat"]
            if elapsed > self.heartbeat_timeout and state["status"] != "FAILED":
                state["status"] = "FAILED"
                self.get_logger().error(
                    f"⚠ ROBOT FAILURE: {robot_id} (no heartbeat for {elapsed:.0f}s)"
                )
                self.recover_task(robot_id)

    # --- Fleet State Publishing ---

    def _publish_fleet_state(self):
        state_str = "FLEET STATE:\n"
        for robot_id, state in self.robot_states.items():
            icon = {"IDLE": "🟢", "BUSY": "🟡", "CHARGING": "🔵", "FAILED": "🔴"}.get(
                state["status"], "⚪"
            )
            state_str += (
                f"  {icon} {robot_id}: {state['status']} "
                f"| battery={state['battery']:.0f}% "
                f"| pos=({state['x']:.1f}, {state['y']:.1f}) "
                f"| task={state['task']}\n"
            )
        state_str += f"  Active: {len(self.active_tasks)} | Completed: {self.completed_tasks}\n"

        msg = String()
        msg.data = state_str
        self.fleet_state_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FleetManager()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
