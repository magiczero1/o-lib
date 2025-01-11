# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/9/17 下午9:28
# @Author: shiyi0x7f
from dotenv import load_dotenv
import os
from loguru import logger

def load_env():
    load_dotenv()
    env = os.getenv("ENV")
    return env
def load_base_host():
    env = load_env()
    if env == "dev":
        BASE_HOST = os.getenv("DEV_API")
        logger.info(f"使用开发API")
    elif env == "test":
        BASE_HOST = os.getenv("TEST_API")
        logger.info(f"使用测试API")
    else:
        BASE_HOST = "free.olib.online"
        logger.info(f"使用标准API")
    return BASE_HOST

if __name__ == '__main__':
    env = load_base_host()
    print(env)