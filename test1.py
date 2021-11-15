#  -*- coding: UTF-8 -*-
import sys
# sys.path.append('C:\ProgramData\python27\Lib\site-packages')
# sys.path.append('C:\Program Files\Dassault Systemes\SimulationServices\V6R2017x\win_b64\code\python2.7\lib')
# test to conferm that abaqus's core packages and local python2.7 site-packages
# are all added to sys.path 

# abaqus and abaqusConstants are in the abaqus core code lib
from odb_Access import *
print sys.path

from abaqus import *
from abaqusConstants import *
