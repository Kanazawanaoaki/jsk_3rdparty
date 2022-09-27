#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rospy
import time
import roslibpy
from std_msgs.msg import UInt16


class RoslibpyFridgeDoor():
    """
    """

    def __init__(self):
        self.robot_ip_dict = {'fetch15':'133.11.216.217', 'pr1040':'133.11.216.211'} # これは全タスクプログラム共通
        # self.robot_priority_list = ['pr1040', 'fetch15']
        self.robot_priority_list = ['fetch15']
        ## Subscribers
        rospy.Subscriber('tof', UInt16, self.tof_cb)
        self.tof = None
        self.tof_threshold = 30
        self.door_open_threshold = 60 # 60s = 1min
        self.door_open_flag = False
        self.door_open_time = None

    def tof_cb(self, msg):
        self.tof = msg.data
        # self.update_last_communication()
        if self.tof is not None and self.tof > self.tof_threshold: # when door is open
            if self.door_open_flag == False: # when door first opens
                self.door_open_flag = True
                self.door_open_time = time.time()
            elif time.time() >= self.door_open_time + self.door_open_threshold: # When door is left open
                self.send_rostopic()
        else: # when door is not open
            self.door_open_flag = False

    def send_rostopic(self):
        for robot in self.robot_priority_list:
            self.ros_client = roslibpy.Ros(self.robot_ip_dict[robot], 9090)
            self.ros_client.run()

            service = roslibpy.Service(client, '/set_ludicrous_speed', 'std_srvs/SetBool')
            request = roslibpy.ServiceRequest({'data': True})

            print('Calling service...')
            result = service.call(request)
            print('Service response: {}'.format(result))
            break

if __name__ == '__main__':
    rospy.init_node('roslibpy_fridge_door')
    rfd = RoslibpyFridgeDoor()
    import ipdb
    ipdb.set_trace()
    rospy.spin()
