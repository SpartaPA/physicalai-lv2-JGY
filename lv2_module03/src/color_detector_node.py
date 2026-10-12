# color_detector_node.py (핵심부)
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped
from cv_bridge import CvBridge
from color_detector import ColorDetector          # 19강 모듈 그대로!

class ColorDetectorNode(Node):
    def __init__(self):
        super().__init__("color_detector")
        self.bridge = CvBridge()
        self.det = ColorDetector(self.load_cfg())
        self.sub = self.create_subscription(Image, "/image_raw", self.on_image,
                                            qos_profile_sensor_data)
        self.pub_pt = self.create_publisher(PointStamped, "/detection", 10)
        self.pub_dbg = self.create_publisher(Image, "/image_annotated", 1)

    def on_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")  # 메시지→ndarray
        r = self.det.step(frame)                   # 19강 코드 재사용
        if r:
            pt = PointStamped()
            pt.header = msg.header                 # 원본 타임스탬프 계승!
            pt.point.x, pt.point.y = r["cx"], r["cy"]
            self.pub_pt.publish(pt)
        dbg = self.det.draw(frame, r)
        self.pub_dbg.publish(self.bridge.cv2_to_imgmsg(dbg, "bgr8"))     # ndarray→메시지