#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2019-07-15 17:13
# @Author  : jacobwu
# @File    : Time_sorting.py

import json
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def read_font(folder_name):
    full_dict = {}
    for root_folder, dirs_folder, folder in os.walk(folder_name):
        if root_folder != folder_name:
            dict_single_folder = {}
            folder_n = root_folder.split("/")[1]
            for f in folder:
                file = open(root_folder + "/" + f, 'r', encoding='utf-8-sig')
                s = json.load(file)
                dict_single_folder[f] = s
                file.close()
            full_dict[folder_n] = dict_single_folder
    return full_dict
    # pass

def file_path_f(rootDir):
    file_path = {}
    for root_folder, dirs_folder, folder in os.walk(rootDir):
        if root_folder != rootDir:
            dict_single_folder = {}
            folder_n = root_folder.split("/")[1]
            for f in folder:
                dict_single_folder[f] = f[:3]
            file_path[folder_n] = dict_single_folder
    return file_path

file_path_f('audio') 

    # Put everyone speaking time zone into one set，Take the union，then can find the speaking time zones


def join_speak_time(speak_time):
    speak_time_final = []
    # Combine all speaking time zone.
    # Compare the time between the current speaking time zone and the next speaking time zone.
    speak_zone_1 = speak_time.pop(0)
    speak_zone_2 = speak_time.pop(0)
    while True:
        try:
            if speak_zone_1[1] < speak_zone_2[0]:
                #  No need to merge，just need to add speaking time zone into final speak time.
                speak_time_final.append(speak_zone_1)
                if not speak_time:
                    speak_time_final.append(speak_zone_2)
                speak_zone_1 = speak_zone_2
                speak_zone_2 = speak_time.pop(0)
            elif speak_zone_1[1] >= speak_zone_2[0]:
                # need to merge，just need to find the earliest time as start time and latest time as end time
                # Set them as new start time and end time.
                start_time = speak_zone_1[0] if speak_zone_1[0] < speak_zone_2[0] else speak_zone_2[0]
                end_time = speak_zone_1[1] if speak_zone_1[1] > speak_zone_2[1] else speak_zone_2[1]
                if not speak_time:
                    speak_time_final.append((start_time, end_time))
                speak_zone_1 = (start_time, end_time)
                speak_zone_2 = speak_time.pop(0)
        except IndexError:
            break
    return speak_time_final


# According to final speak time to find out no speech time
def get_blank_time(speak_time):
    blank_time_zone = []
    blank_time_start = '0:00:00.00'
    for time_zone in speak_time:
        blank_time_end = time_zone[0]
        blank_time_zone.append((blank_time_start, blank_time_end))
        blank_time_start = time_zone[1]
    return blank_time_zone


# write sox command into bash script
def write_command_bash(filename, blank_time_zone):
    path_f = file_path_f('audio')
    logging.debug('writing lines to bash script {}......'.format(filename))
    with open(filename, 'w') as fp:
        fp.write('#!/bin/bash\n')
        commands = [
            'sox {} {} trim {} {}\n'.format(path_f_i, path_f_o, blank_zone[0], blank_zone[1])
            for blank_zone in blank_time_zone
            for path_f_i in path_f
        ]
        fp.writelines(commands)
    logging.debug('writing script done!')


if __name__ == '__main__':
    # list1 = ['dev', 'eval', 'train']
    f_list = read_font("transcriptions")
    # write sox command into shell script，out put shell script and save it into dict script_base_dir
    script_base_dir = 'scripts'

    if not os.path.exists(script_base_dir):
        os.mkdir(script_base_dir)
    for dirname in f_list.keys():
        # Create a subdirectory
        if not os.path.exists(script_base_dir + os.path.sep + dirname):
            os.mkdir(script_base_dir + os.path.sep + dirname)
        for filename in f_list[dirname].keys():
            # get script file name
            script_filename = os.path.splitext(filename)[0] + '.sh'
            script_filepath = script_base_dir + os.path.sep + dirname + os.path.sep + script_filename

            start_time_list = []
            end_time_list = []
            speak_time = []
            # start_time_v = [start_time_list[0]]
            # end_time_v = []
            for i in range(len(f_list[dirname][filename]) - 1):
                f_list_start = f_list[dirname][filename][i]["start_time"]
                f_list_end = f_list[dirname][filename][i]["end_time"]
                start_time = min(f_list_start, key=f_list_start.get)
                end_time = max(f_list_end, key=f_list_start.get)
                speak_time.append((f_list_start[start_time], f_list_end[end_time]))
                start_time_list.append({f_list_start[start_time]})
                end_time_list.append({f_list_end[end_time]})

            # output Debug information
            logging.info('processing json file : {}'.format(dirname + os.path.sep + filename))
            logging.debug('start time：' + str(start_time_list[0:5]))
            logging.debug('end time:' + str(end_time_list[0:5]))
            logging.debug('speak time:' + str(speak_time[0:5]))
            # get final speaking time zone
            speak_time_final = join_speak_time(speak_time)
            logging.debug('speak zone final:' + str(speak_time_final[0:5]))
            # get no speaking time zone
            blank_time_zone = get_blank_time(speak_time_final)
            logging.debug('blank zone:' + str(blank_time_zone[0:5]))
            # write file
            write_command_bash(script_filepath, blank_time_zone)
