# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/6/9 上午10:01
# @Author: shiyi0x7f
from loguru import logger
class Log():
    def __init__(self):
        super().__init__()
        self.log = logger
    def info(self, message):
        self.log.info(message)
    def debug(self, message):
        self.log.debug(message)
    def error(self, message):
        self.log.error(message)
    def warning(self, message):
        self.log.warning(message)
    def success(self, message):
        self.log.success(message)
    def add(self,path,level,rotation):
        self.log.add(path,level=level,rotation=rotation)
log = Log()
if __name__ == '__main__':
    logger.info(f"日志模块")