#  -*- coding: UTF-8 -*-
import sys
sys.path.append('D:\ProgramData\python27\Lib\site-packages')
sys.path.append('D:\Program Files\Dassault Systemes\SimulationServices\V6R2017x\win_b64\code\python2.7\lib')
# test to conferm that abaqus's core packages and local python2.7 site-packages
# are all added to sys.path 

# abaqus and abaqusConstants are in the abaqus core code lib
from abaqus import *
from abaqusConstants import *
# pandas is in the local python lib site-packages
print sys.path
import pandas as pd
print pd