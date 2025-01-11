# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 20:22
# @Author: shiyi0x7f
# 参数模块
# UI模块
import requests
from PyQt5.QtWidgets import QMainWindow, QSizePolicy
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import Qt
from .config_window_func import ConfigChildWindow
from .donate_window_ui import Ui_Donate_Page
from .disclaimer_window_ui import Ui_Disclaimers
from .main_window_ui import Ui_MainWindow
# 功能模块
from Olib.tools import OlibSearcherV4
from Olib.tools import OlibDownloader3
from Olib.tools import DnumThread
from Olib.utils import config_manager
from Olib.utils import log
from Olib.utils import update_check

import qtawesome as qta
import re
import os
import sys
import random
import time
import webbrowser

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        # 固定用法
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # 初始化参数
        self.page = 1
        self.bid = None
        self.m_dctThread2Download = {}  # 下载线程
        self.down_queue = [] #下载队列

        # 按钮绑定槽函数
        self.queryBtn.clicked.connect(self.query)
        self.bookEdit.returnPressed.connect(self.query)
        # 菜单绑定槽函数
        self.exitBtn.triggered.connect(self.close)
        self.configAction.triggered.connect(self.setting)
        self.aboutAction.triggered.connect(self.about_developer)
        self.websiteAction.triggered.connect(self.navigate_page)
        self.helpAction.triggered.connect(self.help)

        self.preBtn.clicked.connect(self.pre_page)
        self.nextBtn.clicked.connect(self.next_page)
        self.donateBtn.clicked.connect(self.donate)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.doubleClicked.connect(self.double_click)
        # 表格初始化
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["书名", "作者", "年份", "格式", "大小"])
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)

        # 书籍格式 combobox初始化
        self.brBox.addItems(['所有', 'txt', 'pdf','epub','mobi', 'azw', 'azw3'])
        self.brBox.setCurrentIndex(0)
        self.modeBox.addItems(['默认', '热度', '名称', '匹配度', '上传日期', '出版日期'])
        idChange = lambda: self.queryBtn.setEnabled(self.bookEdit.text() != '')
        self.bookEdit.textChanged.connect(idChange)
        idChange()

        self.exitBtn.setIcon(qta.icon('mdi.exit-to-app', scale_factor=1.25))
        self.configAction.setIcon(qta.icon('fa.gear', scale_factor=1.25))
        self.aboutAction.setIcon(qta.icon('fa.info-circle', scale_factor=1.25))
        self.websiteAction.setIcon(qta.icon('mdi.web', scale_factor=1.25))
        self.helpAction.setIcon(qta.icon('mdi.help', scale_factor=1.25))
        self.queryBtn.setIcon(qta.icon('fa.search', scale_factor=1.25))
        self.donateBtn.setIcon(qta.icon('mdi6.hand-heart', scale_factor=1.25))
        self.nextBtn.setIcon(qta.icon('mdi.skip-next-outline', scale_factor=1.25))
        self.preBtn.setIcon(qta.icon('mdi6.skip-previous-outline', scale_factor=1.25))

        self.groupBox.setVisible(False)
        self.proBtn.clicked.connect(self.displayPro)
        self.proBtn.setIcon(qta.icon('fa.chevron-down'))

        self.gitBtn.setIcon(qta.icon('fa.github'))
        self.gitBtn.setText("开源地址")
        self.gitBtn.clicked.connect(self.open_git)

        self.disclaimerBtn.setText("免责声明(必看)")
        self.disclaimerBtn.clicked.connect(self.disclaimer)


        path = config_manager.get('save_path')
        self.pathLB.setText(path)
        self.pathBtn.clicked.connect(self.changePath)

    def open_git(self):
        webbrowser.open("https://github.com/shiyi-0x7f/o-lib")

    def manul_update(self):
        url = config_manager.get('update_url')
        webbrowser.open(url)

    def check_ver_latest(self):
        data = update_check()
        client_ver = config_manager.get('client_ver')
        force = data['force'] #强制更新
        update_url = data['update_url']
        latest_ver = data['latest']
        show = data['show']
        msg = data['msg']
        if show:
            QMessageBox.information(self,"公告",msg)
        if force=="-1":
            sys.exit(-1)

        if client_ver!=latest_ver:
            if str(force) == '1':
                QMessageBox.warning(self,"强制更新","修复重要漏洞，版本强制更新")
                webbrowser.open(update_url)
                return 'force'
            update_choice = config_manager.get('update_choice')
            if update_choice == '1':
                return
            if update_choice == '2':
                utime = config_manager.get('update_time')
                if time.time() - int(utime)<7*24*3600:
                    return
            msg_box = QMessageBox(self)
            msg_box.setText(f"有新版本{latest_ver},是否选择更新？")
            msg_box.setWindowTitle("版本更新")
            yes_btn = msg_box.addButton("立即更新",QMessageBox.YesRole)
            no_btn = msg_box.addButton("暂不更新",QMessageBox.NoRole)
            later_btn = msg_box.addButton("一周后更新",QMessageBox.RejectRole)
            msg_box.exec_()
            if msg_box.clickedButton() == yes_btn:
                webbrowser.open(update_url)
                config_manager.set('update_choice','0')
                exit(0)
            elif msg_box.clickedButton() == no_btn:
                config_manager.set('update_choice', '1')
            elif msg_box.clickedButton() == later_btn:
                config_manager.set('update_choice', '2')
                config_manager.set('update_time', str(int(time.time())))
            config_manager.save()

    def help(self):
        webbrowser.open('https://dquyl9k1r5u.feishu.cn/docx/HdPzd8HOwoWrzRxxdM3ckoYJn6c')

    def displayPro(self):
        if self.groupBox.isVisible():
            self.groupBox.setVisible(False)
            self.resize(self.width(),self.height() - self.groupBox.height() + 2)
            self.proBtn.setIcon(qta.icon('fa.chevron-down'))
        else:
            self.resize(self.width(), self.height() + self.groupBox.height() - 2)
            self.groupBox.setVisible(True)
            self.proBtn.setIcon(qta.icon('fa.chevron-up'))

    def clickDownload(self, downid, bookname, extension,booksize=None):
        save_path = config_manager.get('save_path')
        fileList = os.listdir(save_path)
        filename = f"{bookname}.{extension}"
        if self.skipCheck.isChecked() and filename in fileList:
            self.statusBar().showMessage(f'跳过{filename}，已存在。')
            return
        self.oThreadDownload = OlibDownloader3(downid,bookname=bookname, extension=extension,size=booksize)

        if downid in self.down_queue:
            QMessageBox.warning(self,"下载错误","当前下载任务已在进行中，请勿重复下载")
            del self.oThreadDownload
            return
        self.bid = downid
        self.down_queue.append(downid)
        self.otd = self.oThreadDownload
        self.d_book_name = bookname
        self.oThreadDownload.sig_down_process.connect(self.onUpdateProgress)
        self.oThreadDownload.speed.connect(self.updateSpeed)
        self.oThreadDownload.final.connect(self.downFinal)
        self.oThreadDownload.sig_start.connect(self._set_down_items)
        self.oThreadDownload.start()

    def _set_down_items(self,sig):
        if sig:
            iRow = self.tableWidgetDownload.rowCount()
            self.m_dctThread2Download[iRow] = self.otd
            self.tableWidgetDownload.setRowCount(iRow + 1)
            pItem = QTableWidgetItem(self.d_book_name)
            self.tableWidgetDownload.setItem(iRow, 0, pItem)
            pItem = QProgressBar()
            pItem.setValue(0)
            self.tableWidgetDownload.setCellWidget(iRow, 1,pItem)
            pItem = QTableWidgetItem("0KB/s")
            self.tableWidgetDownload.setItem(iRow, 2, pItem)
            self.statusBar().showMessage(f"开始下载{self.d_book_name}，请前往下载页查看。")

    def get_dnum(self):
        self.DT = DnumThread()
        self.DT.query_res.connect(self.update_down_num)
        self.DT.start()

    def update_down_num(self,n):
        config_manager.set('dnum', n)
        config_manager.set('gdntime', f'{int(time.time())}')
        config_manager.save()
        if n > 0:
            return n
        else:
            QMessageBox.warning(self, "下载上限","该账号今日下载数量已达上限，请明日再试或切换remix_key和remix_id。")
            self.statusbar.showMessage("今日下载数量已达上限，请明日再试")
            if self.bid in self.down_queue:
                self.down_queue.remove(self.bid)
            return

    def downFinal(self, sig):
        if sig==1:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("下载完毕")
            msg_box.setText("书籍下载完毕了哦~")
            yes_btn = msg_box.addButton("支持一下",QMessageBox.YesRole)
            #todo
            #关闭会异常打开书架
            no_btn = msg_box.addButton("打开书架",QMessageBox.NoRole)
            msg_box.exec_()
            if msg_box.clickedButton() == yes_btn:
                self.donate()
            elif msg_box.clickedButton() == no_btn:
                os.startfile(config_manager.get('save_path'))
        elif sig==0:
            self.get_dnum()
        else:
            QMessageBox.warning(self, "下载失败","请检查每一项remix_xxx是否填写正确！")

    # 进度更新
    def onUpdateProgress(self, oThread, iProgress):
        for iRow, self.oThreadDownload in self.m_dctThread2Download.items():
            if oThread == self.oThreadDownload:
                self.tableWidgetDownload.cellWidget(iRow, 1).setValue(iProgress)

    def updateSpeed(self, oThread, speed_):
        for iRow, self.oThreadDownload in self.m_dctThread2Download.items():
            if oThread == self.oThreadDownload:
                pItem = QTableWidgetItem(f"{speed_}KB/s")
                self.tableWidgetDownload.setItem(iRow, 2, pItem)

    def navigate_page(self):
        QMessageBox.warning(self,"网站挂了","导航站已经挂了。")

    def about_developer(self):
        webbrowser.open("https://space.bilibili.com/19276680")

    def disclaimer(self):
        self.a = QDialog()
        self.dw = Ui_Disclaimers()
        self.dw.setupUi(self.a)
        self.a.show()

    def donate(self):
        self.a = QDialog()
        self.dw = Ui_Donate_Page()
        self.dw.setupUi(self.a)
        self.a.setWindowIcon(qta.icon('ei.heart-alt'))
        self.a.show()

    # 用户设置配置方法
    def setting(self):
        QMessageBox.warning(self,"限时版本","当前为限时开放版本，不需要配置，请您测试其他功能是否正常。")

    def set_account(self, user_data):
        if user_data is not None:
            self.statusBar().showMessage(f"配置设置成功")
            self.setting.close()


    def changePath(self):
        save_path = config_manager.get('save_path')
        path = QFileDialog.getExistingDirectory(self, '选择下载目录', save_path)
        if path:
            log.success(f"修改下载路径成功{path}")
            config_manager.set('save_path', value=path)
            config_manager.save()
            self.pathLB.setText(path)

    # 查询书籍
    def query(self):
        '''
        todo
        增加校验，如果没有remix数据，不允许搜索。？？
        是否增加违禁词检测。。如果有违禁词检测，就不校验remix。
        违禁词检测，尤其是涉政，限制下载和功能。
        '''
        bookname = self.bookEdit.text()
        accrate_ = "1" if self.accurateCheck.isChecked() else None
        modes = {'默认': None, '热度': 'popular', '匹配度': 'bestmatch', '名称': 'title', '上传日期': 'date',
                 '出版日期': 'year'}
        extens = {'所有': None,'txt':'txt', 'pdf':'pdf', 'epub':'epub', 'mobi':'mobi','azw':'azw', 'azw3':'azw3'}
        mode_ = modes[self.modeBox.currentText()]
        ext = extens[self.brBox.currentText()]
        log.info(f"search {bookname} {mode_} {ext}")
        self.getbooks = OlibSearcherV4(bookname,page=self.page,order=mode_,extensions=ext,e=accrate_)
        self.statusBar().showMessage(f"开始搜索{bookname}......")
        self.getbooks.success.connect(self.show_book)
        self.getbooks.start()

    def pre_page(self):
        pre_page = self.getbooks.pagination.get('before')
        if not pre_page:
            QMessageBox.warning(self, "页码错误","当前已是第一页")
            return
        log.info(f"上一页{pre_page}")
        self.getbooks.page = pre_page
        self.getbooks.start()

    def next_page(self):
        next_page = self.getbooks.pagination.get('next')
        if not next_page:
            QMessageBox.warning(self, "页码错误","当前已是最后一页")
            return
        log.info(f"下一页{next_page}")
        self.getbooks.page = next_page
        self.getbooks.start()

    def show_book(self, books):
        self.label_4.setText("小程序【拾壹工具箱】")
        self.books_list = books

        if type(books) is not list:
            log.error(f"书籍展示异常{type(books)}")
            QMessageBox.warning(self,"书籍展示异常","书籍显示异常，请联系作者进行修复")
            return

        log.info(f"收到书籍{len(books)}本")
        if books is None:
            item_title = QTableWidgetItem("本次搜索无结果，请重新尝试，或者换一本书进行搜索。")
            self.tableWidget.setRowCount(1)
            self.tableWidget.setItem(0, 0, item_title)
        else:
            self.statusbar.showMessage("搜索成功")
            current_page = self.getbooks.pagination.get('current')
            total_pages = self.getbooks.pagination.get('total_pages')
            self.pageLabel.setText(f"{current_page}/{total_pages}页")
            self.tableWidget.setRowCount(len(books))
            self.reset_bookview_size()
            for row in range(len(books)):
                title = books[row]['title']
                author = books[row]['author']
                year = books[row]['year']
                extension = books[row]['file_type']
                filesize = books[row]['file_size']

                item_title = QTableWidgetItem(title)
                item_year = QTableWidgetItem(year)
                item_extension = QTableWidgetItem(extension)
                item_size = QTableWidgetItem(filesize)
                item_author = QTableWidgetItem(author)

                self.tableWidget.setItem(row, 0, item_title)
                self.tableWidget.setItem(row, 1, item_author)
                self.tableWidget.setItem(row, 2, item_year)
                self.tableWidget.setItem(row, 3, item_extension)
                self.tableWidget.setItem(row, 4, item_size)
            self.tableWidget.setWordWrap(True)
            self.tableWidget.resizeRowsToContents()
        self.search_state = 0

    def double_click(self):
        index = self.tableWidget.currentRow()
        thumb_nail = self.books_list[index].get('thumbnail')
        if thumb_nail is not None and thumb_nail !='/img/cover-not-exists.png':
            resp = requests.get(thumb_nail)
            if resp.status_code == 200:
                img = QImage.fromData(resp.content)
                dock = QDockWidget(self.tableWidget)
                label = QLabel()
                label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                dock.setWidget(label)
                label.setPixmap(QPixmap.fromImage(img))
                dock.show()

    def clear_book_view(self):
        self.tableWidget.setRowCount(20)
        self.reset_bookview_size()
        for row in range(20):
            item_title = QTableWidgetItem("")
            item_year = QTableWidgetItem("")
            item_extension = QTableWidgetItem("")
            item_size = QTableWidgetItem("")
            item_author = QTableWidgetItem("")
            self.tableWidget.setItem(row, 0, item_title)
            self.tableWidget.setItem(row, 1, item_author)
            self.tableWidget.setItem(row, 2, item_year)
            self.tableWidget.setItem(row, 3, item_extension)
            self.tableWidget.setItem(row, 4, item_size)

    def generateMenu(self, pos):
        # 获取点击行号，书籍序号
        path = config_manager.get('save_path')
        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()
        try:
            bookurl = self.books_list[row_num]['bookurl']
        except:
            return
        # 使用正则表达式提取所需的部分
        match = re.search(r'/\d+/[a-f0-9]+', bookurl)
        # 获取匹配结果
        downid = match.group(0) if match else None
        title = self.books_list[row_num]['title']
        extension = self.books_list[row_num]['file_type']
        preview = self.books_list[row_num]['readOnlineUrl']
        booksize = self.books_list[row_num]['size']

        if row_num < 500:  # 表格生效的行数，501行点击右键，不会弹出菜单
            menu = QMenu()  # 实例化菜单
            item1 = menu.addAction(u"开始下载")
            item1.setIcon(qta.icon('ph.download'))
            item2 = menu.addAction(u"打开下载文件夹")
            item2.setIcon(qta.icon('fa.folder-open-o'))
            item3 = menu.addAction(u"在线预览")
            item3.setIcon(qta.icon('msc.open-preview'))
            item_push_to_wxread = menu.addAction(u"推送到微信读书")
            item_push_to_wxread.setIcon(qta.icon('fa5b.weixin'))
            item_koodo = menu.addAction(u"koodo云书架")
            item_koodo.setIcon(qta.icon('mdi.web-box'))
            item_help = menu.addAction(u"使用帮助")
            item_help.setIcon(qta.icon('mdi.help'))
            # item_query_num = menu.addAction(u"查询今日下载余量")
            # item_query_num.setIcon(qta.icon('fa5b.searchengin'))
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
        else:
            return

        if action == item1:
            remix_key = config_manager.get('remix_key')
            if not remix_key:
                config_manager.set('remix_key', "123")
                config_manager.set('remix_id', "456")
                config_manager.save()
            self.statusBar().showMessage(f"正在获取{title}下载链接......请耐心等待")
            self.clickDownload(downid, title, extension,booksize)
        elif action == item2:
            log.info("打开文件夹")
            os.startfile(config_manager.get('save_path'))
        elif action == item3:
            try:
                with requests.get(preview,timeout=3) as resp:
                    if resp.status_code != 200:
                        QMessageBox.warning(self.tableWidget,'预览错误',"预览网址受限，无法正常预览~")
                        return
            except Exception as e:
                QMessageBox.warning(self.tableWidget,'预览错误',"预览网页不可用，请使用其他功能~")
                return


            if not preview:
                QMessageBox.warning(self, "预览错误","预览失败，请尝试其他内容。")
            else:
                key = config_manager.get("remix_key")
                id_ = config_manager.get("remix_id")
                if not key or not id_ or len(key) < 10:
                    preview += f'&user_id=38713159&user_key=5dcc5da2ccd3f344c0c66a17c33349cf'
                else:
                    preview += f'&user_id={id_}&user_key={key}'
                webbrowser.open(preview)
        elif action == item_help:
            self.help()
        else:
            return

    def reset_bookview_size(self):
        width = self.tableWidget.size().width()
        rate1 = 320 / 674
        rate2 = 80 / 674
        self.tableWidget.setColumnWidth(0, int(width * rate1))
        self.tableWidget.setColumnWidth(1, int(width * rate2))
        self.tableWidget.setColumnWidth(2,int(width * rate2))
        self.tableWidget.setColumnWidth(3, int(width * rate2))
        self.tableWidget.setColumnWidth(4, int(width * rate2))


def main():
    app = QApplication(sys.argv)
    zlib = MainWindow()
    zlib.show()
    sys.exit(app.exec_())


# 主函数
if __name__ == '__main__':
    # PyQt5的固定用法
    app = QApplication(sys.argv)
    olib = MainWindow()
    olib.show()
    sys.exit(app.exec_())

