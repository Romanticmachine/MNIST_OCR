# 智能制造零件识别系统

## 项目概述

这是一个基于深度学习的智能制造零件识别系统，面向智能制造实训车间，可实时识别加工零件编号并自动匹配/调整加工参数，实现"图像识别→工艺决策"的闭环控制。

![系统界面预览](image/mnist_gui.png)

## 功能特点

- **多模式输入**：支持随机抽取测试集图像和鼠标手写输入两种模式
- **实时识别**：基于CNN深度学习模型，实现高精度数字识别
- **工艺参数管理**：自动匹配识别结果对应的工艺参数
- **历史记录**：记录识别结果和对应的工艺参数，支持查询和管理
- **参数编辑**：支持手动编辑和调整工艺参数

## 安装指南

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/your-username/intelligent-manufacturing-recognition.git
cd intelligent-manufacturing-recognition
```

2. 安装依赖包

```bash
pip install -r requirements.txt
```

3. 运行主程序

```bash
python mnist_cnn_gui_main.py
```

## 使用说明

### 模式选择

- **模式1**：MNIST随机抽取 - 从测试集随机抽取图像进行识别
- **模式2**：鼠标手写输入 - 使用鼠标在输入区域手写数字

### 操作流程

1. 选择输入模式（随机抽取或手写输入）
2. 获取待识别数据（点击"随机抽取"或使用鼠标手写）
3. 点击"识别"按钮进行识别
4. 查看识别结果和对应的工艺参数
5. 可选：点击"修改工艺参数"按钮编辑参数
6. 可选：点击"查看历史记录"按钮查看历史识别记录

## 模型训练

如需重新训练模型，可使用以下命令：

训练简单CNN：

```bash
python train_convnet.py
```

训练深度CNN：

```bash
python train_deepnet.py
```

## 项目结构

```
.
├── common/                 # 通用功能模块
├── dataset/                # 数据集和数据处理
├── image/                  # 图像资源
├── qt/                     # Qt界面相关文件
├── deep_convnet.py         # 深度CNN网络定义
├── deep_convnet_params.pkl # 深度CNN训练参数
├── mnist_cnn_gui_main.py   # 主程序
├── params.pkl              # 模型参数
├── README.md               # 项目说明
├── requirements.txt        # 依赖库列表
├── simple_convnet.py       # 简单CNN网络定义
├── train_convnet.py        # 训练简单CNN的脚本
└── train_deepnet.py        # 训练深度CNN的脚本
```

## 贡献指南

欢迎提交问题和功能请求！如果您想贡献代码，请遵循以下步骤：

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 致谢

- 《深度学习入门-基于Python的理论与实现》
- MNIST数据集
