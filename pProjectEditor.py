"""
Essentially the file that manages the input files required by the POWERS deck. I will add fields 
to the thing as necessary.

TODO
	Add the base name
	Fill in defaults from a text file. 
"""

from Tkinter import *
from tkSimpleDialog import * 
from tkMessageBox import * 
from tkFileDialog import *
import sys
import pProjectDefaults 
import string

from guiModel import editModelFile

##########################################################################
# The project management begins here. I have to create a directory in 
# the folder pointed at by $BASEPOWERSDIR. The default is of course, your
# home directory. 
# 
# 
##########################################################################

fields =( 
		('Project Name', None),
		('  Model File',  None), 
		('  Perfs File',  'PERFS'), 
		('  Rates File', None), 
		('   Recurrent', None)
		)

# Global window handles
filename = None
perfEdit = None
modelEdit = None

def fetch(s,handle):
	print "Input = ", s.get()
	if handle == 'MODEL': modelEdit = editModelFile(s.get(),0)

def makeTheForm(root,fields):
	entries = []
	for field,callhandle in fields:
		row = Frame(root)
		row.pack(side=TOP)
		lbl =Label(row,width=12,text=field)
		lbl.pack(side=LEFT)
		ent =Entry(row,width=64)
		ent.pack(side=LEFT,expand=YES,fill=X)
		a = lambda s=ent : fetch(s,callhandle)
		btn =Button(row,text='Edit',command=a)
		btn.pack(side=RIGHT,expand=NO,fill=X)
		entries.append(ent)
	return entries


def saveProject(entries):
	ofile = asksaveasfilename(filetypes=[("inf","*.inf"),("All Files","*")])		
	if len(ofile) < 1: return 
	fd = open(ofile,'w')
	k = 0
	for ent in entries:
		sx = str(k) + ':' 
		fd.write(sx + ent.get() + "\n")	
		k = k + 1
	fd.close()

def openProject(entries):
	ifile = askopenfilename(filetypes=[("inf","*.inf"),("All Files","*")])		
	if len(ifile) < 1: return 
	lines = open(ifile,'r').readlines()
	for ln in lines:
		if len(ln) < 2:  continue
		if ln[0] == '#': continue
		items = string.split(ln,':')
		#k = len(items)
		k = int(items[0])
		if k < len(entries): 
			entries[k].delete(0,END)
			entries[k].insert(0,string.strip(items[1]))

if __name__ == '__main__':	
	mainWindow=Tk()
	me = makeTheForm(mainWindow,fields)
	fm = Frame(mainWindow)

	fm.pack(side=BOTTOM,fill=X,expand=YES)
	a = lambda m=me : saveProject(m)
	bs = Button(fm,text='Save Project',command=a)
	bs.pack(side=LEFT)

	fm.pack(side=BOTTOM,fill=X,expand=YES)
	a = lambda m=me : openProject(m)
	bs = Button(fm,text='Open Project',command=a)
	bs.pack(side=LEFT)

	qt = Button(fm,text='Quit',command=sys.exit)
	qt.pack(side=RIGHT)
	mainWindow.mainloop()

