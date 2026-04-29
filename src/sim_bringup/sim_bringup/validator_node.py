import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
import math
import sys

# reads data from gazebo sim
class GazeboTestValidator(Node):
    def __init__(self):
        super().__init__("gazebo_test_validator")
        # delcare params defaults
        # discoverable via ros2 param
        self.declare_parameter("robot_model_name", "simple_bot")
        self.declare_parameter("tolerance", 0.5)
        self.declare_parameter("target_x", 0.0)
        self.declare_parameter("target_y", 0.0)
        self.declare_parameter("timeout_sec", 3.0)

        # config
        # get from ros params
        self.robot_model_name = self.get_parameter("robot_model_name").value
        self.tolerance = self.get_parameter("tolerance").value
        self.target_x = self.get_parameter("target_x").value
        self.target_y = self.get_parameter("target_y").value
        self.timeout_sec = self.get_parameter("timeout_sec").value

        # pass fail conditions
        self.passed = False
        self.finished = False
        self.start_time = self.get_clock().now()


        self.get_logger().info(
            f"Starting gz test validator node with params: \n target=({self.target_x}, {self.target_y}), "
            + f"tolerance={self.tolerance}, timeout={self.timeout_sec}s"
        )

        # subscribe to gz ground truth
        # data is publsihed from gz
        self.odom = self.create_subscription(
            msg_type=Odometry,
            topic="/odom",
            callback=self.odom_callback,
            qos_profile=10,
        )

    # pose is the robots' pose in the sim world
    def odom_callback(self, msg: Odometry) -> None:
        if self.finished:
            return None
        try:
            # get ground truth from msg
            curr_x = msg.pose.pose.position.x
            curr_y = msg.pose.pose.position.y

            self.get_logger().info(
                f"Current pose of robot x: {curr_x:.3f}, y: {curr_y:.3f}"
            )

            # distance to target
            # use Euclidean distance formula
            distance = math.sqrt((curr_x - self.target_x)**2 + (curr_y - self.target_y)**2)

            if distance <= self.tolerance:
                elapsed_time = (self.get_clock().now() - self.start_time)
                elapsed = elapsed_time.nanoseconds / 1e9
                self.get_logger().info(f"Reached target within tolerance: distance={distance:.3f}, elapsed time = {elapsed:.2f}")
                self.passed = True
                self.finished = True

        except Exception as e:
            self.get_logger().error(f"Error in odom_callback: {e}")


    def on_timeout(self) -> None:
        if self.finished:
            return
        self.get_logger().error(
            f"FAIL: timeout after {self.timeout_sec}s "
            f"(target=({self.target_x}, {self.target_y}), tolerance={self.tolerance})"
        )
        self.passed = False
        self.finished = True


def main(args=None):
    rclpy.init(args=args)
    node = GazeboTestValidator()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    sys.exit(0 if node.passed else 1)


if __name__ == "__main__":
    main()