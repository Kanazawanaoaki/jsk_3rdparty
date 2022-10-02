#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CalcFridgeDoor():
    """
    """

    def __init__(self):
        self.robot_ability_dict = {'fetch15':{'move':'inside', 'silent_move':'high', 'arm':'single', 'contact':'low', 'dialogue':'able', 'looks':'normal'},
                                   'pr1040':{'move':'inside', 'silent_move':'high', 'arm':'dual', 'contact':'high', 'dialogue':'able', 'looks':'normal'},
                                   'Spot':{'move':'inside_outside', 'silent_move':'low', 'arm':'single', 'contact':'high', 'dialogue':'unable', 'looks':'subtle'},
                                   'Unitree':{'move':'inside_outside', 'silent_move':'low', 'arm':'none', 'contact':'none', 'dialogue':'unable', 'looks':'subtle'},
                                   'Mamoru':{'move':'inside', 'silent_move':'high', 'arm':'none', 'contact':'none', 'dialogue':'able', 'looks':'good'}}
        # self.robot_state_dict = {'fetch15':False, 'pr1040':False, 'Spot':False, 'Unitree':False, 'Mamoru':False}
        self.robot_state_dict = {'fetch15':True, 'pr1040':True, 'Spot':False, 'Unitree':False, 'Mamoru':False}
        print("init")

    def calc(self):
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

if __name__ == '__main__':
    # rospy.init_node('calc_fridge_door')
    cfd = CalcFridgeDoor()
    cfd.calc()
    import ipdb
    ipdb.set_trace()
