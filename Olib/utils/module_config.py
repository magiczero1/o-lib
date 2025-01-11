# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/6/3 下午10:46
# @Author: shiyi0x7f
from configparser import ConfigParser
from .module_log import log
from .module_env import load_base_host
from dotenv import load_dotenv
import os

load_dotenv()
env = os.getenv("ENV")
if env == "dev":
    EXE_MODE = 0
    log.info("开发模式")
else:
    EXE_MODE = 1
    log.info("运行模式")

VERSION = '1.0.9'
class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.config = ConfigParser()
        if not os.path.exists(filename):
            self.config_init()
        self.config.read(self.filename)
        self.version_check()
    def version_check(self):
        if not self.has_option('client_ver'):
            self.set('client_ver',VERSION)
            self.save()
        if self.get('client_ver') != VERSION:
            self.set('client_ver',VERSION)
            self.save()


    def config_init(self):
        defaults = {
            'client_ver':VERSION,
            'latest_ver':'',
            'update_choice':'',
            'time': '',
            'dnum':'0',
            'remix_key': '',
            'remix_id': '',
            'save_path': os.getcwd(),
            'update_time':''
        }
        for key, value in defaults.items():
            self.set(key, value)
        self.save()

    def get(self, option,section='default'):
        if not self.has_option(option):
            self.set(option,'0')
        return self.config.get(section, option)

    def set(self, option=None,value=None,section='default'):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def remove_option(self, option, section='default'):
        if self.config.has_section(section):
            self.config.remove_option(section, option)

    def remove_section(self, section='default'):
        self.config.remove_section(section)

    def has_option(self,option, section='default'):
        return self.config.has_option(section, option)

    def has_section(self, section='default'):
        return self.config.has_section(section)

BASE_DIR =os.getcwd() if EXE_MODE else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log.info(f"当前主文件夹{BASE_DIR}")
# 创建全局的 config_manager 实例
config_manager = ConfigManager(os.path.join(BASE_DIR,'configo.ini'))
if not config_manager.has_option('BASE_DIR'):
    config_manager.set('BASE_DIR',BASE_DIR)
    config_manager.save()

if __name__ == '__main__':
    # 使用示例
    s = config_manager.get('base_host')

