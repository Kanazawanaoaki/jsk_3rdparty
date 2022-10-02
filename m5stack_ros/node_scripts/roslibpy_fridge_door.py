#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rospy
import time
import roslibpy
from std_msgs.msg import UInt16, Bool


class RoslibpyFridgeDoor():
    """
    """

    def __init__(self):
        # self.robot_ip_dict = {'fetch15':'133.11.216.217', 'pr1040':'133.11.216.211'} # これは全タスクプログラム共通
        # self.robot_ip_dict = {'fetch15':'133.11.216.217', 'pr1040':'133.11.216.211', 'mypc':'133.11.216.149'}
        self.robot_ip_dict = {'fetch15':'133.11.216.149', 'pr1040':'133.11.216.153'} # for tmp exec
        self.robot_ability_dict = {'fetch15':{'move':'inside', 'silent_move':'high', 'arm':'single', 'contact':'low', 'dialogue':'able', 'looks':'normal'},
                                   'pr1040':{'move':'inside', 'silent_move':'high', 'arm':'dual', 'contact':'high', 'dialogue':'able', 'looks':'normal'},
                                   'Spot':{'move':'inside_outside', 'silent_move':'low', 'arm':'single', 'contact':'high', 'dialogue':'unable', 'looks':'subtle'},
                                   'Unitree':{'move':'inside_outside', 'silent_move':'low', 'arm':'none', 'contact':'none', 'dialogue':'unable', 'looks':'subtle'},
                                   'Mamoru':{'move':'inside', 'silent_move':'high', 'arm':'none', 'contact':'none', 'dialogue':'able', 'looks':'good'}}
        self.robot_state_dict = {'fetch15':False, 'pr1040':False, 'Spot':False, 'Unitree':False, 'Mamoru':False}
        # self.robot_priority_list = ['pr1040', 'fetch15']
        # self.robot_priority_list = ['fetch15']
        # self.robot_priority_list = ['mypc']

        self.task_name = 'fridge_door_close'
        ## Subscribers
        rospy.Subscriber('tof', UInt16, self.tof_cb)
        rospy.Subscriber('pr2_robot_state', Bool, self.pr2_state_cb)
        rospy.Subscriber('fetch_robot_state', Bool, self.fetch_state_cb)
        self.tof = None
        self.tof_threshold = 30
        # self.door_open_threshold = 60 # 60s = 1min
        self.door_open_threshold = 30 # 60s = 1min
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

    def pr2_state_cb(self, msg):
        self.robot_state_dict['pr1040'] = msg.data

    def fetch_state_cb(self, msg):
        self.robot_state_dict['fetch15'] = msg.data

    def calc_priority(self):
        robot_priority_dict = {}
        for robot in self.robot_ability_dict.keys():
            print(robot)
            now_a = self.robot_ability_dict[robot]
            # print(now_a)

            ability_score = 1
            if now_a['move'] == 'inside' or now_a['move'] == 'inside_outside':
                ability_score *= 10
            else:
                ability_score *= 0

            if now_a['silent_move'] == 'high':
                ability_score *= 5
            else:
                ability_score *= 1

            if now_a['arm'] == 'single' or now_a['arm'] == 'dual':
                ability_score *= 10
            else:
                ability_score *= 0

            if now_a['contact'] == 'high':
                ability_score *= 2
            else:
                ability_score *= 1

            if now_a['dialogue'] == 'able':
                ability_score *= 1
            else:
                ability_score *= 1

            if now_a['looks'] == 'good':
                ability_score *= 1
            else:
                ability_score *= 1

            print("ability_score of {} is : {}".format(robot, ability_score))

            state_score = 1
            if self.robot_state_dict[robot]:
                state_score *= 10
            else:
                state_score *= 0
            print("state_score of {} is : {}".format(robot, state_score))

            all_score = ability_score * state_score
            print("all_score of {} is : {}".format(robot, all_score))
            if all_score > 0:
                robot_priority_dict[str(robot)] = all_score

        self.robot_priority_list = sorted(robot_priority_dict.items(), reverse=True)
        print(self.robot_priority_list)
        return self.robot_priority_list

    def send_order(self):
        self.calc_priority()
        for robot in self.robot_priority_list:
            self.ros_client = roslibpy.Ros(self.robot_ip_dict[robot[0]], 9090)
            self.ros_client.run()

            service = roslibpy.Service(self.ros_client, '/fridge_pi_task', 'jsk_2022_09_fridge_pi/FridgePiOrder')
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
    # rfd.send_order()
    # import ipdb
    # ipdb.set_trace()
    rospy.spin()
