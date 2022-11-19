#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
from cv_bridge import CvBridge
from jsk_robot_startup.msg import EmailBody
from m5stack_ros import EmailRosserial
import os
import rospy
import time
import base64
from sensor_msgs.msg import Image
from std_msgs.msg import UInt16


class EmailFridgeUpperCamera(EmailRosserial):
    """
    This class receives /timer_cam_image topic and send email with the image
    The purpose is to keep the M5 TimerCam in the refrigerator
    and monitor the contents regularly.
    """

    def __init__(self):
        super(EmailFridgeUpperCamera, self).__init__()
        self.sender_address = 'kanazawa@jsk.imi.i.u-tokyo.ac.jp'
        self.receiver_address = 'kanazawa@jsk.imi.i.u-tokyo.ac.jp'
        self.device_name = 'UpperM5TimerCam'
        self.subject = '冷蔵庫の扉が開きました'
        # Subscribers
        rospy.Subscriber('/upper_camera/timer_cam_image', Image, self.image_cb)
        self.img_file_path = '/tmp/email_fridge_upper_camera.png'
        rospy.Subscriber('tof', UInt16, self.tof_cb)
        self.tof = None
        self.tof_threshold = 30
        self.door_open_threshold = 30 # 60s = 1min
        self.door_open_flag = False
        self.door_open_time = None
        self.door_open_images = []
        # Do not send old image
        if os.path.exists(self.img_file_path):
            os.remove(self.img_file_path)

    def image_cb(self, msg):
        self.image = msg
        bridge = CvBridge()
        img = bridge.imgmsg_to_cv2(msg)
        if self.door_open_flag == True: # when door is open
            self.door_open_images.append(img)
            rospy.loginfo('Upper image is added')
        else:
            cv2.imwrite(self.img_file_path, img)
            rospy.loginfo('Saved image is updated')
        self.update_last_communication()

    def tof_cb(self, msg):
        self.tof = msg.data
        if self.tof is not None and self.tof > self.tof_threshold: # when door is open
            if self.door_open_flag == False: # when door first opens
                self.door_open_flag = True
                self.door_open_time = time.time()
                rospy.loginfo('The fridge door is open')
            # elif time.time() >= self.door_open_time + self.door_open_threshold: # When door is left open
            #     self.send_email()
            #     rospy.loginfo('Send email because the fridge door is left open')
        else:  # when door is not open
            if self.door_open_flag == True: # when door is closed
                self.send_email()
                rospy.loginfo('Send email because the fridge door is open and close')
                self.door_open_flag = False
        self.update_last_communication()

    # When door is open, low battery or next day, send email
    def check_status(self, event):
        if self.tof is not None and self.tof > self.tof_threshold:
            self.send_email()
            rospy.loginfo('Send email because the fridge door is left open')
        super(EmailFridgeUpperCamera, self).check_status(event)

    # Check the contents in the fridge by camera
    def email_image_body(self):
        email_body = EmailBody()
        if os.path.exists(self.img_file_path):
            email_body.type = 'img'
            email_body.message = '冷蔵庫上部からの写真です\n'
            email_body.file_path = self.img_file_path
            email_body.img_size = 100
        else:
            email_body.type = 'text'
            email_body.message = '冷蔵庫上部からの写真は届いていません\n'
        email_body.message += '\n'  # end of this section
        return email_body

    def email_added_image_body(self, img):
        email_body = EmailBody()
        email_body.type = 'img'
        email_body.message = '冷蔵庫上部からの写真\n'
        # convert to base64
        encimg = cv2.imencode(".png", img)[1]
        img_str = encimg.tostring()
        img_byte = base64.b64encode(img_str).decode("utf-8")
        email_body.img_data = img_byte
        email_body.img_size = 100
        rospy.loginfo('Upper image is added to email')
        email_body.message += '\n'  # end of this section
        return email_body

    # Check the fridge door state by tof
    def email_tof_body(self):
        email_body = EmailBody()
        email_body.type = 'text'
        if self.tof is None:
            email_body.message = '冷蔵庫のToFのデータは届いていません\n'
        else:
            if self.tof > self.tof_threshold:
                email_body.message += '冷蔵庫の扉が開いたままです。(ToF: {})\n'.format(
                    self.tof)
            else:
                email_body.message += '冷蔵庫の扉は閉じられています。(ToF: {})\n'.format(
                    self.tof)
        email_body.message += '\n'  # end of this section
        return email_body

    def create_email_body(self):
        body = super(EmailFridgeUpperCamera, self).create_email_body()
        body.append(self.email_tof_body())
        body.append(self.email_image_body())
        if self.door_open_images != []:
            for img in self.door_open_images:
                body.append(self.email_added_image_body(img))
            self.door_open_images = []
        return body

    def send_email(self):
        super(EmailFridgeUpperCamera, self).send_email()
        # Do not send the same image twice
        if os.path.exists(self.img_file_path):
            os.remove(self.img_file_path)


if __name__ == '__main__':
    rospy.init_node('email_fridge_upper_camera')
    efuc = EmailFridgeUpperCamera()
    rospy.spin()
