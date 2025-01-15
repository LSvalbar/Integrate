import sys
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QFrame, QLabel, \
    QDialog
import socket
import uuid
import subprocess


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
        self.checkbox1 = QCheckBox('Checkbox 1', self)
        self.checkbox2 = QCheckBox('Checkbox 2', self)
        checkbox_layout.addWidget(self.checkbox1)
        checkbox_layout.addWidget(self.checkbox2)

        self.checkbox1.stateChanged.connect(self.update_buttons)
        self.checkbox2.stateChanged.connect(self.update_buttons)

        # 下部布局 - 左边是按钮，右边是 frame 和标签
        bottom_layout = QHBoxLayout()

        # 左边的按钮布局
        button_layout = QVBoxLayout()
        self.buttons = []
        for i in range(6):
            button = QPushButton(f'Button {i + 1}', self)
            button.setEnabled(False)  # 初始禁用所有按钮
            button_layout.addWidget(button)
            self.buttons.append(button)

        # 右边的 Frame 和标签
        frame_layout = QVBoxLayout()
        self.labels = []
        self.icons = []

        for i in range(6):
            label = QLabel(f'Label {i + 1}', self)
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
        self.setWindowTitle('System Information')

        # 创建布局
        layout = QVBoxLayout()

        # 创建 Frame 用于显示信息
        info_frame = QFrame(self)
        info_layout = QVBoxLayout()

        # 获取并显示系统信息
        self.display_system_info(info_layout)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        self.setLayout(layout)
        self.setFixedSize(400, 300)

    def display_system_info(self, layout):
        # 获取 CPU 型号信息
        cpu_info = subprocess.check_output(
            ["powershell", "-Command", "Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty Name"],
            shell=True
        ).decode().strip()
        cpu_label = QLabel(f"CPU 型号: {cpu_info}", self)
        layout.addWidget(cpu_label)

        # 获取硬盘信息
        disk_count = subprocess.check_output(
            ["powershell", "-Command", "Get-WmiObject -Class Win32_DiskDrive | Measure-Object"]
        ).decode().strip().splitlines()[0]
        disk_capacity = subprocess.check_output(
            ["powershell", "-Command", "Get-WmiObject -Class Win32_DiskDrive | Select-Object -ExpandProperty Size"],
            shell=True
        ).decode().strip().split("\n")
        disk_capacity = [str(int(capacity) / (1024 ** 3)).split('.')[0] + " GB" for capacity in disk_capacity]
        disk_label = QLabel(f"硬盘数量: {disk_count.split(':')[1]}，硬盘容量大小: {disk_capacity[0]}", self)
        layout.addWidget(disk_label)

        # 获取硬盘序列号
        disk_serials = subprocess.check_output(
            ["powershell", "-Command",
             "Get-WmiObject -Class Win32_DiskDrive | Select-Object -ExpandProperty SerialNumber"],
            shell=True
        ).decode().strip().split("\n")
        disk_serial_label = QLabel(f"硬盘序列号: {disk_serials}", self)
        layout.addWidget(disk_serial_label)

        # 获取内存信息
        memory_info = psutil.virtual_memory()
        memory_label = QLabel(f"内存大小: {memory_info.total / (1024 ** 3):.2f} GB", self)
        layout.addWidget(memory_label)

        # 获取 IP 地址
        ip_address = socket.gethostbyname(socket.gethostname())
        ip_label = QLabel(f"IP 地址: {ip_address}", self)
        layout.addWidget(ip_label)

        # 获取 MAC 地址并格式化
        mac_addresses = subprocess.check_output(
            ["powershell", "-Command",
             "Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled -eq $true } | Select-Object -ExpandProperty MACAddress"],
            shell=True
        ).decode().strip().split("\n")
        print()
        mac_addresses = mac_addresses[0].replace("[\'", "").replace("\']", "")
        mac_label = QLabel(f"MAC 地址: {mac_addresses}", self)
        layout.addWidget(mac_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
