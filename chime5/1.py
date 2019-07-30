#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2019-07-25 16:57
# @Author  : jacobwu
# @File    : 1.py
import os


 

import os 
def file_path_f(rootDir): 
    list_dirs = os.walk(rootDir) 
    for root, dirs, files in list_dirs:
        for f in files:
            file_path = os.path.join(root, f)
            print(file_path)


file_path_f('audio') 