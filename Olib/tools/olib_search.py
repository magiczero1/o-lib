# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 20:20
# @Author: shiyi0x7f
# get请求线程类
from PyQt5.QtCore import pyqtSignal,QThread,QMutex
from dotenv import load_dotenv
import os
import time
import requests
from ..utils.module_config import config_manager
from ..utils.module_log import log
from ..utils.module_env import load_env,load_base_host

env = load_env()
BASE_HOST = load_base_host()

search_lock = QMutex()
class OlibSearcherV4(QThread):  # 线程1
    '''
    v4版本
    增加更多筛选参数
    '''
    success = pyqtSignal(object)
    def __init__(self,bookname,languages=None,extensions=None,page=None,order="bestmatch",limit="100",e=None,yearFrom=None,yearTo=None):
        super(OlibSearcherV4, self).__init__()
        self.page = page
        self.bookname = bookname
        self.languages = languages
        self.extensions = extensions
        self.order = order
        self.limit = limit
        self.e = e
        self.yearFrom = yearFrom
        self.yearTo = yearTo
        self.pagination = dict()


    def run(self):
        search_lock.lock()
        start = time.time()
        data = self.book_from_my_api()
        if data['status'] == 0:
            self.success.emit(0)
        elif data['status'] == 1:
            log.info(f"列表获取成功，耗时{time.time() - start:.2f}")
            books_list = data['books_list']
            self.success.emit(books_list)
        elif data['status'] == -1:
            self.success.emit(-1)
        search_lock.unlock()


    def book_from_my_api(self):
        if env == "dev":
            url = f'http://{BASE_HOST}/getbooks'
        elif env == "test" or env == "prod" or env is None:
            url = f'https://{BASE_HOST}/getbooks'
        json_data = {
            "bookname": self.bookname,
            "page": self.page,
            "languages": self.languages,
            "extensions": self.extensions,
            "order": self.order,
            "limit": self.limit,
            "e": self.e,
            "yearFrom": self.yearFrom,
            "yearTo": self.yearTo
        }
        books_list = []
        resp = requests.post(url,json=json_data)
        log.info(f"从服务端接收到数据")
        data = resp.json()

        res = {}
        try:
            books = data['books']
            if len(books) == 0:
                res['status'] = 0
                return res
            else:
                self.pagination = data['pagination']
                log.info(f"加载分页{self.pagination}")
                for b in books:
                    book = {}
                    book['title'] = b.get('title')
                    book['bookurl'] = b.get('href')
                    book['language'] = b.get('language')
                    book['file_size'] = b.get('filesizeString')
                    book['thumbnail'] = b.get('cover')
                    book['publisher'] = b.get('publisher')
                    book['author'] = b.get('author')
                    book['year'] = b.get('year')
                    book['file_type'] = b.get('extension')
                    book['readOnlineUrl'] = b.get('readOnlineUrl')
                    book['dl'] = b.get('dl')
                    book['size'] = b.get('filesize',None)
                    books_list.append(book)
                log.success(f"{BASE_HOST}获取数据成功")
                res['status'] = 1
                res['books_list'] = books_list
        except Exception as e:
            log.error(f"{BASE_HOST}获取数据失败{e}")
            res['status'] = -1
        return res
