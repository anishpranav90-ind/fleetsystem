"""Path Planner ROS 2 Node — Wraps A* planner for ROS 2 integration.

Subscribes to goal requests, computes global paths using A*,
and publishes the result as Nav Path messages for Nav2 to follow.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import String
from path_planner.astar import astar


class PathPlannerNode(Node):
    def __init__(self):
        super().__init__("path_planner")

        # Default warehouse grid (rows x cols)
        self.declare_parameter("grid_width", 20)
        self.declare_parameter("grid_height", 15)
        self.declare_parameter("resolution", 0.5)

        self.resolution = (
            self.get_parameter("resolution").get_parameter_value().double_value
        )

        # Initialize empty warehouse grid
        self.grid = [
            ["." for _ in range(20)] for _ in range(15)
        ]

        # Subscribe to path requests
        self.create_subscription(
            String, "/fleet/path_request", self._path_request_callback, 10
        )

        # Publisher for computed paths
        self.path_pub = self.create_publisher(Path, "/fleet/planned_path", 10)

        self.get_logger().info("Path Planner started (A*)")

    def _path_request_callback(self, msg: String):
        """Handle path planning requests.
        Format: "PLAN:robot_id:start_row:start_col:goal_row:goal_col"
        """
        parts = msg.data.split(":")
        if len(parts) < 6:
            self.get_logger().error(f"Invalid path request: {msg.data}")
            return

        robot_id = parts[1]
        start = (int(parts[2]), int(parts[3]))
        goal = (int(parts[4]), int(parts[5]))

        self.get_logger().info(
            f"Planning path for {robot_id}: {start} → {goal}"
        )

        path_grid = astar(self.grid, start, goal)

        if path_grid is None:
            self.get_logger().warn(f"No path found for {robot_id}")
            return

        # Convert to ROS Path message
        path_msg = Path()
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.header.frame_id = "map"

        for row, col in path_grid:
            pose = PoseStamped()
            pose.header = path_msg.header
            pose.pose.position.x = col * self.resolution
            pose.pose.position.y = row * self.resolution
            path_msg.poses.append(pose)

        self.path_pub.publish(path_msg)
        self.get_logger().info(
            f"Path published for {robot_id}: {len(path_grid)} waypoints"
        )


def main(args=None):
    rclpy.init(args=args)
    node = PathPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
