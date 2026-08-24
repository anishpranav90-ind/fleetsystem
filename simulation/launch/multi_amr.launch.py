"""Launch 5 AMRs in warehouse with fleet manager and all subsystems."""

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros import FindPackageShare
import os

# Robot spawn positions (spread across warehouse)
ROBOT_SPAWNS = {
    "amr01": {"x": "-10.0", "y": "5.0"},
    "amr02": {"x": "-10.0", "y": "-5.0"},
    "amr03": {"x": "-3.0",  "y": "0.0"},
    "amr04": {"x": "5.0",   "y": "5.0"},
    "amr05": {"x": "5.0",   "y": "-5.0"},
}


def generate_launch_description():
    pkg_share = FindPackageShare("simulation").find("simulation")

    world_file = os.path.join(pkg_share, "worlds", "warehouse.sdf")

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world_file}.items(),
    )

    # Spawn all robots (staggered by 2 seconds each)
    spawn_actions = []
    for i, (robot_id, pos) in enumerate(ROBOT_SPAWNS.items()):
        spawn = Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-entity", robot_id,
                "-file", os.path.join(pkg_share, "models", "amr", "model.sdf"),
                "-x", pos["x"],
                "-y", pos["y"],
                "-z", "0.1",
                "-robot_namespace", robot_id,
            ],
            output="screen",
        )
        spawn_actions.append(TimerAction(period=3.0 + i * 2.0, actions=[spawn]))

    # Edge AI for each robot
    edge_ai_nodes = []
    for i, robot_id in enumerate(ROBOT_SPAWNS):
        edge_ai = Node(
            package="edge_ai",
            executable="edge_ai_node",
            name=f"{robot_id}_edge_ai",
            namespace=robot_id,
            parameters=[{"robot_id": robot_id, "use_sim_time": True}],
            output="screen",
        )
        edge_ai_nodes.append(
            TimerAction(period=3.0 + i * 2.0 + 1.0, actions=[edge_ai])
        )

    # Fleet Manager
    robot_ids = list(ROBOT_SPAWNS.keys())
    fleet_manager = Node(
        package="fleet_manager",
        executable="fleet_manager_node",
        name="fleet_manager",
        parameters=[
            {"robot_ids": robot_ids, "heartbeat_timeout": 10.0, "battery_threshold": 20.0}
        ],
        output="screen",
    )

    # Battery Manager
    battery_manager = Node(
        package="battery_manager",
        executable="battery_node",
        name="battery_manager",
        parameters=[
            {"robot_ids": robot_ids, "tick_interval": 2.0}
        ],
        output="screen",
    )

    # Collision Manager
    collision_manager = Node(
        package="collision_manager",
        executable="collision_manager_node",
        name="collision_manager",
        output="screen",
    )

    # Path Planner
    path_planner = Node(
        package="path_planner",
        executable="path_planner_node",
        name="path_planner",
        output="screen",
    )

    # Task Allocator
    task_allocator = Node(
        package="task_allocator",
        executable="task_allocator_node",
        name="task_allocator",
        output="screen",
    )

    return LaunchDescription(
        [
            gazebo,
            *spawn_actions,
            *edge_ai_nodes,
            TimerAction(
                period=15.0,
                actions=[
                    fleet_manager,
                    battery_manager,
                    collision_manager,
                    path_planner,
                    task_allocator,
                ],
            ),
        ]
    )
