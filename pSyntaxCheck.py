
import sys 
import os
from time import *
from Tkinter import *
from guiModelFrames import frameSyntaxErrors
from cModelParser import *
from pPBFutils  import *

if __name__ == '__main__': 
	if (len(sys.argv) < 2): print "Usage : xx filename " ; sys.exit(0)
	filename = sys.argv[1]
	model = modelFileParser();
	#model.verbose = v         # global 
	thisdir = os.getcwd()
	os.chdir(os.path.dirname(filename))
	model.readModelFile(filename); 
	estr = model.getListOfErrors()
	xstr = model.collectSyntaxErrors()
	os.chdir(thisdir)

	root = Tk()
	fe = frameSyntaxErrors(root,ingui=0)
	fe.clearErrors()
	fe.appendErrors(estr)
	fe.appendErrors(xstr)
	fe.showErrors()
	root.mainloop()
		

