

from Dialog_Manual_ui import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import QDateTime, QByteArray
from PyQt5.QtGui import QIcon, QPixmap

from datetime import datetime
from const import *
from copy import deepcopy

DATA_DEFAULT = {}
DATA_PART_DEFAULT = {
    'status': 'end',
    'data': {}
}


class DialogManual(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.data = parent.data
        self.inner_data = {}
        self.init_ui()
        self.init_signal_connections()

    def accept(self):
        if self.dte_start.dateTime() >= self.dte_end.dateTime() or self.plainTextEdit.toPlainText() == '' or self.comboBox.currentText() == '':
            QMessageBox.information(None, '提示', '开始时间不能晚于结束时间, 且工作内容和分类不能为空')
            return
        super().accept()
        self.record_in_data()

    def get_montn_week(self, timestamp):
        dt_object = datetime.fromtimestamp(timestamp)
        month = dt_object.month
        week_number = dt_object.isocalendar()[1]
        return month, week_number

    def init_ui(self):
        self.setWindowTitle('手动添加工作时间记录')
        self.setWindowIcon(self.icon_setup_from_svg(WIN_ICON))
        self.pb_add_item.setIcon(self.icon_setup_from_svg(ADD_ICON))
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setDateTime(QDateTime.currentDateTime().addSecs(1))
        self.setStyleSheet("""
                           QDialog{
                               background-color: #10375C
                           }
                           QLabel{
                               color: #DDDDDD
                           }
                           QTreeWidget{
                               background-color: #DDDDDD
                           }
                           """)
        self.init_comboBox()

    def init_comboBox(self):
        self.comboBox.clear()
        for key, item in self.data.items():
            if item['status'] == 'end':
                self.comboBox.addItem(key)

    def init_signal_connections(self):
        self.dte_start.dateTimeChanged.connect(self.start_time_changed)
        self.dte_start.dateTimeChanged.connect(self.record_in_data)
        self.dte_end.dateTimeChanged.connect(self.record_in_data)
        self.plainTextEdit.textChanged.connect(self.record_in_data)
        self.comboBox.currentIndexChanged.connect(self.combobox_changed)
        self.comboBox.currentIndexChanged.connect(self.record_in_data)
        self.pb_add_item.clicked.connect(self.add_new_item_from_dialog)

    def combobox_changed(self):
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setDateTime(QDateTime.currentDateTime().addSecs(1))
        self.plainTextEdit.clear()

    def record_in_data(self):
        self.start_time = self.dte_start.dateTime().toString('yyyy.MM.dd | hh:mm:ss.000')
        self.start_timestamp = self.dte_start.dateTime().toSecsSinceEpoch()
        self.end_time = self.dte_end.dateTime().toString('yyyy.MM.dd | hh:mm:ss.000')
        self.end_timestamp = self.dte_end.dateTime().toSecsSinceEpoch()
        self.work_content = self.plainTextEdit.toPlainText()
        self.start_month, self.start_week = self.get_montn_week(self.start_timestamp)
        if self.comboBox.currentText() not in self.inner_data:
            self.inner_data[self.comboBox.currentText()] = DATA_PART_DEFAULT

        self.inner_data[self.comboBox.currentText()]['month'] = self.start_month
        self.inner_data[self.comboBox.currentText()]['week'] = self.start_week
        self.inner_data[self.comboBox.currentText()]['start_time'] = self.start_time
        self.inner_data[self.comboBox.currentText()]['start_timestamp'] = self.start_timestamp
        self.inner_data[self.comboBox.currentText()]['end_time'] = self.end_time
        self.inner_data[self.comboBox.currentText()]['end_timestamp'] = self.end_timestamp
        self.inner_data[self.comboBox.currentText()]['content'] = self.work_content

    def get_data(self):
        return self.inner_data

    def icon_setup_from_svg(self, icon_code: str) -> QIcon:
        '''
        设置图标

        参数:
            Icon_code: SVG 的源码(str)
        '''
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(icon_code.encode()))
        return QIcon(pixmap)

    def start_time_changed(self):
        start_datetime = self.dte_start.dateTime()
        self.dte_end.setMinimumDateTime(start_datetime.addSecs(1))

    def add_new_item_from_dialog(self):
        text, ok = QInputDialog.getText(self, '添加分类', '请添加分类名称')
        if ok and text:
            if text in self.data:
                QMessageBox.warning(self, '错误', '分类名称已存在')
                return
            self.comboBox.addItem(text)
            self.ccb_item_name = text
            self.data[self.ccb_item_name] = deepcopy(DATA_PART_DEFAULT)
            self.comboBox.setCurrentText(text)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = DialogManual()
    dlg.show()
    sys.exit(app.exec_())
