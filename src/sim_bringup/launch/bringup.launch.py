from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare



def generate_launch_description() -> None:
    # find this package as base relative/abs dir
    pkg_share = FindPackageShare("sim_bringup")
    pkg_ros_gz_sim = FindPackageShare("ros_gz_sim")

    urdf_path = PathJoinSubstitution([pkg_share, "description", "simple_bot.urdf"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "default.rviz"])

    use_sim_time = LaunchConfiguration("use_sim_time")

    declare_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="use Gazebo simulation clock"
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_ros_gz_sim, "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": "-r -v 3 empty.sdf"}.items()
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "robot_description": ParameterValue(
                Command(["xacro ", urdf_path]), value_type=str
            )
        }]
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "/robot_description",
            "-name", "simple_bot",
            "-z", "0.1",
        ]
    )

    # bridge between gz.msgs with Ros2 msgs
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            # add this for validator
            "/model/simple_bot/pose@geometry_msgs/msg/Pose[gz.msgs.Pose"
        ],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    validator_node = Node(
        package="sim_bringup",
        executable="validator_node",
        name="validator_node",
        output="screen",
    )

    return LaunchDescription([
        declare_sim_time,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        bridge,
        rviz,
        validator_node
    ])