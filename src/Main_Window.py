from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor

from Main_Window_ui import *
from Dialog_Manual import *


import json
import os
import sys
import time
import copy

APP_FOLDER_PATH = os.getcwd()
# APP_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(APP_FOLDER_PATH, '.WorkingTimer_(Dont_Delete)')

DATA_DEFAULT = {}
HEADER = ['次数', '开始时间', '结束时间', '工时', '周工时', '月工时']
COLOR_LIST = ['#0096ff', '#FF8343', '#F1DEC6']
COLOR_WEEK_LIST = ['#B7E0FF', '#FFF5CD', '#FFCFB3', '#E78F81']


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_parameter()
        self.init_ui()
        self.init_signal_connections()

    def init_parameter(self):
        self.init_data()
        self.timer = QTimer()

    def init_ui(self):
        self.setWindowIcon(self.icon_setup_from_svg(WIN_ICON))
        self.setWindowTitle('Working Timer')

        self.setStyleSheet("""
                            QWidget[objectName="centralwidget"]{
                                background-color: #10375C;
                            }
                            QLabel{
                                color: #DDDDDD;
                                font: 14px "黑体";
                            }
                            QPushButton[objectName="pb_add_manual"], QPushButton[objectName="pb_export"]{
                                font:16px '黑体';
                            }
                            QTreeWidget{
                                background-color: #DDDDDD;
                            }
                            QComboBox{
                                font: 18px  '黑体';
                                color: rgb(19, 24, 66);
                                border: 0px solid;
                                border-radius: 10px;
                                background-color: rgb(251, 246, 226);
                            }
                            QComboBox::drop-down {
                                subcontrol-origin: padding;
                                subcontrol-position: top right;
                                border-left-width: 1px;
                                border-left-style: solid;
                                border-top-right-radius: 3px;
                                border-bottom-right-radius: 3px;
                            }
                            QComboBox QAbstractItemView {
                                color: #DDDDDD;
                                background-color: #10375C;
                                border: None;
                                selection-background-color: #FF8343;
                                selection-color: rgb(19, 24, 66);
                                padding: 5px;
                            }
                            """)
        self.treeWidget.setColumnCount(len(HEADER))
        self.treeWidget.setHeaderLabels(HEADER)
        self.treeWidget.setColumnWidth(0, 50)
        self.treeWidget.setColumnWidth(1, 170)
        self.treeWidget.setColumnWidth(2, 170)
        self.plainTextEdit.setStyleSheet("""
                                         font: 20px "幼圆";
                                         padding: 10px;
                                         background-color: #b0f1ff;
                                         border: None;
                                         border-radius:10px
                                         """)
        self.pb_start.setStyleSheet("""
                                    font: 20px "幼圆";
                                    font-weight:bold;
                                    background-color: #3cc800;
                                    color: #000000;
                                    border: None;
                                    border-radius:10px
                                    """)
        self.pb_end.setStyleSheet("""
                                  font: 20px "幼圆";
                                  font-weight:bold;
                                  background-color: #ee2d00;
                                  color: #FFFFFF;
                                  border: None;
                                  border-radius:10px
                                  """)
        self.pb_start.setCursor(Qt.PointingHandCursor)
        self.pb_end.setCursor(Qt.PointingHandCursor)
        self.pb_add_manual.setCursor(Qt.PointingHandCursor)
        self.display_data()

    def init_signal_connections(self):
        self.pb_start.clicked.connect(self.record_start_time_auto)
        self.pb_end.clicked.connect(self.record_end_time_auto)
        self.timer.timeout.connect(self.update_time)
        self.pb_add_manual.clicked.connect(self.dialog_manual_add_time)
        self.comboBox.currentIndexChanged.connect(self.on_combobox_change)

    def init_data(self):
        if not os.path.exists(DATA_FILE_PATH):
            self.data = DATA_DEFAULT
            self.write_data()
        else:
            self.read_data()
