"""Edge AI — Local decision engine running on each AMR.

This is where the "Edge" in EdgeFleet becomes meaningful.
Each AMR gets its own edge_ai_node that makes quick local decisions
using sensor data without waiting for the central Fleet Manager.

Inputs:
- Laser scan (obstacle distances)
- Battery level
- Nearby robots (from local sensors)
- Current velocity
- Current route

Outputs:
- STOP / SLOW / REROUTE / GO_CHARGE commands
- Local status updates

Rule-based initially, with ML model integration point for later.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import LaserScan
import math
from enum import Enum


class EdgeDecision(Enum):
    STOP = "STOP"
    SLOW = "SLOW"
    REROUTE = "REROUTE"
    GO_CHARGE = "GO_CHARGE"
    CONTINUE = "CONTINUE"


class EdgeAINode(Node):
    """Local AI decision engine for a single AMR."""

    def __init__(self):
        super().__init__("edge_ai")

        self.declare_parameter("robot_id", "amr01")
        self.declare_parameter("emergency_stop_distance", 1.0)
        self.declare_parameter("slow_distance", 2.0)
        self.declare_parameter("critical_battery", 15.0)
        self.declare_parameter("low_battery_warning", 25.0)

        self.robot_id = (
            self.get_parameter("robot_id").get_parameter_value().string_value
        )
        self.emergency_dist = (
            self.get_parameter("emergency_stop_distance")
            .get_parameter_value()
            .double_value
        )
        self.slow_dist = (
            self.get_parameter("slow_distance").get_parameter_value().double_value
        )
        self.critical_battery = (
            self.get_parameter("critical_battery").get_parameter_value().double_value
        )
        self.low_battery = (
            self.get_parameter("low_battery_warning").get_parameter_value().double_value
        )

        self.current_battery = 100.0
        self.current_velocity = 0.0
        self.obstacle_distances = []

        ns = f"/{self.robot_id}"

        # Subscribers
        self.create_subscription(
            LaserScan, f"{ns}/scan", self._laser_callback, 10
        )
        self.create_subscription(
            Float32, f"{ns}/battery", self._battery_callback, 10
        )

        # Publishers
        self.decision_pub = self.create_publisher(
            String, f"{ns}/edge_decision", 10
        )
        self.status_pub = self.create_publisher(
            String, f"{ns}/status", 10
        )

        # Decision loop — runs every 0.1s for quick local response
        self.create_timer(0.1, self._make_decision)

        self.get_logger().info(f"Edge AI started for {self.robot_id}")

    def _laser_callback(self, msg: LaserScan):
        """Process laser scan data and find nearest obstacles."""
        self.obstacle_distances = [
            r for r in msg.ranges if r > 0.0 and r < float("inf")
        ]

    def _battery_callback(self, msg: Float32):
        self.current_battery = msg.data

    def _make_decision(self):
        """Rule-based decision engine.

        Priority:
        1. Emergency stop (obstacle too close)
        2. Go charge (battery critical)
        3. Slow down (obstacle nearby or low battery)
        4. Reroute (path blocked but not critical)
        5. Continue normally
        """
        decision = EdgeDecision.CONTINUE
        reason = "All clear"

        # --- Check 1: Emergency stop ---
        if self.obstacle_distances:
            min_dist = min(self.obstacle_distances)
            if min_dist < self.emergency_dist:
                decision = EdgeDecision.STOP
                reason = f"Emergency: obstacle at {min_dist:.2f}m"

        # --- Check 2: Go charge ---
        if self.current_battery < self.critical_battery:
            decision = EdgeDecision.GO_CHARGE
            reason = f"Critical battery: {self.current_battery:.1f}%"

        # --- Check 3: Slow down ---
        elif self.current_battery < self.low_battery:
            decision = EdgeDecision.SLOW
            reason = f"Low battery warning: {self.current_battery:.1f}%"
        elif self.obstacle_distances:
            min_dist = min(self.obstacle_distances)
            if min_dist < self.slow_dist and decision != EdgeDecision.STOP:
                decision = EdgeDecision.SLOW
                reason = f"Obstacle nearby: {min_dist:.2f}m"

        # Publish decision
        decision_msg = String()
        decision_msg.data = f"{decision.value}:{reason}"
        self.decision_pub.publish(decision_msg)

        # Publish updated status
        status_msg = String()
        status_msg.data = f"EDGE_AI:{decision.value}:{self.current_battery:.0f}%"
        self.status_pub.publish(status_msg)

        if decision != EdgeDecision.CONTINUE:
            self.get_logger().info(
                f"🤖 {self.robot_id} Edge AI decision: {decision.value} — {reason}"
            )


def main(args=None):
    rclpy.init(args=args)
    node = EdgeAINode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
