import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


# only for headless launches
def generate_launch_description() -> None:
    pkg_gazebo_ros = get_package_share_directory("ros_gz_sim")
    pkg_sim_bringup = get_package_share_directory("sim_bringup")
    # headless
    start_gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={'gz_args': '-r -s empty.sdf'}.items(),
    )

    # validator node
    start_validator_node = Node(
        package="sim_bringup",
        executable="validator_node",
        name="validator_node", # must match config/goal_forward_2m.yaml
        output="screen",
        parameters=[
            os.path.join(pkg_sim_bringup, "config", "goal_forward_2m.yaml")
        ]
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

            "/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock",
            # outwards from gz
            "/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry",
            # inwards to gz
            "/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist"
        ]
    )

    # publshing state of robot
    urdf_path = PathJoinSubstitution([pkg_sim_bringup, "description", "simple_bot.urdf"])
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": ParameterValue(
                Command(["xacro ", urdf_path]), value_type=str
            )
        }]
    )

    # launch the robot
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "/robot_description",
            # should match description.urdf.
            "-name", "simple_bot",
            "-z", "0.1",
        ]
    )

    # simulate robot moving forward
    start_driver_node = TimerAction(
        # start after sometime. wait for the other nodes to start first.
        # need the bridge to be up before msg transform ign > ros msg.
        period=3.0,
        actions=[
            Node(
                package="sim_bringup",
                executable="driver_node",
                name="driver_node",
                output="screen",
                emulate_tty=True,
                parameters=[
                    # parses from the yaml file into the class 
                    os.path.join(pkg_sim_bringup, "config", "goal_forward_2m.yaml")
                ]
            )
        ]
    )

    return LaunchDescription(
        [
            start_gz_server,
            start_validator_node,
            bridge_node,
            robot_state_publisher,
            spawn_robot,
            start_driver_node
        ]
    )