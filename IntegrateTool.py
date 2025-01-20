import sys
import psutil
import wmi
import netifaces
from PyQt5.QtGui import QTextLine
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QFrame, QLabel, \
    QDialog, QLineEdit, QTextEdit
import socket
import uuid
import subprocess

from psutil import disk_partitions


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('-----整合工具-----                   Author:吕铜')
        self.setGeometry(300, 300, 450, 400)

        # 主布局
        main_layout = QVBoxLayout()

        # 上部布局 - 两个 Checkbox
        checkbox_layout = QHBoxLayout()
        self.checkbox1 = QCheckBox('新电脑安装', self)
        self.checkbox2 = QCheckBox('单独执行', self)
        checkbox_layout.addWidget(self.checkbox1)
        checkbox_layout.addWidget(self.checkbox2)

        self.checkbox1.stateChanged.connect(self.update_buttons)
        self.checkbox2.stateChanged.connect(self.update_buttons)

        # 下部布局 - 左边是按钮，右边是 frame 和标签
        bottom_layout = QHBoxLayout()

        # 左边的按钮布局
        button_layout = QVBoxLayout()
        button_name_arr = ['全新自动安装','设置IP','复制安装软件','禁用U盘','禁止系统更新']
        self.buttons = []
        for i in range(len(button_name_arr)):
            button = QPushButton(f'{button_name_arr[i]}', self)
            button.setEnabled(False)  # 初始禁用所有按钮
            button_layout.addWidget(button)
            self.buttons.append(button)

        # 右边的 Frame 和标签
        frame_layout = QVBoxLayout()
        self.labels = []
        self.icons = []

        label_name_arr = ['设置IP','复制安装软件','禁用U盘','禁止系统更新']
        for i in range(len(label_name_arr)):
            label = QLabel(f'{label_name_arr[i]}', self)
            self.labels.append(label)
            icon = QLabel(self)
            self.icons.append(icon)
            frame_layout.addWidget(label)
            frame_layout.addWidget(icon)

        self.frame = QFrame(self)
        self.frame.setLayout(frame_layout)

        bottom_layout.addLayout(button_layout)
        bottom_layout.addWidget(self.frame)

        # 合并所有布局
        main_layout.addLayout(checkbox_layout)
        main_layout.addLayout(bottom_layout)

        # 添加 "button3"
        self.button3 = QPushButton('显示系统信息', self)
        self.button3.clicked.connect(self.show_system_info)
        main_layout.addWidget(self.button3)

        self.setLayout(main_layout)

    def update_buttons(self):
        # 根据 Checkbox 的状态来更新按钮的可用性
        if self.checkbox1.isChecked():
            self.buttons[0].setEnabled(True)
            for index in range(len(self.buttons)):
                self.buttons[index].setEnabled(False)  # 其他按钮禁用
        else:
            self.buttons[0].setEnabled(False)

        if self.checkbox2.isChecked():
            for i in range(1, len(self.buttons)):
                self.buttons[i].setEnabled(True)  # 启用其他按钮
            self.buttons[0].setEnabled(False)  # 禁用第一个按钮

    def show_system_info(self):
        dialog = SystemInfoDialog(self)
        dialog.exec_()


class SystemInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('系统信息')

        # 创建布局
        layout_label = QVBoxLayout()
        layout_text = QVBoxLayout()
        layout = QHBoxLayout()

        # 获取并显示系统信息
        self.display_system_info(layout_label, layout_text)

        layout.addLayout(layout_label)
        layout.addLayout(layout_text)

        self.setLayout(layout)
        self.setAutoFillBackground(True)
        self.setFixedSize(500, 400)

    def display_system_info(self, layout1, layout2):
        # 获取 CPU 型号信息
        systeminfo = wmi.WMI()
        cpu = systeminfo.Win32_Processor()[0].Name
        cpu_label = QLabel(self)
        cpu_label.setText("CPU型号：")
        layout1.addWidget(cpu_label)
        cpu_text = QTextEdit(self)
        cpu_text.setText(cpu)
        cpu_text.setReadOnly(True)
        layout2.addWidget(cpu_text)

        # 获取硬盘序列号
        diskinfo = systeminfo.Win32_DiskDrive()
        for disk in diskinfo:
            disk_serial = disk.SerialNumber.replace(' ', '')
            disk_number_label = QLabel(self)
            disk_number_label.setText("硬盘序列号：")
            layout1.addWidget(disk_number_label)
            disk_text = QTextEdit(self)
            disk_text.setText(disk_serial)
            disk_text.setReadOnly(True)
            layout2.addWidget(disk_text)

        # 获取内存信息
        memory_info = psutil.virtual_memory()
        memory_label = QLabel(self)
        memory_label.setText("内存：")
        layout1.addWidget(memory_label)
        memory_text = QTextEdit(self)
        memory_text.setText(f"{round(memory_info.total / (1024 ** 3))}GB")
        memory_text.setReadOnly(True)
        layout2.addWidget(memory_text)

        # 获取 IP 地址
        ip_address = socket.gethostbyname(socket.gethostname())
        ip_label = QLabel(self)
        ip_label.setText("IP地址：")
        layout1.addWidget(ip_label)
        ip_text = QTextEdit(self)
        ip_text.setText(ip_address)
        ip_text.setReadOnly(True)
        layout2.addWidget(ip_text)

        # 获取 计算机名
        comp_name = socket.gethostname()
        comp_name_label = QLabel(self)
        comp_name_label.setText("计算机名：")
        layout1.addWidget(comp_name_label)
        comp_name_text = QTextEdit(self)
        comp_name_text.setText(comp_name)
        comp_name_text.setReadOnly(True)
        layout2.addWidget(comp_name_text)

        # 获取 MAC 地址并格式化
        mac_addr = psutil.net_if_addrs()
        for mac in mac_addr:
            if mac.lower().__contains__('loopback'):
                continue
            mac_label = QLabel(self)
            mac_label.setText("MAC地址：")
            layout1.addWidget(mac_label)
            mac_text = QTextEdit(self)
            mac_text.setText(f'网卡名称：{str(mac)}------网卡地址：{mac_addr[mac][0].address}')
            mac_text.setReadOnly(True)
            layout2.addWidget(mac_text)
        # interfaces = netifaces.interfaces()
        # for interface in interfaces:
        #     mac_address = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
        #     if mac_address:
        #         mac_label = QLabel(self)
        #         mac_label.setText("MAC地址：")
        #         layout1.addWidget(mac_label)
        #         mac_text = QTextEdit(self)
        #         mac_text.setText(mac_address.replace(':', '-'))
        #         mac_text.setReadOnly(True)
        #         layout2.addWidget(mac_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
