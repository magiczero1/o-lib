# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/13 20:27
# @Author: shiyi0x7f
from Olib.views import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
def main():
    app = QApplication(sys.argv)
    olib = MainWindow()
    olib.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()