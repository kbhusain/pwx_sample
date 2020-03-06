
import os
from sys import *


a = os.getenv("POWERSBASEDIR")
if a == None :  a = os.getenv("HOME") + os.sep + "powersData"
powers_Base_Directory = a
