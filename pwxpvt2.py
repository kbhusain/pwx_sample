#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4.1 on Sun Oct 15 10:56:24 2006

import sys, os
import wx
import wx.grid
import numarray
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.numerix import arange, sin, pi
import pylab
import string 
from pObject import *
from pSATTables import *
from pPVTTables import *
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import escape
from pwxSimplePlot import pwxSimpleXYPlotter, pwxPlotHolder

class pwxPVTframe(wx.Frame):
	def __init__(self, *args, **kwds):
		self.satorpvtparms =  None
		self.selectedColumns = []
		self.filename = ''
		# begin wxGlade: pwxPVTframe.__init__
		kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
		self.sizer_5_staticbox = wx.StaticBox(self, -1, "Tables")
		self.sizer_4_staticbox = wx.StaticBox(self, -1, "Controls")
		self.button_readfile = wx.Button(self, -1, "Read File")
		self.button_replot = wx.Button(self, -1, "Re-plot")
		self.button_savefile = wx.Button(self, -1, "To\nSpreadsheet")
		self.button_editfile = wx.Button(self, -1, "Edit File")
		self.list_box_1 = wx.ListBox(self, -1, choices=[], style=wx.LB_SINGLE|wx.LB_ALWAYS_SB)
		self.button_quit = wx.Button(self, -1, "Quit")
		self.window_1_pane_1 = pwxGraphPanel(self.window_1,-1,masterframe=self)
		self.window_1_pane_2 = pwxGridPanel(self.window_1,-1,masterframe=self)

		self.__set_properties()
		self.__do_layout()
		# end wxGlade
		
		self.Bind(wx.EVT_BUTTON,self.readFile,self.button_readfile)
		self.Bind(wx.EVT_BUTTON,self.toVim,self.button_editfile)
		self.Bind(wx.EVT_BUTTON,self.toSpreadsheet,self.button_savefile)
		# self.Bind(wx.EVT_BUTTON,self.deleteTable,self.m_deleteTableBtn)
		self.Bind(wx.EVT_BUTTON,self.replotTable,self.button_replot)
		self.Bind(wx.EVT_LISTBOX,self.selectedTableHandler,self.list_box_1)
		self.Bind(wx.EVT_BUTTON,self.doQuit,self.button_quit)
		
	def doQuit(self,event):	self.Destroy()
	
	def saveFile(self,event): 
		odlg = wx.FileDialog(self,message="Save a file", style=wx.SAVE,
				wildcard="SAT PVT File (*.inc)|*.inc|SAT PVT File (*.prn)|*.prn|All Files |*.*", 
				defaultFile="*.inc",
				defaultDir=os.getcwd())
		if odlg.ShowModal() == wx.ID_OK:
			fname = odlg.GetPath()
			self.m_saveTableToDisk(fname)

	def toSpreadsheet(self,event):
		odlg = wx.FileDialog(self,message="Save a file", style=wx.SAVE,
				wildcard="Spreadsheet File (*.csv)|*.csv|All Files | *.*", 
				defaultFile="*.csv",
				defaultDir=os.getcwd())
		if odlg.ShowModal() == wx.ID_OK:
			fname = odlg.GetPath()
			f,ext = os.path.splitext(fname)
			if not ext == '.csv': fname = fname + ".csv"
			self.m_saveTableToDisk(fname)
			if os.fork() == 0: 
				os.execl('/usr/bin/oocalc',"oocalc", "-calc", "-quickstart", fname)

	def toVim(self,event):
		if os.fork() == 0: 
			os.execl('/usr/X11R6/bin/gvim',"gvim", self.filename)




	def selectedTableHandler(self,event):
		print "selectedTableHandler", event.GetString(), event.GetInt() # if you want to get the string selected.
		self.window_1_pane_1.mainTitle = self.filename  + "\n" + event.GetString()
		self.showTableData(event.GetInt() )
		print self.selectedColumns
		self.window_1_pane_2.setSelectedColumns(self.selectedColumns)
		self.replotTable(self.selectedColumns)
		
	def readFile(self,event): self.readTable()
	#def deleteTable(self,event): print "Delete", self.listOfTables.GetSelection()
	#def importFile(self,event):self.masterframe.importTable()
	def replotTable(self,event): 
		self.selectedColumns = self.window_1_pane_2.getSelectedColumns()
		self.plotTheTable(self.selectedColumns)
		
	def setListOfTables(self,slist): self.listbox_1.Set(slist)

	def plotTheTable(self,cols):
		"""
		# Step 1. Determine selected columns.
		# Step 2. Collect the data from each column and create an array.
		# Step 3. Collect the names for each column from the table for labels.
		# Step 4. Send the data to the plotting program for plotting.
		"""
		print "names = ",  cols 
		if cols <>  None:	self.window_1_pane_2.setSelectedColumns(cols)
		data = []
		tbl =  self.window_1_pane_2.mypvttable
		rows = tbl.GetNumberRows()       # Get the number of rows.
		rlen = range(rows)
		for col in cols: 
			va = [ tbl.GetValue(row,col) for row in rlen ]
			data.append(numarray.array(map(float,va),'f'))
		# I have not tested to see if floats were entered... I have to check this.
		names = self.window_1_pane_2.getSelectedColumnNames(cols)
		self.window_1_pane_1.m_plotTable(names,data)

	def showTableData(self, tableIndex): 
		self.window_1_pane_2.showTableData(tableIndex)
		
	def __set_properties(self):
		# begin wxGlade: pwxPVTframe.__set_properties
		self.SetTitle("PVT SAT Table Viewer")
		self.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
		#self.button_savefile.Enable(False)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: pwxPVTframe.__do_layout
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3 = wx.BoxSizer(wx.VERTICAL)
		sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
		sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
		sizer_4.Add(self.button_readfile, 1, wx.EXPAND, 0)
		sizer_4.Add(self.button_replot, 0, wx.EXPAND, 0)
		sizer_4.Add(self.button_editfile, 1, wx.EXPAND, 0)
		sizer_4.Add(self.button_savefile, 1, wx.EXPAND, 0)
		sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
		sizer_5.Add(self.list_box_1, 1, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_3.Add(sizer_5, 1, wx.EXPAND, 0)
		sizer_3.Add(self.button_quit, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
		sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
		self.window_1.SplitHorizontally(self.window_1_pane_1, self.window_1_pane_2,sashPosition=-100)
		sizer_2.Add(self.window_1, 1, wx.EXPAND, 0)
		sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
		self.SetAutoLayout(True)
		self.SetSizer(sizer_1)
		sizer_1.Fit(self)
		sizer_1.SetSizeHints(self)
		self.Layout()
		# end wxGlade

	def readTable(self):
		fname = self.getOpenFileName() 
		if fname == None: return 
		self.processInputFilen(fname)


	def processInputFilen(self,fname):
		incominglines = open(fname,"r").readlines()  # Read the line.
		self.satorpvtparms.resetTables()             # Set the count to zero 
		self.window_1_pane_1.satorpvtparms  = self.satorpvtparms
		self.window_1_pane_2.satorpvtparms = self.satorpvtparms
		self.filename = fname 
		self.SetTitle("Using "+fname)
		for xline in incominglines:                  # Parse the table
			ilo = pLineObject(xline)                 # One line at at time 
			self.satorpvtparms.parseLine(ilo)        # 
		# print "I have read the table. ", self.satorpvtparms.getEditableString()
		self.satorpvtparms.initKeywordIndices()
		self.window_1_pane_2.clearGrid() 
		self.m_resetTable()         # Show the tables in the list box.
		self.m_resetEntries()              

	def addTable(self,event):
		"""
		Does nothing. We don't edit files. 
		"""
		pass

	def m_createNewTable(self,numberOfColumns):
		"""
		Starts a new table from scratch . This has a nest of problems. I will 
		probably export this to another application like oocalc.
		"""
		if number < 2 or number > 8: 
			return 
		g1 = ['GRAPH_LABELS']
		u1 = ['GRAPH_UNITS']
		for i in range(number):
			g1.append(' NAME%d' % i)
			u1.append(' UNIT%d' % i)
		glbls = "".join(g1)
		gunit = "".join(u1)
		lineNumber = 1
		ilo = pLineObject('TABLE')
		self.satorpvtparms.parseLine(ilo)
		ilo = pLineObject(glbls)
		self.satorpvtparms.parseLine(ilo)
		ilo = pLineObject(gunit)
		self.satorpvtparms.parseLine(ilo)
		ilo = pLineObject('ENDTABLE')
		self.satorpvtparms.parseLine(ilo)
		self.m_resetTable()

	def m_saveTableToDisk(self,fname):
		fd = open(fname,"w")
		k = 1
		for tbl in self.satorpvtparms.tablesArray:        # A list of Line objects
			fd.write('TABLE %d\n' % k)
			for xstr in tbl:
				fd.write(xstr.getRawLine())
			fd.write('ENDTABLE %d\n\n' % k)
			k = k + 1
		fd.close()

	def deleteTable(self, tableIndex ):
		if self.satorpvtparms == None: return
		r =  self.satorpvtparms.removeTable(tableIndex)
		self.window_1_pane_2.showTableData(tableIndex)

	def getOpenFileName(self):
		"""
		shows a FileDialog, and return the selected file name. 
		"""
		dlg = wx.FileDialog(self,"Read table data", os.getcwd(),
			style=wx.OPEN | wx.CHANGE_DIR,
			defaultFile = "*.inc", 
			wildcard = "INCLUDE (*.inc) |*.inc|PVT or SAT |*.prn |All Files |*.*")
		fname = None
		if dlg.ShowModal() == wx.ID_OK: fname = dlg.GetPath()
		dlg.Destroy()
		return fname

	def m_resetTable(self):
		"""
		Set the list of tables in the list box.
		"""
		slist = [ "TABLE %d" % (i+1) for i in range(len(self.satorpvtparms.tablesArray)) ]
		self.list_box_1.Set(slist)

	def m_resetEntries(self):
		"""
		Please find a way to show this information in a table. I think a grid will work.
		"""
		pass 

	
# end of class pwxPVTframe

class myGenericTable(wx.grid.PyGridTableBase):
	"""
	##########################################################################################
	#  The backend of tables. The user can make changes to the data and have them reflected.
	##########################################################################################
	"""
	def __init__(self,data,rowLabels=None,colLabels=None):
		wx.grid.PyGridTableBase.__init__(self)
		self.data = data
		self.rowLabels = rowLabels
		self.colLabels = colLabels
		self.glabels = self.data[0]
		self.gunits  = self.data[1]
		glen = len(self.data[0])
		self.columnNames = [ '%s\n%s' % (self.glabels[i],self.gunits[i]) for i in range(glen)]

	def GetNumberRows(self):
		return len(self.data) -2 

	def GetNumberCols(self):
		return len(self.data[0])

	def GetColLabelValue(self,col):
		return self.columnNames[col]

	def GetRowLabelValue(self,row):
		return "%s" % (row + 1)

	def IsEmptyCell(self,row,col):
		return False

	def GetValue(self,row,col):
		thisrow = self.data[row+2]
		return thisrow[col]

	def SetValue(self,row,col,value):
		thisrow = self.data[row+2]
		thisrow[col] = value

class pwxGridPanel(wx.Panel):
	def __init__(self,parent,id=-1,masterframe=None):
		wx.Panel.__init__(self,parent,id)
		self.masterframe  = masterframe
		self.satorpvtparms = self.masterframe.satorpvtparms
		self.mypvttable = None
		self.rsizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.grid.Grid(self)
		self.grid.CreateGrid(5,6)            # 
		aa = numarray.arange(30)
		aa.resize(5,6)                                 # I have to set the data here.
		for i in range(5):
			for j in range(6):
				self.grid.SetCellValue(i,j,'%d'% aa[i][j])
		self.rsizer.Add(self.grid,1,wx.TOP | wx.LEFT | wx.GROW)
		self.SetSizer(self.rsizer)
		self.SetAutoLayout(True)

	def setSelectedColumns(self,slen):
		for c in slen: self.grid.SelectCol(c,1)  

	def getSelectedColumns(self):
		return self.grid.GetSelectedCols()  

	def getSelectedColumnNames(self,cols):
		return  [ self.mypvttable.GetColLabelValue(c) for c in cols]

	def showTableData(self, tableIndex): 
		if self.satorpvtparms == None: return 
		if tableIndex < 0 or tableIndex >= len(self.satorpvtparms.tablesArray): return 
		tbl = self.satorpvtparms.tablesArray[tableIndex]      # get the date for it
		self.gtable  = []   # All the strings in the table.
		self.glabels = []   # All the column names  
		self.gunits  = []
		self.columnNames = []
		 
		 # Make a table for these
		 # self.names = self.satorpvtparms.specificParameters and 
		 # 'BUBBLE_POINT_PRESSURE' 'STANDARD_DENSITY_OIL',
		 # 'STANDARD_DENSITY_WATER','STANDARD_DENSITY_GAS'
		
		self.m_str_bubble = ""
		self.m_str_density = "" 
		for xln in tbl:
			xstr = xln.getRawLine()	
			items = xstr.split()               # Hello? What are you?
			token = items[0].strip()           # use only numbers
			if len(items) == 2:
				if token == 'BUBBLE_POINT_PRESSURE':  
					self.m_str_bubble = items[1]
				if token in ['STANDARD_DENSITY_OIL','STANDARD_DENSITY_WATER','STANDARD_DENSITY_GAS']:
					self.m_str_density =  items[1]
				continue
			if len(items) <= 2: continue            # Dont use special keywords TODO
			if find(items[0],'GRAPH_LABELS') == 0:  # Get the labels  
				ostr = [ "%12s " % item for item in items[1:] ]  
				self.gtable.append(ostr)
				self.glabels = items[1:]
				continue
			if find(items[0],'GRAPH_UNITS') == 0:   # Get the axes
				ostr = [ "%12s " % item for item in items[1:] ]  
				self.gtable.append(ostr)
				self.gunits = items[1:]
				continue
			if not token[0] in floatingDigits : continue
			ostr = [ "%12s " % x for x in items ]  
			self.gtable.append(ostr)
		self.mypvttable = myGenericTable(self.gtable)
		self.grid.SetTable(self.mypvttable)
		self.grid.ForceRefresh()
	
	def saveUserChanges(self):
		pass
		
	
	def clearGrid(self):
		self.grid.ClearGrid()

class pwxGraphPanel(wx.Panel):
	def __init__(self,parent=None,id=-1,masterframe=None):
		wx.Panel.__init__(self,parent,id)
		self.masterframe = masterframe 
		self.mainTitle = ''
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.m_myPlot = pwxSimpleXYPlotter(self,id)
		self.sizer.Add(self.m_myPlot, 1, wx.GROW | wx.TOP | wx.LEFT )
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
	
	def m_smoothColumn(self):
		return 
		smoothMe    = self.doSmooth.get()

		smoothOrder = int(self.smoothordercounter.get())
		rows = range(2,len(self.gtable))
		xd = []
		for i in rows: xd.append(self.columnarArray[i,0])
		xdata = numarray.array(map(float,xd), 'f')
		for cur in cursel:
			scur = cur.replace('-','_')
			k = self.glabels.index(scur) 
			dy = []
			for i in rows: dy.append(self.columnarArray[i,k])
			ydata = numarray.array(map(float,dy), 'f')
			pf = pylab.polyfit(xdata,ydata,smoothOrder)
			df = pylab.polyval(pf,xdata)
			#ydata = map("%6.3f",df.tolist())
			ydata = ["%6.3f" % x for x in df.tolist() ]
			# Now set the data back into the array.
			for i in rows: self.columnarArray[i,k] = ydata[i-2]
		#self.m_plotTable()

	def m_plotTable(self,names,values):
		"""
		You are passed an array of names and an array of values.	
		values[0] = x vector 
		values[1:] = y vectors 
		names[0] = x label, y1 label, etc.
		"""
		if len(values) < 1: return 
		smoothMe    = 0; #  Falsei
		smoothOrder = 3; # 
		
		self.m_myPlot.clearData()
		markThesePlots = []
		xdata = values[0]
		i = 1
		xtitle  = names[0].replace('\n', '-')
		ytitle = ''
		for nm in names[1:]: 
			ydata = values[i]
			name = nm.split()[0]
			self.m_myPlot.setData(name,xdata,ydata)
			if ydata.min() == ydata.max(): 	
				print "Ymax == Ymin for ", name
			markThesePlots.append(name)
			if len(ytitle) < 1: ytitle += nm.replace('\n', '-')
			if smoothMe == 1:
				lbl = name + '_smooth'
				pf = pylab.polyfit(xdata,ydata,smoothOrder)
				df = pylab.polyval(pf,xdata)
				self.m_myPlot.setData(lbl,xdata,df,linetype='--')
			i = i + 1
		if len(markThesePlots) < 1: return
		self.m_myPlot.showTheseOnly(markThesePlots)
		self.m_myPlot.setTitle(self.mainTitle)		       # Title is set to X axis. Legends cover the Y labels.
		self.m_myPlot.setYtitle(ytitle)		
		self.m_myPlot.setXtitle(xtitle)		
		self.m_myPlot.redraw()
		
	
if __name__ == "__main__":
	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	frame_1 = pwxPVTframe(None, -1, "")
	frame_1.satorpvtparms = pPVTTable()
	app.SetTopWindow(frame_1)
	frame_1.Show()
	if len(sys.argv) > 1: 
		frame_1.processInputFilen(sys.argv[1])
	app.MainLoop()