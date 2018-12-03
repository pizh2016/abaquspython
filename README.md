#哈哈哈
#学习abaqus python二次开发

用ANSYS 做有限元分析很久了，功能很强大。无奈APDL语言实在是太太太太反人类了，相关书籍不成体系，用来做前后处理二次开发实在是难度略大，从log文件拷贝宏命令简单修改勉强能用，与主流开发语言相差太远，甚至连VBA都比他强，懒得折腾了orz  于是怒转ABAQUS!!!

目前 ABAQUS 二次开发有两种语言接口，求解器层次的FORTRAN接口和前后处理层次的Python接口。 你没有看错，就是Python！看来索达公司还是很有前瞻性的！人生苦短，赶紧燥起来吧！

# abaqus 安装
网上很多教程，我安装的是2017V6版本，内置python版本为python2.7.3版本（索达定制版）

# python环境
anaconda3(包管理强大) + vscode(颜值高), 安装好后用conda创建python2.7虚拟环境（配置参见网络教程），配置vscode在虚拟环境下运行（参见.vscode/task.json），ctrl + shift + B 运行 task

# packages 关联
默认情况下，本地python无法使用abaqus内置的核心python lib库，里面包含了如abaqus、abaqusConstants等核心函数库。而abaqus python也无法调用本地python环境中的第三方package如numpy、scipy等。所以在py文件中要加上以下语句将lib路径添加到解释器搜索路径sys.path中，这样不管用哪个解释器运行任务task都能get到abaqus内置的核心pyc lib库和本地python虚拟环境中的第三方package。

"""
import sys
sys.path.append('D:\ProgramData\python27\Lib\site-packages')
sys.path.append('D:\Program Files\Dassault ystemes\SimulationServices\V6R2017x\win_b64\code\python2.7\lib')
"""
运行abaqus python脚本需要在vscode的命令行窗口或本地命令行窗口输入 abaqus cae noGUI=xxxx.py 或者 abaqus cae script=xxxx.py 或者打开abaqus CAE窗口点击File->Run Script 选择当前 xxxx.py文件

受限于ABAQUS 的 license 机制，第三方IDE直接调试带有abaqus python的脚本是不行的（from abaqus import * 会报错），因为没有特定的解释器（abaqus内置了很多个python解释器用于不同的模块）能调用core code， 然而命令行abaqus cae noGUI却能使用，这玩意儿对应某个abaqus内置exe可执行程序，把它设置为vscode的python.pythonpath 不能识别！欢迎有经验的大神前来补充和解答。

#等我想起来再写吧，溜了溜了
