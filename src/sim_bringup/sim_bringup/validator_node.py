import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import math

# reads data from gazebo sim
class GazeboTestValidator(Node):
    def __init__(self):
        super().__init__("gazebo_test_validator")

        # config
        self.robot_model_name = "simple_bot"
        self.tolerance = 0.5
        self.target_x = None
        self.target_y = None

        # subscribe to gz ground truth
        # data is publsihed from gz
        self.truth_sub = self.create_subscription(
            msg_type=Pose,
            topic="/model/simple_bot/pose",
            callback=self.model_state_callback,
            qos_profile=10,
        )

    # pose is the robots' pose in the sim world
    def model_state_callback(self, msg: Pose) -> None:
        try:
            if not self.target_x or not self.target_y:
                return None

            # get ground truth from msg
            curr_x = msg.pose.position.x
            curr_y = msg.pose.position.y

            # distance to target
            distance = math.sqrt((curr_x - self.target_x)**2 + (curr_y - self.target_y)**2)

            if distance <= self.tolerance:
                self.get_logger().info(f"Reached target within tolerance: distance={distance:.3f}")
        except Exception as e:
            self.get_logger().error(f"Error in model_state_callback: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = GazeboTestValidator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()