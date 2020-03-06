
from Tkinter import *
import Pmw
import Numeric
from tkMessageBox import showwarning, askyesno
from tkSimpleDialog import askstring, askinteger
from tkFileDialog import *
import string 
from pObject import *
from cModelParser import *
from pModel import *
from pRockFluid import *
from pComparator import *
from pEquilibration import *
from pFlowTable import *
from pSATTables import *
from pPVTTables import *
from pGridData  import *
from pModify	import *
from pMigration import *
from pRegion	import *
from pTableReader import *
from pEditPVTSAT	  import *
from pUtils import *
from pMyChart import *
from pSimpleTable import *
from pSimplePlot import *
from TableList import *
import sys, os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import escape
##########################################################################################
# Create a frame and put all the PVT or SAT table information into it
# TODO: 
# Currently one include statement is supported in the structure. The last one seen by 
# the parser persists. We must add support for multiple inclusions.
#
# How do I force the changes to go to the model after they have edited the data in the 
# tables?
#
##########################################################################################
class frameSATorPVTtableParms(Frame):
	def __init__(self,master,useitem,enabled=0,showQuitBtn=0):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=X)
		self.satorpvtparms = useitem
		self.lastIndexTable = -1 
		self.showQuitBtn = showQuitBtn 


		#############################################################################3
		# Top frame - chart only
		# Bottom frame  - all others 
		#############################################################################3
		self.m_mainFrame = Pmw.PanedWidget(self)
		self.m_mainFrame.pack(side=TOP,fill=BOTH,expand=1)
		self.m_mainFrame.add('top',size=.8)
		self.m_mainFrame.add('bottom',min=100)
		self.daGraph = pSimpleXYPlotter(self.m_mainFrame.pane('top'))

		#############################################################################3
		# Buttons for controlling the action.
		#############################################################################3
		self.m_bulkFrame = Frame(self.m_mainFrame.pane('bottom'))
		self.m_bulkFrame.pack(side=TOP,fill=BOTH,expand=1)

		#############################################################################3
		# Buttons for controlling the action.
		#############################################################################3
		self.listForm = Frame(self.m_bulkFrame,width=30)
		self.listForm.pack(side=LEFT,expand=0,fill=Y)

		self.cmdForm = Frame(self.listForm)
		self.cmdForm.pack(side=TOP,fill=X,expand=0)
		self.btn_replot = Button(self.cmdForm,text='RePlot',command=self.m_plotTable)
		self.btn_replot.pack(side=LEFT,padx=0,pady=0,expand=0,fill=X)
		self.btn_saveChanges = Button(self.cmdForm,text='Save Chgs',command=self.m_saveChanges)
		self.btn_saveChanges.pack(side=LEFT,padx=0,pady=0,expand=0,fill=X)

		Litems = ('None','Yet')
		self.listOfTables = Pmw.ScrolledListBox(self.listForm,
					listbox_selectmode = SINGLE,
					items = Litems, 
					labelpos = N, 
					label_text = 'Tables',
					selectioncommand = self.selectCommand, # dblclickcommand = self.selectCommand,
					listbox_exportselection=0)
		self.listOfTables.pack(side=TOP,fill=BOTH,expand=1)

		#############################################################################3
		# Buttons for controlling the action.
		#############################################################################3
		self.buttonsForm = Frame(self.m_bulkFrame,width=30)
		self.buttonsForm.pack(side=LEFT,fill=Y,expand=0)
		self.defaultButtonColor = self.btn_replot['bg'] 
		if self.showQuitBtn == 1: 
			self.btn_Quit = Button(self.buttonsForm,text='Quit',command=sys.exit)
			self.btn_Quit.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_readFile = Button(self.buttonsForm,text='Read',command=self.m_readTable)
		self.btn_readFile.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_writeFile = Button(self.buttonsForm,text='Write',command=self.m_saveTable)
		self.btn_writeFile.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_addTable = Button(self.buttonsForm,text='Tbl+',command=self.m_createNewTable)
		self.btn_addTable.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_delTable = Button(self.buttonsForm,text='Tbl-',command=self.m_createNewTable)
		self.btn_delTable.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_addRow = Button(self.buttonsForm,text='Row+',command=self.m_addRowToTable)
		self.btn_addRow.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)
		self.btn_delRow = Button(self.buttonsForm,text='Row-',command=self.m_delRowFromTable)
		self.btn_delRow.pack(side=TOP,padx=0,pady=0,expand=0,fill=X)


		#############################################################################3
		# The table options have to go here.
		#############################################################################3
		self.f1 = Frame(self.m_bulkFrame,relief=GROOVE,width=150)
		self.f1.pack(side=LEFT,fill=Y,expand=0)
		self.widgets = []
		xrow = 0
		self.names = self.satorpvtparms.specificParameters 
		for name in self.names:
			w = Pmw.EntryField(self.f1,labelpos=W,label_text=name, validate={'validator':'real','minstrict':0},value=10)
			w.pack(side=TOP,fill=X,expand=0)
			xrow=xrow+1
			val = w.component('entry'); val['width']=8
			self.widgets.append(w)

		self.m_bubble = Pmw.EntryField(self.f1,labelpos=W,label_text='', validate={'validator':'real','minstrict':0},value=0)
		self.m_bubble.pack(side=TOP,fill=X,expand=0)
		xrow=xrow+1
		val = self.m_bubble.component('entry'); val['width']=8
		self.m_stdDensityEntry = val
		self.m_stdDensityEntryLabel = self.m_bubble.component('label'); 
		self.widgets.append(self.m_bubble)

		self.m_stdDensity = Pmw.EntryField(self.f1,labelpos=W,label_text='', validate={'validator':'real','minstrict':0},value=0)
		self.m_stdDensity.pack(side=TOP,fill=X,expand=0)
		xrow=xrow+1
		val = self.m_stdDensity.component('entry'); val['width']=8; 
		self.m_bubblePointEntry = val
		self.m_bubblePointEntryLabel = self.m_stdDensity.component('label'); 
		self.widgets.append(self.m_stdDensity)

		self.m_stdDensityEntry['state'] = 'disabled'
		self.m_bubblePointEntry['state'] = 'disabled'

		Pmw.alignlabels(self.widgets)

		#self.txtButtonBox = Pmw.ButtonBox(self.buttonForm,labelpos='n',label_text='Table',orient='vertical')
		#self.txtButtonBox.pack(side=RIGHT,expand=1,fill=Y)
		#self.txtButtonBox.add('Save Changes',command = lambda s=self :  s.m_saveChanges());
		#self.txtButtonBox.add('Load 1 Table',command = lambda s=self :  s.m_readTable());
		#self.txtButtonBox.add('Save 1 Table',command = lambda s=self :  s.m_saveTable());
		#self.txtButtonBox.add('Read XML Tbl',command = lambda s=self :  s.m_importOneTable());
		#self.txtButtonBox.add('Save XML Tbl',command = lambda s=self :  s.m_saveAsXML());
		#self.txtButtonBox.add('<RePlot>',command = lambda s=self :  s.m_plotTable());

		####################################################################################
		#
		####################################################################################
		self.f2 = Frame(self.m_bulkFrame)
		self.f2.pack(side=RIGHT,fill=BOTH,expand=1)

		self.tableFrame = Pmw.PanedWidget(self.f2) 
		self.tableFrame.pack(side=TOP,fill=BOTH,expand=1)
		self.tableFrame.add('checks',min=20,size=20)
		self.tableFrame.add('text1',min=100,size=.9)

		self.anotherButtonFrame =Frame(self.tableFrame.pane('checks'))
		self.anotherButtonFrame.pack(side=BOTTOM,fill=X,expand=0)

		self.columnarText = Pmw.ScrolledText(self.tableFrame.pane('text1'),borderframe=1,labelpos=N,label_text
		='EDIT',text_wrap='none')
		self.columnarText.pack(side=TOP,fill=BOTH,expand=1)
		self.columnarText.pack_forget()
		self.columnarData = ScrolledTableList(self.tableFrame.pane('text1'),columns=(), editendcommand=self.m_editEndCommand)
		self.columnarData.pack(side=TOP,fill=BOTH,expand=1)
		self.columnarDataVisible = 1

		self.selectedColumns = Pmw.RadioSelect(self.anotherButtonFrame,labelpos=W,buttontype='checkbutton',
			label_text='Plot:',selectmode=MULTIPLE,frame_relief=RIDGE, command=self.m_selectedPlotTable)
		self.selectedColumns.pack(side=BOTTOM,expand=0,fill=X)

	def m_editEndCommand(self,tbl,row,col,txt):
		try:
			v = float(txt)
		except:
			tbl.rejectinput()
			return
		self.btn_replot['bg'] = 'red'
		self.btn_saveChanges['bg'] = 'red'
		return txt

	def m_readTable(self,filename=None):
		"""
		Reads entire table. Completely over-writes the one in memory
		"""
		if self.satorpvtparms == None: return
		if filename == None:
			fname = askopenfilename(filetypes=[("PVT SAT","*.inc"),("PVT SAT","*.prn"),("Text","*.txt"),("All Files","*")])
		else:
			fname = filename 
		if fname=='': return
		incominglines = open(fname,"r").readlines()
		self.satorpvtparms.resetTables()
		for xline in incominglines:
			ilo = pLineObject(xline)
			self.satorpvtparms.parseLine(ilo)
		self.columnarData.clear()
		self.m_resetTable()
		self.m_resetEntries()

	def m_saveTable(self):
		""" 
		This function will save a TEXT file to disk. This will not save an XML file.  
		""" 
		fname = asksaveasfilename(filetypes=[("PVT SAT","*.inc"),("PVT SAT","*.prn"),("Text","*.txt"),("All Files","*")])
		if fname=='': return
		if fname==None: return
		fd = open(fname,"w")
		k = 1
		for tbl in self.satorpvtparms.tablesArray:        # A list of Line objects
			fd.write('TABLE %d\n' % k)
			for xstr in tbl:
				fd.write(xstr.getRawLine() +'\n')
			fd.write('ENDTABLE %d\n\n' % k)
			k = k + 1
		fd.close()

	def m_saveChanges(self):
		"""
		Saves changes that have interactively been made to the table 
		"""
		self.btn_saveChanges['bg'] = self.defaultButtonColor 
		if self.satorpvtparms == None: return
		if self.lastIndexTable == -1 : return
		##################################################################
		# This is where you have to do some sanity checks.
		##################################################################
		ndx = self.lastIndexTable 
		self.satorpvtparms.tablesArray[ndx] = []
		xstrs = self.columnarData.get(0,"end")                # A list of strings
		k = 0 
		for xstr in xstrs:
			ostr = string.join(xstr)
			if k==0: ostr = "GRAPH_LABELS " + ostr ; 
			if k==1: ostr = "GRAPH_UNITS " + ostr ; 
			oln = pLineObject(ostr)
			self.satorpvtparms.tablesArray[ndx].append(oln)  # A list of pLineObjects
			k = k + 1
			
	def m_editTable(self):
		if self.satorpvtparms == None: return
		listbox = self.listOfTables.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		ndx = int(sel[0])                               # of the table.
		self.lastIndexTable = ndx

		if self.columnarDataVisible == 1:
			tbl = self.satorpvtparms.tablesArray[ndx]      # get the date for it
			ostr = '' 
			for xln in tbl:
				xstr = xln.getRawLine()	
				ostr += xstr 
			xstrs = self.columnarText.settext(ostr)
			self.columnarDataVisible = 0
			self.columnarData.pack_forget()
			self.columnarText.pack(side=TOP,fill=BOTH,expand=1)
		else:
			self.satorpvtparms.tablesArray[ndx] = []
			xstrs = self.columnarText.get()
			k = 1 
			for xstr in xstrs: 
				ilo = pLineObject(xstr,k)
				k = k + 1
				self.satorpvtparms.tablesArray[ndx].append(ilo)
			self.columnarDataVisible = 1
			self.columnarText.pack_forget()
			self.columnarData.pack(side=TOP,fill=BOTH,expand=1)

	def m_showTable(self):
		if self.satorpvtparms == None: return
		listbox = self.listOfTables.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if len(sel) < 1: 
			showwarning("Select the table above", "Select the table to reload")
			return
		ndx = int(sel[0])                               # of the table.
		self.lastIndexTable = ndx

		########################################################################
		# TODO: I have to line up the columns here or 
		# start a table of sorts.
		#
		# Perhaps put only the data in the table. Translate all non-data lines
		# into entry field widgets. Mark the columns with names. 
		#
		########################################################################
		if ndx >= len(self.satorpvtparms.tablesArray): return
		tbl = self.satorpvtparms.tablesArray[ndx]      # get the date for it
		otbl = []

		rf = self.satorpvtparms.sIdString.find('PVTTABLE')
		if rf > -1: 
			self.m_bubblePointEntry['state'] = 'normal'
			self.m_bubblePointEntryLabel['text'] = 'BUBBLE_POINT_PRESSURE' 
			self.m_stdDensityEntry['state'] = 'normal'
		else: # it is a SAT table
			self.m_stdDensityEntry['state'] = 'disabled'
			self.m_bubblePointEntry['state'] = 'disabled'
			self.m_stdDensityEntryLabel['text'] = ''
			self.m_bubblePointEntryLabel['text'] = ''
			
		for xln in tbl:
			xstr = xln.getRawLine()	
			items = xstr.split()               # Hello? What are you?
			token = items[0]      	           # use only numbers
			if len(items) == 2:
				if token == 'BUBBLE_POINT_PRESSURE':  
					self.m_bubble.setentry(items[1])
				if token in ['STANDARD_DENSITY_OIL','STANDARD_DENSITY_WATER','STANDARD_DENSITY_GAS']:
					self.m_stdDensity.setentry(items[1])
					self.m_stdDensityEntryLabel['text'] = token
				continue
			if len(items) <= 2: continue            # Dont use special keywords TODO
			if find(items[0],'GRAPH_LABELS') == 0:  # Get the labels  
				ostr = ''
				for item in items[1:]: ostr = ostr + "%12s " % item
				otbl.append(ostr)
				glabels = items[1:]
				#print "LABELS = ", glabels, items
				continue
			if find(items[0],'GRAPH_UNITS') == 0:   # Get the axes
				ostr = ''
				for item in items[1:]: ostr = ostr + "%12s " % item
				otbl.append(ostr)
				gunits = items[1:]
				#print "UNITS  = ", gunits, items
				continue

			if not token[0] in floatingDigits : continue

			ostr = ''
			for item in items: ostr = ostr + "%12s " % item
			otbl.append(ostr)

		ostr = ''
		for item in glabels: ostr = ostr + "%12s " % item
		otbl[0] = ostr
		ostr = ''
		for item in gunits: ostr = ostr + "%12s " % item
		otbl[1] = ostr

		columnNames = []
		for nm in glabels:
			columnNames.append(0)
			columnNames.append(nm)
		self.columnarData.configure(columns=tuple(columnNames))
		for k in range(len(glabels)): 
			self.columnarData.columnconfigure(k,editable='yes')
		self.columnarData.clear()
		for xline in otbl:
			self.columnarData.insert("end",xline)

		##############################################################
		# Now set the items in the checkbox area. 
		##############################################################

		##############################################################
		# Check which columns are currently on and off
		##############################################################

		cursel = self.selectedColumns.getcurselection()
		#print cursel
		self.selectedColumns.deleteall()
		for txt in glabels[1:]:                # Only select Y values
			txt = txt.replace('_','-')	       # Get rid of the underscore
			self.selectedColumns.add(txt)
		if len(cursel) > 0:
			for i in cursel:
				try:
					self.selectedColumns.invoke(i)
				except:
					pass
		else:
			self.m_plotTable()


	def m_delRowFromTable(self):
		tbl = self.columnarData.get(0,"end")
		#print tbl
		selection = self.columnarData.curselection()
		#print selection
		if len(selection) < 1: 
			showwarning("Error", "Select row to delete...")
			return
		row = selection[0]
		if row < 2: 
			showwarning("Error", "Cannot delete top two rows \n Delete table instead ...")
			return
		del tbl[row]
		#
		# Populate the table 
		#
		self.columnarData.clear()
		for xline in tbl: self.columnarData.insert("end",xline)
		self.m_saveChanges()


	def m_addRowToTable(self):
		tbl = self.columnarData.get(0,"end")
		if len(tbl)< 1: return
		selection = self.columnarData.curselection()
		if len(selection) < 1: 
			self.columnarData.insert("end",tbl[-1])
			return 
		row = selection[0]
		if row < 2: 
			showwarning("Error", "Cannot insert in top two rows \n Select another row instead ...")
			return
		xlen = len(tbl[0])
		nrow = []
		for r in range(xlen): nrow.append('0.0')
		tbl.insert(row,tuple(nrow))
		self.columnarData.clear()
		for xline in tbl: self.columnarData.insert("end",xline)
		self.m_saveChanges()
			

	def m_selectedPlotTable(self,a,b):
		self.m_plotTable()

	def m_plotTable(self):
		tbl = self.columnarData.get(0,"end")
		#print tbltxt; return

		self.btn_replot['bg'] = self.defaultButtonColor 

		maxlen = 0
		##############################################################
		# Find the labels. 
		##############################################################
		glabels = list(tbl[0])    # Get labels 
		gunits  = tbl[1]    # Get units
		for items in tbl[2:]:
			token = items[0]     # use only numbers
			if not token[0] in floatingDigits: continue
			if maxlen < len(items): maxlen = len(items)

		##############################################################
		# Construct another matrix. 
		##############################################################
		matrix = []              # Just a simple list to init with
		k = 0 
		for items in tbl:
			token = items[0]
			if not token[0] in floatingDigits: continue
			for v in map(float,items):
				matrix.append(v)
				k = k + 1
		#print maxlen, k, len(matrix)
		#print glabels, gunits
		if maxlen == 0: return 
		a = Numeric.array(matrix) #,typecode=Numeric.Float32)
		a = Numeric.reshape(a,(k/maxlen,maxlen))
		lbl = glabels[0] + ' ' + gunits[0]

		cursel = self.selectedColumns.getcurselection()   # List of columns you want to display
		if len(cursel) < 1: return
		markThesePlots = []
		#print cursel, glabels
		#self.daGraph.setMarker('o')                    # Unless we kill it later.

	
		for cur in cursel:
			scur = cur.replace('-','_')
			lbl = glabels, scur
			k = glabels.index(scur) 
			#print k
			lbl = glabels[k] + ' ' + gunits[k]
			vx = a[:,0]
			vy = a[:,k]
			if len(vx) <> len(vy):
				showwarning("Bad Data", "The y and x axis are not the same length " + lbl)
				continue

			if len(vx) < 2 : 
				showwarning("Bad Data", "The x axis has only one row in it " + lbl)
				continue
			diff = 0
			for i in range(1,len(vx)):
				v1 = vx[i-1]
				v2 = vx[i]	
				if v1 <> v2: 
					diff = 1
					break
			if diff == 0: 
				showwarning("Bad Data", "The x axis has only one value in it for " + lbl)
				continue

			#-- This does not work--> self.daGraph.setData(lbl,vx,vy)
			self.daGraph.setData(lbl,a[:,0],a[:,k])    # Mark the vectors ....
			markThesePlots.append(lbl)

		if len(markThesePlots) < 1: return
		#print "I will show these plots: ", markThesePlots
		self.daGraph.showTheseOnly(markThesePlots)
		self.daGraph.redraw()
		listbox = self.listOfTables.component('listbox')  # Get the list of items. 
		cursel  = listbox.curselection()
		lbl = ''
		if len(cursel) == 1: lbl = listbox.get(cursel[0])

		#self.daGraph.showGrid(useLast=self.daGraph.lastGridSetting)       
		#self.lastGridSetting = self.daGraph.lastGridSetting 
		self.daGraph.setTitle(lbl)		       # Title is set to X axis. Legends cover the Y labels.
		self.daGraph.setXtitle('Pressure')	# Title is set to X axis. Legends cover the Y labels.

		lbl = ''
		if len(markThesePlots) == 1: 
			self.daGraph.setYtitle(markThesePlots[0])		
		else: 
			self.daGraph.setYtitle('')		
		#self.daGraph.testLegend()

	def m_createNewTable(self):
		"""
		Starts a new table.
		"""
		number = askinteger('COLUMNS','Enter number of Columns\nfor data')
		if number == None: return 
		if number < 2 or number > 8: 
			showwarning("Error","Choose at least two but no more than 8 columns")
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

	def m_resetTable(self):
		slist = [] 
		for i in range(len(self.satorpvtparms.tablesArray)):
			slist.append("TABLE %d" % (i+1))
		self.listOfTables.setlist(slist)

	def m_resetEntries(self):
		for w in self.widgets:    # Keyword specific parameter
			txt = w.component('label')				   # Get the keyword from label 
			val  = self.satorpvtparms.getKeywordValue(txt['text']) # get value from object for label
			w.setentry(val)

	def m_deleteTable(self):
		if self.satorpvtparms == None: return
		listbox = self.listOfTables.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		ndx = int(sel[0])                               # of the table.
		r =  self.satorpvtparms.removeTable(ndx)
		#print "I have removed this table...", ndx, " and r =", r

		self.m_resetTable()
		self.m_resetEntries()
		pass

	def selectCommand(self):
		self.m_showTable()


	#################################################################################################
	#
	#################################################################################################
	def mapObjToGui(self,satorpvtparms):
		if (satorpvtparms == None): return # No parameters.
		self.satorpvtparms = satorpvtparms 
		satorpvtparms.initKeywordIndices()
		############################################################################
		# Check if you have enough include file widgets, if not, adjust the size. 
		############################################################################
		#print " I have found ", len(self.satorpvtparms.tablesArray), " table entries "
		self.m_resetTable()
		self.m_resetEntries()

	#################################################################################################
	# Only maps specific keywords. I cannot see how this will work.
	#################################################################################################
	def mapGuiToObj(self,satorpvtparms):
		if (satorpvtparms == None): return;
		self.satorpvtparms = satorpvtparms 

	def sageThyEntries(self):
		for self.widget in self.widgets:				   # Handles all but include files
			lbl = self.widget.component('label')
			txt = lbl['text'] 
			val = self.widget.component('entry').get()	
			satorpvtparms.addKeyword(txt,val)			  # Regardless.
		#for w in self.includeWidgets: 
			#lbl = w.entryField.component('label')		   # 
			#txt = lbl['text'] 
			#val = w.entryField.component('entry').get()	# get the name of the text file.
			#satorpvtparms.addKeyword(txt,val)			  # Regardless.


	def m_saveAsXML(self):
		showwarning('Not implemented','This is for the future')
		return
		if self.satorpvtparms == None: return
		listbox = self.listOfTables.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if len(sel) < 1: return
		ndx = int(sel[0])                               # of the table.
		self.lastIndexTable = ndx

	def m_importOneTable(self):
		"""
		This table should know whether you are importing a PVT or SAT table.
		"""
		typeOfTable = self.satorpvtparms.typeOfTable 
		if typeOfTable == 'PVT':
			fname = askopenfilename(filetypes=[("PVT","P*.xml"),("All Files","*")])
		else:
			fname = askopenfilename(filetypes=[("SAT","S*.xml"),("All Files","*")])
		if fname==None: return
		if fname=='': return
		lineNumber = 1
		ilo = pLineObject('TABLE',fname,lineNumber)
		self.satorpvtparms.parseLine(ilo)
		ch = pPST_tableHandler()
		ch.setObj(self.satorpvtparms,fname)
		qx = make_parser()
		qx.setContentHandler(ch)
		qx.parse(fname)
		lineNumber = 2
		ilo = pLineObject('ENDTABLE',fname,lineNumber)
		self.satorpvtparms.parseLine(ilo)
		self.m_resetTable()
		self.m_resetEntries()


if __name__ == '__main__': 
	setPlatformSpecificPaths()
	root = Tk()
	root.geometry("%dx%d+0+0" %(800,650))
	useItem = pPVTTable()
	fm = frameSATorPVTtableParms(root,useItem,showQuitBtn=1)
	fm.pack(side=TOP,fill=BOTH,expand=1)
	root.mainloop()

