"""Launch file for Fleet Manager node."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    robot_ids_arg = DeclareLaunchArgument(
        "robot_ids",
        default_value='["amr01", "amr02", "amr03", "amr04", "amr05"]',
        description="List of robot IDs to monitor",
    )

    heartbeat_timeout_arg = DeclareLaunchArgument(
        "heartbeat_timeout",
        default_value="10.0",
        description="Seconds before a robot is declared failed",
    )

    battery_threshold_arg = DeclareLaunchArgument(
        "battery_threshold",
        default_value="20.0",
        description="Minimum battery percentage to accept a task",
    )

    fleet_manager_node = Node(
        package="fleet_manager",
        executable="fleet_manager_node",
        name="fleet_manager",
        output="screen",
        parameters=[
            {
                "robot_ids": LaunchConfiguration("robot_ids"),
                "heartbeat_timeout": LaunchConfiguration("heartbeat_timeout"),
                "battery_threshold": LaunchConfiguration("battery_threshold"),
            }
        ],
    )

    return LaunchDescription(
        [
            robot_ids_arg,
            heartbeat_timeout_arg,
            battery_threshold_arg,
            fleet_manager_node,
        ]
    )
