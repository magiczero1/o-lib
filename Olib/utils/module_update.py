# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/6/14 上午10:15
# @Author: shiyi0x7f
import requests
from .module_config import config_manager
from .module_log import log
from .module_env import load_base_host,load_env
BASE_HOST = load_base_host()
env = load_env()
def update_check():
    ver = config_manager.get("client_ver")
    if env == "dev":
        url = f'http://{BASE_HOST}/latest'
    else:
        url = f'https://{BASE_HOST}/latest'
    data = requests.get(url).json()
    latest_ver = data['latest']
    update_url = data['update_url']
    config_manager.set("latest_ver", latest_ver)
    config_manager.set("update_url", update_url)
    config_manager.save()
    log.info(f"当前版本{ver},最新版本{latest_ver}")
    return data

