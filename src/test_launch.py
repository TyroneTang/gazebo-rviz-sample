from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/model/simple_bot/pose@geometry_msgs/msg/Pose[gz.msgs.Pose"
        ]
    )
    return LaunchDescription([bridge_node])
