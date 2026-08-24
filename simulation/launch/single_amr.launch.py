"""Launch single AMR in Gazebo warehouse world with Nav2."""

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros import FindPackageShare
import os


def generate_launch_description():
    pkg_share = FindPackageShare("simulation").find("simulation")

    # Arguments
    robot_id_arg = DeclareLaunchArgument(
        "robot_id", default_value="amr01", description="Robot namespace"
    )

    x_arg = DeclareLaunchArgument("x", default_value="-10.0", description="Initial X")
    y_arg = DeclareLaunchArgument("y", default_value="0.0", description="Initial Y")

    robot_id = LaunchConfiguration("robot_id")

    # Gazebo world
    world_file = os.path.join(pkg_share, "worlds", "warehouse.sdf")

    # Include Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world_file}.items(),
    )

    # Spawn AMR
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", robot_id,
            "-file", os.path.join(pkg_share, "models", "amr", "model.sdf"),
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", "0.1",
            "-robot_namespace", robot_id,
        ],
        output="screen",
    )

    # Nav2 — bring up navigation stack
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                FindPackageShare("nav2_bringup").find("nav2_bringup"),
                "launch",
                "navigation_launch.py",
            )
        ),
        launch_arguments={
            "namespace": robot_id,
            "use_sim_time": "true",
            "autostart": "true",
        }.items(),
    )

    # Edge AI node for this robot
    edge_ai_node = Node(
        package="edge_ai",
        executable="edge_ai_node",
        name=f"{robot_id}_edge_ai",
        namespace=robot_id,
        parameters=[{"robot_id": robot_id, "use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription(
        [
            robot_id_arg,
            x_arg,
            y_arg,
            gazebo,
            TimerAction(
                period=3.0,
                actions=[spawn_robot, nav2_bringup, edge_ai_node],
            ),
        ]
    )
