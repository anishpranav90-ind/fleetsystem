"""Task Allocator — Assigns warehouse tasks to the optimal AMR.

Algorithm:
1. Receive task (pickup → dropoff)
2. For each IDLE robot with sufficient battery:
   a. Calculate Euclidean distance to pickup
   b. Select nearest robot
3. Publish assignment to fleet
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseStamped
from std_msgs.msg import String
import math
import time


class TaskAllocator(Node):
    def __init__(self):
        super().__init__("task_allocator")

        self.declare_parameter("battery_threshold", 20.0)
        self.battery_threshold = (
            self.get_parameter("battery_threshold").get_parameter_value().double_value
        )

        # Known robot positions (updated via fleet state)
        self.robot_states = {}

        # Subscribe to fleet state updates
        self.create_subscription(
            String, "/fleet/state", self._fleet_state_callback, 10
        )

        # Subscribe to incoming task requests
        self.create_subscription(
            String, "/fleet/task_request", self._task_request_callback, 10
        )

        # Publisher for assignments
        self.assignment_pub = self.create_publisher(String, "/fleet/task_assign", 10)

        self.get_logger().info("Task Allocator started")

    def _fleet_state_callback(self, msg: String):
        """Parse fleet state updates to track robot positions."""
        # TODO: Use proper message types instead of string parsing
        pass

    def _task_request_callback(self, msg: String):
        """Handle incoming task requests."""
        # Format: "TASK:task_id:pickup_x:pickup_y:dropoff_x:dropoff_y"
        parts = msg.data.split(":")
        if len(parts) < 5:
            self.get_logger().error(f"Invalid task format: {msg.data}")
            return

        task_id = parts[1]
        pickup_x, pickup_y = float(parts[2]), float(parts[3])
        dropoff_x, dropoff_y = float(parts[4]), float(parts[5])

        self._allocate_task(task_id, pickup_x, pickup_y, dropoff_x, dropoff_y)

    def _allocate_task(
        self,
        task_id: str,
        pickup_x: float,
        pickup_y: float,
        dropoff_x: float,
        dropoff_y: float,
    ):
        """Find the nearest available robot and assign the task."""
        best_robot = None
        best_dist = float("inf")

        for robot_id, state in self.robot_states.items():
            if state["status"] != "IDLE":
                continue
            if state["battery"] < self.battery_threshold:
                self.get_logger().warn(
                    f"{robot_id} battery too low ({state['battery']:.0f}%)"
                )
                continue

            dist = math.sqrt(
                (state["x"] - pickup_x) ** 2 + (state["y"] - pickup_y) ** 2
            )

            if dist < best_dist:
                best_dist = dist
                best_robot = robot_id

        if best_robot is None:
            self.get_logger().warn(f"No robot available for {task_id}, queued")
            return

        self.get_logger().info(
            f"Assigned {task_id} → {best_robot} ({best_dist:.1f}m to pickup)"
        )

        assignment = String()
        assignment.data = f"ASSIGN:{task_id}:{best_robot}"
        self.assignment_pub.publish(assignment)


def main(args=None):
    rclpy.init(args=args)
    node = TaskAllocator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
