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
        # self.robot_ip_dict = {'fetch15':'133.11.216.217', 'pr1040':'133.11.216.211'} # これは全タスクプログラム共通
        self.robot_ip_dict = {'fetch15':'133.11.216.217', 'pr1040':'133.11.216.211', 'mypc':'133.11.216.149'}
        # self.robot_priority_list = ['pr1040', 'fetch15']
        # self.robot_priority_list = ['fetch15']
        self.robot_priority_list = ['mypc']
        self.task_name = 'fridge_door_close'
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
                self.send_order()
        else: # when door is not open
            self.door_open_flag = False

    def send_order(self):
        for robot in self.robot_priority_list:
            self.ros_client = roslibpy.Ros(self.robot_ip_dict[robot], 9090)
            self.ros_client.run()

            service = roslibpy.Service(self.ros_client, '/firdge_pi_task', 'jsk_2022_09_fridge_pi/FridgePiOrder')
            request = roslibpy.ServiceRequest({'task': self.task_name})

            print('Calling service...')
            result = service.call(request)
            print('Service response: {}'.format(result))
            print('Task result : {}'.format(result["success"]))
            print('Message : {}'.format(result["message"]))
            self.ros_client.run()
            if result["success"]:
                break

if __name__ == '__main__':
    rospy.init_node('roslibpy_fridge_door')
    rfd = RoslibpyFridgeDoor()
    rfd.send_order()
    # import ipdb
    # ipdb.set_trace()
    # rospy.spin()
