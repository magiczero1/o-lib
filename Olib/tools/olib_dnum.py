# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/9/8 下午6:22
# @Author: shiyi0x7f
import requests
import os
from PyQt5.QtCore import QThread,pyqtSignal
from ..utils.module_config import config_manager
from ..utils.module_log import log
from ..utils.module_env import load_env,load_base_host

env = load_env()
BASE_HOST = load_base_host()

class DnumThread(QThread):
    query_res = pyqtSignal(int)
    def __init__(self):
        super().__init__()

    def run(self):
        n = self.get_down_num()
        self.query_res.emit(n)

    def get_down_num(self):
        if env == "dev":
            url = f'http://{BASE_HOST}/getdnum'
        elif env == "test" or env == "prod" or env is None:
            url = f'https://{BASE_HOST}/getdnum'

        json_data = {
            "remix_id": config_manager.get('remix_id'),
            "remix_key": config_manager.get('remix_key')
        }
        try:
            resp = requests.post(url,json=json_data)
            n = int(resp.text)
            log.success(f"获取下载数量成功{n}")
        except Exception as e:
            log.error(f"获取下载数量失败{e}")
            n = -1
        return n

if __name__ == '__main__':
    n = DnumThread()
    n.get_down_num()
