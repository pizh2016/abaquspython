# 学习abaqus python二次开发
## 接口选择
目前 ABAQUS 二次开发有两种语言接口，求解器层次的FORTRAN接口和前后处理层次的Python接口。 你没有看错，就是Python！看来索达公司还是很有前瞻性的！人生苦短！


## python环境
anaconda3(包管理强大) + vscode(颜值高), 安装好后用conda创建python2.7虚拟环境（配置参见网络教程），配置vscode在虚拟环境下运行（参见.vscode/task.json），ctrl + shift + B 运行 task

# packages 关联
2019版本已支持numpy，在abaqus python中也能使用原生numpy了,版本仍然是python2.7

## 关联
默认情况下，本地python无法使用abaqus内置的核心python lib库，里面包含了如abaqus、abaqusConstants等核心函数库。而abaqus python也无法调用本地python环境中的第三方package如numpy、scipy等。所以在py文件中要加上以下语句将lib路径添加到解释器搜索路径sys.path中，这样不管用哪个解释器运行任务task都能get到abaqus内置的核心pyc lib库和本地python虚拟环境中的第三方package。


"""

import sys

sys.path.append('C:\ProgramData\python27\Lib\site-packages')

sys.path.append('C:\Program Files\Dassault ystemes\SimulationServices\V6R2017x\win_b64\code\python2.7\lib')

"""


## 运行
运行abaqus python脚本需要在vscode的命令行窗口或本地命令行窗口输入 abaqus cae noGUI=xxxx.py 或者 abaqus cae script=xxxx.py 或者打开abaqus CAE窗口点击File->Run Script 选择当前 xxxx.py文件，如果不依赖cae模块(只处理odb)可以使用 abaqus python xxxx.py 命令调用abaqus内置解释器


受限于ABAQUS 的 license 机制，第三方IDE直接调试带有abaqus python的脚本是不行的，而命令行abaqus cae noGUI 和 abaqus python却能使用，把它设置为vscode的python.pythonpath，并且在task.json文件中新增task，"command"设置为"abaqus"，"args"中添加相应的指令即可。

"""
"tasks": 
   [ 
   
        {
            "label": "Abaqus python",
            "type": "shell",
            "command": "abaqus",
            "args": ["python","${file}"], 
            "group": {
                "kind": "build",  
                "isDefault": true  
            }
        },

        {
            "label": "Abaqus CAE",
            "type": "shell",
            "command": "abaqus",
            "args": ["cae","script=${file}"],
            "group": {
                "kind": "build",
                "isDefault": true  
            }
        },
    ]
    
"""


# 测试

"wire_lattice_Zscale.py" 用CAE生成基于wire的梁单元模型，使用命令 "abaqus cae script=wire_lattice_Zscale.py"(ctrl + shift + B 运行 task，选择 Abaqus CAE )

"wire_odbAccess.py" 查看ODB的historyOutputs，使用命令 "abaqus python wire_odbAccess.py" (ctrl + shift + B 运行 task，选择 Abaqus python )

