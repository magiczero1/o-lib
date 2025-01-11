# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 22:42
# @Author: shiyi0x7f
import webbrowser
import requests
import qtawesome as qta
from PyQt5.QtWidgets import QMessageBox,QDialog
from PyQt5.QtCore import pyqtSignal
from .config_window_ui import Ui_Dialog
from Olib.utils import log
from Olib.utils import config_manager
from Olib.utils import load_base_host

BASE_HOST = load_base_host()
#配置子窗口

class ConfigChildWindow(QDialog,Ui_Dialog):
    user_data = pyqtSignal(object)
    def __init__(self):
        super(ConfigChildWindow, self).__init__()
        self.setupUi(self)
        self.dnumBtn.clicked.connect(self.api_validator)
        self.howBtn.clicked.connect(self.get_key_id)
        self.configBtn.clicked.connect(self.setting_config)
        txtChange = lambda: self.configBtn.setEnabled(self.keyEdit.text() != '' and self.idEdit.text() != '')
        self.keyEdit.textChanged.connect(txtChange)
        self.idEdit.textChanged.connect(txtChange)
        self.setWindowIcon(qta.icon('ri.settings-4-line'))
        try:
            key_ = config_manager.get("remix_key")
            id_ = config_manager.get("remix_id")
            if len(key_)<len(id_):
                key_,id_ = id_,key_
            self.keyEdit.setText(key_)
            self.idEdit.setText(id_)
        except KeyError:
            log.error("配置加载失败")

    def get_key_id(self):
        webbrowser.open('https://dquyl9k1r5u.feishu.cn/docx/HdPzd8HOwoWrzRxxdM3ckoYJn6c')
        self.user_data.emit(None)

    def setting_config(self):
        valid = self.key_id_validator()
        if not valid:
            return

        key_ = config_manager.get("remix_key")
        id_ = config_manager.get("remix_id")
        key_text = self.keyEdit.text()
        id_text = self.idEdit.text()
        if len(key_text) < len(id_text):
            key_text,id_text = id_text,key_text

        if key_text != key_:
            config_manager.set("remix_key", key_text)
        if id_text != id_:
            config_manager.set("remix_id", id_text)
        config_manager.save()
        log.success("配置设置成功")
        self.close()

    def key_id_validator(self):
        act_text = self.keyEdit.text()
        pwd_text = self.idEdit.text()
        if act_text.replace(" ","") == "" or pwd_text.replace(" ","") == "":
            QMessageBox.warning(self,"空值","请勿输入空值")
        elif "remix" in act_text.lower() or "remix" in pwd_text.lower():
            QMessageBox.warning(self, "格式错误","请输入【等号】后面的部分，比如remix_key=abc,只填abc")
            return False
        return True

    def api_validator(self):
        self.key_id_validator()
        if env == "dev":
            url = f"http://{BASE_HOST}/getnum"
        else:
            url = f"https://{BASE_HOST}/getnum"
        json_data = {
            "remix_id": self.idEdit.text(),
            "remix_key": self.keyEdit.text()
        }
        dnum = requests.post(url,json=json_data)
        if str(dnum.text) == "-1":
            QMessageBox.warning(self,"配置错误","key和id配置错误，请查看教程进行获取")
        else:
            QMessageBox.information(self, "配置正确",f"欢迎使用Olib,当前余量{dnum.text}")

if __name__ == '__main__':
    pass