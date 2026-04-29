import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class Driver(Node):
    def __init__(self):
        super().__init__("driver_node")

        self.declare_parameter("linear_x", 0.0)
        self.declare_parameter("linear_y", 0.0)
        self.declare_parameter("angular_z", 0.0)

        self.declare_parameter("duration_sec", 10.0)

        # 10hz
        self.declare_parameter("publishing_rate_hz", 10.0)

        # configuration init
        self.linear_x = self.get_parameter("linear_x").value
        self.linear_y = self.get_parameter("linear_y").value
        self.angular_z = self.get_parameter("angular_z").value
        self.publishing_rate = self.get_parameter("publishing_rate_hz").value
        
        self.duration = self.get_parameter("duration_sec").value
        
        self.start_time = self.get_clock().now()

        self.pub = self.create_publisher(
            msg_type=Twist,
            topic="/cmd_vel",
            qos_profile=10
        )

        self.timer = self.create_timer(
            # convert publishing hz to sleep sec
            1.0 / self.publishing_rate, self.timed_pub_callback
        )

    def timed_pub_callback(self) -> None:
        # NOTE: this publishes to /cmd_vel and gets transformed in plugin () -> /odom.
        # /odom -> transform ign.msg.odom -> ros2 odom.
        time = self.get_clock().now() - self.start_time
        elapsed = time.nanoseconds/1e9
        

        msg = Twist()

        if elapsed < self.duration:
            # only publish movement within duration
            msg.linear.x = self.linear_x
            msg.linear.y = self.linear_y

        # self.get_logger().info(f"Publishing updating cmd_vel message x: {msg.linear.x}, y: {msg.linear.y}, z: {msg.angular.z}")

        # pub 0 once duration expires.
        self.pub.publish(msg)


# entry point
def main(args=None) -> None:
    rclpy.init(args=args)
    node = Driver()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()