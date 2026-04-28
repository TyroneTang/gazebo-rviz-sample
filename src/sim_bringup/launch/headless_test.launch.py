import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


# only for headless launches
def generate_launch_description() -> None:
    pkg_gazebo_ros = get_package_share_directory("ros_gz_sim")

    # headless
    start_gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={'gz_args': '-r -s empty.sdf'}.items()
    )

    # validator node
    start_validator_node = Node(
        package="sim_bringup",
        executable="validator_node",
        name="validator_node",
        output="screen",
    )

    # this only needed for new gz sim, prev versions use ros msg natively,
    # this one is new, and uses its own gz.msg. hence bridge is to translate this msg from gz.msg to
    # ros msg
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            # Bridge the Ignition model pose topic to ROS 2
            # Syntax: /ignition_topic@ROS2_Type[Ignition_Type
            # this pose needs to match sim bring up Pose and not posestamped
            "/model/simple_bot/pose@geometry_msgs/msg/Pose[gz.msgs.Pose" # [ inwards to gazebo

        ]
    )

    return LaunchDescription(
        [
            start_gz_server,
            start_validator_node,
            bridge_node
        ]
    )