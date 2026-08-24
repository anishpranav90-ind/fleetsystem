"""Collision Manager — Multi-robot collision avoidance.

Detects path conflicts between AMRs and resolves them via:
1. Priority-based: lower-priority robot waits
2. Reroute: lower-priority robot takes alternate path
3. Wait: both slow down in conflict zone
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
import math
from typing import Dict, List, Tuple, Optional


class CollisionManager(Node):
    """Detects and resolves path conflicts between multiple AMRs."""

    def __init__(self):
        super().__init__("collision_manager")

        self.declare_parameter("conflict_distance_threshold", 2.0)
        self.declare_parameter("prediction_horizon", 5.0)

        self.conflict_threshold = (
            self.get_parameter("conflict_distance_threshold")
            .get_parameter_value()
            .double_value
        )

        # Robot states and planned paths
        self.robot_positions: Dict[str, Tuple[float, float]] = {}
        self.robot_paths: Dict[str, List[Tuple[float, float]]] = {}
        self.robot_priorities: Dict[str, int] = {}

        # Subscribers
        self.create_subscription(
            String, "/fleet/state", self._fleet_state_callback, 10
        )
        self.create_subscription(
            String, "/fleet/planned_paths", self._paths_callback, 10
        )

        # Publishers
        self.conflict_pub = self.create_publisher(
            String, "/fleet/conflict", 10
        )
        self.resolution_pub = self.create_publisher(
            String, "/fleet/resolution", 10
        )

        # Periodic conflict check
        self.create_timer(0.5, self._check_conflicts)

        self.get_logger().info("Collision Manager started")

    def _fleet_state_callback(self, msg: String):
        """Parse fleet state to track robot positions."""
        # TODO: Use proper message types
        pass

    def _paths_callback(self, msg: String):
        """Parse planned paths for conflict detection."""
        # TODO: Use proper message types
        pass

    def _check_conflicts(self):
        """Check all robot path pairs for conflicts."""
        robot_ids = list(self.robot_positions.keys())

        for i in range(len(robot_ids)):
            for j in range(i + 1, len(robot_ids)):
                rid_a, rid_b = robot_ids[i], robot_ids[j]
                conflict = self._detect_conflict(rid_a, rid_b)

                if conflict:
                    self._resolve_conflict(rid_a, rid_b, conflict)

    def _detect_conflict(
        self, robot_a: str, robot_b: str
    ) -> Optional[Tuple[float, float]]:
        """Detect if two robots' paths will intersect."""
        pos_a = self.robot_positions.get(robot_a)
        pos_b = self.robot_positions.get(robot_b)

        if pos_a is None or pos_b is None:
            return None

        dist = math.sqrt(
            (pos_a[0] - pos_b[0]) ** 2 + (pos_a[1] - pos_b[1]) ** 2
        )

        if dist < self.conflict_threshold:
            # Conflict point is midpoint
            return (
                (pos_a[0] + pos_b[0]) / 2,
                (pos_a[1] + pos_b[1]) / 2,
            )

        return None

    def _resolve_conflict(
        self, robot_a: str, robot_b: str, conflict_point: Tuple[float, float]
    ):
        """Resolve a path conflict using priority-based approach."""
        priority_a = self.robot_priorities.get(robot_a, 100)
        priority_b = self.robot_priorities.get(robot_b, 100)

        # Lower number = higher priority
        if priority_a <= priority_b:
            waiting_robot = robot_b
            priority_robot = robot_a
        else:
            waiting_robot = robot_a
            priority_robot = robot_b

        self.get_logger().warn(
            f"⚠ PATH CONFLICT: {robot_a} ↔ {robot_b} "
            f"at ({conflict_point[0]:.1f}, {conflict_point[1]:.1f})"
        )
        self.get_logger().info(
            f"Resolution: {waiting_robot} waits for {priority_robot}"
        )

        # Publish conflict event
        conflict_msg = String()
        conflict_msg.data = (
            f"CONFLICT:{robot_a}:{robot_b}:"
            f"{conflict_point[0]:.1f}:{conflict_point[1]:.1f}:WAIT"
        )
        self.conflict_pub.publish(conflict_msg)

        # Tell waiting robot to pause
        resolution_msg = String()
        resolution_msg.data = f"WAIT:{waiting_robot}:{priority_robot}"
        self.resolution_pub.publish(resolution_msg)


def main(args=None):
    rclpy.init(args=args)
    node = CollisionManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
