#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2019-07-25 16:57
# @Author  : jacobwu
# @File    : 1.py
import os
from pprint import pprint


def file_path_f(rootDir):
    file_path = {}
    for root_folder, dirs_folder, folder in os.walk(rootDir):
        if root_folder != rootDir:
            dict_single_folder = {}
            folder_n = root_folder.split("/")[1]
            for f in folder:
                dict_single_folder[f] = f[:7]
            file_path[folder_n] = dict_single_folder
    return file_path


def get_key(dict, value):
    return [k for k, v in dict.items() if v == value]


f = file_path_f('audio')
a = []

for key in f:
    key_v = get_key(f[key], 'S02_P05')
    if len(key_v):
        a.append(key_v)
pprint(a[0])
