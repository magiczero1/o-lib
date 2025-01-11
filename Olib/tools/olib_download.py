# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 22:39
# @Author: shiyi0x7f
from PyQt5.QtCore import QThread,pyqtSignal,QMutexLocker,QMutex
import time
import requests
import os
import re
from ..utils.module_config import config_manager
from ..utils.module_log import log
from ..utils.module_env import load_env,load_base_host

env = load_env()
BASE_HOST = load_base_host()

class OlibDownloader3(QThread):
    sig_down_process = pyqtSignal(QThread,int)  # 下载量信号 list: value flag
    speed = pyqtSignal(QThread,float)
    final = pyqtSignal(int) #是否下载完毕
    sig_start = pyqtSignal(bool) #是否开始下载
    def __init__(self,bookid,bookname,extension,size=None):
        self.mutex = QMutex()
        super().__init__()
        self.bookid = bookid
        self.name = bookname.replace(':',"")
        self.extension = extension
        self.base_url = config_manager.get('base_url')
        self.path = config_manager.get('save_path')
        self.remix_id = config_manager.get('remix_id')
        self.remix_key = config_manager.get('remix_key')
        self.size = size

    def get_durl(self):
        api_url = f'https://{BASE_HOST}/gd'
        json_data={
            "remix_id":self.remix_id,
            "remix_key":self.remix_key,
            "bookid":self.bookid
        }
        resp = requests.post(api_url,json=json_data)
        return resp.json()


    def run(self):#run中不带返回值
        locker = QMutexLocker(self.mutex)
        data = self.get_durl()
        status = data['status']
        try:
            durl = data['durl']
            response = requests.get(durl,stream=True)
            self.sig_start.emit(True)
            chunk_size = 1024
            read = 0
            #修正命名异常
            the_filename = self.name
            sets = ['/', '\\', ':', '*', '?', '"', '<', '>','|','&','#','@','!','-','+','=']
            for char in the_filename:
                if char in sets:
                    the_filename = the_filename.replace(char, '')

            the_filename+=f'.{self.extension}'
            the_sourceFile = os.path.join(os.path.abspath(self.path),the_filename)
            with open(the_sourceFile, 'ab') as f:
                file_size = int(self.size) if self.size else int(response.headers.get('content-length', 0))
                start_time = time.time()
                if file_size == 0:
                    log.error(f"获取文件大小失败{0}")
                    file_size = 1

                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    read += chunk_size
                    read = min(read,file_size)
                    current_time = time.time()+1
                    dspeed =read//1024/(current_time-start_time)
                    if current_time-start_time>1:
                        self.speed.emit(self,round(dspeed,2))
                    self.progressToEmit(int(read / file_size * 100))
            response.close()
            self.final.emit(1)
        except Exception as e:
            print(data)
            log.error(f"下载失败,错误代码{status}")
            self.final.emit(status)
        finally:
            del locker

    def progressToEmit(self, iProgress):
        self.sig_down_process.emit(self, iProgress)


