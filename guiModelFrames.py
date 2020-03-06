
##########################################################################################
#
# This program is the major user interface to the MODEL file. 
#
##########################################################################################
from Tkinter import *
import Pmw
from tkMessageBox import showwarning , showerror
from tkSimpleDialog import askstring
from tkFileDialog import *
import string
from pObject import *

from cModelParser import *
from pModel import *
from pRockFluid import *
from pComparator import *
from pSector import *
from pEquilibration import *
from pGridData import *
from pFlowTable import *
from pSATTables import *
from pPVTTables import *
from pModify	import *
from pMigration import *
from pRegion	import *
from pSimpleTable import *
from pEquilibrium import *
from pTableReader import *
from pEditPVTSAT	  import *
from pUtils import *
from pDepthBubble import *
from pSimplePlot import *
from TableList import *
from copy import copy
import sys


class frameRegionInfo(Frame):
	def __init__(self,master):
		Frame.__init__(self,master)
		self.modelParserObject = None
		self.pack(expand=YES,side=TOP)
		self.nb= Pmw.NoteBook(self)

		self.fm_equilibriumFrame = self.nb.add('Equilibrium')
		self.fm_sectorFrame = self.nb.add('Sectors')
		self.fm_lgrFrame = self.nb.add('LGR')
		self.fm_migrationFrame = self.nb.add('Migration')
		self.fm_fluidFrame = self.nb.add('Fluid')
		self.nb.pack(side=TOP,expand=YES,fill=BOTH)

		self.fm_equilibrium = frameEquilibrationParms(self.fm_equilibriumFrame)
		self.fm_lgr =  frameLGRParms(self.fm_lgrFrame)
		self.fm_sector = frameSectorExtractParms(self.fm_sectorFrame)
		self.fm_migration =  frameMigrationParms(self.fm_migrationFrame)
		self.fm_fluidInPlace = frameFluidInPlaceParms(self.fm_fluidFrame)

############################################################################################
#		self.pane = Pmw.PanedWidget(self)
#		self.pane.pack(side=TOP,expand=YES,fill=BOTH)
#		self.pane.add('f1',min=100,size=.4)
#		self.pane.add('f2',min=100,size=.6)
#
#		self.fe = Pmw.PanedWidget(self.pane.pane('f1'),orient=HORIZONTAL)
#		self.fe.add('equilibrium', min=100,size=.65)
#		self.fe.add('lgr', min=100,size=.35)
#		self.fe.pack(side=TOP,expand=YES,fill=BOTH)
#
#		self.fm = Pmw.PanedWidget(self.pane.pane('f2'),orient=HORIZONTAL)
#		self.fm.add('migration', min=200,size=.5)
#		self.fm.add('sector', min=200,size=.5)
#		self.fm.pack(side=TOP,expand=YES,fill=BOTH)
#
#		#
#		# Now create the frames here.
#		#
#		self.fm_equilibrium = frameEquilibrationParms(self.fe.pane('equilibrium'))
#		self.fm_lgr =  frameLGRParms(self.fe.pane('lgr'))
#		self.fm_sector = frameSectorExtractParms(self.fm.pane('sector'))
##		self.fm_migration =  frameMigrationParms(self.fm.pane('migration'))
############################################################################################

	def mapObjToGui(self, modelParser):
		self.modelParserObject = modelParser;
		self.fm_sector.mapObjToGui(self.modelParserObject.m_internalBlocks['SECTOR_EXTRACT'])
		self.fm_equilibrium.mapObjToGui(self.modelParserObject.m_internalBlocks['EQUILIBRIUM'])
		self.fm_migration.mapObjToGui(self.modelParserObject.m_internalBlocks['MIGRATION'])
		self.fm_lgr.mapObjToGui(self.modelParserObject.m_internalBlocks['LGRPARMS'])
		self.fm_fluidInPlace.mapObjToGui(self.modelParserObject.m_internalBlocks['GRID'].aFluidInPlaceObject)

	def mapGuiToObj(self,modelParser):
		self.modelParserObject = modelParser;
		self.fm_sector.mapGuiToObj(self.modelParserObject.m_internalBlocks['SECTOR_EXTRACT'])
		self.fm_equilibrium.mapGuiToObj(self.modelParserObject.m_internalBlocks['EQUILIBRIUM'])
		self.fm_migration.mapGuiToObj(self.modelParserObject.m_internalBlocks['MIGRATION'])
		self.fm_lgr.mapGuiToObj(self.modelParserObject.m_internalBlocks['LGRPARMS'])


class frameSectorExtractParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master,relief='raised',bd=3)
		self.pack(side=LEFT,expand=YES,fill=X)
		self.fx = Frame(self)
		self.fx.pack(fill=BOTH,expand=1,side=TOP)
		self.sectorThing = pSectorExtract();
		self.lbl = Label(self.fx,text='Sector Extraction Parameters')
		self.lbl.pack(side=TOP,expand=1,fill=X)
		self.table = ScrolledTableList(self.fx,background='gray',
			columns=(10,'ID',5,'I1',5,'I2',5,'J1',5,'J2',5,'K1',5,'K2'),height=10)
		for col in range(7): self.table.columnconfigure(col,editable='yes')

		self.table.pack(side=TOP,expand=YES,fill=BOTH)
		self.table.addHorizontalBar()


		self.buttonBox = Frame(self.fx)
		self.buttonBox.pack(side=TOP,fill=X, expand=0) #,padx=5,pady=9)
		self.btn_add = Button(self.buttonBox,text='ADD',command = lambda s=self :  s.addSectorLine());
		self.btn_del = Button(self.buttonBox,text='DEL',command = lambda s=self :  s.delSectorLine());
		self.btn_sav = Button(self.buttonBox,text='Save',command = lambda s=self :  s.saveSectorLine());
		self.btn_add.pack(side=LEFT,expand=0)
		self.btn_sav.pack(side=LEFT,expand=0)
		self.btn_del.pack(side=LEFT,expand=0)
		self.direntry = Pmw.EntryField(self.fx, labelpos=W,label_text='Bin. Dir. Entry:')
		self.direntry.pack(side=TOP,expand=1,fill=X)

	def addSectorLine(self):
		"""
		Add a new line to the rows and columns in the table.
		"""
		self.table.insert("end",('ID','0','0','0','0','0','0'))
		return

	def delSectorLine(self):
		"""
		Delete a selected line to the rows and columns in the table.
		"""
		xt = self.table.curcellselection()
		self.table.delete(xt)

	def saveSectorLine(self):
		"""
		for each line in the farging table
		 	Take the first seven items and shove them into aLineContents
		 	Take the value in the last column and set the value in SECTOR_BINARY_DIRECTORY
		"""
		self.sectorThing.clearContents()                    # Remove line contents
		self.table.cellselection_set('@0,0',"end")
		xstrs = self.table.getcurselection()
		for line in xstrs:
			thisStr = "".join(line[:6])
			ilo = pLineObject(thisStr)
		self.sectorThing.setKeywordValue('SECTOR_BINARY_DIRECTORY',self.direntry.get())


	def mapObjToGui(self,myparms):
		"""
		Copies the current structure to the GUI to the myparms object. It does not keep
		a reference but it keeps a copy.
		"""
		if (myparms == None): return;            # No parameters.
		self.sectorThing = copy(myparms)    # Keep a copy, not a pointer.
		self.table.clear()            # Get the line objects and place them in the lists. 
		self.direntry.setentry(myparms.getKeywordValue('SECTOR_BINARY_DIRECTORY'))
		for ilo in myparms.aLineContents:
			if ilo.mustProcess == 0: return   # Ignore the comments
			if len(ilo.splitcookedItems) > 6:
				lineItem = tuple(ilo.splitcookedItems)     # for table entry
				self.table.insert("end",lineItem)

	def mapGuiToObj(self,myparms):
		"""
		Copies the current structure in the GUI to the myparms object.
		"""
		if (myparms == None): return;
		myparms = copy.copy(self.sectorThing)


class frameFluidInPlaceParms(Frame):
	"""
	This class is designed to handle more than one fluid in place. However,
	I only work with one fluid block at one time at the moment based on the
	input specification. 
	"""
	def __init__(self,master):
		Frame.__init__(self,master)
		self.pack(side=TOP,expand=YES,fill=X)
		self.fluidInPlaceObject = None
		self.thisRegionBlock     = None
		self.leftFrame = Frame(self,width=100)
		self.leftFrame.pack(side=LEFT,expand=0,fill=Y)
		self.middleFrame = Frame(self)
		self.middleFrame.pack(side=LEFT,expand=0,fill=BOTH)
		self.rightFrame = Frame(self)
		self.rightFrame.pack(side=LEFT,expand=1,fill=BOTH)

		#####################################################################
		# The following lines are placed here to allow multiple fluid blocks
		#####################################################################
		#Litems = []
		#self.listOfFluidBlocks= Pmw.ScrolledListBox(self.leftFrame,
					#listbox_selectmode = SINGLE,
					#items = Litems,
					#labelpos = N,
					#label_text = 'Fluid In Place',
					#listbox_exportselection=0,
					#selectioncommand = self.selectFluidCommand)
		#self.listOfFluidBlocks.pack(side=TOP,fill=BOTH,expand=1)
		#
		# Now create some buttons here ... for up and down?
		#
		#self.btnsFrame = Frame(self.leftFrame)
		#self.btnsFrame.pack(side=BOTTOM,expand=0,fill=X)
		##self.upBtn = Button(self.btnsFrame,text='UP',command=None)
		##self.dnBtn = Button(self.btnsFrame,text='DN',command=None)
		#self.addBtn = Button(self.btnsFrame,text='ADD',command=None)
		#self.addBtn.pack(side=LEFT,expand=0)
		#self.delBtn = Button(self.btnsFrame,text='DEL',command=None)
		#self.delBtn.pack(side=LEFT,expand=0)
		#self.savBtn = Button(self.btnsFrame,text='Save',command=None)
		#self.savBtn.pack(side=LEFT,expand=0)

		#####################################################################
		# The following keeps a track of regions per fluid block
		#####################################################################
		Litems = []
		self.listOfRegions = Pmw.ScrolledListBox(self.middleFrame,
					listbox_selectmode = SINGLE,
					items = Litems,
					labelpos = N,
					label_text = 'Regions',
					listbox_exportselection=0,
					selectioncommand = self.selectRegionCommand)
		self.listOfRegions.pack(side=TOP,fill=BOTH,expand=0)
		self.mbtnsFrame = Frame(self.middleFrame)
		self.mbtnsFrame.pack(side=BOTTOM,expand=0,fill=X)
		#self.upBtn = Button(self.btnsFrame,text='UP',command=None)
		#self.dnBtn = Button(self.btnsFrame,text='DN',command=None)


		self.addBtn = Button(self.mbtnsFrame,text='NEW',command=self.addOneRegion)
		self.addBtn.pack(side=LEFT,expand=0)
		self.delBtn = Button(self.mbtnsFrame,text='DEL',command=self.delRegion)
		self.delBtn.pack(side=LEFT,expand=0)
		self.savBtn = Button(self.mbtnsFrame,text='RENAME',command=self.renameRegion)
		self.savBtn.pack(side=LEFT,expand=0)


		self.table = ScrolledTableList(self.rightFrame,background='gray',
			columns=(5,'I1',5,'I2',5,'J1',5,'J2',5,'K1',5,'K2',30,'Condition'),height=10)
		for col in range(7): self.table.columnconfigure(col,editable='yes')
		self.table.pack(side=TOP,expand=1,fill=BOTH)

		self.regionNameForm = Frame(self.rightFrame)
		self.regionNameForm.pack(side=TOP,expand=1,fill=X)
		self.regionNamesText = Pmw.EntryField(self.regionNameForm,labelpos=W,label_text='Regions',validate=None)
		self.regionNamesText.pack(side=LEFT,expand=1,fill=X)

		self.listBtnsFrame = Frame(self.rightFrame)
		self.listBtnsFrame.pack(side=BOTTOM,expand=1,fill=X)
		self.laddBtn = Button(self.listBtnsFrame,text='ADD',command=self.addLine)
		self.laddBtn.pack(side=LEFT,expand=0)
		self.ldelBtn = Button(self.listBtnsFrame,text='DEL',command=self.deleteLine)
		self.ldelBtn.pack(side=LEFT,expand=0)
		self.lsavBtn = Button(self.listBtnsFrame,text='Save',command=self.saveLine)
		self.lsavBtn.pack(side=LEFT,expand=0)

	def addOneRegion(self):
		if self.fluidInPlaceObject  == None: return
		name = askstring("Kamran","Please enter a name or list of regions using { and } with spaces in between names")
		if name:
			ok =self.fluidInPlaceObject.addRegion(name)
			if ok > 0: 
				self.listOfRegions.setlist(self.fluidInPlaceObject.getRegionNames())
				self.thisRegionBlock = self.fluidInPlaceObject.getRegion(name)
			else:
				showerror("Error","Check the name\nPerhaps the curly braces are not set correctly\nYou may not be using spaces\n and using commas instead\nThe braces could be mismatched or the list may be empty ")


	def delRegion(self):
		if self.fluidInPlaceObject  == None: return
		listbox = self.listOfRegions.component('listbox')
		sel = listbox.curselection()							  # The index
		if sel == None: return
		if len(sel) <> 1: return
		ndx = int(sel[0])
		name = listbox.get(ndx)
		response = askyesno('Confirm','Are you sure you want to delete ' + name + '?')
		if response: 
			self.fluidInPlaceObject.delRegion(name)
			xlist = self.fluidInPlaceObject.getRegionNames()
			self.listOfRegions.setlist( xlist )
			if len(xlist) > 0:
				self.showRegionContents(name)

	def renameRegion(self):
		if self.fluidInPlaceObject == None: return
		listbox = self.listOfRegions.component('listbox')
		sel = listbox.curselection()							  # The index
		if sel == None: 
			return
		if len(sel) <> 1: 
			return
		ndx = int(sel[0])
		oldname = listbox.get(ndx)
		name = askstring("Kamran","Please enter a name or list of regions using { and } with spaces in between names")
		if name:
			ok= pFluidInPlaceRegion.checkRegionName(self,name)
			if ok > 0: 
				self.thisRegionBlock = self.fluidInPlaceObject.getRegion(oldname)
				self.thisRegionBlock.changeRegionName(oldname,name)
				self.listOfRegions.setlist(self.fluidInPlaceObject.getRegionNames())
				self.showRegionContents(name)
			else:
				showerror("Error","Check the name\nPerhaps the curly braces are not set correctly\nYou may not be using spaces\n and using commas instead\nThe braces could be mismatched or the list may be empty ")

	def getSelectedRegion(self):
		listbox = self.listOfRegions.component('listbox')
		sel = listbox.curselection()							  # The index
		if sel == None: return None
		if len(sel) <> 1: return None
		ndx = int(sel[0])
		name = listbox.get(ndx)
		return name
		
	def selectRegionCommand(self):
		name = self.getSelectedRegion()
		if name <> None: 
			self.showRegionContents(name)
			self.thisRegionBlock = self.fluidInPlaceObject.getRegion(name)

	def showRegionContents(self,name):
		name = self.getSelectedRegion()
		if name == None: return
		self.thisRegionBlock = self.fluidInPlaceObject.getRegion(name)
		xlist = self.thisRegionBlock.getContentsAsList(showHeader=0)
		self.regionNamesText.setentry(self.thisRegionBlock.getIdString())
		self.table.clear()
		for x in xlist:
			self.table.insert("end",tuple(split(x)))

	def saveLine(self):
		"""
		for each line in the farging table
		 	Take the first seven items and shove them into aLineContents
		 	Take the value in the last column and set the value in SECTOR_BINARY_DIRECTORY
		"""
		name = self.getSelectedRegion()
		if name == None: return
		self.thisRegionBlock = self.fluidInPlaceObject.getRegion(name)
		self.table.cellselection_set('@0,0',"end")   # Select all 
		xstrs = self.table.getcurselection()         # Read it 
		self.thisRegionBlock.aLineContents = []
		for line in xstrs:
			thisStr = "".join(line)
			ilo = pLineObject(thisStr)
			self.thisRegionBlock.parseLine(ilo)

	def deleteLine(self):
		self.table.delete('active')

	def addLine(self):
		xt = self.table.curcellselection()
		items = tuple(map(str,[1,self.fluidInPlaceObject.maxX,1,self.fluidInPlaceObject.maxY, 1,self.fluidInPlaceObject.maxZ]))
		self.table.insert('active',items)

	#######################################################################
	#
	#######################################################################
	def mapObjToGui(self,myparms):
		"""
		Only the fluid in place region information in a grid block is
		passed to this function. All parameters are copied from the
		block to the GUI here.
		"""
		if (myparms == None): # No parameters.
			return;
		self.fluidInPlaceObject= myparms
		flist = []
		i = 1
		#for fb in self.fluidInPlaceObject:
		#	flist.append('FLUID_IN_PLACE_%d' % i)
		#	i = i + 1
		#self.listOfFluidBlocks.setlist(flist)
		self.listOfRegions.setlist(self.fluidInPlaceObject.getRegionNames())

	#######################################################################
	# This maps my user interface objects to the comparator
	#######################################################################
	def mapGuiToObj(self,myparms):
		"""
		Only the fluid in place region information in a grid block is
		passed to this function. All parameters are copied to the
		block from the GUI here.
		"""
		if (myparms == None): # No parameters.
			return;
		myparms = self.fluidInPlaceObject


class frameComparatorParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master)
		self.pack(side=TOP,expand=YES,fill=X)
		self.widgets = []
		self.comparator = pComparator();
		names = self.comparator.getKeywords();
		xrow = 0
		names.sort()
		for n in names:
			w = Pmw.EntryField(self,labelpos=W,label_text=n, validate={'validator':'real','minstrict':0},value=10)
			self.widgets.append(w)
			w.pack(side=TOP,anchor=W,expand=0)
			val = w.component('entry')
			val['width']=10
			xrow = xrow + 1
		# Create them first, pack them later in another loop
		Pmw.alignlabels(self.widgets)

	#######################################################################
	#
	#######################################################################
	def mapObjToGui(self,myparms):
		if (myparms == None): # No parameters.
			return;
		self.comparator = myparms
		for w in self.widgets:
			txt = w.component('label')			   # Get the keyword from label
			val  = myparms.getKeywordValue(txt['text']) # get value from object for label
			w.setentry(val)

	#######################################################################
	# This maps my user interface objects to the comparator
	#######################################################################
	def mapGuiToObj(self,myparms):
		if (myparms == None): # No parameters.
			return;
		self.comparator = myparms
		for self.widget in self.widgets:
			self.txt = self.widget.component('label')
			self.val = self.widget.component('entry').get()
			myparms.parseKeyword(self.txt['text'],self.val)


### HERE 

##########################################################################################
# Create a frame and put all the ROCK and FLUID information in it.
##########################################################################################
class frameRockFluidParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master,relief='raised',bd=3)
		self.pack(expand=YES)

		self.widgets = []
		self.rockparms = pRockFluid();
		names = self.rockparms.getKeywords(); 
		self.simulatorform = None
		xrow = 0
		names.sort()
		for n in names:
			lname = self.rockparms.getKeywordLabel(n)
			f1 = Frame(self)
			f1.pack(side=TOP,fill=X,expand=0)
			w = Pmw.EntryField(f1,labelpos=W,label_text=lname, validate={'validator':'real','minstrict':0},value=10)
			self.widgets.append(w)
			w.pack(side='left',fill=X,expand=0)
			val = w.component('entry')
			val['width']=10
			xrow = xrow + 1
		Pmw.alignlabels(self.widgets)
		f1 = Frame(self)
		f1.pack(side=TOP,fill=X,expand=0)
		self.enabledWidget = Button(f1,text ="Save Changes",command=self.saveme)
		self.enabledWidget.pack(side=LEFT,expand=0)

	#######################################################################
	# This maps my rock fluid parameters to the user interface objects. 
	####################################################################### 
	def mapObjToGui(self,myparms,simform):
		if (myparms == None): # No parameters.
			return;
		for w in self.widgets:
			txt = w.component('label')			        # Get the keyword from label 
			val  = myparms.getKeywordValue(txt['text']) # get value from object for label
			w.setentry(val)
		if self.simulatorform <> None:
			r = simform.showFractures()
			for w in self.widgets: 
				xtxt = w.component('label')			   # Get the keyword from label 
				txt = xtxt['text']
				if txt in myparms.aFractureKeywords:
					if r == 0: 
						w.pack_forget()
					else:
						w.pack(anchor=W)
		self.rockparms = myparms
		self.simulatorform = simform

	def saveme(self):
		for w in self.widgets:
			txt = w.component('label')
			val = w.component('entry').get()
			self.rockparms.parseKeyword(txt['text'],val)
		
	#######################################################################
	# This maps my user interface objects to the rock fluid parameters ...
	####################################################################### 
	def mapGuiToObj(self,myparms):
		"""
		Copy the items from the gui to the myparms object.
		"""
		if (myparms == None): return;
		self.rockparms = myparms
		for w in self.widgets:
			txt = w.component('label')
			val = w.component('entry').get()
			myparms.setKeywordValue(txt['text'],val)

##########################################################################################
# Begin of Equilibration parameters here. They are called Equilibrium now.
# This is to be defined. How do I get the text from this widget and parse it?
##########################################################################################
class frameEquilibrationParms(Frame):
	def __init__(self,master,incoming=None):
		Frame.__init__(self,master,relief='raised',bd=3)
		self.pack(expand=YES,fill=X)
		self.eqparms = copy(incoming )

		#self.eqDatumFrame = Frame(self)
		#self.datumEntry = Pmw.EntryField(self.eqDatumFrame,labelpos=W,label_text='DEPTH_DATUM', \
		#		validate={'validator':'real','minstrict':0},value=10)
		#self.datumEntry.pack(side=LEFT,expand=0)
		#self.eqDatumFrame.pack(side=TOP,expand=0,fill=X)

		self.f1 = Frame(self)
		self.f1.pack(side=TOP,fill=BOTH,expand=1)
		self.eqListFrame = Frame(self.f1)
		self.eqListFrame.pack(side=LEFT,fill=Y,expand=1)
		Litems = []
		self.eqListOfEqBlocks = Pmw.ScrolledListBox(self.eqListFrame,
					listbox_selectmode = SINGLE,
					items = Litems,
					labelpos = N,
					label_text = 'Equilibrium Tables',
					listbox_exportselection=0,
					selectioncommand = self.selectCommand)
					#, dblclickcommand = self.selectCommand,
					#, usehullsize=1, hull_width=30, hull_height=60)
		self.eqListOfEqBlocks.pack(side=TOP,fill=BOTH,expand=YES)

		#Litems = []
		#self.bbListOfEqBlocks = Pmw.ScrolledListBox(self.eqListFrame,
					#listbox_selectmode = SINGLE,
					#items = Litems, 
					#labelpos = N, 
					#label_text = 'BubblePoint Tables',
					#selectioncommand = self.selectCommand, # dblclickcommand = self.selectCommand,
					#usehullsize=1, hull_width=80, hull_height=100)
		#self.bbListOfEqBlocks.pack(side=TOP,fill=BOTH,expand=YES)

		self.buttonBox = Frame(self.eqListFrame)
		self.buttonBox.pack(side=TOP,fill=X,expand=0)
		self.btn_add = Button(self.buttonBox,text='ADD',command = lambda s=self :  s.m_appendEqBlock());
		self.btn_del = Button(self.buttonBox,text='DEL',command = lambda s=self :  s.m_deleteEqBlock());
		self.btn_sav = Button(self.buttonBox,text=' Save ',command=self.m_keepValuesInEqTable)
		self.btn_add.pack(side=LEFT)
		self.btn_sav.pack(side=LEFT)
		self.btn_del.pack(side=RIGHT)

		self.eqDetailsFrame = Frame(self.f1)
		self.eqDetailsFrame.pack(side=LEFT,fill=BOTH,expand=1)
		self.widgets = {}

		self.frmKeywds = Frame(self.eqDetailsFrame,relief='sunken')
		self.frmKeywds.pack(side=LEFT,fill=Y,expand=0)

		#self.frmP1 = Frame(self.frmKeywds)
		#self.frmP1.pack(side=LEFT,fill=Y,expand=0)
		#self.frmP2 = Frame(self.frmKeywds)
		#self.frmP2.pack(side=RIGHT,fill=Y,expand=0)


		self.showLbl = Label(self.frmKeywds,text="Details")
		self.showLbl.pack(side=TOP,fill=X,expand=0)
		dummy = pEquilibrium()
		useThis = self.frmKeywds
		nlen = len(sEquilibriumAllowedKeywords) / 2
		xrow=0
		for key in sEquilibriumAllowedKeywords:
			if key == 'ENDEQUILIBRIUM_REGION': continue 
			lname = dummy.getKeywordLabel(key)
			self.widgets[key] = Pmw.EntryField(useThis,labelpos=W,label_text=lname,validate=None,value='')
			self.widgets[key].pack(side=TOP,anchor=W,expand=0)
			val = self.widgets[key].component('entry')
			val['width']=10
			xrow=xrow+1
			#if xrow >= nlen: useThis = self.frmP2
		Pmw.alignlabels(self.widgets.values())

		self.datumEntry = Pmw.EntryField(self.frmKeywds,labelpos=W,label_text='Depth Datum', \
				validate={'validator':'real','minstrict':0},value=10)
		self.datumEntry.pack(side=LEFT,expand=0)

		self.bbTableText = Pmw.ScrolledText(self.eqDetailsFrame,borderframe=1,labelpos=N,label_text ='Bubble Point', text_wrap='none')
		self.bbTableText.pack(side=RIGHT,fill=Y,expand=YES)

	def m_appendEqBlock(self):
		id = len(self.eqparms.aEquilibriumTables) + 1
		peq = pEquilibrium(id)
		self.eqparms.aEquilibriumTables.append(peq)
		for key in self.widgets.keys():	
			w = self.widgets[key]
			xstr = w.get()
			if key <> 'EQUILIBRIUM': peq.setKeywordValue(key,xstr) # Don't override the index
		self.updateListOfEquilibriumTables()

	def updateListOfEquilibriumTables(self):
		Litems = []
		items = range(self.eqparms.getEquilibriumCount())
		for item in items: Litems.append("EQUILIBRIUM %d" % (item+1))
		self.eqListOfEqBlocks.setlist(Litems)

		#Litems = []
		#items = range(self.eqparms.getBubblePointCount())
		#for item in items: Litems.append("BUBBLEPOINT %d" % (item+1))
		#self.bbListOfEqBlocks.setlist(Litems)


	def m_deleteEqBlock(self):
		if (self.eqparms == None): return
		listbox = self.eqListOfEqBlocks.component('listbox')  # Get the list of items.
		sel = listbox.curselection()							  # The index
		if sel == None: return
		if len(sel) <> 1: return
		ndx = int(sel[0])
		self.eqparms.deleteEquilibriumTable(ndx)
		self.updateListOfEquilibriumTables()
		for key in self.widgets: self.widgets[key].setentry('')

	def m_keepValuesInEqTable(self):
		xstr = 	self.widgets['EQUILIBRIUM'].get()
		try:
			ndx = int(xstr) - 1
		except:
			print "Invalid index in guiModelFrames:m_keepValuesInEqTable. Bailing on:", xstr
			return
		peq = self.eqparms.aEquilibriumTables[ndx]
		for key in self.widgets.keys():	
			w = self.widgets[key]
			xstr = w.get()
			#print key,xstr
			if key <> 'EQUILIBRIUM': peq.setKeywordValue(key,xstr) # Don't override the index

	def mapGuiToObj(self,eqparms):
		"""
		The user must save the changes himself if (s)he modifies a data item
		in a table.
		"""
		v = self.datumEntry.get()
		try:
			self.eqparms.fDepthDatum = float(v) 
		except:
			self.eqparms.fDepthDatum = 0.0

		eqparms = copy(self.eqparms)         # Just overwrite everything.

	def mapObjToGui(self,eqparms):
		if (eqparms == None): return;
		#print "I am being called here in migration lines ... around line 307, guiModelFrames.py" 
		self.eqparms = copy(eqparms )
		self.datumEntry.setentry("%f" % self.eqparms.fDepthDatum )
		self.updateListOfEquilibriumTables()

	def selectCommand(self):
		if (self.eqparms == None): return
		listbox = self.eqListOfEqBlocks.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if len(sel) == 0: return
		ndx = int(sel[0])
		eq = self.eqparms.aEquilibriumTables[ndx]
		for key in self.widgets:
			self.widgets[key].setentry(eq.getKeywordValue(key))
		self.widgets['EQUILIBRIUM'].setentry(str(ndx+1))

		#print "ndx ", ndx, " and ", len(self.eqparms.aBubblePointTables)
		if len(self.eqparms.aBubblePointTables) < 1: 
			self.bbTableText.settext('') 
			return
		if ndx >= len(self.eqparms.aBubblePointTables):  ndx = 0
		bb = self.eqparms.aBubblePointTables[ndx]
		self.bbTableText.settext(bb.getEditableString())

##########################################################################################
# Begin of LGR frame
##########################################################################################
class frameLGRParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master,relief='raised',bd=3)
		self.pack(side=LEFT,expand=YES)
		

		self.f0 = Frame(self,width=400,height=400)
		self.f0.pack(side=TOP,fill=BOTH,expand=0)

		self.f1 = Frame(self.f0)
		self.f1.pack(side=LEFT,fill=Y,expand=0)
		self.f2 = Frame(self.f0)
		self.f2.pack(side=LEFT,fill=Y,expand=0)
		self.lgrBlock		 = None
		self.selectedIndex	= 0
		self.selectedFineGrid = None
		self.LGRblock = None                      # Initialize to None. Copy of original?
		
		Litems = []
		self.listOfLGRblocks = Pmw.ScrolledListBox(self.f1,
					listbox_selectmode = SINGLE,
					items = Litems, 
					labelpos = N, 
					label_text = 'LGR',
					listbox_exportselection=0,
					selectioncommand = self.selectCommand ,
					usehullsize=1, hull_width=100, hull_height=200)
		self.listOfLGRblocks.pack(side=TOP,fill=Y,expand=YES)

		tempBlock = pLGRfineGrid()
		self.widgets = []
		for name in tempBlock.aAllowedKeywords:
				lname = tempBlock.getKeywordLabel(name)
				widget = Pmw.EntryField(self.f2,labelpos=W,label_text=lname, validate=None,value=0)
				widget.pack(side=TOP)
				v = widget.component('entry')
				v['width']=8
				self.widgets.append(widget);
		Pmw.alignlabels(self.widgets)

		self.buttonBox = Frame(self)
		self.buttonBox.pack(side=BOTTOM,fill=X,expand=0)
		self.btn_add = Button(self.buttonBox,text='ADD',command = lambda s=self :  s.addFineGridObject());
		self.btn_del = Button(self.buttonBox,text='DEL',command = lambda s=self :  s.deleteFineObject());
		self.btn_sav = Button(self.buttonBox,text='Save', command = lambda s=self :  s.overwriteFineObject());
		self.btn_add.pack(side=LEFT)
		self.btn_sav.pack(side=LEFT)
		self.btn_del.pack(side=LEFT)

	def selectCommand(self):
		if (self.LGRblock == None): return
		listbox = self.listOfLGRblocks.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()						 # The index 
		if (len(sel)<>0):
			i = int(sel[0])                       # Get the i-th item.
			self.selectedIndex	= i               # Save it 
			self.selectedFineGrid = self.LGRblock.tableArray[i]  # Get the line item. 
			for widget in self.widgets:
				self.txt = widget.component('label')
				val = self.selectedFineGrid.getKeywordValue(self.txt['text'])
				widget.setentry(val)


	###########################################################################
	#
	###########################################################################
	def mapObjToGui(self,LGRdataObj):
		if (LGRdataObj == None): return
		self.LGRblock = LGRdataObj
		sz = self.listOfLGRblocks.size()	  #
		self.listOfLGRblocks.delete(0,sz-1)   # Clear the list 
		Litems = range(1,len(self.LGRblock.tableArray)+1)
		self.listOfLGRblocks.setlist(Litems)
		i = 0
		if i < len(Litems): return
		self.selectedIndex	= i
		if (len(self.LGRblock.tableArray)==0): return
		self.selectedFineGrid = self.LGRblock.tableArray[i]  # Get the line item. 
		# Display this in the 
		for widget in self.widgets:
			self.txt = widget.component('label')
			val = self.selectedFineGrid.getKeywordValue(self.txt['text'])
			widget.setentry(val)

	###########################################################################
	#
	###########################################################################
	def testFineObject(self):
		print self.LGRblock.getEditableString();

	###########################################################################
	#
	###########################################################################
	def mapGuiToObj(self,LGRdataObj):
		if (LGRdataObj == None) or self.LGRblock == None: return
		LGRdataObj.tableArray = []
		for iLine in self.LGRblock.tableArray:
			LGRdataObj.tableArray.append(iLine)
		LGRdataObj.aLineContents = []
		xstr = LGRdataObj.getContentsAsList(0,0)
		for x in xstr:
			LGRdataObj.addContentLine(pLineObject(x))
	   
	###########################################################################
	# Save the information from text fields into the fine GRID 
	###########################################################################
	def overwriteFineObject(self):
		if self.LGRblock == None: return
		sz = self.listOfLGRblocks.size()	  
		if (self.selectedIndex > sz) or (self.selectedIndex  < 0): return
		self.selectedFineGrid = self.LGRblock.tableArray[self.selectedIndex]
		for widget in self.widgets:
			txt = widget.component('label')
			val = widget.component('entry').get()
			print "Setting ", txt['text'] , " to ", val
			self.selectedFineGrid.setKeywordValue(txt['text'],val)  
		self.updateListOfLGRS()

	###########################################################################
	#
	###########################################################################
	def deleteFineObject(self):
		if self.LGRblock == None: return	  #
		sz = self.listOfLGRblocks.size()	  
		if (self.selectedIndex > sz) or (self.selectedIndex  < 0): return
		i = self.selectedIndex
		#self.listOfLGRblocks.delete(i)
		del self.LGRblock.tableArray[i]
		self.updateListOfLGRS()
		for widget in self.widgets: widget.set('')

	def updateListOfLGRS(self):
		sz = len(self.LGRblock.tableArray)
		Litems = map(str,range(1,sz+1))
		self.listOfLGRblocks.setlist(Litems)

	###########################################################################
	# 
	###########################################################################
	def addFineGridObject(self):
		if self.LGRblock == None: return	                      #
		self.selectedFineGrid = pLGRfineGrid()
		self.LGRblock.tableArray.append(self.selectedFineGrid)
		for widget in self.widgets:
			txt = widget.component('label')
			val = widget.component('entry').get()
			#print "Setting ", txt['text'] , " to ", val
			self.selectedFineGrid.addKeyword(txt['text'],val)  
		self.updateListOfLGRS()

##########################################################################################
#
# Migration parameters here.
# 
##########################################################################################
class frameMigrationParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master,relief='raised',bd=3,width=300)
		self.m_migrationObject  = None
		self.pack(side=LEFT, expand=YES)
		self.f1 = Frame(self)
		self.f1.pack(expand=0,side=LEFT)                      # For the list of migrations.
		self.f2 = Frame(self)
		self.f2.pack(expand=1,side=RIGHT)                  # For the detailed list.

		self.selectedLineIndex = 0
		self.selectedLineItem =  None
		Litems = ('None')
		self.listOfMigrationLines = Pmw.ScrolledListBox(self.f1,
					listbox_selectmode = SINGLE,
					items = Litems, 
					labelpos = N, 
					label_text = 'Migration Lines',
					listbox_exportselection=0,
					selectioncommand = self.selectCommand) # ,  dblclickcommand = self.selectCommand,
					#usehullsize=1, hull_width=180, hull_height=200)
		self.listOfMigrationLines.pack(side=TOP,fill=BOTH,expand=YES)

		self.f4 = Frame(self.f1)
		self.f4.pack(expand=NO,side=TOP,fill=X)                  # For the detailed list.
		self.btn_savLine = Button(self.f4,text='Save Chg', command = lambda s=self :  s.overwriteLineObject());
		self.btn_delLine = Button(self.f4,text='Del Line',command = lambda s=self :  s.deleteLineObject());
		self.btn_newLine = Button(self.f4,text='New Line',	command = lambda s=self :  s.addLineObject());
		self.btn_newWind = Button(self.f4,text='New Window',	command = lambda s=self :  s.newLineInObject());
		self.btn_clrRow  = Button(self.f4,text='Clear Row',	command = lambda s=self :  s.clearLineObject(0));
		self.btn_clrLine = Button(self.f4,text='Clear All',	command = lambda s=self :  s.clearLineObject(1));
		self.btn_savLine.pack(side=TOP,expand=0,fill=X)
		self.btn_delLine.pack(side=TOP,expand=0,fill=X)
		self.btn_newLine.pack(side=TOP,expand=0,fill=X)
		self.btn_newWind. pack(side=TOP,expand=0,fill=X)
		self.btn_clrLine.pack(side=TOP,expand=0,fill=X)

		self.entryName = Pmw.EntryField(self.f2,labelpos=W,label_text='MIGRATION_LINE_NAME', validate=None,value='Unspecified')
		self.entryName.pack(side=TOP,fill=X,expand=0)
		val = self.entryName.component('entry')
		val['width']=40

		self.f3 = Frame(self.f2)
		self.f3.pack(expand=YES,side=TOP,fill=BOTH)                  # For the detailed list.
		self.table = ScrolledTableList(self.f3,background='white',columns=(0,'I1',0,'I2',0,'J1',0,'J2',0,'K1',0,'K2',0,'DIR'),height=15)
		for col in range(7): self.table.columnconfigure(col,editable='yes')
		self.table.pack(side=LEFT,expand=YES,fill=BOTH)



	def selectCommand(self):
		if (self.m_migrationObject == None): return
		listbox = self.listOfMigrationLines.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if (len(sel)<>0):
			i = int(sel[0])   # Get the i-th item.
			self.selectedLineIndex = i
			self.selectedLineItem = self.m_migrationObject.pLineItems[i]  # Get the line item. 
			self.entryName.setentry(self.selectedLineItem.id)
			self.table.clear()
			for x in self.selectedLineItem.dataItems:   
				y = tuple(x[1:])
				self.table.insert("end",y)


	###########################################################################
	#
	###########################################################################
	def mapObjToGui(self,migrationObj):
		if (migrationObj == None): return
		print "Mapping migration ", len(migrationObj.pLineItems), " lines "
		self.m_migrationObject = copy(migrationObj)
		sz = self.listOfMigrationLines.size()	  #
		self.listOfMigrationLines.delete(0,sz-1)   # Clear the list 
		Litems = []
		for ln in self.m_migrationObject.pLineItems:
			Litems.append(ln.id)
		self.listOfMigrationLines.setlist(Litems)

	###########################################################################
	#
	###########################################################################
	def mapGuiToObj(self,migrationObj):
		if (migrationObj == None) or self.m_migrationObject == None: return
		#print "I am being called here in migration lines ... around line 559, guiModelFrames.py" 
		migrationObj = copy(self.m_migrationObject)



		return 
	   
	###########################################################################
	#
	###########################################################################
	def testLineObject(self):
		pass

	###########################################################################
	# Set the name in the entry widget; and set a temporary line in the test 
	###########################################################################
	def clearLineObject(self,how):
		reply = askokcancel('Whoa!',"Are you sure you want to clear the entries for this migration line?")
		if reply <> True: return 
		self.entryName.setentry('')               # New line for the user to edit

		if how == 1:
			self.table.clear()
		if how == 0:
			xt = self.table.curcellselection() 
			self.table.delete(xt) 

	def newLineInObject(self):
		self.table.insert("end",('0','0','0','0','0','0','+X'))

	###########################################################################
	# Deletes a migration line from the master object.
	###########################################################################
	def deleteLineObject(self):
		if self.m_migrationObject == None: return	     #
		reply = askokcancel('Whoa!',"Are you sure you want to delete this migration line?")
		if reply <> True: return 
		name = self.entryName.get() 
		i = 0
		for iLine in self.m_migrationObject.pLineItems:
			if iLine.id == name:
				del self.m_migrationObject.pLineItems[i]
				break
			i = i + 1
		self.updateListOfMigrationLines()
		self.entryName.setentry('')               # New line for the user to edit
		self.table.clear()

	###########################################################################
	# Takes the text in the table and shoves it in the iLine object
	###########################################################################
	def updateListOfMigrationLines(self):
		Litems = []
		for ln in self.m_migrationObject.pLineItems: 
			Litems.append(ln.id)
		self.listOfMigrationLines.setlist(Litems)
		self.m_migrationObject.mergeIntoLineContents()

	###########################################################################
	#
	###########################################################################
	def overwriteLineObject(self):
		if self.m_migrationObject == None: return	  # Selecting somethin
		name = self.entryName.get()
		iLine = None
		for iLine in self.m_migrationObject.pLineItems:
			if iLine.id == name:
				found = 1; break
		if not found: return 
		self.setDataItemsPerLine(iLine)
		
	###########################################################################
	# Takes the text in the table and shoves it in the iLine object
	###########################################################################
	def setDataItemsPerLine(self,iLine):
		iLine.dataItems = []			  # Clear the line object.
		#xstr = self.table.get()		      # Get the text
		#xlines = string.split(xstr,'\n') # return 

		self.table.cellselection_set('@0,0',"end")
		xstrs = self.table.getcurselection()
		for line in xstrs:
			#print line
			kstr = ['WINDOW']
			for x in line: kstr.append(x)
			iLine.dataItems.append(kstr)
		

	###########################################################################
	# Creates a new migration line object 
	###########################################################################
	def addLineObject(self):
		name  = askstring("New Migration Line",  "Enter new name for migration line")
		if name == None: return 

		Litems = []
		found = 0
		iLine = None
		for iLine in self.m_migrationObject.pLineItems:
			if iLine.id == name:
				found = 1
				reply = askokcancel('Found', 'Must overwrite existing line object')
				if reply <> True: return
		if not found:
			iLine = pMigrationLine(name)
			self.m_migrationObject.pLineItems.append(iLine)

		iLine.setName(name) 						# forces the name.
		self.entryName.setentry(name)               # New line for the user to edit
		self.setDataItemsPerLine(iLine)        # Uses the text.
		self.updateListOfMigrationLines()      # Shows the new item in the list of lines

##########################################################################################
# Syntax Errors are shown here. 
##########################################################################################
class frameSyntaxErrors(Frame):
	def __init__(self,master,ingui=1):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=BOTH)
		self.ingui = ingui 
		#self.table = Pmw.ScrolledText(self,borderframe=1,labelpos=N,
			#label_text ='Syntax Errors (Upon reading File)',
			#hull_width=200,hull_height=300,text_wrap='none')
		self.table = Pmw.ScrolledListBox(self,
			listbox_selectmode = SINGLE,
			items = [],
			hull_width=200,hull_height=300,
			selectioncommand = self.selectError)
		self.table.pack(side=TOP,fill=BOTH,expand=1)

		self.buttonBox = Pmw.ButtonBox(self,labelpos='n',label_text='User Actions')
		self.buttonBox.pack(side=BOTTOM,fill=NONE, expand=0,padx=5,pady=5)

		self.buttonBox.add('CLEAR',command= lambda s=self :  s.clearErrors());
		self.buttonBox.add('SAVE', command= lambda s=self :  s.doWrite());
		if (ingui==0): self.buttonBox.add('QUIT', command=sys.exit);


		self.iErrorCount   = 0
		self.iWarningCount = 0
		self.sAccumulatedStrings = []

		
	def selectError(self):
		if self.ingui == 1: return
		listbox = self.table.component('listbox')  # Get the list of items.
		sel = listbox.curselection()							  # The index
		if sel == None: return
		if len(sel) <> 1: return
		ndx = int(sel[0])
		theString = self.sAccumulatedStrings[ndx]

		items = theString.split()
		try:
			fFile = items.index('File')
		except: 
			fFile = -1
		try:
			fLine = items.index('Line')
		except: 
			fLine = -1
		if fFile > -1 and fLine > -1: 
			filename = items[fFile+1].strip()
			linenum  = items[fLine+1].strip()
			filename = filename.replace(',',"")
			linenum = linenum.replace(',',"")
			try:
				linecall = "+%d" % int(linenum)
			except: 
				linecall = None

			if linecall == None: return
			if os.fork() == 0: 
				os.execl("/usr/bin/xterm","xterm", "-e", '/usr/bin/vim', linecall,filename)

	# ACTION 
	def doWrite(self):
		ofile = asksaveasfilename(filetypes=[("Text","*.txt"),("All Files","*")])
		if (ofile==''):
			return;

		fd = open(ofile,'w')
		fd.write("".join(self.sAccumulatedStrings))
		fd.close()

	# ACTION 
	def clearErrors(self):
		self.table.setlist([])
		self.iErrorCount   = 0
		self.iWarningCount = 0
		self.sAccumulatedStrings = []

	def appendOneError(self,str):
		self.sAccumulatedStrings.append(str)

	def appendErrors(self,listOfStrings):
		for x in listOfStrings: self.sAccumulatedStrings.append(x)

	def setErrors(self,listOfStrings):
		self.sAccumulatedStrings = listOfStrings

	def showErrors(self):
		#self.table.settext("".join(self.sAccumulatedStrings));
		self.table.setlist(self.sAccumulatedStrings)

	def getSyntaxErrors(self,item=None):
		if(item == None):
			return
		self.iErrorCount =  self.iErrorCount + item.getErrorCount();
		self.iWarningCount = self.iWarningCount + item.getWarningCount();
		xlist = item.getErrorReport()
		for x in xlist: self.sAccumulatedStrings.append(x)

	def SAVEgetSyntaxErrors(self,item=None):
		if(item == None):
			return
		self.iErrorCount =  self.iErrorCount + item.getErrorCount();
		self.iWarningCount = self.iWarningCount + item.getWarningCount();
		if len(item.sStartOfBlock) <> 0:
			self.str = '%d Errors, %d Warnings between %s and %s\n' % (item.getErrorCount(),item.getWarningCount(),item.sStartOfBlock,item.sEndOfBlock)
		else:
			self.str = '%d Errors, %d Warnings in this block: %s \n' % (item.getErrorCount(),item.getWarningCount(),item.sIdString)
		self.sAccumulatedStrings = self.sAccumulatedStrings + self.str
		if (item.getErrorCount() > 0):
			self.str = join(item.aErrorMessages); 
			self.sAccumulatedStrings = self.sAccumulatedStrings + self.str
		if (item.getWarningCount() > 0):
			self.str = join(item.aWarningMessages); 
			self.sAccumulatedStrings = self.sAccumulatedStrings + self.str

	# Meaningless place holder for inheritance
	def mapGuiToObj(self,modelObject=None):
		pass

#################################################################################################
# Creates an entry  [---text---] [edit][plot][...] for include files.
#################################################################################################
class pIncludeFileEntry(Frame):
	def __init__(self,master,name='',labelCaption='INCLUDE_FILE'):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=X)
		self.entryField = Pmw.EntryField(self,labelpos=W,label_text=labelCaption, validate=None,value=name)
		xrow = 0
		val = self.entryField.component('entry')
		val['width']=32
		self.entryField.grid(row=xrow,column=0)
		self.cmd =lambda s=self, l=self.entryField: s.viewIncludeFile(l);
		self.includeBtn  = Button(self,text='View',command=self.cmd)
		self.includeBtn.grid(row=xrow,column=1)
		self.cmd =lambda s=self, l=self.entryField: s.editIncludeFile(l);
		self.plotBtn  = Button(self,text='Edit',command=self.cmd)
		self.plotBtn.grid(row=xrow,column=2)
		self.cmd =lambda s=self, l=self.entryField: s.selectIncludeFile(l);
		self.selectBtn  = Button(self,text='...',command=self.cmd)
		self.selectBtn.grid(row=xrow,column=3)

	#################################################################################################
	#
	#################################################################################################
	def dialogReply(self,btnName):
		if (btnName <> None):
			if (btnName == 'Save'):
				ofile = asksaveasfilename(filetypes=[("Model","*.model"),("All Files","*")])
				if (ofile==''):
					return;
				self.dlgEdit.exportfile(ofile)
		self.dlgEdit.deactivate()

	#################################################################################################
	#
	#################################################################################################
	def editIncludeFile(self,filename):
		self.xx = pPmwTableReader()
		self.i = filename.component('entry')
		if (self.xx.parseFile(self.i.get())):
			self.xx.plotFile()

	#################################################################################################
	#
	#################################################################################################
	def viewIncludeFile(self,filename):
		self.i = filename.component('entry')
		self.dlgEdit = Pmw.TextDialog(self,scrolledtext_labelpos='n',title=self.i.get(),
					buttons=('Save','Close'),defaultbutton=0,text_wrap='none', command=self.dialogReply)
		self.ok = 0
		try:
			filename = self.i.get()
			if filename[0:5] == 'data/':
				filename = filename[5:]
			#print filename
			self.fd=open(filename,'r')
			self.ok = 1
			self.fd.close()
		except IOError:
			dialog = showwarning('FILE NOT FOUND',self.i.get())
		if self.ok == 1:
			self.dlgEdit.importfile(filename)
			self.dlgEdit.activate()
			self.dlgEdit.tkraise() 

	#################################################################################################
	#
	#################################################################################################
	def selectIncludeFile(self,item):
		self.str = askopenfilename(filetypes=[("All Files","*")])
		if(self.str <> ''):
			item.setentry(self.str)




##########################################################################################
# Test application
##########################################################################################
class App:
	def __init__(self,master):
		fm = Frame(master) # the graph must exist on the master.
		sm = (fm)
		fm.pack()
		 
##########################################################################################
# Repository
##########################################################################################
if __name__ == '__main__':
	#sys.exit()
	root =Tk()
	root.option_add('*font',('courier',10,'bold'))
	root.title("Kamran Husain")
	#f = frameRegionInfo(root)
	f =  frameRockFluidParms(root)
	root.mainloop()
