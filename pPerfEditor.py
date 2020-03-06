"""
##################################################################################################
This file reads in a PERF file and displays it as a tree. 
TODO:
	Nodes can be added and deleted.
	Edit contents of nodes
##################################################################################################
"""
import os
import sys
import string
from  Tree import *
from Plex import *
import pLexicon
import sys
from Tkinter import *
import Pmw

class pPerfBaseClass:
	def __init__(self,id=''):
		self.id = id
		self.tag = 'NONE'
		self.keywords = {}

	def getID(self):
		return self.id

	def addKeyword(self,ky,vl):
		self.keywords[ky]=vl

class pPerfDate(pPerfBaseClass):
	def __init__(self,dt=''):
		pPerfBaseClass.__init__(self,dt)
		self.wells = []
		self.tag = 'DATE'
		
	def addWell(self,w):
		self.wells.append(w)

	def getNumberOfWells(self):
		return len(self.wells)

class pPerfThisWell(pPerfBaseClass):
	def __init__(self,nm=''):
		pPerfBaseClass.__init__(self,nm)
		self.perfs = []
		self.wellName = ''
		self.tag   = 'WELL'

	def addPerforation(self,pe):
		self.perfs.append(pe) 

	def getWellName(self):
		return self.wellName

	def setWellName(self,nm):
		self.wellName = nm

	def getNumberOfPerfs(self):
		return len(self.perfs)

class pPerfNode(pPerfBaseClass):
	def __init__(self,id,wn):
		pPerfBaseClass.__init__(self,id)
		self.tag = 'PERF'
		self.wellName = wn

	def getWellName(self):  # For this perforation
		return self.wellName 


class pPerfFileReader:
	def __init__(self):
		self.ST_IDLE = 0
		self.ST_IN_DATE    = 1
		self.ST_IN_WELL    = 2
		self.ST_IN_PERF    = 3
		self.lastWell = ""
		self.allDates = []
		self.allNodes = {}
		self.lastWells = None

	def convertFile(self,scanner,fdout):
		self.state = 0
		self.lastDate = ""
		self.nodeCounter = 0
		while 1: 
			token = scanner.read()          # Check for input end
			if token[0] == None: break;
			elif token[1] == 'DATE': 		# Check end condition
				token = scanner.read()      # Read next token
				self.lastDate = 'DATE_' + token[1]    # for the actual value
				self.thisDate = pPerfDate(self.lastDate)
				self.allDates.append(self.thisDate)
				self.allNodes[self.lastDate] = self.thisDate
				self.thisWell = None
				continue
			elif token[1] == '&WELL':      # got another well
				value = scanner.read()     # Read 'Name' keyword
				value = scanner.read()     # Read next token for well name 
				id = 'W_' + value[1] + '_' + self.lastDate # W_WELLNAME_DATE
				self.thisWell = pPerfThisWell(id)       # 
				self.thisWell.setWellName(value[1])
				self.allNodes[id] = self.thisWell
				self.allNodes[self.lastDate].addWell(self.thisWell)
				self.state = self.ST_IN_WELL
				continue
			elif token[1] == '&PERF':        # 
				self.state = self.ST_IN_PERF
				self.nodeCounter += 1; 
				self.nodeID = 'P_' + str(self.nodeCounter)
				self.thisPerf = pPerfNode(self.nodeID,self.thisWell.getID())
				self.thisWell.addPerforation(self.thisPerf)
				self.allNodes[self.nodeID] = self.thisPerf
				continue
			if self.state == self.ST_IN_WELL:
				if token[0] == 'eob':          # Otherwise read the value
					self.state = self.ST_IN_DATE
					continue
				if token[0] == 'ident':        # Otherwise read the value
					value = scanner.read()     # Read next token
					self.thisWell.addKeyword(token[1],value[1]);
					continue
			if self.state == self.ST_IN_PERF:
				if token[0] == 'eob':          # Otherwise read the value
					self.state = self.ST_IN_WELL
					continue
				if token[0] == 'ident':        # Otherwise read the value
					value = scanner.read()     # Read next token
					self.thisPerf.addKeyword(token[1],value[1]);
					continue
					

###################################################################
# 
###################################################################
def get_contents(obj,node):
	myname = node.full_id()     # get the list of parent ids, and self.
	fullname = string.join(myname,'/')
	outstr = ''
	if fullname == 'perfs':
		for dt in myHandler.allDates:
			thisID = dt.getID()
			t.add_node(name=thisID,id=thisID, flag=1)
	else:
		print myname, fullname
		node = myHandler.allNodes[myname[-1]]
		print node.tag
		if node.tag == 'DATE':
			for wl in node.wells:
				print wl.getID(), " has ", wl.getNumberOfPerfs()
				if wl.getNumberOfPerfs() > 0: 
					t.add_node(name=wl.getWellName(),id=wl.getID(), flag=1)
				else:	
					t.add_node(name=wl.getWellName(),id=wl.getID(), flag=0)
		if node.tag == 'WELL':
			print len(node.perfs), node.getID()
			for pe in node.perfs:
				t.add_node(name=pe.getID(),id=pe.getID(), flag=1)
		if node.tag == 'PERF':
			node = myHandler.allNodes[myname[-1]]
			print myname, node
			for k in node.keywords.keys():
				thisID = node.keywords[k]
				lbl = k + ":" + thisID
				outstr = outstr + lbl + '\n'
				t.add_node(name=lbl,id=thisID, flag=0)
	editBox.settext(outstr)
		
def buttonPress(b):
	print "Hey -> ", b

#
# The main program that displays your tree. 
#
if __name__ == '__main__':
	root=Tk()
	root.title("Perforations viewer")

	f = open(sys.argv[1],'r')
	scanner = Scanner(pLexicon.ratesLexicon, f, sys.argv[1])
	myHandler = pPerfFileReader()
	myHandler.convertFile(scanner,sys.stdout)

	####
	#### Make a tree

	t=Tree(master=root, root_id='perfs', root_label='Perforations',
		get_contents_callback=get_contents, width=300)
	t.grid(row=0, column=0, sticky='nsew') 

	root.grid_rowconfigure(0, weight=1)
	root.grid_columnconfigure(0, weight=1)
	sb=Scrollbar(root)
	sb.grid(row=0, column=1, sticky='ns')
	t.configure(yscrollcommand=sb.set)
	sb.configure(command=t.yview)
	sb=Scrollbar(root, orient=HORIZONTAL)
	sb.grid(row=1, column=0, sticky='ew')
	t.configure(xscrollcommand=sb.set)
	sb.configure(command=t.xview) 
	t.focus_set()

   
	btnBox = Pmw.ButtonBox(root)
	btnBox.grid(row=2, column=0, columnspan=3)
	btnBox.add('Quit',   command=root.quit)
	btnBox.add('Add',    command= lambda b = 'add': buttonPress(b)) 
	btnBox.add('Del',    command= lambda b = 'del': buttonPress(b)) 
	
	editBox  = Pmw.ScrolledText(root,labelpos=N,label_text='Contents',usehullsize=1,
			hull_height=400,hull_width=300,text_wrap=None)
	editBox.grid(row=0,rowspan=2,column=2,sticky='nsew')
	
	# expand out the root 
	t.root.expand() 
	root.mainloop()
