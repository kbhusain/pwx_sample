
"""
Show 'BY WELL' information here. The list of wells are shown here and a list of
attributes per well collected from the recurrent, rates and perforations files. 
The user selects a well and one or more attributes to show the data as a list or
as a chart. 
"""

from pObject import *
from Tkinter import *
import Pmw
from tkMessageBox import showwarning, askyesno
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
from pModifiableList import *
from pObject import *
import pWellInfo 
import Tree 
import cPerfParser 
import cRateParser 
from TableList import *
import os
import string
from copy import copy
import datetime
import dateutil
from pSimplePlot import *

##########################################################################################
# Show 'BY WELL' information here.
##########################################################################################
class frameByWellParameters(Frame):
	def __init__(self,master,parserObject=None):
		Frame.__init__(self,master)
		self.parserObject = parserObject
		self.pack(expand=YES,fill=X)
		self.gcFrame = Frame(self)
		self.gcFrame.pack(side=LEFT,fill=X,expand=0)
		self.cbWellNames = Pmw.ComboBox(self.gcFrame,labelpos=W, label_text='Wells', listheight=360, dropdown=1, scrolledlist_items=[], 
			selectioncommand = self.mf_selectWell)
		e = self.cbWellNames.component('entryfield')
		t = e.component('entry'); t['width'] = 15
		self.cbWellNames.pack(side=TOP,expand=0,fill=X)
		self.listParmsPerWell = Pmw.ScrolledListBox(self.gcFrame,
			items = [],	labelpos = N, 
			label_text = 'Parameters', listbox_exportselection=0,
			listbox_selectmode = EXTENDED,
			selectioncommand = self.mf_selectAttribute,
			usehullsize=1, hull_width=50, hull_height=150)
		self.listParmsPerWell.pack(side=TOP,fill=BOTH,expand=YES)
		self.Wpg_buttonBox = Pmw.ButtonBox(self.gcFrame,padx=0,pady=0,orient=VERTICAL)
		self.Wpg_buttonBox.pack(side=TOP,fill=X,expand=0)
		#self.Wpg_buttonBox.add('Show',command = lambda s=self :  s.m_getData())

		self.Wpg_buttonBox.add('Show',command = lambda s=self :  s.m_getData2())
		self.Wpg_buttonBox.add('Clear',command = lambda s=self :  s.m_clrData())
		self.Wpg_buttonBox.add('Save',command = lambda s=self :  s.m_saveData())
		self.outFrame = Frame(self)
		self.outFrame.pack(side=LEFT,expand=1,fill=BOTH)
					
		self.nb= Pmw.NoteBook(self.outFrame)
		self.tabText = self.nb.add('Text') 			 # For general parameters.
		self.tabGraph = self.nb.add('Graph')			# For INPUT file specifiers
		self.nb.pack(padx=5,pady=5,fill=BOTH,expand=1)
		self.m_textWindow = Pmw.ScrolledText(self.tabText,labelpos=N,label_text='Text',text_wrap='none')
		self.m_textWindow.pack(side=TOP,fill=BOTH,expand=1)
		self.daGraph = pSimpleXYPlotter(self.tabGraph)

	def mf_selectWell(self,parm):
		print "Selected ... ", parm
		if self.parserObject==None: return
		scolumns = self.listParmsPerWell.getcurselection()
		if len(scolumns) < 1: return
		self.m_getData2()

	def mf_selectAttribute(self):
		if self.parserObject==None: return
		wname = self.cbWellNames.get()
		print "Selected ... ", wname
		scolumns = self.listParmsPerWell.getcurselection()
		if len(scolumns) < 1: return
		self.m_getData2()


	def m_getData2(self):
 		if self.parserObject==None: return
		arr = []
		wname = self.cbWellNames.get()
		welldates = self.parserObject.allDatesPerWell.get(wname,None)
		if welldates == None: return 
		scolumns = self.listParmsPerWell.getcurselection()
		columns = []
		for n in scolumns: columns.append(n)
		columns.sort()
		if len(columns) < 1: return
		vectors = {}
		vectors['DATE'] = []
		for nm in columns: vectors[nm] = []

		lastvalue = copy(vectors)
		ncolumns = len(vectors.keys())
		for nm in columns: lastvalue[nm] = 0.0

		fmtstr = '%s ' + ' %f' * (ncolumns-1)
		
		dates = self.parserObject.allDatesArray.keys()
		dates.sort()
		allstrs = []
		plotdates = []

		xstr = 'DATE'
		for nm in columns: xstr += '%10s ' % nm
		xstr += '\n'
		allstrs.append(xstr)
		
		for dn in dates:
			dte = self.parserObject.allDatesArray[dn]
			lastvalue['DATE'] = dte.sIdString
			d1 =datetime.date(int(dte.year),int(dte.month),int(dte.day))
			plotdates.append(d1.toordinal())
			
			if not dn in welldates:
				for nm in columns:
					vectors[nm].append(lastvalue[nm])
			else:
				wellObject = dte.Wells[wname]	  # Get definition of well at date.
				for nm in columns:
					value = wellObject.getKeywordValue(nm)
					if len(value) > 1:
						fv = float(value)
						lastvalue[nm] = fv
					vectors[nm].append(lastvalue[nm])
			xstr = lastvalue['DATE'] 
			for nm in columns:
				xstr += ' ' + '%10.3f' % lastvalue[nm]
			xstr += '\n'
			allstrs.append(xstr)
		self.m_textWindow.settext("".join(allstrs))
		markThesePlots = [];
		self.daGraph.m_colorIndex = 0					# Be consistent with colors
		self.daGraph.m_plotType = 'dates'
		for nm in columns:
			lbl = wname + ':' + nm
			self.daGraph.setTupleData(lbl,plotdates,vectors[nm])
			markThesePlots.append(lbl)
		self.daGraph.showTheseOnly(markThesePlots)
		self.daGraph.m_plotType = 'dates'
		self.daGraph.redraw()
		
	def m_getData(self):
		if self.parserObject==None: return
		arr = []
		keys = self.parserObject.allDatesArray.keys()
		keys.sort()
		for key in keys:
			dte = self.parserObject.allDatesArray[key]
			xstr = dte.sIdString + "\n"
			arr.append(xstr)
		self.m_textWindow.settext("".join(arr))
			
	def m_clrData(self):
		self.m_textWindow.settext('')

	def m_saveData(self):
		fname = asksaveasfilename(filetypes=[("Text","*.txt"),("All Files","*")])
		if fname=='': return
		if fname==None: return
		fd = open(fname,"w")
		fd.write(self.m_textWindow.get())
		fd.close()

				
	def m_setWellList(self,names):
		sb = self.cbWellNames.component('scrolledlist')
		sb.setlist(names)
			
	def makeComboBox(self,where,txt,opts,lw=15):
		w = Pmw.ComboBox(where,labelpos=W, label_text=txt, listheight=360, dropdown=1, scrolledlist_items=opts, 
			selectioncommand = self.mf_selectGroupWell)
		e = w.component('entryfield')
		t = e.component('entry')
		t['width'] = lw
		return w


	def mapObjToGui(self,parserObject):
		self.parserObject = parserObject

		names = self.parserObject.allDatesPerWell.keys()
		names.sort()
		sb = self.cbWellNames.component('scrolledlist')
		sb.setlist(names)

		self.listParmsPerWell.setlist(pWellInfo.sPlottableWellParms)
		

	def mapGuiToObj(self,parserObject):
		parserObject = self.parserObject

