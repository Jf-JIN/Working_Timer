

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QTreeWidgetItem, QMessageBox, QInputDialog, QListView
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QColor, QMouseEvent

from Main_Window_ui import *
from Dialog_Manual import *
from Inner_Decorators import try_except_log
from Message_Notification import MessageNotification


import json
import os
import sys
from inspect import getmembers, isfunction
from time import localtime, strftime, time
from copy import deepcopy
from xlsxwriter import Workbook


APP_FOLDER_PATH = os.getcwd()
# APP_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(APP_FOLDER_PATH, '.WorkingTimer_(Dont_Delete)')
DATA_EXCEL_PATH = os.path.join(APP_FOLDER_PATH, f'WorkingTimer_{datetime.now().strftime("%Y%m%d-%H%M%S")}.xlsx')


HEADER = ['次数', '开始时间', '结束时间', '工时', '周工时', '月工时']
COLOR_LIST = ['#0096ff', '#FF8343', '#F1DEC6']
COLOR_WEEK_LIST = ['#B7E0FF', '#FFF5CD', '#FFCFB3', '#E78F81']


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_parameter()
        self.init_ui()
        self.init_signal_connections()

    def init_parameter(self) -> None:
        self.message_box = QMessageBox(self)
        for name, method in getmembers(self, predicate=isfunction):
            decorated_method = try_except_log(message_box=self.message_box)(method)
            setattr(self, name, decorated_method)
        self.init_data()
        self.message_notification = MessageNotification(self, position='bottom', offset=40, move_in_point=(None, '+40'), hold_duration=3000)
        self.timer = QTimer()
        self.blick_timer = QTimer()
        self.blick_timer.start(1000)
        self.comboBox.view().setContextMenuPolicy(Qt.CustomContextMenu)
        self.comboBox.view().viewport().installEventFilter(self)
        self.comboBox.view().customContextMenuRequested.connect(self.show_context_menu)

    def init_ui(self) -> None:
        self.setWindowIcon(self.icon_setup_from_svg(WIN_ICON))
        self.setWindowTitle('Working Timer')
        self.setStyleSheet("""
                            QWidget[objectName="centralwidget"]{
                                background-color: #10375C;
                            }
                            QDialog{
                                background-color: #10375C;
                            }
                            QLabel{
                                font: 14px "黑体";
                            }
                            QWidget[objectName="widget_left"] QLabel, QWidget[objectName="widget_right"] QLabel, QDialog QLabel{
                                color: #DDDDDD;
                                font: 14px "黑体";
                            }
                            QPushButton[objectName="pb_add_manual"], QPushButton[objectName="pb_export"]{
                                font:16px '黑体';
                            }
                            QTreeWidget{
                                background-color: #DDDDDD;
                            }
                            QHeaderView {
                                font: 16px "黑体";
                                color: #000000;
                            }
                            QComboBox{
                                font: 18px  '黑体';
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
                                background-color: #10375C;
                                border: None;
                                selection-background-color: #b0f1ff;
                                selection-color: #000000;
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
        self.pb_add_item.setIcon(self.icon_setup_from_svg(ADD_ICON))
        self.pb_start.setCursor(Qt.PointingHandCursor)
        self.pb_end.setCursor(Qt.PointingHandCursor)
        self.pb_add_manual.setCursor(Qt.PointingHandCursor)
        self.init_comboBox()
        self.display_data()

    def init_signal_connections(self) -> None:
        self.timer.timeout.connect(self.update_time)
        self.blick_timer.timeout.connect(self.blick_font_by_1s)
        self.pb_start.clicked.connect(self.record_start_time_auto)
        self.pb_end.clicked.connect(self.record_end_time_auto)
        self.pb_add_manual.clicked.connect(self.dialog_manual_add_time)
        self.pb_add_item.clicked.connect(self.add_new_item_from_dialog)
        self.pb_export.clicked.connect(self.export_excel)
        self.comboBox.currentIndexChanged.connect(self.display_data)

    def init_data(self) -> None:
        if not os.path.exists(DATA_FILE_PATH):
            self.data = DATA_DEFAULT
            self.write_data()
        else:
            self.read_data()

    def init_comboBox(self):
        self.comboBox.clear()
        self.comboBox.addItems(self.data.keys())

    def eventFilter(self, source, event) -> bool:
        if source == self.comboBox.view().viewport():
            if event.type() == QMouseEvent.MouseButtonPress and event.button() == Qt.RightButton:
                index = self.comboBox.view().indexAt(event.pos()).row()
                if index != -1:
                    self.show_context_menu(event.pos())
                    return True
        return super().eventFilter(source, event)

    def dialog_manual_add_time(self) -> None:
        """
        手动添加对话框时间的方法.
        用于打开一个对话框, 允许用户手动输入时间信息. 用户输入的时间信息将被用于记录开始时间和结束时间.
        对话框只返回一个字典, 包含开始时间、结束时间、内容等信息. 该字典不等同于self.data
        字典结构为: {
            分类名: {
                start_time:
                start_timestamp:
                ...
            }
        }

        参数:
            无

        返回:
            无
        """
        self.dialog_manual_add = DialogManual(self)
        if self.dialog_manual_add.exec_() == QDialog.Accepted:
            dict_time = self.dialog_manual_add.get_data()
            for key, value in dict_time.items():
                self.record_start_time(
                    ccb_item_name=key,
                    start_time=value['start_time'],
                    start_timestamp=value['start_timestamp'],
                    month=value['month'],
                    week=value['week'],
                    content=value['content']
                )
                self.record_end_time(
                    ccb_item_name=key,
                    start_timestamp=value['start_timestamp'],
                    end_time=value['end_time'],
                    end_timestamp=value['end_timestamp'])
            self.write_data()
            self.display_data()

    def display_data(self) -> None:
        """
        显示数据的方法. 
        根据当前选择的ccb_item_name, 显示相应的数据. 如果ccb_item_name为空或者不在数据中, 或者数据为空, 则清空所有显示内容并隐藏按钮. 否则, 根据数据的状态进行相应的显示. 

        参数: 
            无

        返回: 
            无
        """
        self.ccb_item_name = self.comboBox.currentText()
        self.update_combobox_item()
        if self.ccb_item_name == '' or self.ccb_item_name not in self.data or self.data == {}:
            self.treeWidget.clear()
            self.plainTextEdit.clear()
            self.lb_start_time.clear()
            self.lb_duration.clear()
            self.pb_start.hide()
            self.pb_end.hide()
            return
        else:
            self.display_data_in_treewiget(self.data[self.ccb_item_name]['data'])
        # 准备就绪, 可以计时
        if self.data[self.ccb_item_name]['status'] == 'end':
            self.timer.stop()
            self.lb_start_time.clear()
            self.plainTextEdit.clear()
            self.pb_start.show()
            self.pb_end.hide()
        # 正在计时, 等待停止
        else:
            self.timer.start(1000)
            self.lb_duration.clear()
            self.plainTextEdit.clear()
            self.lb_start_time.setText(self.data[self.ccb_item_name]['data'][str(len(self.data[self.ccb_item_name]['data']))]['start_time'][0])
            self.pb_start.hide()
            self.pb_end.show()

    def display_data_in_treewiget(self, data: dict) -> None:
        """
        在树形控件中显示数据的方法. 
        根据传入的数据字典, 在树形控件中显示相应的数据. 对于每个数据项, 创建一个树形控件的节点, 并设置节点的文本和背景颜色. 

        参数: 
            data (dict): 包含数据的字典, 键为数据项的名称, 值为包含各种时间信息的字典. 

        返回: 
            无
        """
        self.treeWidget.clear()
        temp = deepcopy(data)
        for key, value in temp.items():
            for i in ['start_time', 'end_time', 'work_time', 'sum_work_time_week', 'sum_work_time_month']:
                if i not in value:
                    value[i] = ['', 0]
            item = QTreeWidgetItem([
                key,
                value['start_time'][0],
                value['end_time'][0],
                value['work_time'][0],
                value['sum_work_time_week'][0],
                value['sum_work_time_month'][0]
            ])
            for i in range(0, len(HEADER)):
                item.setToolTip(i, value['content'])
                item.setBackground(i, QColor(value['color']))
            item.setBackground(4, QColor(value['color_week']))
            self.treeWidget.addTopLevelItem(item)

    def update_time(self) -> None:
        """
        更新时间的方法. 
        用于更新持续时间的显示. 根据当前选择的ccb_item_name, 获取最新的开始时间和结束时间, 并计算时间差. 将时间差转换为小时、分钟和秒, 并更新持续时间的文本显示. 

        参数: 
            无

        返回: 
            无
        """
        item = self.data[self.ccb_item_name]['data']
        start_timestamp = item[str(len(item))]['start_time'][1]
        end_timestamp = self.get_time()[1]
        list_time = self.calculate_time_diff(start_timestamp=start_timestamp, end_timestamp=end_timestamp)
        hour, min, sec = [f'{item:02d}' for item in list_time[:3]]
        self.lb_duration.setText(f'{hour}: {min}: {sec}')

    def read_data(self) -> None:
        """
        读取数据的方法. 
        用于从文件中读取数据, 并进行数据的完整性检查. 检查包括必要的键是否存在以及结束时间相关的键是否在适当的状态下存在. 

        参数: 
            无

        返回: 
            无
        """
        self.data = self.read_data_from_file(DATA_FILE_PATH)
        list_required_keys = ['month', 'week', 'start_time', 'content', 'color', 'color_week']
        list_end_required_keys = ['end_time', 'work_time', 'sum_work_time_month', 'sum_work_time_week']
        for key, item in self.data.items():
            for i in ['data', 'status']:
                if i not in item:
                    self.message_box.critical(self, '错误', f'存储文件被修改, 数据错误, 关键字丢失: {key} / {i}')
                    sys.exit()
            for entry_key, value in item.get('data', {}).items():
                list_missing_keys = [f'{entry_key}-{missing_key}' for missing_key in list_required_keys if missing_key not in value]
                list_end_missing_keys = [f'{entry_key}-{missing_key}' for missing_key in list_end_required_keys if missing_key not in value]
                if list_missing_keys:
                    self.message_box.critical(self, '错误', f'存储文件被修改, 数据错误, 时间关键字丢失:  {key} / {", ".join(list_missing_keys)}')
                    sys.exit()
                if list_end_missing_keys and item['status'] != 'start':
                    self.message_box.critical(self, '错误', f'存储文件被修改, 数据错误, 时间关键字丢失:  {key} / {", ".join(list_end_missing_keys)}')
                    sys.exit()

    def write_data(self) -> None:
        self.write_data_to_file(DATA_FILE_PATH, self.data)

    def read_data_from_file(self, file_path: str) -> dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except:
            self.message_box.critical(self, '错误', '文件格式不正确, 不符合Json文件格式')
            sys.exit()

    def write_data_to_file(self, file_path: str, data: dict) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_time(self) -> list[str, str]:
        """
        获取时间的方法. 
        用于获取当前的时间, 并返回格式化后的时间字符串和时间戳. 

        参数: 
            无

        返回: 
            list: 包含格式化后的时间字符串和时间戳的列表, 格式为 [formatted_time_with_ms, seconds]
                - formatted_time_with_ms (str): 格式化后的时间字符串, 包括年、月、日、时、分、秒和毫秒. 
                - seconds (int): 时间戳, 表示从1970年1月1日午夜开始经过的秒数. 

        示例: 
            get_time() 返回 ['2022.01.01 | 12:34:56.789', 1641022496]
        """
        timestamp = time()
        seconds = int(timestamp)
        milliseconds = int((timestamp - seconds) * 1000)
        local_time = localtime(seconds)
        formatted_time = strftime('%Y.%m.%d | %H:%M:%S', local_time)
        formatted_time_with_ms = f"{formatted_time}.{milliseconds}"
        return [formatted_time_with_ms, seconds]

    def record_start_time(self, ccb_item_name: str, start_time: str, start_timestamp: int, month: int, week: int, content: str) -> None:
        """
        记录开始时间的方法. 
        用于记录开始时间, 并将相关信息存储到数据中. 根据传入的参数, 创建一个新的数据项, 并将其添加到对应的ccb_item_name下的数据字典中. 

        参数: 
            ccb_item_name (str): 数据项的名称. 
            start_time (str): 开始时间的字符串表示. 
            start_timestamp (int): 开始时间的时间戳. 
            month (int): 月份. 
            week (int): 周数. 
            content (str): 数据项的内容. 

        返回: 
            无
        """
        length = len(self.data[ccb_item_name]['data'])
        index_int = length+1
        index = str(index_int)
        if ccb_item_name not in self.data:
            self.data[ccb_item_name] = deepcopy(DATA_PART_DEFAULT)
        self.data[ccb_item_name]['data'][index] = {
            'month': month,
            'week': week,
            'start_time': [start_time, start_timestamp],
            'content': content,
        }
        self.data[ccb_item_name]['status'] = 'start'
        if index_int <= 2 or self.data[ccb_item_name]['data'][str(index_int-1)]['start_time'][1] != self.data[ccb_item_name]['data'][index]['start_time'][1]:
            self.data[ccb_item_name]['data'][index]['color'] = COLOR_LIST[month % len(COLOR_LIST)]
            self.data[ccb_item_name]['data'][index]['color_week'] = COLOR_WEEK_LIST[week % len(COLOR_WEEK_LIST)]
        else:
            self.data[ccb_item_name]['data'][index]['color'] = self.data[ccb_item_name]['data'][str(index_int-1)]['color']
            self.data[ccb_item_name]['data'][index]['color_week'] = self.data[ccb_item_name]['data'][str(index_int-1)]['color_week']

    def record_start_time_auto(self) -> None:
        """
        自动记录开始时间的方法. 
        用于自动记录开始时间, 并将相关信息存储到数据中. 获取当前的本地时间, 提取月份和周数, 并调用record_start_time方法将开始时间和相关信息添加到数据中. 最后, 将数据写入文件并更新显示. 

        参数: 
            无

        返回: 
            无
        """
        local_time = localtime()
        month_num = local_time.tm_mon
        start_time, start_timestamp = self.get_time()
        self.record_start_time(
            ccb_item_name=self.ccb_item_name,
            start_time=start_time,
            start_timestamp=start_timestamp,
            month=month_num,
            week=int(strftime("%W", local_time)),
            content=self.plainTextEdit.toPlainText()
        )
        self.write_data()
        self.display_data()

    def record_end_time(self, ccb_item_name: str, start_timestamp: int, end_time: str, end_timestamp: int) -> None:
        """
        记录结束时间的方法. 
        用于记录结束时间, 并计算工作时间. 根据传入的参数, 获取当前数据项的索引, 计算工作时间的小时、分钟和秒, 并将结束时间、工作时间和状态更新到数据中. 

        参数: 
            ccb_item_name (str): 数据项的名称. 
            start_timestamp (int): 开始时间的时间戳. 
            end_time (str): 结束时间的字符串表示. 
            end_timestamp (int): 结束时间的时间戳. 

        返回: 
            无
        """
        index = str(len(self.data[ccb_item_name]['data']))
        work_time_h, work_time_min, work_time_s, work_time_in_s = self.calculate_time_diff(start_timestamp=start_timestamp, end_timestamp=end_timestamp)
        self.data[ccb_item_name]['data'][index]['end_time'] = [end_time, end_timestamp]
        self.data[ccb_item_name]['data'][index]['work_time'] = [f'{work_time_h}h {work_time_min}min {work_time_s}s', work_time_in_s]
        self.data[ccb_item_name]['status'] = 'end'
        self.calculate_work_time_in_month(ccb_item_name, index)
        self.calculate_work_time_in_week(ccb_item_name, index)

    def record_end_time_auto(self) -> None:
        """
        自动记录结束时间的方法. 
        用于自动记录结束时间, 并更新相关信息. 根据当前选择的ccb_item_name, 获取数据项的索引和开始时间的时间戳. 调用record_end_time方法记录结束时间, 并计算工作时间. 根据不同的情况, 更新数据项的内容. 最后, 将数据写入文件并更新显示. 

        参数: 
            无

        返回: 
            无
        """
        length = len(self.data[self.ccb_item_name]['data'])
        index = str(length)
        self.record_end_time(
            ccb_item_name=self.ccb_item_name,
            start_timestamp=self.data[self.ccb_item_name]['data'][str(len(self.data[self.ccb_item_name]['data']))]['start_time'][1],
            end_time=self.get_time()[0],
            end_timestamp=self.get_time()[1]
        )
        if self.data[self.ccb_item_name]['data'][index]['content'] == '' and self.plainTextEdit.toPlainText() == '':
            self.message_box.information(None, '提示', '请输入工作内容')
            return
        elif self.data[self.ccb_item_name]['data'][index]['content'] != '' and self.plainTextEdit.toPlainText() != '':
            content: str = self.data[self.ccb_item_name]['data'][index]['content'].replace('\n', '<br>')
            ans = self.message_box.question(None, '提示', f'是否覆盖原内容?<br>{content}', QMessageBox.Yes | QMessageBox.No)
            if ans == QMessageBox.Yes:
                self.data[self.ccb_item_name]['data'][index]['content'] = self.plainTextEdit.toPlainText()
            else:
                self.plainTextEdit.clear()
        elif self.data[self.ccb_item_name]['data'][index]['content'] == '':
            self.data[self.ccb_item_name]['data'][index]['content'] = self.plainTextEdit.toPlainText()
        self.write_data()
        self.display_data()

    def calculate_time_diff(self, start_timestamp: int, end_timestamp: int) -> list[int, int, int, float]:
        """
        用于计算给定的开始时间和结束时间之间的时间差. 将时间差转换为小时、分钟和秒, 并返回结果. 

        参数: 
            start_timestamp (int): 开始时间的时间戳. 
            end_timestamp (int): 结束时间的时间戳. 

        返回: 
            List[int, int, int, float]: 包含时间差的元组, 格式为 (work_time_h, work_time_min, work_time_s, work_time_in_s)
                - work_time_h (int): 工作时间的小时数. 
                - work_time_min (int): 工作时间的分钟数. 
                - work_time_s (int): 工作时间的秒数. 
                - work_time_in_s (float): 工作时间的总秒数. 

        示例: 
            calculate_time_diff(1641022496, 1641022596) 返回 (0, 0, 10, 10.0)
        """
        work_time_in_s: float = end_timestamp - start_timestamp
        work_time_h: int = work_time_in_s // 3600
        work_time_min: int = work_time_in_s % 3600 // 60
        work_time_s: int = work_time_in_s % 3600 % 60 % 60
        return work_time_h, work_time_min, work_time_s, work_time_in_s

    def calculate_work_time_in_month(self, ccb_item_name: str, index: str) -> None:
        """
        用于计算给定数据项在当前月份的累计工作时间. 根据传入的参数, 判断数据项的索引和月份信息, 然后进行相应的计算和更新. 

        参数: 
            ccb_item_name (str): 数据项的名称. 
            index (str): 数据项的索引. 

        返回: 
            无
        """
        if len(self.data[ccb_item_name]['data']) < 1:
            return
        if index == '0' or len(self.data[ccb_item_name]['data']) == 1 or self.data[ccb_item_name]['data'][str(int(index)-1)]['month'] != self.data[ccb_item_name]['data'][index]['month']:
            self.data[ccb_item_name]['data'][index]['sum_work_time_month'] = self.data[ccb_item_name]['data'][index]['work_time']
            return
        last_total_time = self.data[ccb_item_name]['data'][str(int(index)-1)]['sum_work_time_month'][1]
        sum_seconds = self.data[ccb_item_name]['data'][index]['work_time'][1] + last_total_time
        self.data[ccb_item_name]['data'][index]['sum_work_time_month'] = [f'{sum_seconds//3600}h {sum_seconds%3600//60}min {sum_seconds%3600%60%60}s', sum_seconds]

    def calculate_work_time_in_week(self, ccb_item_name, index):
        if len(self.data[ccb_item_name]['data']) < 1:
            return
        if index == '0' or len(self.data[ccb_item_name]['data']) == 1 or self.data[ccb_item_name]['data'][str(int(index)-1)]['week'] != self.data[ccb_item_name]['data'][index]['week']:
            self.data[ccb_item_name]['data'][index]['sum_work_time_week'] = self.data[ccb_item_name]['data'][index]['work_time']
            return
        last_total_time = self.data[ccb_item_name]['data'][str(int(index)-1)]['sum_work_time_week'][1]
        sum_seconds = self.data[ccb_item_name]['data'][index]['work_time'][1] + last_total_time
        self.data[ccb_item_name]['data'][index]['sum_work_time_week'] = [f'{sum_seconds//3600}h {sum_seconds%3600//60}min {sum_seconds%3600%60%60}s', sum_seconds]

    def icon_setup_from_svg(self, icon_code: str) -> QIcon:
        '''
        设置图标

        参数:
            Icon_code: SVG 的源码(str)
        '''
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_code.encode()))
        return QIcon(pixmap)

    def add_new_item_from_dialog(self):
        text, ok = QInputDialog.getText(self, '添加分类', '请添加分类名称')
        if ok and text:
            if text in self.data:
                self.message_box.warning(self, '错误', '分类名称已存在')
                return
            self.comboBox.addItem(text)
            self.comboBox.setItemData(self.comboBox.count()-1, QColor('#3cc800'), Qt.BackgroundRole)  # 绿色
            self.ccb_item_name = text
            self.timer.stop()
            self.data[self.ccb_item_name] = deepcopy(DATA_PART_DEFAULT)
            self.comboBox.setCurrentText(text)
            self.pb_start.show()
            self.write_data()

    def show_context_menu(self, pos: QPoint) -> None:
        """
        用于从对话框中获取用户输入的分类名称, 并将其作为新的数据项添加到数据中. 如果分类名称已存在, 则显示错误提示. 如果分类名称不存在, 则将其添加到下拉列表中, 并设置相应的背景颜色. 同时, 停止计时器, 更新当前选择的分类名称, 显示开始按钮, 并将数据写入文件. 

        参数: 
            无

        返回: 
            无
        """
        index = self.comboBox.view().indexAt(pos).row()
        if index != -1:
            menu = QMenu(self)
            action_del = QAction(f'删除 {self.comboBox.itemText(index)}', self)
            menu.addAction(action_del)
            action_del.triggered.connect(lambda: self.delete_item(index))
            menu.exec_(self.comboBox.view().mapToGlobal(pos))

    def delete_item(self, index: int) -> None:
        """
        用于删除指定索引的项. 根据传入的索引, 获取对应的分类名称, 并弹出确认对话框进行确认. 如果用户确认删除, 则再次弹出确认对话框进行最终确认. 如果用户最终确认删除, 则从数据中删除对应的分类项, 并从下拉列表中移除该项. 最后, 将数据写入文件并更新显示. 

        参数: 
            index (int): 要删除项的索引. 

        返回: 
            无
        """
        item_name = self.comboBox.itemText(index)
        ans = QMessageBox.question(None, '删除', f'确定要删除 {item_name} 吗？', QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            ans2 = QMessageBox.question(None, '删除', f'删除后数据不可撤回, 确认要删除 {item_name} 吗？', QMessageBox.Yes | QMessageBox.No)
            if ans2 == QMessageBox.Yes:
                del self.data[item_name]
                self.comboBox.removeItem(index)
                self.write_data()
                self.display_data()

    def update_combobox_item(self) -> None:
        """
        用于更新下拉列表中的项的显示样式. 首先清空持续时间标签. 然后遍历数据字典中的每个项, 根据项的状态设置对应的前景色和背景色. 如果项的状态为'end', 则设置背景色为绿色；否则, 设置背景色为红色. 

        参数: 
            无

        返回: 
            无
        """
        self.lb_duration.clear()
        for key, item in self.data.items():
            index = self.comboBox.findText(key)
            self.comboBox.setItemData(index, QColor('#000000'), Qt.ForegroundRole)
            if item['status'] == 'end':
                self.comboBox.setItemData(index, QColor('#3cc800'), Qt.BackgroundRole)  # 绿色
            else:
                self.comboBox.setItemData(index, QColor('#ee2d00'), Qt.BackgroundRole)  # 红色

    def blick_font_by_1s(self) -> None:
        """
        用于每秒闪烁下拉列表中正在进行的项的字体颜色. 遍历数据字典中的每个项, 如果项的状态为'start', 则获取对应的下拉列表索引. 根据当前字体颜色判断, 如果字体颜色为黑色, 则将字体颜色设置为白色；否则, 将字体颜色设置为黑色. 

        参数: 
            无

        返回: 
            无
        """
        for key, item in self.data.items():
            if item['status'] == 'start':
                index = self.comboBox.findText(key)
                font_color = self.comboBox.itemData(index, Qt.ForegroundRole)
                if font_color == QColor('#000000'):
                    self.comboBox.setItemData(index, QColor('#ffffff'), Qt.ForegroundRole)
                else:
                    self.comboBox.setItemData(index, QColor('#000000'), Qt.ForegroundRole)
        # for index in range(self.comboBox.count()):
        #     background_color = self.comboBox.itemData(index, Qt.BackgroundRole)
        #     if background_color == QColor('#ee2d00'):
        #         font_color = self.comboBox.itemData(index, Qt.ForegroundRole)
        #         if font_color == QColor('#000000'):
        #             self.comboBox.setItemData(index, QColor('#ffffff'), Qt.ForegroundRole)
        #         else:
        #             self.comboBox.setItemData(index, QColor('#000000'), Qt.ForegroundRole)

    def export_excel(self) -> None:
        """
        用于将数据导出为Excel文件. 首先定义了两个辅助函数: `format_datetime` 和 `format_time`, 用于格式化日期时间和时间. 然后创建一个Workbook对象, 并定义了不同颜色的格式. 接下来, 遍历数据字典中的每个项, 为每个项创建一个工作表, 并设置列宽和表头样式. 然后, 按行写入数据, 并根据颜色设置相应的单元格样式. 最后, 关闭Workbook对象, 并显示导出完成的通知. 

        参数: 
            无

        返回: 
            无
        """
        def format_datetime(time_str):
            date_str, time_str = time_str.split(' | ')
            year, month, day = date_str.split('.')
            return f'{year}/{month}/{day} {time_str}'

        def format_time(time_str):
            hour, minute_second = time_str.split('h ')
            minute, second = minute_second.split('min ')
            return f'{hour}:{minute}:{second[:-1]}'

        workbook = Workbook(DATA_EXCEL_PATH)
        dict_color = {
            'header': workbook.add_format({'bg_color': '#5983b0', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#0096ff': workbook.add_format({'bg_color': '#0096ff', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#FF8343': workbook.add_format({'bg_color': '#FF8343', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#F1DEC6': workbook.add_format({'bg_color': '#F1DEC6', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#B7E0FF': workbook.add_format({'bg_color': '#B7E0FF', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#FFF5CD': workbook.add_format({'bg_color': '#FFF5CD', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#FFCFB3': workbook.add_format({'bg_color': '#FFCFB3', 'border': 1, 'font_name': 'Arial', 'font_size': 12}),
            '#E78F81': workbook.add_format({'bg_color': '#E78F81', 'border': 1, 'font_name': 'Arial', 'font_size': 12})
        }
        for key, item in self.data.items():
            worksheet = workbook.add_worksheet(key)
            worksheet.set_column(0, 0, 5)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 30)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 15)
            worksheet.set_column(5, 5, 15)
            worksheet.write_row(0, 0, HEADER, dict_color['header'])

            for index_str, value in item['data'].items():
                row = int(index_str)
                worksheet.write(row, 0, index_str, dict_color[value['color']])
                worksheet.write(row, 1, format_datetime(value['start_time'][0]), dict_color[value['color']])
                worksheet.write(row, 2, format_datetime(value['end_time'][0]), dict_color[value['color']])
                worksheet.write(row, 3, format_time(value['work_time'][0]), dict_color[value['color']])
                worksheet.write(row, 4, format_time(value['sum_work_time_week'][0]), dict_color[value['color_week']])
                worksheet.write(row, 5, format_time(value['sum_work_time_month'][0]), dict_color[value['color']])
        workbook.close()
        path_format = DATA_EXCEL_PATH.replace('\\', '  /  ')
        self.message_notification.notification(f'已完成导出, 文件位置: {path_format}')


if __name__ == '__main__':
    from traceback import format_exc
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(format_exc())
