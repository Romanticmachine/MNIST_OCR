#!/usr/bin/python3
# -*- coding: utf-8 -*-
#test
import sys, os
import numpy as np
import csv
import datetime
import pandas as pd
from dataset.mnist import load_mnist
from PIL import Image

from qt.layout import Ui_MainWindow
from qt.paintboard import PaintBoard

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QLabel, QMessageBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QImage
from PyQt5.QtCore import Qt, QPoint, QSize, QDateTime

from simple_convnet import SimpleConvNet
from common.functions import softmax
from deep_convnet import DeepConvNet



MODE_MNIST = 1    # MNIST随机抽取
MODE_WRITE = 2    # 手写输入

Thresh = 0.5      # 识别结果置信度阈值

# 工艺参数数据库文件路径
PARAM_DB_PATH = "./dataset/process_params.csv"

# 历史记录文件路径
HISTORY_DB_PATH = "./dataset/recognition_history.csv"

# 读取MNIST数据集
(_, _), (x_test, _) = load_mnist(normalize=True, flatten=False, one_hot_label=False)


# 初始化网络

# 网络1：简单CNN
"""
conv - relu - pool - affine - relu - affine - softmax
"""
network = SimpleConvNet(input_dim=(1,28,28), 
                        conv_param = {'filter_num': 30, 'filter_size': 5, 'pad': 0, 'stride': 1},
                        hidden_size=100, output_size=10, weight_init_std=0.01)
network.load_params("./params.pkl")

# 网络2：深度CNN
# network = DeepConvNet()
# network.load_params("deep_convnet_params.pkl")


# 辅助函数：将PIL图像转换为QImage
def pil_to_qimage(pil_image):
    if pil_image.mode == "RGB":
        r, g, b = pil_image.split()
        pil_image = Image.merge("RGB", (b, g, r))
    elif pil_image.mode == "RGBA":
        r, g, b, a = pil_image.split()
        pil_image = Image.merge("RGBA", (b, g, r, a))
    elif pil_image.mode == "L":
        pil_image = pil_image.convert("RGBA")
    
    im_data = pil_image.tobytes("raw", "RGBA")
    qimage = QImage(im_data, pil_image.size[0], pil_image.size[1], QImage.Format_RGBA8888)
    return qimage

# 辅助函数：将QImage转换为PIL图像
def qimage_to_pil(qimage):
    buffer = qimage.bits().asstring(qimage.byteCount())
    width, height = qimage.width(), qimage.height()
    
    if qimage.format() == QImage.Format_RGB32:
        pil_image = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1)
    else:
        # 转换为RGBA格式
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)
        buffer = qimage.bits().asstring(qimage.byteCount())
        pil_image = Image.frombuffer("RGBA", (width, height), buffer, "raw", "RGBA", 0, 1)
    
    return pil_image


# 工艺参数管理类
class ProcessParameterManager:
    def __init__(self, db_path=PARAM_DB_PATH):
        self.db_path = db_path
        self.params = {}
        self.load_parameters()
    
    def load_parameters(self):
        """加载工艺参数数据库"""
        # 如果数据库文件不存在，创建默认数据库
        if not os.path.exists(self.db_path):
            self.create_default_db()
        
        try:
            # 读取CSV文件
            with open(self.db_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    part_id = int(row['零件编号'])
                    self.params[part_id] = {
                        '材料': row['材料'],
                        '加工速度': float(row['加工速度']),
                        '主轴转速': int(row['主轴转速']),
                        '进给量': float(row['进给量']),
                        '切削深度': float(row['切削深度']),
                        '冷却液流量': float(row['冷却液流量']),
                        '加工时间': float(row['加工时间'])
                    }
        except Exception as e:
            print(f"加载工艺参数数据库失败: {e}")
            self.create_default_db()
    
    def create_default_db(self):
        """创建默认工艺参数数据库"""
        # 默认参数
        default_params = []
        for i in range(10):  # 对应数字0-9
            default_params.append({
                '零件编号': i,
                '材料': f'材料{i}',
                '加工速度': 100 + i * 10,
                '主轴转速': 1000 + i * 100,
                '进给量': 0.1 + i * 0.02,
                '切削深度': 0.5 + i * 0.1,
                '冷却液流量': 2.0 + i * 0.2,
                '加工时间': 10 + i
            })
        
        # 写入CSV文件
        with open(self.db_path, 'w', newline='') as csvfile:
            fieldnames = ['零件编号', '材料', '加工速度', '主轴转速', '进给量', '切削深度', '冷却液流量', '加工时间']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for param in default_params:
                writer.writerow(param)
        
        # 加载到内存
        for param in default_params:
            part_id = param['零件编号']
            self.params[part_id] = {
                '材料': param['材料'],
                '加工速度': param['加工速度'],
                '主轴转速': param['主轴转速'],
                '进给量': param['进给量'],
                '切削深度': param['切削深度'],
                '冷却液流量': param['冷却液流量'],
                '加工时间': param['加工时间']
            }
    
    def get_parameters(self, part_id):
        """获取指定零件编号的工艺参数"""
        if part_id in self.params:
            return self.params[part_id]
        return None
    
    def update_parameters(self, part_id, new_params):
        """更新指定零件编号的工艺参数"""
        if part_id in self.params:
            self.params[part_id].update(new_params)
            self.save_parameters()
            return True
        return False
    
    def save_parameters(self):
        """保存工艺参数到数据库文件"""
        try:
            with open(self.db_path, 'w', newline='') as csvfile:
                fieldnames = ['零件编号', '材料', '加工速度', '主轴转速', '进给量', '切削深度', '冷却液流量', '加工时间']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for part_id, params in self.params.items():
                    row = {'零件编号': part_id}
                    row.update(params)
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"保存工艺参数数据库失败: {e}")
            return False


# 历史记录管理类
class HistoryManager:
    def __init__(self, db_path=HISTORY_DB_PATH):
        self.db_path = db_path
        self.history = []
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.db_path):
            try:
                self.history = pd.read_csv(self.db_path).to_dict('records')
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self.history = []
        else:
            self.history = []
    
    def add_record(self, part_id, confidence, params):
        """添加历史记录"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            '时间戳': timestamp,
            '零件编号': part_id,
            '置信度': confidence
        }
        # 添加工艺参数
        for key, value in params.items():
            record[key] = value
        
        self.history.append(record)
        self.save_history()
    
    def get_history(self, limit=100):
        """获取历史记录，默认最近100条"""
        return self.history[-limit:]
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            df = pd.DataFrame(self.history)
            df.to_csv(self.db_path, index=False)
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return False


# 参数编辑对话框
class ParameterEditDialog(QDialog):
    def __init__(self, part_id, params, parent=None):
        super(ParameterEditDialog, self).__init__(parent)
        self.part_id = part_id
        self.params = params
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"编辑零件 {self.part_id} 的工艺参数")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 创建表单
        form_layout = QFormLayout()
        
        self.param_inputs = {}
        for key, value in self.params.items():
            if key != '零件编号':
                line_edit = QLineEdit(str(value))
                form_layout.addRow(f"{key}:", line_edit)
                self.param_inputs[key] = line_edit
        
        layout.addLayout(form_layout)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_updated_params(self):
        """获取更新后的参数"""
        updated_params = {}
        for key, input_widget in self.param_inputs.items():
            try:
                # 尝试转换为原始类型
                if isinstance(self.params[key], int):
                    updated_params[key] = int(input_widget.text())
                elif isinstance(self.params[key], float):
                    updated_params[key] = float(input_widget.text())
                else:
                    updated_params[key] = input_widget.text()
            except ValueError:
                # 如果转换失败，保持原值
                updated_params[key] = self.params[key]
        
        return updated_params


# 历史记录对话框
class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super(HistoryDialog, self).__init__(parent)
        self.history = history
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("识别历史记录")
        self.setMinimumSize(800, 400)
        
        layout = QVBoxLayout()
        
        # 创建表格
        self.table = QTableWidget()
        self.update_table()
        
        layout.addWidget(self.table)
        
        # 添加关闭按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def update_table(self):
        """更新表格内容"""
        if not self.history:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        
        # 获取所有列名
        columns = list(self.history[0].keys())
        
        self.table.setRowCount(len(self.history))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # 填充数据
        for row, record in enumerate(self.history):
            for col, key in enumerate(columns):
                item = QTableWidgetItem(str(record.get(key, '')))
                self.table.setItem(row, col, item)
        
        # 调整列宽
        self.table.resizeColumnsToContents()


class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
    
        # 初始化参数
        self.mode = MODE_MNIST
        self.result = [0, 0]
        
        # 初始化工艺参数管理器
        self.param_manager = ProcessParameterManager()
        
        # 初始化历史记录管理器
        self.history_manager = HistoryManager()
        
        # 当前工艺参数
        self.current_params = None

        # 初始化UI
        self.setupUi(self)
        self.center()
        
        # 设置固定大小，防止布局变化
        self.setMinimumSize(1000, 700)

        # 初始化画板 - 将画板和数据显示标签放在同一区域
        self.paintBoard = PaintBoard(self, Size = QSize(224, 224), Fill = QColor(0,0,0,0))
        self.paintBoard.setPenColor(QColor(0,0,0,0))
        
        # 创建一个固定大小的容器来包含画板和标签
        self.dataContainer = QFrame()
        self.dataContainer.setFixedSize(224, 224)
        self.dataContainer_layout = QGridLayout(self.dataContainer)
        self.dataContainer_layout.setContentsMargins(0, 0, 0, 0)
        self.dataContainer_layout.setSpacing(0)  # 移除网格间距
        
        # 设置标签的对齐方式为居中
        self.lbDataArea.setAlignment(Qt.AlignCenter)
        
        # 设置标签的样式，确保图片居中显示
        self.lbDataArea.setStyleSheet("border: 2px solid black; background-color: white; qproperty-alignment: AlignCenter;")
        self.lbDataArea.setScaledContents(True)  # 图片自适应标签大小
        
        # 将画板和标签添加到网格布局的中心位置
        self.dataContainer_layout.addWidget(self.paintBoard, 0, 0, Qt.AlignCenter)
        self.dataContainer_layout.addWidget(self.lbDataArea, 0, 0, Qt.AlignCenter)
        
        # 将容器添加到数据区域布局，并设置居中对齐
        self.dArea_Layout.addWidget(self.dataContainer, 0, Qt.AlignCenter)
        
        # 确保数据区域布局也居中对齐
        self.dataInputLayout.setAlignment(Qt.AlignCenter)
        self.dArea_Layout.setAlignment(Qt.AlignCenter)
        
        # 设置画板和标签的堆叠
        self.paintBoard.setVisible(False)  # 初始隐藏画板
        
        self.clearDataArea()
        
        # 设置窗口标题
        self.setWindowTitle("智能制造零件识别系统")

    # 窗口居中
    def center(self):
        # 获得窗口
        framePos = self.frameGeometry()
        # 获得屏幕中心点
        scPos = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        framePos.moveCenter(scPos)
        self.move(framePos.topLeft())
    
    # 窗口关闭事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()   
    
    # 清除数据待输入区
    def clearDataArea(self):
        self.paintBoard.Clear()
        self.lbDataArea.clear()
        self.lbResult.clear()
        self.lbCofidence.clear()
        self.result = [0, 0]
        self.current_params = None
        self.update_param_display(None)
        self.btn_edit_params.setEnabled(False)
    
    # 更新工艺参数显示
    def update_param_display(self, params):
        if params:
            for key, label in self.param_labels.items():
                if key in params:
                    label.setText(f"{key}: {params[key]}")
            
            # 启用参数修改按钮
            self.btn_edit_params.setEnabled(True)
        else:
            # 清空参数显示
            for label in self.param_labels.values():
                label.setText(f"{label.text().split(':')[0]}: --")
            
            # 禁用参数修改按钮
            self.btn_edit_params.setEnabled(False)
    
    # 显示历史记录
    def show_history(self):
        history = self.history_manager.get_history()
        dialog = HistoryDialog(history, self)
        dialog.exec_()
    
    # 编辑工艺参数
    def edit_parameters(self):
        if self.current_params and self.result[0] is not None:
            dialog = ParameterEditDialog(self.result[0], self.current_params, self)
            if dialog.exec_() == QDialog.Accepted:
                # 获取更新后的参数
                updated_params = dialog.get_updated_params()
                
                # 更新参数
                if self.param_manager.update_parameters(self.result[0], updated_params):
                    # 更新显示
                    self.current_params = self.param_manager.get_parameters(self.result[0])
                    self.update_param_display(self.current_params)
                    QMessageBox.information(self, "成功", "工艺参数已更新")
                else:
                    QMessageBox.warning(self, "错误", "更新工艺参数失败")

    """
    回调函数
    """
    # 模式下拉列表回调
    def cbBox_Mode_Callback(self, text):
        if text == '1：MNIST随机抽取':
            self.mode = MODE_MNIST
            self.clearDataArea()
            self.pbtGetMnist.setEnabled(True)
            
            # 显示标签，隐藏画板
            self.lbDataArea.raise_()
            self.lbDataArea.setVisible(True)
            self.paintBoard.setVisible(False)
            
            self.paintBoard.setBoardFill(QColor(0,0,0,0))
            self.paintBoard.setPenColor(QColor(0,0,0,0))

        elif text == '2：鼠标手写输入':
            self.mode = MODE_WRITE
            self.clearDataArea()
            self.pbtGetMnist.setEnabled(False)
            
            # 隐藏标签，显示画板
            self.paintBoard.raise_()
            self.lbDataArea.setVisible(False)
            self.paintBoard.setVisible(True)

            # 更改背景
            self.paintBoard.setBoardFill(QColor(0,0,0,255))
            self.paintBoard.setPenColor(QColor(255,255,255,255))


    # 数据清除
    def pbtClear_Callback(self):
        self.clearDataArea()
        
        # 根据当前模式显示相应控件
        if self.mode == MODE_MNIST:
            self.lbDataArea.raise_()
            self.lbDataArea.setVisible(True)
            self.paintBoard.setVisible(False)
        else:
            self.paintBoard.raise_()
            self.lbDataArea.setVisible(False)
            self.paintBoard.setVisible(True)
 

    # 识别
    def pbtPredict_Callback(self):
        __img, img_array =[],[]      # 将图像统一从qimage->pil image -> np.array [1, 1, 28, 28]
        
        # 获取qimage格式图像
        if self.mode == MODE_MNIST:
            __img = self.lbDataArea.pixmap()  # label内若无图像返回None
            if __img == None:   # 无图像则用纯黑代替
                # 创建一个空白的QImage
                __img = QImage(224, 224, QImage.Format_RGBA8888)
                __img.fill(Qt.black)
            else: 
                __img = __img.toImage()
        elif self.mode == MODE_WRITE:
            __img = self.paintBoard.getContentAsQImage()

        # 转换成pil image类型处理
        pil_img = qimage_to_pil(__img)
        pil_img = pil_img.resize((28, 28), Image.LANCZOS)
        
        # 转换为灰度图
        pil_img = pil_img.convert('L')
        
        # pil_img.save('test.png')

        img_array = np.array(pil_img).reshape(1,1,28, 28) / 255.0
        # img_array = np.where(img_array>0.5, 1, 0)
    
        # reshape成网络输入类型 
        __result = network.predict(img_array)      # shape:[1, 10]

        # print (__result)

        # 将预测结果使用softmax输出
        __result = softmax(__result)
       
        self.result[0] = np.argmax(__result)          # 预测的数字
        self.result[1] = __result[0, self.result[0]]     # 置信度

        self.lbResult.setText("%d" % (self.result[0]))
        self.lbCofidence.setText("%.8f" % (self.result[1]))
        
        # 获取工艺参数
        self.current_params = self.param_manager.get_parameters(self.result[0])
        self.update_param_display(self.current_params)
        
        # 添加历史记录
        if self.current_params:
            self.history_manager.add_record(
                self.result[0], 
                self.result[1], 
                self.current_params
            )


    # 随机抽取
    def pbtGetMnist_Callback(self):
        self.clearDataArea()
        
        # 随机抽取一张测试集图片，放大后显示
        img = x_test[np.random.randint(0, 9999)]    # shape:[1,28,28] 
        img = img.reshape(28, 28)                   # shape:[28,28]  

        img = img * 0xff      # 恢复灰度值大小 
        pil_img = Image.fromarray(np.uint8(img))
        pil_img = pil_img.resize((224, 224))        # 图像放大显示

        # 将pil图像转换成qimage类型
        qimage = pil_to_qimage(pil_img)
        
        # 将qimage类型图像显示在label
        pix = QPixmap.fromImage(qimage)
        self.lbDataArea.setPixmap(pix)
        
        # 确保标签可见，画板不可见
        self.lbDataArea.raise_()
        self.lbDataArea.setVisible(True)
        self.paintBoard.setVisible(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    Gui = MainWindow()
    Gui.show()

    sys.exit(app.exec_())