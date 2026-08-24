"""Battery Manager — Simulates battery drain and charge for each AMR.

Battery behavior:
- Moving: -0.5% per tick
- Idle:   -0.1% per tick
- Charging: +1.0% per tick (when at charging station)

Fleet Manager uses battery state to avoid assigning tasks to low-battery robots.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import random


class BatteryManager(Node):
    """Simulates battery levels for all AMRs in the fleet."""

    def __init__(self):
        super().__init__("battery_manager")

        self.declare_parameter("robot_ids", ["amr01", "amr02", "amr03"])
        self.declare_parameter("tick_interval", 2.0)
        self.declare_parameter("drain_rate_moving", 0.5)
        self.declare_parameter("drain_rate_idle", 0.1)
        self.declare_parameter("charge_rate", 1.0)
        self.declare_parameter("critical_battery", 15.0)

        self.robot_ids = (
            self.get_parameter("robot_ids").get_parameter_value().string_array_value
        )
        self.drain_moving = (
            self.get_parameter("drain_rate_moving").get_parameter_value().double_value
        )
        self.drain_idle = (
            self.get_parameter("drain_rate_idle").get_parameter_value().double_value
        )
        self.charge_rate = (
            self.get_parameter("charge_rate").get_parameter_value().double_value
        )
        self.critical_battery = (
            self.get_parameter("critical_battery").get_parameter_value().double_value
        )

        # Battery state per robot
        self.batteries = {}
        self.robot_statuses = {}

        # Initialize batteries
        for rid in self.robot_ids:
            self.batteries[rid] = 100.0 - random.uniform(0, 30)
            self.robot_statuses[rid] = "IDLE"

        # Publishers — one battery topic per robot
        self.battery_pubs = {}
        for rid in self.robot_ids:
            self.battery_pubs[rid] = self.create_publisher(
                Float32, f"/{rid}/battery", 10
            )

        self.fleet_battery_pub = self.create_publisher(
            String, "/fleet/battery_status", 10
        )

        # Subscribe to robot statuses
        for rid in self.robot_ids:
            self.create_subscription(
                String,
                f"/{rid}/status",
                lambda msg, r=rid: self._status_callback(r, msg),
                10,
            )

        # Battery update timer
        tick_interval = (
            self.get_parameter("tick_interval").get_parameter_value().double_value
        )
        self.create_timer(tick_interval, self._update_batteries)

        self.get_logger().info(
            f"Battery Manager started for {len(self.robot_ids)} robots"
        )

    def _status_callback(self, robot_id: str, msg: String):
        self.robot_statuses[robot_id] = msg.data

    def _update_batteries(self):
        """Update battery levels based on robot status."""
        status_str = "BATTERY STATUS:\n"

        for rid in self.robot_ids:
            status = self.robot_statuses.get(rid, "IDLE")

            if status == "CHARGING":
                self.batteries[rid] = min(
                    100.0, self.batteries[rid] + self.charge_rate
                )
            elif status == "BUSY":
                self.batteries[rid] = max(
                    0.0, self.batteries[rid] - self.drain_moving
                )
            else:  # IDLE or FAILED
                self.batteries[rid] = max(
                    0.0, self.batteries[rid] - self.drain_idle
                )

            # Publish individual battery level
            msg = Float32()
            msg.data = self.batteries[rid]
            self.battery_pubs[rid].publish(msg)

            # Check critical level
            if self.batteries[rid] < self.critical_battery:
                self.get_logger().warn(
                    f"⚠ {rid} CRITICAL BATTERY: {self.batteries[rid]:.1f}%"
                )

            icon = "🔴" if self.batteries[rid] < self.critical_battery else "🟢"
            status_str += f"  {icon} {rid}: {self.batteries[rid]:.1f}%\n"

        fleet_msg = String()
        fleet_msg.data = status_str
        self.fleet_battery_pub.publish(fleet_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BatteryManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
