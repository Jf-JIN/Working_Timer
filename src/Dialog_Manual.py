

from Dialog_Manual_ui import Ui_Dialog

from PyQt5.QtWidgets import QDialog, QMessageBox, QMenu, QAction, QInputDialog
from PyQt5.QtCore import QDateTime, QByteArray, Qt, QPoint
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap, QMouseEvent

from datetime import datetime
from const import *
from copy import deepcopy

DATA_DEFAULT = {}
DATA_PART_DEFAULT = {
    'status': 'end',
    'data': {}
}
DATA_INNER_DEFAULT = {
    'start_time': ''
}
# DETAIL_DATE_TIME = True
DETAIL_DATE_TIME = False


class DialogManual(QDialog, Ui_Dialog):
    def get_data(self):
        return self.inner_data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.data = parent.data
        self.inner_data = {}
        self.init_ui()
        self.init_signal_connections()

    def accept(self):
        list_incomplete_item = []
        for key, item in self.inner_data.items():
            if len(item) != 8:
                list_incomplete_item.append(key)
        if len(list_incomplete_item) > 0:
            ans = QMessageBox.question(None, '提示', ('数据不完整<br>'
                                                    f""""{'" "'.join(list_incomplete_item)}" 项未填写工作内容<br>"""
                                                    '不完整部分将不会被保存, 是否继续?<br><br>'
                                                    '点击 Yes 将保存数据<br>'
                                                    '点击 No 将放弃保存<br><br>'
                                                    '如需新建分类, 请在主界面进行新建'), QMessageBox.Yes | QMessageBox.No)
            if ans == QMessageBox.No:
                return
        if self.inner_data == {}:
            self.parent().message_notification.notification('尚未输入有效内容')
        super().accept()
        self.record_in_data()

    def reject(self):
        self.close()

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.inner_data != {}:
            ans = QMessageBox.question(None, '提示', ('关闭将清空输入的所有内容, 确定关闭吗?<br><br>'
                                                    '点击 close 将关闭窗口并清空包括之前输入的内容<br>'
                                                    '点击 save 将只保存之前输入的内容<br>'
                                                    '点击 No 可以继续编辑<br><br>'
                                                    '如果输入有误需要删除, 建议在主界面中手动删除'), QMessageBox.Close | QMessageBox.Save | QMessageBox.No)
            if ans == QMessageBox.Close:
                self.inner_data = {}
                self.comboBox.clear()
                self.plainTextEdit.clear()
                self.dte_start.setDateTime(QDateTime.currentDateTime())
                self.accept()
            elif ans == QMessageBox.No:
                a0.ignore()
            elif ans == QMessageBox.Save:
                self.comboBox.setCurrentText('')
                self.plainTextEdit.clear()
                self.accept()
        else:
            a0.accept()

    def eventFilter(self, source, event) -> bool:
        if source == self.comboBox.view().viewport():
            if event.type() == QMouseEvent.MouseButtonPress and event.button() == Qt.RightButton:
                index = self.comboBox.view().indexAt(event.pos()).row()
                if index != -1:
                    self.show_context_menu(event.pos())
                    return True
        return super().eventFilter(source, event)

    def init_ui(self):
        self.setWindowTitle('手动添加工作时间记录')
        self.comboBox.view().setContextMenuPolicy(Qt.CustomContextMenu)
        self.comboBox.view().viewport().installEventFilter(self)
        self.comboBox.view().customContextMenuRequested.connect(self.show_context_menu)
        self.plainTextEdit.setPlaceholderText('请在此输入工作内容')
        self.pb_add_item.setIcon(self.icon_setup_from_svg(ICON_ADD))
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        if DETAIL_DATE_TIME:
            self.dte_start.setDisplayFormat("yyyy-MM-dd HH:mm:ss.zzz")
            self.dte_end.setDisplayFormat("yyyy-MM-dd HH:mm:ss.zzz")
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
        self.update_display()

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
        self.comboBox.currentIndexChanged.connect(self.record_in_data)
        self.comboBox.currentIndexChanged.connect(self.combobox_changed)
        self.pb_add_item.clicked.connect(self.add_new_item_from_dialog)

    def combobox_changed(self):
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))
        self.plainTextEdit.clear()

    def record_in_data(self, ):
        if self.comboBox.currentText() == '' or self.plainTextEdit.toPlainText().strip() == '' or self.plainTextEdit.toPlainText() == '请先点击上方加号 "+" 添加分类':
            return
        start_time = self.dte_start.dateTime().toString('yyyy.MM.dd | hh:mm:ss.000')
        start_timestamp = self.dte_start.dateTime().toSecsSinceEpoch()
        end_time = self.dte_end.dateTime().toString('yyyy.MM.dd | hh:mm:ss.000')
        end_timestamp = self.dte_end.dateTime().toSecsSinceEpoch()
        if DETAIL_DATE_TIME:
            start_time = self.dte_start.dateTime().toString('yyyy.MM.dd | hh:mm:ss.zzz')
            end_time = self.dte_end.dateTime().toString('yyyy.MM.dd | hh:mm:ss.zzz')
        work_content = self.plainTextEdit.toPlainText()
        start_year, start_month, start_week = self.get_montn_week(start_timestamp)
        if self.comboBox.currentText() not in self.inner_data:
            self.inner_data[self.comboBox.currentText()] = deepcopy(DATA_INNER_DEFAULT)

        self.inner_data[self.comboBox.currentText()]['year'] = start_year
        self.inner_data[self.comboBox.currentText()]['month'] = start_month
        self.inner_data[self.comboBox.currentText()]['week'] = start_week
        self.inner_data[self.comboBox.currentText()]['start_time'] = start_time
        self.inner_data[self.comboBox.currentText()]['start_timestamp'] = start_timestamp
        self.inner_data[self.comboBox.currentText()]['end_time'] = end_time
        self.inner_data[self.comboBox.currentText()]['end_timestamp'] = end_timestamp
        self.inner_data[self.comboBox.currentText()]['content'] = work_content

    def show_context_menu(self, pos: QPoint) -> None:
        index = self.comboBox.view().indexAt(pos).row()
        if index != -1:
            menu = QMenu(self)
            action_del = QAction(f'删除 {self.comboBox.itemText(index)}', self)
            action_del.setIcon(self.icon_setup_from_svg(ICON_DELETE))
            menu.addAction(action_del)
            action_del.triggered.connect(lambda: self.delete_item(index))
            menu.exec_(self.comboBox.view().mapToGlobal(pos))

    def delete_item(self, index):
        item_name = self.comboBox.itemText(index)
        ans = QMessageBox.question(None, '删除', f'确定要删除 {item_name} 吗？', QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            ans2 = QMessageBox.question(None, '删除', f'删除后数据不可撤回, 确认要删除 {item_name} 吗？', QMessageBox.Yes | QMessageBox.No)
            if ans2 == QMessageBox.Yes:
                del self.inner_data[item_name]
                self.comboBox.removeItem(index)
                self.record_in_data()
                self.update_display()

    def update_display(self):
        self.dte_start.setDateTime(QDateTime.currentDateTime())
        self.dte_end.setDateTime(QDateTime.currentDateTime().addSecs(60))
        self.plainTextEdit.clear()
        if self.comboBox.currentText() == '':
            self.plainTextEdit.setPlainText('请先点击上方加号 "+" 添加分类')
            self.plainTextEdit.setEnabled(False)
        else:
            self.plainTextEdit.clear()
            self.plainTextEdit.setEnabled(True)

    def get_montn_week(self, timestamp):
        dt_object = datetime.fromtimestamp(timestamp)
        year = dt_object.year
        month = dt_object.month
        week_number = dt_object.isocalendar()[1]
        return year, month, week_number

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
        self.dte_end.setMinimumDateTime(start_datetime.addSecs(60))

    def add_new_item_from_dialog(self):
        if self.comboBox.currentText() != '' and self.plainTextEdit.toPlainText() != '':
            ans = QMessageBox.question(self, '提示', '是否保留当前数据? <br>点击 Yes 将保存当前数据<br>点击 No 将不保存当前数据', QMessageBox.Save | QMessageBox.No)
            if ans == QMessageBox.No:
                del self.inner_data[self.comboBox.currentText()]
        while True:
            text, ok = QInputDialog.getText(self, '添加分类', '请添加分类名称')
            if not ok:
                return
            if text.strip() == '':
                QMessageBox.warning(self, '错误', '分类名称不能为空')
                continue
            if text in self.data or text in self.inner_data:
                QMessageBox.warning(self, '错误', '分类名称已存在')
                continue
            break
        self.comboBox.addItem(text)
        self.comboBox.setCurrentText(text)
        self.ccb_item_name = text
        self.inner_data[self.ccb_item_name] = deepcopy(DATA_INNER_DEFAULT)
        self.update_display()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = DialogManual()
    dlg.show()
    sys.exit(app.exec_())
