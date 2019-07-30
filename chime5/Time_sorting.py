#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2019-07-15 17:13
# @Author  : jacobwu


import json
import os
# import logging
import re
import sys
# from pprint import pprint

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def read_font(folder_name):
    full_dict = {}
    for root_folder, dirs_folder, folder in os.walk(folder_name):
        if root_folder != folder_name:
            dict_single_folder = {}
            folder_n = re.sub('\W', ' ', root_folder).split(' ')[1]
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
            folder_n = re.sub('\W', ' ', root_folder).split(' ')[1]
            for f in folder:
                dict_single_folder[f] = f[:3]
            file_path[folder_n] = dict_single_folder
    return file_path


file_path_f('audio')


def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]


def naming(index):
    re.compile('wav')
    f = file_path_f('audio')
    a = []
    names_list = []
    for key in f:
        key_v = get_key(f[key], index)
        if len(key_v):
            a.append(key_v)
    if len(a):
        for fnames in a[0]:
            fnames_l = list(fnames)
            for i in range(4):
                fnames_l.pop()
            names_list.append(''.join(fnames_l))

    return names_list


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
def write_command_bash(sh_name, wav_file_list, input_path, ultimate, wav_out_dir):

    with open(sh_name, 'w') as fp:
        fp.write('#!/bin/bash\n')
        for i in range(len(wav_file_list)):
            for j in range(len(ultimate)):
                commands = [
                    'sox {0} {1} trim {2} {3}\n'.format(input_path + '/' + wav_file_list[i] + '.wav',
                                                        wav_out_dir + '/' + wav_file_list[i] + ultimate[j][0] + str(j) + '.wav',
                                                        ultimate[j][2][0], ultimate[j][2][1])
                ]
                fp.writelines(commands)


def guided_sort(index_list, target_list):
    result_list = []
    for j in range(len(index_list)):
        result_list.append(target_list[index_list[j]])
    return result_list


if __name__ == '__main__':
    # list1 = ['dev', 'eval', 'train']

    # write sox command into shell script，out put shell script and save it into dict script_base_dir
    # trans_dir = 'transcriptions'
    # script_base_dir = 'scripts'
    # output_path = '.'
    # audiodir = 'audio'
    # wav_file_output_dir = '.'

    trans_dir = sys.argv[1]
    script_base_dir = sys.argv[2]
    output_path = sys.argv[3]
    audiodir = sys.argv[4]
    wav_file_output_dir = sys.argv[5]

    f_list = read_font("transcriptions")
    if not os.path.exists(script_base_dir):
        os.mkdir(script_base_dir)

    for dirname in f_list.keys():
        # Create a subdirectory
        if not os.path.exists(script_base_dir + os.path.sep + dirname):
            os.mkdir(script_base_dir + os.path.sep + dirname)
        for filename in f_list[dirname].keys():
            # get script file name
            S_xx = os.path.splitext(filename)[0]
            script_filename = S_xx + '.sh'
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
            # logging.info('processing json file : {}'.format(dirname + os.path.sep + filename))
            # logging.debug('start time：' + str(start_time_list[0:5]))
            # logging.debug('end time:' + str(end_time_list[0:5]))
            # logging.debug('speak time:' + str(speak_time[0:5]))
            # get final speaking time zone
            speak_time_final = join_speak_time(speak_time)
            # logging.debug('speak zone final:' + str(speak_time_final[0:5]))
            # get no speaking time zone
            blank_time_zone = get_blank_time(speak_time_final)
            # logging.debug('blank zone:' + str(blank_time_zone[0:5]))
            # write file
            time_len = len(blank_time_zone) + len(speak_time_final)
            ultimate_list = []
            for i in range(len(blank_time_zone)):
                ultimate_list.append(['_noise_', i, blank_time_zone[i]])
            for i in range(len(speak_time_final)):
                ultimate_list.append(['_speech_', i + len(blank_time_zone), speak_time_final[i]])

            # pprint(len(ultimate_list))
            sorting_dict = {}
            for i in range(len(ultimate_list)):
                sorting_dict[ultimate_list[i][1]] = ultimate_list[i][2][0]
            sorting_index = sorted(sorting_dict.items(), key=lambda item: item[1])
            for i in range(len(sorting_index)):
                sorting_index[i] = sorting_index[i][0]
            # pprint(sorting_index)

            real_ultimate_list = guided_sort(sorting_index, ultimate_list)
            # pprint(real_ultimate_list)

            write_command_bash(script_filepath, naming(S_xx), audiodir + '/' + dirname, real_ultimate_list, wav_file_output_dir)


