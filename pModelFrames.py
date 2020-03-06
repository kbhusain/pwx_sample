

##########################################################################################
#
# This program is the major user interface to the MODEL file. 
#
##########################################################################################
from Tkinter import *
import Pmw
from tkMessageBox import showwarning, askyesno, showerror
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
from pObject import *
from cModelParser import *
from pModel import *
from pRockFluid import *
from pComparator import *
from pEquilibration import *
from pUtils import *
import sys


##########################################################################################
# Model File Size parameters here.
# This has to be redone to group the parameters together instead of alphabetically.
##########################################################################################
class frameModelSizeParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=BOTH)
		self.modelParser =  None
		dummyParser = modelFileParser()
		dummyParser.createEmptyObject()
		self.simulatorParms = dummyParser.m_internalBlocks['SIMULATOR'];   # Get the model object.

		self.allnames = self.simulatorParms.getKeywords()      # All the keywords.
		self.allnames.sort() 							       # Unnecessary
		self.optednames  = self.simulatorParms.aOptions.keys() # Limited option items.
		self.optednames.sort()
		self.validatorString = {'validator':'real','minstrict':0}    # for floats if you need them
		self.compositionalNames = self.simulatorParms.getCompositionalNames()
		self.compositionalWidgets = []        # Dual Copy

		self.entrywidgets =   {}
		self.combowidgets =   {}
		self.booleanwidgets = {}

		#
		# Create a "required" frame.
		#

		self.mainPane = Pmw.PanedWidget(self) 
		self.mainPane.add('F1',min=100)
		self.mainPane.add('F2')
		self.mainPane.pack(side=TOP,fill=BOTH,expand=1)

		self.nb= Pmw.NoteBook(self.mainPane.pane('F2'))
		self.tabMainParms = self.nb.add('General') 		     # For general parameters.
		self.tabInputParms = self.nb.add('Included Files')            # For INPUT file specifiers
		self.tabOutputParms = self.nb.add('Output Control')          # for each tab
		self.tabOptionsParms = self.nb.add('Simulator Options')
		self.tabGridParms = self.nb.add('Graphics Control')
		self.tabLGRParms = self.nb.add('LGR')           # for each tab
		self.nb.pack(padx=1,pady=1,fill=BOTH,expand=1)

		self.m_requiredFrame = Pmw.PanedWidget(self.mainPane.pane('F1'),orient=HORIZONTAL)
		self.m_requiredFrame.pack(side=TOP,fill=BOTH,expand=1)
		self.m_requiredFrame.add('LEFT')
		self.m_requiredFrame.add('RIGHT',size=0.6)
		self.m_requiredFrame.configurepane('LEFT',size=0.3) 
		self.mainPane.configurepane('F1',size=0.2) 
		self.mainPane.configurepane('F2',size=0.8) 

		self.m_requiredParmKeywords = ['XNODES','YNODES','ZNODES','PHASES','NUMBER_OF_GRID_LEVELS','NUMBER_OF_COMPONENTS']
		self.m_requiredWidgets = self.mf_makeRowColumn('REQUIRED',self.m_requiredFrame.pane('LEFT'),self.m_requiredParmKeywords)
		self.m_inputParmKeywords = ['WELL_PERFS','WELL_RATES','RECURRENT_DATA','RESTART_INPUT','BOUNDARY_FLUX','SURFACE_NETWORK']
		self.m_inputWidgets = self.mf_makeRowColumn('Input Files',self.m_requiredFrame.pane('RIGHT'),self.m_inputParmKeywords,filebtn=1)

		self.m_frameMain = Frame(self.tabMainParms)
		self.m_mainParmKeywords = ['TITLE','VALIDATION','RESERVOIR_TYPE', 
				'MODEL_TYPE', 'FRACTURE_PERMEABILITY_VALUE_X', 'FRACTURE_PERMEABILITY_VALUE_Y', 
				'FRACTURE_PERMEABILITY_VALUE_Z', 'WELLS_COMPLETED_IN_FRACTURE']
		self.m_mainWidgets = self.mf_makeRowColumn('General Options and Parameters for the model',self.m_frameMain,self.m_mainParmKeywords)

		self.m_frameInput = Frame(self.tabInputParms)
		self.m_frameInput.pack(side=TOP,fill=BOTH,expand=1)
		self.m_otherIncludes = frameIncludeParms(self.m_frameInput)
		self.fileInfo_name = Label(self.m_frameInput,relief='sunken')
		self.fileInfo_name.pack(side=BOTTOM,fill=X,expand=1)

		self.m_frameLGR = Frame(self.tabLGRParms)
		self.m_lgrParmKeywords = [ 'NUMBER_OF_LGR_REGIONS','MAX_WELLS_LGR',
			'NUMBER_OF_MIGRATION_LINES', 'NUMBER_OF_FLUID_TABLES', 'NUMBER_OF_EQUILIBRIUM_REGIONS' ,
			'NUMBER_OF_ROCK_TABLES']
		self.m_lgrWidgets = self.mf_makeRowColumn('LGR and GRID related parameters',self.m_frameLGR,self.m_lgrParmKeywords)

		self.m_frameOptions = Frame(self.tabOptionsParms)
		self.m_optionsParmKeywords = ['ACCEPT_DEPTH_VIOLATION','CAPILLARY_PRESSURE_OPTION', 'INITIALIZATION_OPTION',\
			'INPUT_DATA_SYSTEM','LINEARIZATION_OPTION', 'LINEAR_SOLUTION_OPTION',  
			'PERMEABILITY_VALUE_X','PERMEABILITY_VALUE_Y',
			'PERMEABILITY_VALUE_Z','PRESSURE_DEPENDENCE_OPTION',
			'PRESSURE_INTERPOLATION_OPTION','SATURATION_INTERPOLATION_OPTION', 'TRANSMISSIBILITY_OPTION', 
			'LINEAR_SOLUTION_OPTION', 'NONLINEAR_UPDATE', 'PRE_CONDITIONER_OPTION', 'WELL_FORMULATION']
		self.m_optionsWidgets = self.mf_makeRowColumn('Simulator Options',self.m_frameOptions,self.m_optionsParmKeywords)

		self.m_frameOutput = Frame(self.tabOutputParms)
		self.m_outputParmKeywords = ['ASCII_MIG_LINE_OUTPUT','COMPLETION_DATA', 
			'DETAILED_SIMVIEW_DATA', 'MAPS_COORDINATE_SYSTEM', 'MAPS_OUTPUT', 'MATBAL_OUTPUT', 'OUTPUT_CUM_RATES', 
			'ASCII_WELL_OUTPUT', 'WELL_OUTPUT', 'SHOW_INACTIVE_CELLS', 'RESTART_OUTPUT', 'BINARY_DATA_DIRECTORY' ]
		self.m_outputWidgets = self.mf_makeRowColumn('Output files and locations',self.m_frameOutput,self.m_outputParmKeywords)

		self.m_frameGrid = Frame(self.tabGridParms)
		self.m_gridParmKeywords = [ 'GRID_SYSTEM_ORIENTATION','DRAW_SYSTEM_ORIENTATION', \
			'GRID_INPUT','GRID_OUTPUT', 'X_ORIGIN_UTM','Y_ORIGIN_UTM','GRID_ROTATION_ANGLE']
		self.m_gridWidgets = self.mf_makeRowColumn('Graphics orientation parameters', self.m_frameGrid,self.m_gridParmKeywords)

		#Removed Sep 20, 2005
		#self.m_frameGroups = Frame(self.tabGroupParms)
		#self.m_groupParmKeywords = ['MAX_NO_OF_GROUPS','MAX_WELL_PARAMETERS','MAX_GROUP_PARAMETERS','WM_MAX_RULES_PER_GROUP',\
		#	'WM_MAX_GROUP_CONDITIONS','WM_MAX_ACTIONS_PER_GROUP','WM_MAX_WELL_CONDITIONS']
		#self.m_groupWidgets = self.mf_makeRowColumn('GROUP',self.m_frameGroups ,self.m_groupParmKeywords)

		#####################################################################################
		# TODO maybe I ought to just map the guitotheobj at time of the switch
		#####################################################################################
		#self.enabledWidget = Button(self,text="SAVE Chgs")
		#self.enabledWidget.pack(side=BOTTOM,anchor=E)   # Set the command on the where and what!

	def mf_makeRowColumn(self,titleStr,where,what,filebtn=0):
		"""
		Put the names in order they are sent in.
		Also, put a file search button on some of them if you need it.
		"""
		where.pack(side=TOP,expand=YES,fill=BOTH)     # Pack the master form

		lbl = Label(where,text=titleStr,relief='raised',foreground='white',background='blue')
		lbl.pack(side=TOP,fill=X,expand=0)
		x_row = 0  # Left row  for all drop down items
		widgets = []
		for name in what:                                                 # Actual keywords
			if name in self.optednames: 
				sValue = self.simulatorParms.getKeywordValue(name)
				labelName  = self.simulatorParms.getKeywordLabel(name)
				opts = self.simulatorParms.getOptionsList(name)
				if (len(opts) > 2):
					acmd = lambda s=self,n=name : self.checkValueOfComboBox(n)
					widget = self.makeComboBox(where,labelName,self.simulatorParms.getOptionsList(name),cmd=acmd);
					widget.pack(side=TOP,expand=0,anchor=W)
					ef = widget.component('entryfield'); ef.setentry(sValue)    # Set the name in the GUI
					widgets.append(widget)
					self.combowidgets[name] = widget
				else:
					acmd = lambda s=self,n=name : self.checkValueOfBoolean(n)
					widget = Pmw.RadioSelect(where,labelpos=W,label_text=labelName,buttontype='radiobutton',command=acmd,pady=0)
					widget.pack(side=TOP,expand=0,anchor=W)
					for nm in self.simulatorParms.getOptionsList(name): 
						nm = nm.replace('_','-')
						widget.add(nm)
					widgets.append(widget)
					self.booleanwidgets[name] = widget
			else: 
				sValue = self.simulatorParms.getKeywordValue(name)
				labelName  = self.simulatorParms.getKeywordLabel(name)
				fm = Frame(where)
				fm.pack(side=TOP,expand=0,anchor=W)
				if name in self.simulatorParms.sQuotedKeywords: 
					widget = Pmw.EntryField(fm,labelpos=W,label_text=labelName,validate=None,value=sValue)
				else:
					widget = Pmw.EntryField(fm,labelpos=W,label_text=labelName,validate=self.validatorString,value=sValue)
				val = widget.component('entry')
				val['width']=self.simulatorParms.getRecommendedWidth(name)
				widget.pack(side=LEFT,expand=1,anchor=W)
				if filebtn == 1: 
					acmd = lambda s=self,l=labelName,w=widget : s.getIncludeFileValue(w,l)
					gBtn = Button(fm,text='...',command=acmd)
					gBtn.pack(side=RIGHT,expand=0)
				x_row = x_row+ 1
				widgets.append(widget);
				self.entrywidgets[name] = widget
		Pmw.alignlabels(widgets)
		return widgets

	def getIncludeFileValue(self,widget,lbl):
		ifile = askopenfilename(filetypes=[ ("All Files","*")])
		if ifile: 
			widget.setentry(ifile)
			#
			# At this point I would have to read the file all over again
			#
		

	def makeComboBox(self,where,txt,opts,cmd=None):
		self.i = Pmw.ComboBox(where,labelpos=W, label_text=txt, listheight=60, dropdown=1,
						listbox_width=10,scrolledlist_items=opts,selectioncommand=cmd);
		return self.i

	def checkValueOfBoolean(self,parm):
		if parm == 'MODEL_TYPE': 
			widget = self.entrywidgets['NUMBER_OF_COMPONENTS']
			bw  = self.booleanwidgets[parm]
			sel = bw.getcurselection()
			if sel == 'BLACK-OIL': 
				widget.pack_forget()
			else: 
				widget.pack(anchor=W)
			return
		if parm == 'RESERVOIR_TYPE':
			bw  = self.booleanwidgets[parm]
			sel = bw.getcurselection()
			for wn in ['FRACTURE_PERMEABILITY_VALUE_X', 'FRACTURE_PERMEABILITY_VALUE_Y', \
				'FRACTURE_PERMEABILITY_VALUE_Z', 'WELLS_COMPLETED_IN_FRACTURE']:
				widget = self.booleanwidgets[wn]
				if sel == 'NON-FRACTURE':
					widget.pack_forget()
				else: 
					widget.pack()
			# 
			# I somehow have to warn the ROCK_FLUID page too!!!
			#
			return
		

	def showFractures(self):
		bw  = self.booleanwidgets['RESERVOIR_TYPE']
		sel = bw.getcurselection()
		if sel == 'NON-FRACTURE':
			return 0
		else:
			return 1

	def checkValueOfComboBox(self,parm):
		widget = self.combowidgets[parm]
		if parm == 'MODEL_TYPE':
			xtxt = widget.get()
			print parm, xtxt
			widget = self.entrywidgets['NUMBER_OF_COMPONENTS']
			if xtxt == 'BLACK_OIL': 
				widget.pack_forget()
			else: 
				widget.pack(anchor=W)
			return
		return

	##########################################################################################
	# Get all the entry field and comboBox entries
	# NOT WORKING!!
	# TODO: This has to be fixed to work across all the tabbed pages.
	##########################################################################################
	def mapObjToGui(self,simulatorParms,modelParser):
		if (simulatorParms == None): # No parameters.
			return;
		self.simulatorParms = simulatorParms
		self.modelParser = modelParser
		for widget in self.entrywidgets.values():
			txt = widget.component('label')			     # Get the keyword from label 
			xtxt = txt['text']
			val  = simulatorParms.getKeywordValue(txt['text']) # get value from object for label
			if (val[0:5] <> 'Error'): widget.setentry(val)
		for widget in self.combowidgets.values():
			txt = widget.component('label')			   # Get the keyword from label 
			val  = simulatorParms.getKeywordValue(txt['text']) # get value from object for label
			entry = widget.component('entryfield')
			insertText = entry.get()
			lenInsertText = len(insertText)
			entry.delete(0,lenInsertText)
			entry.insert(0,val)
		for widget in self.booleanwidgets.values():
			txt = widget.component('label')			   # Get the keyword from label 
			xtxt = txt['text']
			val  = simulatorParms.getKeywordValue(xtxt)
			val = val.replace('_','-')
			try:
				widget.invoke(val)
			except:
				print "Exception processing in pModelFrames; near line 360;", xtxt,val

		self.m_otherIncludes.mapObjToGui(self.modelParser) # The parser.

		nl = self.fileInfo_name['text']
		print "I have nl=",nl, "line 264 of pModelFrames.py "
		#if (len(nl) > 0): self.fileInfo_name.delete(0,len(nl))

		self.fileInfo_name['text'] = self.modelParser.filename

		#self.fileInfo_size['text'] = self.modelParser.filename

	##########################################################################################
	# Map variables from GUI to object here. NOTE THE FUNCTION MAY NOT WORK
	##########################################################################################
	def mapGuiToObj(self,simulatorParms):
		if (simulatorParms == None): # No parameters.
			return;
		self.simulatorParms = simulatorParms;   # Get the model object.
		for widget in self.entrywidgets.values():
			txt = widget.component('label')
			val = widget.get() 
			simulatorParms.parseKeyword(txt['text'],val)
			#print "Setting ", txt['text'] , " to ", val
		for widget in self.combowidgets.values():
			txt = widget.component('label')
			val = widget.component('entryfield').get()
			simulatorParms.parseKeyword(txt['text'],val)
			#print "Setting ", txt['text'] , " to ", val
		for widget in self.booleanwidgets.values():
			try:
				txt = widget.component('label')			   # Get the keyword from label 
				xtxt  = widget.getcurselection()
				val = xtxt.replace('-','_')
				simulatorParms.parseKeyword(txt['text'],val)
			except:
				print "Exception Setting ", txt['text'] , " to ", val

##########################################################################################
# 
##########################################################################################
class frameIncludeParms(Frame):
	def __init__(self,master,parserObject=None):
		Frame.__init__(self,master)
		self.pack(side=TOP,expand=YES,fill=BOTH)
		if parserObject <> None: 
			self.modelParserNames = parserObject.sIncludedFilenames  # Just the names please 
		else: 
			self.modelParserNames = []
		self.mf_makeIncludeFileFrame(self)
		
	def mf_makeIncludeFileFrame(self,where):
		#self.includeFileList = Pmw.ScrolledListBox(where,
		#			listbox_selectmode = SINGLE,
		#			items = self.modelParserNames, 
		#			labelpos = N, 
		#			label_text = 'Included Files - Click To View - You will not get an editor',
		#			listbox_exportselection=0,
		#			selectioncommand = self.mf_selectIncludedFile)
		self.includeFileList = Pmw.ComboBox(where,
					scrolledlist_items = self.modelParserNames, 
					labelpos = N, 
					label_text = 'Included Files - Click To View - You will not get an editor',
					listbox_exportselection=0,
					dropdown=1,
					selectioncommand = self.mf_selectIncludedFile)
		self.includeFileList.pack(side=TOP,fill=X,expand=YES)
		self.includeFileText = Pmw.ScrolledText(where,borderframe=1,labelpos=N,label_text ='Selected Include File ',
				 	text_wrap='none')
		self.includeFileText.pack(side=TOP,fill=BOTH,expand=YES)

	def mf_selectIncludedFile(self,parm):
		if self.modelParserNames == None: return

		listbox = self.includeFileList.component('scrolledlist') # Get the list of items. 
		sel = listbox.curselection()				   # The index 
		ndx = int(sel[0])
		if ndx >= len(self.modelParserNames): return 
		name = self.modelParserNames[ndx]
		self.includeFileText.clear()
		self.includeFileText.importfile(name)

	def mapObjToGui(self,modelParser): # Not the object
		self.modelParserNames = modelParser.sIncludedFilenames
		self.includeFileList.setlist(self.modelParserNames)
		self.includeFileText.clear()

	def mapGuiToObj(self,simulatorparms):   # place holder
		pass

