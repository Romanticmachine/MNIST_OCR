#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame
from PyQt5.QtCore import Qt


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # 设置窗口大小
        MainWindow.resize(1000, 600)
        
        # 创建中央部件
        self.centralWidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralWidget)
        
        # 创建主布局
        self.mainLayout = QGridLayout(self.centralWidget)
        
        # 设置界面元素
        self.setup_ui_elements()
        
        # 设置窗口标题
        MainWindow.setWindowTitle("智能制造零件识别系统")
    
    def setup_ui_elements(self):
        # 创建说明标签
        self.lblInstructions = QLabel()
        self.lblInstructions.setText("""
        <b>使用说明</b>
        <p>1、点击下拉列表进行模式选择，输入待识别数据后点击"识别"按键进行识别</p>
        <p>2、经CNN网络计算后输出，显示识别结果与置信度值</p>
        <p>3、点击"清除"按键重新输入数据</p>
        <p>模式1：随机从测试集抽取图像作为待识别数据，点击"随机抽取"按键抽取</p>
        <p>模式2：使用鼠标在数据输入区域手写输入作为待识别数据</p>
        """)
        self.mainLayout.addWidget(self.lblInstructions, 0, 0, 1, 3)
        
        # 创建左侧控制区域
        self.controlFrame = QFrame()
        self.controlFrame.setFrameShape(QFrame.StyledPanel)
        self.controlLayout = QVBoxLayout(self.controlFrame)
        
        # 模式选择
        self.modeLayout = QHBoxLayout()
        self.lblMode = QLabel("模式选择:")
        self.modeLayout.addWidget(self.lblMode)
        
        self.cbBox_Mode = QComboBox()
        self.cbBox_Mode.addItem("1：MNIST随机抽取")
        self.cbBox_Mode.addItem("2：鼠标手写输入")
        self.cbBox_Mode.currentTextChanged.connect(self.cbBox_Mode_Callback)
        self.modeLayout.addWidget(self.cbBox_Mode)
        self.controlLayout.addLayout(self.modeLayout)
        
        # 添加按钮
        self.pbtGetMnist = QPushButton("随机抽取")
        self.pbtGetMnist.clicked.connect(self.pbtGetMnist_Callback)
        self.controlLayout.addWidget(self.pbtGetMnist)
        
        self.pbtClear = QPushButton("清除")
        self.pbtClear.clicked.connect(self.pbtClear_Callback)
        self.controlLayout.addWidget(self.pbtClear)
        
        self.pbtPredict = QPushButton("识别")
        self.pbtPredict.clicked.connect(self.pbtPredict_Callback)
        self.controlLayout.addWidget(self.pbtPredict)
        
        # 添加结果显示
        self.resultFrame = QFrame()
        self.resultFrame.setFrameShape(QFrame.StyledPanel)
        self.resultLayout = QVBoxLayout(self.resultFrame)
        
        self.lblResultTitle = QLabel("<b>识别结果:</b>")
        self.resultLayout.addWidget(self.lblResultTitle)
        
        self.lbResult = QLabel()
        self.lbResult.setStyleSheet("font-size: 48px; font-weight: bold;")
        self.lbResult.setAlignment(Qt.AlignCenter)
        self.resultLayout.addWidget(self.lbResult)
        
        self.lblConfidenceTitle = QLabel("<b>置信度:</b>")
        self.resultLayout.addWidget(self.lblConfidenceTitle)
        
        self.lbCofidence = QLabel()
        self.lbCofidence.setStyleSheet("font-size: 12px;")
        self.lbCofidence.setAlignment(Qt.AlignCenter)
        self.resultLayout.addWidget(self.lbCofidence)
        
        # 添加左侧控制区域和结果显示区域到主布局
        self.mainLayout.addWidget(self.controlFrame, 1, 0)
        self.mainLayout.addWidget(self.resultFrame, 1, 1)
        
        # 创建数据输入区域
        self.dataInputFrame = QFrame()
        self.dataInputFrame.setFrameShape(QFrame.StyledPanel)
        self.dataInputLayout = QVBoxLayout(self.dataInputFrame)
        
        self.lblDataTitle = QLabel("数据输入区域")
        self.lblDataTitle.setAlignment(Qt.AlignCenter)
        self.dataInputLayout.addWidget(self.lblDataTitle)
        
        # 创建数据显示标签
        self.dArea_Layout = QVBoxLayout()
        self.lbDataArea = QLabel()
        self.lbDataArea.setAlignment(Qt.AlignCenter)
        self.lbDataArea.setMinimumSize(224, 224)
        self.lbDataArea.setStyleSheet("border: 2px solid black; background-color: white;")
        self.dArea_Layout.addWidget(self.lbDataArea)
        self.dataInputLayout.addLayout(self.dArea_Layout)
        
        # 添加数据输入区域到主布局
        self.mainLayout.addWidget(self.dataInputFrame, 1, 2)
        
        # 创建工艺参数区域
        self.paramFrame = QFrame()
        self.paramFrame.setFrameShape(QFrame.StyledPanel)
        self.paramLayout = QVBoxLayout(self.paramFrame)
        
        self.lblParamTitle = QLabel("<b>工艺参数</b>")
        self.paramLayout.addWidget(self.lblParamTitle)
        
        # 创建参数标签
        self.param_labels = {}
        param_keys = ['材料', '加工速度', '主轴转速', '进给量', '切削深度', '冷却液流量', '加工时间']
        
        for key in param_keys:
            label = QLabel(f"{key}: --")
            self.paramLayout.addWidget(label)
            self.param_labels[key] = label
        
        # 添加功能按钮
        self.btnLayout = QVBoxLayout()
        
        self.btn_history = QPushButton("查看历史记录")
        self.btn_history.clicked.connect(self.show_history)
        self.btnLayout.addWidget(self.btn_history)
        
        self.btn_edit_params = QPushButton("修改工艺参数")
        self.btn_edit_params.clicked.connect(self.edit_parameters)
        self.btn_edit_params.setEnabled(False)  # 初始禁用
        self.btnLayout.addWidget(self.btn_edit_params)
        
        self.paramLayout.addLayout(self.btnLayout)
        
        # 添加工艺参数区域到主布局
        self.mainLayout.addWidget(self.paramFrame, 2, 0, 1, 3)
        
        # 设置列宽比例
        self.mainLayout.setColumnStretch(0, 2)  # 控制区域
        self.mainLayout.setColumnStretch(1, 2)  # 结果显示区域
        self.mainLayout.setColumnStretch(2, 3)  # 数据输入区域
        
        # 设置行高比例
        self.mainLayout.setRowStretch(0, 1)  # 说明区域
        self.mainLayout.setRowStretch(1, 4)  # 主要操作区域
        self.mainLayout.setRowStretch(2, 2)  # 工艺参数区域
