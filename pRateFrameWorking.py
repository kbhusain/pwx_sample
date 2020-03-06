
"""
This file contains the code to display and information displayed from 
a tree constructed with the cRateFile object. 

"""
from Tkinter import *
import Pmw
import numarray
from tkMessageBox import showwarning
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
from pModifiableList import *
from pObject import *
from cRateParser import *
from TreeBrowser import *

class frameRateFileParameters(Frame):
	def __init__(self,master,rateObject=None):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=BOTH)
		self.frm_tree = Frame(self);
		self.m_treeBrowser = TreeBrowser(self.frm_tree)   # Get the delete 
		self.m_treeBrowser.pack(side=TOP,fill=BOTH,expand=1)
		self.frm_tree.pack(side=LEFT,fill=BOTH,expand=1)

		self.treeIsThere = 0

		# if rateObject <> None:  self.mapObjToGui(rateObject):
		
		self.buttonBox = Pmw.ButtonBox(self.frm_tree,labelpos='n',label_text='Actions')
		self.buttonBox.pack(side=BOTTOM,fill=X, expand=0,padx=0,pady=0)
		self.buttonBox.add('ADD DATE',command = lambda s=self :  s.m_addDate());
		self.buttonBox.add('DEL DATE',command = lambda s=self :  s.m_deleteDate());
		self.buttonBox.add('ADD WELL',command = lambda s=self :  s.m_addWell());
		self.buttonBox.add('DEL WELL',command = lambda s=self :  s.m_deleteWell());

		self.frm_details = Frame(self);
		#self.m_WellsPerDate = pModifiableList(self.frm_details,useThis=['None','Yet'])
		#self.m_WellsPerDate.pack(side=TOP,fill=X,expand=1)

		dummy = cRateFile()
		self.widgets = []

		lbl = Label(self.frm_details,text="Last Selected Well")
		lbl.pack(side=TOP,fill=X,expand=0)
		for nm in dummy.getAllowedKeywords():
			w = Pmw.EntryField(self.frm_details,labelpos=W,label_text=nm, validate=None)	
			val = w.component('entry')
			val['width']= 10
			w.pack(side=TOP,fill=X,expand=0)
			self.widgets.append(w)
		Pmw.alignlabels(self.widgets)
		self.btnSaveWell = Button(self.frm_details,text="Save Selected Well")
		self.btnSaveWell.pack(side=TOP,fill=X,expand=0)
		self.frm_details.pack(side=RIGHT,expand=1,fill=Y,pady=10)

		self.lastDate = None
		self.lastWell = None

	############################################################################yy
	# Tree manipulation functions
	############################################################################yy
	def m_addDate(self):
		if self.lastDate == None: return
		index = self.m_treeBrowser.index(self.lastDate)
		print "I will add a new date after " , index
		pass

	def m_deleteDate(self):
		if self.lastDate <> None: 
			print "I will delete a Date here.", type(self.lastDate.treeNode)
			self.m_treeBrowser.delete(self.lastDate.treeNode)
			self.lastDate = None

	def m_addWell(self):
		print "I will add a Well here."

	def m_deleteWell(self):
		if self.lastWell <> None: 
			print "I will delete a Well here.", type(self.lastWell.treeNode)
			self.m_treeBrowser.delete(self.lastWell.treeNode)
			self.lastWell = None


	def mapObjToGui(self,rateObject,forceTheIssue=0):
		#
		# Reconstruct the entire Pmw.Tree on the left 
		#
		self.myObject = rateObject
		if forceTheIssue == 1: self.treeIsThere = 0
		if self.treeIsThere == 1: return
		self.m_treeBrowser.destroy()
		self.m_treeBrowser = TreeBrowser(self.frm_tree)   # Get the delete 
		self.m_treeBrowser.pack(side=TOP,fill=BOTH,expand=1)
		self.allDateBranches = []
		self.allWellLeaves   = []
		for dt in self.myObject.allDates:        # Get the dates
			a = lambda s=self,k=dt: self.f_showDate(k)            # Create nodes.
			thisBranch = self.m_treeBrowser.addbranch(label=dt.sDateString,selectcommand=a) # This is for the simulator parms.
			self.allDateBranches.append(thisBranch)
			for well in dt.Wells.keys():
				daWell = dt.Wells[well]
				a = lambda s=self,k=daWell: self.f_showWell(k)
				thisLeaf = thisBranch.addleaf(label=well,selectcommand=a)
				self.allWellLeaves.append(thisLeaf)
				daWell.treeNode = thisLeaf

		self.treeIsThere = 1    # Finally, mark the existance of the tree in the memory area.

	def mapGuiToObj(self,rateObject):
		# Create an entire tree from the objects in t
		# from self.tree = []
		pass 

	def f_saveDate(self,well):
		# Collect the stuff from the form on frm_item and plunk it into the well
		if self.lastWell == None: 
			return 
		for w in self.widgets: 
			lbl = w.component('label')
			txt = lbl['text']             # Get the text
			val = w.get()
			if len(val) > 0: 
				self.lastWell.setKeywordValue(txt,val)   # Validate here @@@@!!!!LOOK I AM NOT DOING IT HERE 

	def f_showWell(self,kk):
		# 
		print "f_showWell ", kk
		for w in self.widgets: 
			lbl = w.component('label')
			txt = lbl['text']             # Get the text
			val = kk.getKeywordValue(txt)
			w.setentry(val)
			print txt, val
		self.lastWell = kk;


	def f_saveWell(self):
		pass
	
	def f_showDate(self,kk):
		# 
		print "f_showDate - Selected date object ", kk
		self.lastDate = kk
		self.lastWell = None
		pass
	

