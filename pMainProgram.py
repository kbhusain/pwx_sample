

"""

This is the main program for the POWERS GUI. The main application will include in many 
features from the existing classes for the original POWERS model file editor. 

The display is divided into several sections. The top section is reserved for the menu.
The bottom section is reserved for error messages and other status indicators.
The left side of the display will be reserved for project details with the right side 
based on the input selected from either the menu or items from the left. 

The left side of the menu is divided into two parts (a) for the project case to select
and (b) for the items within a project.

Version 0.47
-------------------
Added OUT_modelname to the list of outputs that can be tailed. 
Removed output monitor.

Version 0.46
-------------------
Changed parallel extract to go to simdata


Version 0.45
-------------------
Added ECL slicer 
Added PVT/SAT table viewer

Version 0.44
-------------------
Added new pwxsos - beta version 

Version 0.43
-------------------
Replaced references to my program with those to 64 bit


Version 0.42
-------------------
Added singular reference from /red/ssd/appl/khusain  to 64bit dir

Version 0.41
-------------------
Added the reference in JCL to copy command shell to OUTPUTDIR
Fixed bug in model manager to display output from /red/restart/$USER 

Version 0.40
-------------------
Changed default font to size 12. 
Look for manager.inf in /peasd/ssd/husainkb/template/powersdata if not in HOME

Version 0.39
-------------------
Added simc instead of sim to the submit job string
Added SciTE callout to the text editor

Version 0.38
-------------------
Added difference between two model files. 
Added reference to XYplotter but did not invoke it. 

Version 0.37
-------------------
Fixed XML escape problem in pModelManager.py

Version 0.36
-------------------
Fixed extract problem of not displaying the CNTLF files ...

Version 0.35
-------------------
Added seperate menu to main case directory

Version 0.34
-------------------
Added HOME to the user directory

Version 0.33
-------------------
Added XY plotter to list of executables

Version 0.32
-------------------
Clipped Extracted file information to CNTLF and tu_xml only 

Version 0.31
-------------------
Added Extracted Information Tab

Version 0.30
-------------------
Added Information Tab

Version 0.29
-------------------
Added User ID list from Majdi  to dialogs

Version 0.28
-------------------
Added User ID list dialog

Version 0.27
-------------------
Added lots of stuff in the pModelManager based on input from Chung Lin.

Version 0.26
-------------------
Added lots of stuff in the pModelManager

Version 0.25
-------------------
Added text and binary file recognition code to Model Manager code. 
Added output file listing based on the type of outputs.

Version 0.24
-------------------
Added Model Manager code. 

Version 0.23
-------------------
Modified inclusion directory path derivation

Version 0.22
-------------------
Moved the submit job to its own tabbed page. 
Added a new job monitor page on its own. 

Version 0.21
-------------------
Modified fluid in place region  job dialog to add new lines.
Modified grid object frame to check on x,y,z limits

Version 0.20
-------------------
Modified submit job dialog to separate the path name and base name from path name
Removed the JobID drop down box from the monitor parameter. 
Added two timers to the pMonitor.py program. 

Version 0.19
-------------------
Modified grid data to isolate FLUID_IN_PLACE_REGION objects to separate tab in regions
Add new pFluidInPlace object and pRegion object

Version 0.17 - 0.18: 
-------------------

Modified the monitor class 
Modified the GridFrames Object

Version 0.01 - 0.16: 
-------------------


Removed the monitor information into it's own python module. It runs on its own 

The filtering option is added


Attempt to fix the accumulation of group rules per date.

The $HOME/powersdata/optionDB file contains all the X defaults parameters for the user
interface. Use it wisely. If you blow it away by mistake, the file at 
/peasd/ssd/husainkb/powers/GUI shall be used instead. If you destroy my directory (how?)
then you will have X defaults to work with. Won't be pretty but it will work.

The program writes its saved parameters in the file: $HOME/powersdata/germ.inf
The current working directory and the status of the read rates flag is the only 
thing I save per se. 

TODO ITEMS: 
	Search on TODO

"""

from Tkinter import *
import Pmw
import sys
import os

from tkSimpleDialog import * 
from tkMessageBox import * 
from tkFileDialog import *
from ProgressBar import *
from cModelParser import modelFileParser
from guiModelFrames import *
from pModelFrames import *
from pPVTframes import *
from pGridFrames import *
from TreeBrowser import *
from cPerfParser import *
from pFlowTableFrame import *
from cRateParser import *
from cRecurrentParser import *
from pDateInfoFrame import *
from pUsageLogger import sendMessage
from pSubmitJob import *
from pMonitor import *
from pCompFrame import *
from pModelManager import *
from pWellInfoFrame import frameByWellParameters
from pUserIdInfoFrame import *
import cPickle
import time
from xml.sax import make_parser

myVersionString = """Version 0.47 - Nov 13, 2006 """

class makeMainProgram:	
	def __init__(self,rootWindow,filename=None):
		self.m_rootWindow = rootWindow
		self.m_modelFilename = filename
		self.m_allModelFrames = None
		self.m_allFileBranches = {} 			# For tracking subtrees
		self.m_allModelParserObjects = {}       # For tracking objects for trees 
		self.modelParserObject     = None
		self.m_allRateFileObjects = {}
		self.m_allPerfFileObjects = {}
		self.m_allRecurrentFileObjects = {}
		self.rateFileObject = None
		self.perfFileObject = None
		self.recurrentFileObject= None
		self.currentFrameName = None
		self.pickleFilename  = None
		self.processTimeInfo = IntVar() 
		self.processTimeInfo.set(1)
		self.lastWorkingDir = None
		self.readSavedParameters()               # for main GUI
		self.defaultwindowscursor = self.m_rootWindow['cursor'] 

		##################################### FIX THE MENU BAR
		self.f_makeMenuBar(self.m_rootWindow)
		
		self.nb= Pmw.NoteBook(self.m_rootWindow)
		self.tabManageParms = self.nb.add('Office') 	
		self.tabUseridsParms = self.nb.add('View Others Project') 	
		#self.tabSubmitParms = self.nb.add('Manage Jobs')  
		#self.tabMonitorParms = self.nb.add('Monitor Files')
		
		#self.circleOfTrust = ['husainkb','lincx','baddouma']
		#uname = os.getenv('USER')
		#if uname in self.circleOfTrust: self.tabSimReport   = self.nb.add('SimReport Files') 		     # From output directory
		#self.tabSimReport = self.nb.add('SimReport Files')
		
		if 1:
			self.tabPVT = self.nb.add('Show PVT')	     # For PVT parameters.
			self.tabFlow = self.nb.add('Show Flow')	     # For Flow table parameters.
			self.usePVTitem = pPVTTable()
			self.pvtfm = frameSATorPVTtableParms(self.tabPVT,self.usePVTitem)
			self.pvtfm.pack(side=TOP,fill=BOTH,expand=1)
			self.flow = frameFlowParms(self.tabFlow)
			self.tabEditParms = self.nb.add('Use GUI') 	

		self.nb.pack(padx=5,pady=5,fill=BOTH,expand=1)
		self.ff = Frame(self.tabManageParms)
		self.ff.pack(side=TOP,fill=BOTH,expand=1)
		self.manageParameters = pModelManagerFrame(self.ff,self)
		self.manageParameters.readGUIstate()

		self.uidfm = pUserIdFrame(self.tabUseridsParms,self.manageParameters,self) # Set the object later
		self.uidfm.pack(expand=YES,fill=BOTH)

		##################################### GENERAL INFORMATION AREA
		#
		# self.tabExternalProgram = self.nb.add('External tools')
		#
		#self.m_topFrame = Frame(self.tabExternalProgram,relief=RAISED)
		#self.logoImage = PhotoImage(file='/peasd/ssd/husainkb/template/Logo1.gif') 
		#self.m_text = Label(self.m_topFrame,image=self.logoImage)
		#self.m_text.pack(side=LEFT,fill=X,expand=1)
		#self.buttonBox = Pmw.ButtonBox(self.m_topFrame,labelpos='E',label_text='Test',padx=0)
		#self.buttonBox.pack(side=TOP,fill=X, expand=0,padx=0,pady=0)
		#self.buttonBox.add('GOCAD',command = lambda s=self, nm='GOCAD' :  s.m_startExternalProgram(nm));
		#self.buttonBox.add('TECPLOT',command = lambda s=self, nm='TECPLOT' :  s.m_startExternalProgram(nm));
		#self.buttonBox.add('RS3D',command = lambda s=self, nm='RS3D' :  s.m_startExternalProgram(nm));
		#self.buttonBox.add('VI',command = lambda s=self, nm='VIM' :  s.m_startExternalProgram(nm));
		#self.buttonBox.add('OTHER',command = lambda s=self, nm='OTHER' :  s.m_checkInputFile(nm));
		#self.buttonBox.pack(side=RIGHT,expand=0)
		#self.m_topFrame.pack(side=TOP,fill=X,expand=0)

		##################################### PROJECT DATA  AREA WITH PANED WIDGETS
		self.m_bulkFrame = Pmw.PanedWidget(self.tabEditParms,orient=HORIZONTAL)
		self.m_bulkFrame.pack(side=TOP,fill=BOTH,expand=1)
		self.m_bulkFrame.add('left',min=50)
		self.m_bulkFrame.add('right',min=100)
		self.m_leftFrame = Frame(self.m_bulkFrame.pane('left'),width=150,height=100,relief=GROOVE)
		self.m_leftFrame.pack(side=LEFT,fill=BOTH,expand=1)

		self.m_rightFrame = Frame(self.m_bulkFrame.pane('right'))
		self.m_rightFrame.pack(side=RIGHT,fill=BOTH,expand=1)

	
		##################################### AFFIX THE STATUS BAR
		self.m_bottomFrame = Frame(self.m_rightFrame)
		self.m_bottomFrame.pack(side=BOTTOM,fill=X,expand=0)
		self.f_makeStatusBar(self.m_bottomFrame)

		
		##################################### Finally map the tree to the interface
		### Create



		#self.mpFrame = Frame(self.tabSubmitParms)
		#self.mpFrame.pack(side=TOP,expand=1,fill=BOTH)

		self.mpFrame = Frame(self.m_rightFrame)  # DO NOT PACK
		self.mpFrame_bottom = Frame(self.mpFrame)
		self.mpFrame_top = Frame(self.mpFrame)
		self.mpFrame_bottom.pack(side=BOTTOM,expand=0)
		self.mpFrame_top.pack(side=TOP,expand=1,fill=BOTH)
		self.jobInfoObject = pJobInfoFrame(self.mpFrame_top)
		self.submitJobParms = makeSubmitForm(self.mpFrame_bottom, tellme=self.jobSubmissionHandler,obj=self)
		self.submitJobParms.pack_forget()
		self.jobInfoObject.monitorPageObject = self
		self.manageParameters.submitJobParms = self.submitJobParms    # Keep a reference

		##################################### Finally map the tree to the interface
		self.modelComponentsFrame = Frame(self.m_leftFrame)
		self.modelComponentsFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.f_makeTreeBrowser(self.modelComponentsFrame)

		###########################################################################
		# This is used to display the status of monitored 
		###########################################################################
		#self.monitorObject = pMonitorFrame(self.tabMonitorParms)
		#self.monitorObject.modelFilename = self.m_modelFilename 
		#self.monitorObject.outputFilename = ''
		#self.monitorObject.commandFilename = ''
		#self.submitJobParms.setDefaultModelFile(self.m_modelFilename)
		#self.manageParameters.monitorObject = self.monitorObject    # Keep a reference
		#self.manageParameters.guiEditor = self
		#self.jobInfoObject.setMonitorObject(self.monitorObject)



	def jobSubmissionHandler(self,obj,modelName,outputName,errName):
		"""
		This is a kludge to set the file names for a batch job from the submitJobParms object
		The obj is myself, whereas the self in the submitJob object
		"""
		obj.monitorObject.modelFilename = modelName
		obj.monitorObject.outputFilename = outputName
		obj.monitorObject.commandFilename = errName
		print "I am setting ... ", modelName,outputName,errName

	def switchToMonitor(self):
		self.nb.selectpage('Monitor')

	def writeSaveParameters(self,where):
		filename = os.getenv('HOME') + os.sep + 'powersdata' + os.sep + 'germ.inf'
		#print "I will write to ", filename
		#print "I will write about ", where
		#print "Where I am ", os.getcwd()
		lastdir = 'LASTDIR : ' + where + '\n'
		fd=open(filename,'w')
		fd.write('#Saved for POWERS GUI\n')
		fd.write(lastdir); 
		fd.write('READRATES : ' + str(self.processTimeInfo.get()) + '\n')
		fd.close()

	def readSavedParameters(self):
		if os.name == 'posix':
			self.repository = os.getenv('HOME')
			if self.repository == None:
				self.repository = "/peasd/ssd/husainkb/expt"
			else:
				self.repository += os.sep + 'powersdata'
		else: 
			self.repository = os.getenv('HOMEPATH')
			if self.repository == None:
				self.repository = "/powers/temp"
		try:
			os.mkdir(self.repository)
		except:
			pass
		os.chdir(self.repository)
		filename = self.repository + os.sep + 'germ.inf'
		try:
			fd=open(filename,'r')
			xlines=fd.readlines()
			for ln in xlines:
				if ln == None: continue
				items = ln.split(':')
				if len(items) == 2:
					token = items[0].strip()
					value = items[1].strip()
					if token == 'LASTDIR': 
						self.lastWorkingDir = value
						os.chdir(value)
					if token == 'READRATES': 
						self.processTimeInfo.set(int(value))
			fd.close()
		except:
			return


	def m_disableTimeInfo(self,doit):
		self.processTimeInfo.set(doit)
		if doit == 1:
			showwarning('Caution','I will process the rates, perfs and recurrent data')
		else:
			showwarning('Caution','I will NOT process the rates, perfs and recurrent data')

	def m_checkInputFile(self,name):
		showwarning(name,'I will check the input into this program '+name)
		self.m_runSyntaxChecker()
		self.bFrameSyntaxErrors.clearErrors()
		self.m_collectSyntaxErrors()

	def m_startParallelSimReport(self,b):
		if b == 'PEXTRACT':
			ifile = askopenfilename(filetypes=[ ("SMSPEC ","*.smspec"),  ("SMSPEC ","*.SMSPEC"), \
				("All Files","*")])
			if ifile: 
				bname, ext = os.path.splitext(ifile)
				print "Extract with ", bname, ext
				if os.fork() == 0: 
					os.execl('/bin/bash',"/bin/bash", \
						"/red/ssd/appl/khusain/64bit/srcs/extractWithPython.ksh", \
						bname, ext, "/red/simdata/EXT400/" + os.getenv('USER'))
				
		if b == 'PVTSAT':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runPVT.ksh")
		if b == 'FlowTable':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runFlow.ksh")
		if b == 'wxSOS':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runSimRpt2.ksh")
		if b == 'SOSimRpt':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runSimRpt.ksh")
		elif b == 'XYplotter':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runXYplotter.ksh")
		elif b == 'RS3D':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/runRS3D.ksh")
		elif b == 'ECLbrowser':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runECLbrowser.ksh")
		elif b == 'Text':
			if os.fork() == 0: 
				os.execl('/red/ssd/appl/khusain/64bit/srcs/scite/bin/SciTE',"SciTE")
		elif b == 'Ripper':
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runRipper.ksh")
				
	def m_startExternalProgram(self,name):
		"""
		Sends the name of the script to execute	
		self.toolDir = "/peasapps/ssd/test_lnx/scripts/Linux/"	
		"""
		if not name in self.toolCommands.keys(): return
		tcmd = self.toolDir + name
		print "Execute", tcmd
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def f_makeModelFrames(self,where):
		"""
		This function creates the frames for the model file.
		The where is the frame to draw on. 
		"""
		self.m_allModelFrames = {}                                           # Create the dictionary.
		self.m_allModelFrames['SIMULATOR'] = frameModelSizeParms(where)      # Just create a frame. 
		self.m_allModelFrames['ROCKFLUID'] = frameRockFluidParms(where)
		self.m_allModelFrames['FLOW'] = frameFlowParms(where)
		self.m_allModelFrames['GRID'] = frameGridParms(where)
		#self.m_allModelFrames['COMPARATOR'] = frameComparatorParms(where)

		self.m_allModelFrames['COMPOSITION'] =  frameCompositionalParms(where)

		self.m_allModelFrames['REGIONINFO'] = frameRegionInfo(where)

		#____________________ IMPORTANT
		# Don't erase the following frame calls-->
		#self.m_allModelFrames['SECTOR_EXTRACT'] = frameSectorExtractParms(where)
		#self.m_allModelFrames['MIGRATION'] = frameMigrationParms(where)
		#self.m_allModelFrames['LGRPARMS'] = frameLGRParms(where)
		#self.m_allModelFrames['EQUILIBRIUM'] = frameEquilibrationParms(where)
		#____________________ IMPORTANT
		
		self.m_allModelFrames['TIMEINFO'] = frameListOfWells(where,None) # By date
		self.m_allModelFrames['WELLINFO'] = frameByWellParameters(where,None) # By well
		self.m_allModelFrames['Error-Check'] = frameSyntaxErrors(where)


		#
		# Create dummy frames. 
		#
		self.satTableGasOil   = pSATTable('BEGIN_SATTABLES_GAS_OIL');    
		self.satTableOilWater = pSATTable('BEGIN_SATTABLES_OIL_WATER');
		self.pvtTableOil      = pPVTTable('BEGIN_PVTTABLES_OIL');
		self.pvtTableWater    = pPVTTable('BEGIN_PVTTABLES_WATER');
		self.pvtTableGas      = pPVTTable('BEGIN_PVTTABLES_GAS');

		self.m_allModelFrames['PVT-OIL'] = frameSATorPVTtableParms(where,self.pvtTableOil,0)
		self.m_allModelFrames['PVT-WATER'] = frameSATorPVTtableParms(where,self.pvtTableWater,0)
		self.m_allModelFrames['PVT-GAS'] = frameSATorPVTtableParms(where,self.pvtTableGas,0)
		self.m_allModelFrames['SAT-GAS-OIL'] = frameSATorPVTtableParms(where,self.satTableGasOil,0)
		self.m_allModelFrames['SAT-OIL-WATER'] = frameSATorPVTtableParms(where,self.satTableOilWater,0)
		self.f_clearAllFrames()

	def f_clearAllFrames(self):
		for key in self.m_allModelFrames.keys():
			fm = self.m_allModelFrames[key]; fm.forget()
		
	def f_showThisFrame(self,key):
		if self.m_allModelFrames.has_key(key): 
			self.m_allModelFrames[key].pack(side=TOP,fill=BOTH,expand=1)
			return self.m_allModelFrames[key]
		return None
		
	def f_makeTreeBrowser(self,where):
		self.modelOpsBtns = Frame(where)
		self.modelOpsBtns.pack(side=TOP,fill=X,expand=1)
		self.modelOpsbuttonBox = Pmw.ButtonBox(self.modelOpsBtns,padx=0,orient=VERTICAL)
		self.modelOpsbuttonBox.pack(side=TOP,fill=X, expand=0,padx=0,pady=0)
		self.modelOpsbuttonBox.add('Open',command = lambda s=self :  s.f_openModelFile());
		self.modelOpsbuttonBox.add('Save',command = lambda s=self :  s.m_saveTheModelFile());
		self.modelOpsbuttonBox.add('Close',command = lambda s=self :  s.m_closeTheModelFile());
		self.modelOpsbuttonBox.add('New',command = lambda s=self :  s.f_createModelFile());
		self.modelOpsbuttonBox.add('Time',command = lambda s=self :  s.f_readTimeAgain());

		self.m_showRateStatus = Checkbutton(self.modelOpsBtns,text='Read Time Info',var=self.processTimeInfo)
		self.m_showRateStatus.pack(side=LEFT,expand=0)

		#self.m_menuBar.addmenuitem('File', 'command','Save as XML set', label='Save XML set', command = self.f_testme)
		#self.m_menuBar.addmenuitem('File', 'command','Save Model', label='Save Model File', command = self.m_saveTheModelFile)
		#self.m_menuBar.addmenuitem('File', 'command','Close a file', label='Close', command = self.m_closeTheModelFile)
		#self.m_menuBar.addmenuitem('File', 'command','Re-read Time', label='Read Time', command = self.f_readTimeAgain)

		self.m_treeBrowser = TreeBrowser(where)
		self.m_treeBrowser.pack(side=TOP,expand=1,fill=BOTH) 
		if self.m_modelFilename <> None: 
			self.f_loadModelFile(self.m_modelFilename)
			self.m_mapAllBlocksToGui()
			self.f_showThisFrame('Error-Check')
			self.m_collectSyntaxErrors()
			self.bFrameSyntaxErrors.showErrors();
			self.m_messageBar.message('state','I have finished mapping the input files')
			self.m_messageBar.update()

	def h_editFrameFromFile(self,filename,blockName):
		"""
		# Unfortunately, this handler has only one parameter to send: the object itself.
		# Therefore a function is required per invocation. Perhaps the Tree widget 
		# can be modified to rid of this fluff. 
		"""
		if self.currentFrameName <> None: 
			self.m_collectUserInputForFrame(self.currentFrameName)
		self.f_clearAllFrames()
		self.f_setCurrentFile(filename)                       # Read the salient parts or cache
		self.m_mapBlockToGui(blockName)                       # 
		self.currentFrameName = blockName
		self.submitJobParms.setDefaultModelFile(self.m_modelFilename)

	def m_mapAllBlocksToGui(self):
		self.defaultwindowscursor = self.m_rootWindow['cursor'] 
		#cursor = self.m_rootWindow['cursor'] 
		self.m_rootWindow['cursor']  = 'watch'
		self.m_rightFrame.pack_forget()
		for blockName in self.m_allModelFrames.keys(): 
			fm = self.m_allModelFrames[blockName]; 
			self.m_messageBar.message('state','Mapping '+ blockName)
			self.m_messageBar.update()
			self.m_mapBlockToGui(blockName)
			fm.forget()
		self.m_messageBar.message('state','I have finished reading the input files. Now I am setting up links in memory...')
		self.m_messageBar.update()
		self.m_rightFrame.pack(side=RIGHT,fill=BOTH,expand=1)
		self.m_rootWindow['cursor']  = self.defaultwindowscursor 

	def m_mapBlockToGui(self,blockName):
		"""
		Internal function. Switch on blockName to map internal object to GUI

		"""
		f= self.f_showThisFrame(blockName)
		if blockName == 'SIMULATOR':
			f.mapObjToGui(self.modelParserObject.m_internalBlocks[blockName], self.modelParserObject)
			return
		if blockName == 'ROCKFLUID': 
			# Special case, requires information about RESERVOIR_TYPE from simulatorParms as read only
			f.mapObjToGui(self.modelParserObject.m_internalBlocks[blockName], self.m_allModelFrames['SIMULATOR'])
			return
		#if blockName == 'COMPARATOR': 
			#f.mapObjToGui(self.modelParserObject.m_internalBlocks['COMPARATOR'])
			#return

		if blockName == 'COMPOSITION': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['COMPOSITION'])
			return

		if blockName == 'REGIONINFO': 
			f.mapObjToGui(self.modelParserObject)
			return

		#if blockName == 'MIGRATION': 
		#	f.mapObjToGui(self.modelParserObject.m_internalBlocks['MIGRATION'])
		##	return
		##if blockName == 'SECTOR_EXTRACT': 
		#	f.mapObjToGui(self.modelParserObject.m_internalBlocks['SECTOR_EXTRACT'])
		#	return
		#if blockName == 'EQUILIBRIUM': 
		#	#eqOBJ = self.modelParserObject.m_internalBlocks['MIGRATION']
		#	f.mapObjToGui(self.modelParserObject.m_internalBlocks['EQUILIBRIUM'])
		#	return
		#if blockName == 'LGRPARMS': 
		# 	f.mapObjToGui(self.modelParserObject.m_internalBlocks['LGRPARMS'])
		#	return

		if blockName == 'GRID': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['GRID'])
			return
		if blockName == 'FLOW': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['FLOW'])
			return
		if blockName == 'PVT-OIL': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['PVT-OIL'])
			return
		if blockName == 'PVT-GAS': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['PVT-GAS'])
			return
		if blockName == 'PVT-WATER': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['PVT-WATER'])
			return
		if blockName == 'SAT-OIL-WATER': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['SAT-OIL-WATER'])
			return
		if blockName == 'SAT-GAS-OIL': 
			f.mapObjToGui(self.modelParserObject.m_internalBlocks['SAT-GAS-OIL'])
			return
		if blockName == 'TIMEINFO': 
			self.mapTimeRelatedInfo()
			f.mapObjToGui(self.modelParserObject)     # The big daddy.
			return
		if blockName == 'WELLINFO': 
			self.mapTimeRelatedInfo()
			f.mapObjToGui(self.modelParserObject)
			return
		if blockName == 'Error-Check': 
			self.m_collectSyntaxErrors()
			return


	################################################################################################
	# The cache has to be seen for both the rates and the perfs files.
	################################################################################################
	def f_readTimeAgain(self):
		reply = askyesno('Confirm!',"Are you sure you want to read the information again? This will take some time to read.")
		if reply <> True: return
		self.mapTimeRelatedInfo(forceRecache=1)


	################################################################################################
	def mapTimeRelatedInfo(self,forceRecache=0):
		self.m_messageBar.message('state','Rates file='+self.m_ratesFileName)
		doit = self.processTimeInfo.get()
		if doit == 0: 
			self.m_messageBar.message('state','Bypassing Mapping Rates file ...')
			return

		#############################################################################################
		# First check if have a key-ed entry,
		# then check if you have a cached version, 
		# then read, parse and create cache.
		#############################################################################################

		if self.m_allRateFileObjects.has_key(self.m_ratesFileName) \
			and self.m_allPerfFileObjects.has_key(self.m_perfsFileName):
			self.rateFileObject= self.m_allRateFileObjects[self.m_ratesFileName] 
			self.perfFileObject= self.m_allPerfFileObjects[self.m_perfsFileName] 
			self.recurrentFileObject= self.m_allRecurrentFileObjects[self.m_recurrentFileName] 
			self.m_messageBar.message('state','Reading from memory')
			self.m_messageBar.update()
			return 

		self.pickleFilename = self.m_ratesFileName + ".pickle"
		print "Look at  ", self.pickleFilename                  # Attempt to open here. 
		cfd = None
		pStat = None
		try:
			pStat = os.stat(self.pickleFilename)
			cacheFound = 1	
		except: 
			cacheFound = 0	

		if cacheFound == 0: 
			self.pickleFilename = os.getenv('HOME')+os.sep+os.path.basename(self.m_ratesFileName)+".pickle"
			print "Now Look at  ", self.pickleFilename
			try:
				pStat = os.stat(self.pickleFilename)
				cacheFound = 1	
			except: 
				cacheFound = 0	

		if cacheFound == 1: # Cache found.
			print "Cache Found ... now checking date of manufacture...!" 
			rStat = os.stat(self.m_ratesFileName)
			fStat = os.stat(self.m_perfsFileName)
			if rStat[-1] > pStat[-1]  or fStat[-1] > pStat[-1]:
				print "Cache is old or outdated. ..", rStat[-1], fStat[-1], pStat[-1] 
				cacheFound = 0 

		if cacheFound == 1 and forceRecache == 0: # Cache found and you are not forcing a read.
			print "Cache Found and times are okay...!" 
			tmA = time.time()
			try:
				cfd = open(self.pickleFilename,'rb')
				self.modelParserObject.allWellsArray = cPickle.load(cfd) 
				self.modelParserObject.allDatesArray = cPickle.load(cfd) 
				print "Finished Reading ... "
				cfd.close()
			except:
				print "Unable to read from pickle file..."

			print "Reading took... ", time.time() - tmA
			self.rateFileObject= None
			self.perfFileObject= None
			self.m_allPerfFileObjects[self.m_perfsFileName]  = None
			self.m_allRateFileObjects[self.m_ratesFileName]  = None

			self.recurrentFileObject= None
			if self.m_allRecurrentFileObjects.has_key(self.m_recurrentFileName): 
				self.recurrentFileObject= self.m_allRecurrentFileObjects[self.m_recurrentFileName] 
			else: 
				self.m_allRecurrentFileObjects[self.m_recurrentFileName] = \
					cRecurrentFile(self.modelParserObject.allDatesArray, self.modelParserObject.allWellsArray)
				self.recurrentFileObject= self.m_allRecurrentFileObjects[self.m_recurrentFileName] 
				tmB = time.time()
				self.recurrentFileObject.readFile(self.m_recurrentFileName)    # This has more information
				print "Reading recurrent took... ", time.time() - tmB
			self.m_messageBar.message('state','Reading from cache' + self.pickleFilename)
			self.modelParserObject.createWellToDate()   # populate the list of wells.
			self.m_messageBar.message('state','Reading from cache' + self.pickleFilename)
			self.m_messageBar.update()
		else:   # Cache not found and reading for first time.
			self.modelParserObject.allDatesArray = {}
			tmA = time.time()
			self.m_allRateFileObjects[self.m_ratesFileName] = \
				cRateFile(self.modelParserObject.allDatesArray,self.modelParserObject.allWellsArray)
			self.rateFileObject= self.m_allRateFileObjects[self.m_ratesFileName] 
			self.rateFileObject.readDataFile(self.m_ratesFileName,keepCopyOfLine=0,notifyFunction=self.updateProgressBar)
			tmB = time.time()
		
			self.m_messageBar.message('state','Reading entire Perfs file='+self.m_perfsFileName)
			self.m_messageBar.update()

			self.m_allPerfFileObjects[self.m_perfsFileName] = \
				cPerfFile(self.modelParserObject.allDatesArray,self.modelParserObject.allWellsArray)
			self.perfFileObject= self.m_allPerfFileObjects[self.m_perfsFileName] 
			self.perfFileObject.readDataFile(self.m_perfsFileName,keepCopyOfLine=0,notifyFunction=self.updateProgressBar)

			self.m_allRateFileObjects[self.m_ratesFileName] = self.rateFileObject  
			self.m_allPerfFileObjects[self.m_perfsFileName] = self.perfFileObject  


			#print "Len of PerfParser allWellNames", len(self.perfFileObject.allWellNames.keys())
			self.m_messageBar.message('state','Recurrent file='+self.m_recurrentFileName)
			self.m_messageBar.update()

		#############################################################################################3
		# Read them all
		#############################################################################################3
			print "Mapping recurrent file now"
			tmB = time.time()
			self.m_allRecurrentFileObjects[self.m_recurrentFileName] = \
				cRecurrentFile(self.modelParserObject.allDatesArray, self.modelParserObject.allWellsArray)
			self.recurrentFileObject= self.m_allRecurrentFileObjects[self.m_recurrentFileName] 
			self.recurrentFileObject.readFile(self.m_recurrentFileName)    # This has more information
			print "2 Reading recurrent took... ", time.time() - tmB
			self.m_messageBar.message('state','Mapping wells')
			self.modelParserObject.createWellToDate()   # populate the list of wells.


			tmA = time.time()
			cfd = open(self.pickleFilename,'wb')
			cPickle.dump(self.modelParserObject.allWellsArray,cfd,1)
			cPickle.dump(self.modelParserObject.allDatesArray,cfd,1)
			print  "\nTime required to pickle file ", self.pickleFilename , time.time() - tmA , " seconds"
			cfd.close()

		### In both instances ### cached or not ### set the recurrent file object
		self.modelParserObject.recurrentFileObject =  self.recurrentFileObject
		self.m_messageBar.message('state','Done with time related information')

	################################################################################################
	def adjustAbsolutePath(self, lblText):
		"""
		Utility function to compensate for the idiotic data/ directory redirection 
		"""
		if lblText == None   : return ''
		if len(lblText) < 1  : return ''
		if lblText[0] == '/' : return lblText
		workpath, projectpath = deriveWorkpaths(self.m_modelFilename)
		retpath = deriveIncludePath(lblText,workpath,projectpath)
		if retpath == None: 
			showwarning("WARNING!"," I cannot open this file: " + lblText)
			return '' 
		else:
			return retpath 

	################################################################################################
	def f_setCurrentFile(self,filename,create=0):
		"""
		Sets the model filename for future saves. Creates a model parser object.
		Calls f_setTimeRelatedItems()
		"""
		self.m_modelFilename = filename
		if not self.m_allModelParserObjects.has_key(filename):
			self.m_allModelParserObjects[filename] = modelFileParser();
			self.modelParserObject = self.m_allModelParserObjects[filename]
			if create == 1: 
				self.modelParserObject.createEmptyObject(filename)
			else:
				self.modelParserObject.readModelFile(filename);                  # Do consistency check too
		else:
			self.modelParserObject = self.m_allModelParserObjects[filename]
		self.f_setTimeRelatedNames()

	def f_setTimeRelatedNames(self):
		"""
		Internal function to read items from  WELL_RATES, WELL_PERFS and RECURRENT_DATA
		"""
		lblText = self.modelParserObject.m_internalBlocks['SIMULATOR'].getKeywordValue('WELL_RATES')
		self.m_ratesFileName =  self.adjustAbsolutePath(lblText) 
		lblText = self.modelParserObject.m_internalBlocks['SIMULATOR'].getKeywordValue('WELL_PERFS')
		self.m_perfsFileName = self.adjustAbsolutePath(lblText) 
		lblText = self.modelParserObject.m_internalBlocks['SIMULATOR'].getKeywordValue('RECURRENT_DATA')
		self.m_recurrentFileName = self.adjustAbsolutePath(lblText) 

	def f_loadModelFile(self,filename=None):
		"""
		Load in a model file using the cModelParser module and display the tree in the 
		left frame of the main window.

		I have to make this function destroy any previous nodes in the tree.
		This may cause some memory leaks unless I destroy the leftframe and rebuild it.
		"""
		print "Opening file: ", filename
		os.chdir(os.path.dirname(filename))
		print "Current Working dir : ", os.getcwd()

		sendMessage('PowersGUI','OPEN',filename)
		self.f_setCurrentFile(filename)
		if self.m_allModelFrames == None:  self.f_makeModelFrames(self.m_rightFrame)  
		#
		# Look at past the if statement
		if not self.m_allFileBranches.has_key(filename): 
			a = lambda s=self,b=filename: self.f_setCurrentFile(b)
			self.m_fileBranch     = self.m_treeBrowser.addbranch(label='FILE:'+ os.path.basename(filename) \
					,selectcommand=a) 
			self.m_allFileBranches[filename] = self.m_fileBranch
			a = lambda s=self,b=filename: self.f_clearAllFrames()
			self.m_modelBranch       = self.m_fileBranch.addbranch(label='Model File Input',selectcommand=a)
			self.m_simulatorBranch   = self.makeLeafForBlock(self.m_modelBranch,'SIMULATOR',filename,'Simulation')
			self.m_flowBranch        = self.makeLeafForBlock(self.m_modelBranch,'FLOW',filename,'Flow Table')
			self.m_gridBranch        = self.makeLeafForBlock(self.m_modelBranch,'GRID',filename,'Grid Parameters')
			self.m_compositionalBranch       = self.makeLeafForBlock(self.m_modelBranch,'COMPOSITION',filename,'Compositional')

			a = lambda s=self,b=filename: self.f_clearAllFrames()
			self.m_rockDataBranch = self.m_fileBranch.addbranch(label='Rock and Fluid Data',selectcommand=a)
			self.m_rockFluidBranch   = self.makeLeafForBlock(self.m_rockDataBranch,'ROCKFLUID',filename,'Rock Fluid Parameters')
			self.m_satGOBranch       = self.makeLeafForBlock(self.m_rockDataBranch,'SAT-GAS-OIL',filename,'Gas Saturation Parameters')
			self.m_satOWBranch       = self.makeLeafForBlock(self.m_rockDataBranch,'SAT-OIL-WATER',filename,'Oil Saturation Parameters')

			a = lambda s=self,b=filename: self.f_clearAllFrames()
			self.m_fluidDataBranch = self.m_fileBranch.addbranch(label='Fluid Data Parameters',selectcommand=a)
			self.m_pvtOilBranch      = self.makeLeafForBlock(self.m_fluidDataBranch,'PVT-OIL',filename,'Oil PVT tables')
			self.m_pvtGasBranch      = self.makeLeafForBlock(self.m_fluidDataBranch,'PVT-GAS',filename,'Gas PVT tables')
			self.m_pvtWaterBranch    = self.makeLeafForBlock(self.m_fluidDataBranch,'PVT-WATER',filename,'Water PVT tables')
			
			a = lambda s=self,b=filename: self.h_editFrameFromFile(b,'REGIONINFO')
			self.m_regionDataBranch = self.m_fileBranch.addbranch(label='Show Region Info',selectcommand=a) 

			#self.m_regionDataBranch = self.m_fileBranch.addbranch(label='Regional Data Parameters')
			#self.m_equilibriumBranch = self.makeLeafForBlock(self.m_regionDataBranch,'EQUILIBRIUM',filename,'Equilibrium Tables')
			#self.m_migrationBranch   = self.makeLeafForBlock(self.m_regionDataBranch,'MIGRATION',filename,'Migration Line Parameters')
			#self.m_lgrBranch         = self.makeLeafForBlock(self.m_regionDataBranch,'LGRPARMS',filename,'LGR parameters')
			#self.m_sectorExtractBranch = self.makeLeafForBlock(self.m_regionDataBranch,'SECTOR_EXTRACT',filename, 'Sector Extractions')

			a = lambda s=self,b=filename: self.f_clearAllFrames()
			self.m_timeMgmtBranch       = self.m_fileBranch.addbranch(label='Well Management',selectcommand=a)
			a = lambda s=self,b=filename: self.h_editFrameFromFile(b,'TIMEINFO')
			self.m_timeMgmtBranch.addleaf(label='DATES',selectcommand=a)
			a= lambda s=self,b=filename: self.h_editFrameFromFile(b,'WELLINFO')
			self.m_timeMgmtBranch.addleaf(label='WELLS',selectcommand=a)
			a = lambda s=self,b=filename: self.h_editFrameFromFile(b,'Error-Check')
			self.m_syntaxBranch = self.m_fileBranch.addbranch(label='Show Syntax Errors',selectcommand=a) 
		self.submitJobParms.setDefaultModelFile(filename)

	def makeLeafForBlock(self,branch,ilabel,filename,showString=''):
		"""
		Internal function.
		"""
		a = lambda s=self,b=filename: self.h_editFrameFromFile(b,ilabel)
	
		#return self.m_modelBranch.addleaf(label=ilabel,selectcommand=a)
		if len(showString) < 1: showString = ilabel

		return branch.addleaf(label=showString,selectcommand=a)

	def m_runSyntaxChecker(self):
		"""
		Calls the syntax checker on the self.modelParser object if it exists.
		"""
		if self.modelParserObject <> None:
			self.modelParserObject.doMainConsistencyCheck()
			self.bFrameSyntaxErrors.clearErrors()

	def m_closeTheModelFile(self):
		filename = self.modelParserObject.filename
		del self.m_allModelParserObjects[filename]
		self.m_allModelParserObjects[filename] = None
		self.modelParserObject = None
		self.m_treeBrowser.delete(self.m_allFileBranches[filename])
		del self.m_allFileBranches[filename]
		self.m_allFileBranches[filename] = None

	def m_saveTheModelFile(self):
		"""
		Asks the user for a filename to save the powers model file to.
		"""
		fname = asksaveasfilename(filetypes=[("Models","*.model"),("All Files","*")])
		if fname == '': return
		t = fname.find('.model')
		if t < 0: fname.append('.model')               # Append extension if none 
		pathname = os.path.dirname(fname)              # Get absolute path
		self.m_collectUserInformation()                # maps GUI to objects.
		#
		# I have to adjust these items to absolute path names.
		#
		blk= self.modelParserObject.m_internalBlocks['SIMULATOR']
		blk.setKeywordValue('WELL_RATES',self.m_ratesFileName)
		blk.setKeywordValue('WELL_PERFS',self.m_perfsFileName)
		blk.setKeywordValue('RECURRENT_DATA',self.m_recurrentFileName)

		#print "The rates file information ..."
		#print 'Rates =', blk.getKeywordValue('WELL_RATES')

		self.modelParserObject.writeModelFile(fname)   # Actually write to disk 
		filename = fname + ".recurrent"
		self.writeRecurrentData(filename)


	def doNotPressThisButton(self):
		filename = os.getenv('HOME')+"/test.recurrent"
		self.writeRecurrentData(filename)

	def writeRecurrentData(self,filename):
		"""
		The recurrent files' keywords are not tallied here....
		Where do I record these???
		"""
		fd = open(filename,'w') 
		self.recurrentFileObject= self.m_allRecurrentFileObjects[self.m_recurrentFileName] 
		xdkeys = self.recurrentFileObject.keywordHolder.aKeywords.keys()
		xdkeys.sort()
		for xdk in xdkeys:
			v = self.recurrentFileObject.keywordHolder.getKeywordValue(xdk)
			if v <> 'None': 
				fd.write('%s %s\n'% (xdk, v))

		dkeys = self.modelParserObject.allDatesArray.keys();
		dkeys.sort()
		for dk in dkeys:
			dte = self.modelParserObject.allDatesArray[dk]
			if dte.mSource <> sourceRECURRENT: continue
			fd.write(dte.getOneLiner()+'\n')                      # Write DATE keyword,
			xdkeys = dte.aKeywords.keys()                         # Any keywords in date.
			xdkeys.sort()                      # Alphabetically, please.
			for xdk in xdkeys:
				v = self.recurrentFileObject.keywordHolder.getKeywordValue(xdk)
				if v == 'None': 
					fd.write('%s \n'% (xdk))
					continue
				if v <> None: fd.write('%s %s\n'% (xdk, v))
			print "Writing ...", dte.getOneLiner() 
			# This is in accordance with page 10-2 of the manual. 
			# Write the items in this order per date since the 
			# order of the blocks matters.
			# General items FIRST, 
			# 1. connections 
			# 2. pseudo 
			# 3. Rigs
			# 4. Rules
			# THEN write the WELL specific information.  
			hasConnections = 0
			cnames = dte.collections.keys()
			for cname in cnames:
				clist = dte.collections[cname].keys()
				if len(clist) > 0: hasConnections = 1
			#
			# connections
			#
			if hasConnections == 1: 
				fd.write("\nCONNECTIONS\n")
				for cname in cnames:
					ckeys = dte.collections[cname].keys()
					ckeys.sort()
					for ck in ckeys: 
						fd.write("%s %s { " % (cname, ck))
						clist = dte.getNamedCollection(cname,ck)
						i = 0
						for item in clist:
							if (i%8) == 0: fd.write('\n')
							fd.write(clist[i] + ' ')
							i = i + 1
						fd.write("}\n\n")
				fd.write("END_CONNECTIONS\n")
			#
			# pseudo 
			#
			if len(dte.pseudoItems.keys()) > 0:
				sk = dte.pseudoItems.keys()
				sk.sort()
				fd.write("\nPSEUDO\n")
				for psk in sk:
					ps = dte.pseudoItems[psk]
					fd.write(ps.getEditableString(showHeader=1))	
				fd.write("ENDPSEUDO\n")
			#
			# Rigs
			#
			if len(dte.allRigs) > 0:
				fd.write("\nRIGS\n")
				for rig in dte.allRigs:
					fd.write(rig.getEditableString(showHeader=1))	
				fd.write("ENDRIGS\n")
			#
			# 4. Rules
			#
			if len(dte.groupRules) > 0:
				fd.write("\nGROUPRULES\n")
				for rule in dte.groupRules:
					fd.write(rule.getEditableString(showHeader=1))	
					fd.write('\n')
				fd.write("END_GROUPRULES\n")

			#
			# FINALLY, write the WELL specific information
			#
			wkeys = dte.Wells.keys()
			if len(wkeys) > 0: 
				fd.write("WELLS\n")
				for wk in wkeys: 
					well = dte.Wells[wk]              # get the pointer.
					well.printWellLine(fd)            # 
				fd.write("\nENDWELLS\n")
			fd.write('\n')
		fd.close()
		
	def m_collectUserInputForFrame(self,blockName):
		"""
		Map GUI to Obj for all objects in the system. Called before a tab switch
		in the notebook.
		"""
		f = self.m_allModelFrames[blockName]
		if self.modelParserObject.m_internalBlocks.has_key(blockName):
			f.mapGuiToObj(self.modelParserObject.m_internalBlocks[blockName])


	def m_collectUserInformation(self):
		"""
		Map GUI to Obj for all objects in the system. Called before a write to disk.
		"""
		for name in self.modelParserObject.m_internalBlocks.keys(): 
			if name in ['COMPARATOR', 'SECTOR_EXTRACT', 'MIGRATION', 'LGRPARMS', 'EQUILIBRIUM'] : continue
			f = self.m_allModelFrames[name]
			f.mapGuiToObj(self.modelParserObject.m_internalBlocks[name])

		# TODO: I will worry about this in next step - April 10, 2005
	


	def m_collectSyntaxErrors(self):
		self.bFrameSyntaxErrors = self.m_allModelFrames['Error-Check'] 
		self.bFrameSyntaxErrors.clearErrors()
		self.bFrameSyntaxErrors.appendErrors(self.modelParserObject.getListOfErrors())        #
		for name in self.modelParserObject.m_internalBlocks.keys(): 
			self.bFrameSyntaxErrors.getSyntaxErrors(self.modelParserObject.m_internalBlocks[name]);
		#print "Len of errors = ", len(self.bFrameSyntaxErrors.sAccumulatedStrings)
		for item in self.modelParserObject.m_internalBlocks['GRID'].aModifyObjects:			
			self.bFrameSyntaxErrors.getSyntaxErrors(item);
		for item in self.modelParserObject.m_internalBlocks['GRID'].aArrayObjects:
			self.bFrameSyntaxErrors.getSyntaxErrors(item);
		for item in self.modelParserObject.m_internalBlocks['GRID'].aRegionObjects:
			self.bFrameSyntaxErrors.getSyntaxErrors(item);
		if self.rateFileObject <> None: 
			self.bFrameSyntaxErrors.appendErrors(self.rateFileObject.getListOfErrors())        #
		if self.perfFileObject <> None: 
			self.bFrameSyntaxErrors.appendErrors(self.perfFileObject.getListOfErrors())        #
		if self.recurrentFileObject <> None: 
			self.bFrameSyntaxErrors.appendErrors(self.recurrentFileObject.getListOfErrors())        #

		#print "Len of errors = ", len(self.bFrameSyntaxErrors.sAccumulatedStrings)
		self.bFrameSyntaxErrors.showErrors();

	def f_unimplemented(self):
		print "Not implemented"

	def f_writePickle(self):
		pass
		


	def f_testme(self,filename=None):
		#
		# The environment variable USERNAME or HOME must be set. I am using
		# /peasapps/ssd/husainkb/expt
		#

		#
		#
		modelname = askstring("Name of Model","Name That Model");
		if modelname == None: return

		pathname = self.repository + os.sep + modelname
		print "Okay, now I write...", modelname, " in\n" , pathname

		#
		# Adjust the path names of the rates, perfs and recurrent to be absolute.
		# Perhaps all the changes we make to the model in the 
		#

		blk= self.modelParserObject.m_internalBlocks['SIMULATOR']
		blk.setKeywordValue('WELL_RATES',self.m_ratesFileName)
		blk.setKeywordValue('WELL_PERFS',self.m_perfsFileName)
		blk.setKeywordValue('RECURRENT_DATA',self.m_recurrentFileName)
		self.modelParserObject.writeXMLFiles(modelname,pathname)
		
		#Now the subdirectory exists, so write this file.
		#wellinfo = pathname + os.sep + modelname + ".wells.pickle"
		#fd = open(wellinfo,'wb')
		#cPickle.dump(self.modelParserObject.allDatesArray,fd)
		#fd.close()


	def f_createModelFile(self):
		filename  = asksaveasfilename(filetypes=[("POWERS model","*.model"),  ("All Files","*")])
		if not filename: return
		self.f_setCurrentFile(filename,create=1)   # Create an empty object or use existing
		#self.m_rightFrame.pack_forget()            # Blank it out
		if self.m_allModelFrames == None:  self.f_makeModelFrames(self.m_rightFrame)
		self.f_loadModelFile(filename)
		self.m_mapAllBlocksToGui()
		self.m_messageBar.message('state','Opened '+filename)
		self.submitJobParms.setDefaultModelFile(self.m_modelFilename)
		self.m_messageBar.message('state','I have finished mapping the new files')
		self.m_messageBar.update()

	def f_openModelFile(self):
		ifile = askopenfilename(filetypes=[("POWERS model","*.model"),  ("All Files","*")])
		if ifile: 
			self.f_loadInFile(ifile)

	def f_loadInFile(self,ifile):
		self.f_loadModelFile(ifile)
		self.m_rightFrame.pack_forget()
		self.m_mapAllBlocksToGui()
		self.m_messageBar.message('state','Opened '+ifile)
		self.m_rightFrame.pack(side=RIGHT,fill=BOTH,expand=1)
		pathname = os.path.dirname(ifile)
		self.writeSaveParameters(pathname)
		
		basename = os.path.basename(ifile)
		f = basename.find('.model.xml')
		if f<0: return

		modelname = basename[0:f]
		pathname = os.path.dirname(ifile)
		self.writeSaveParameters(pathname)
		wellinfo = pathname + os.sep + modelname + ".wells.pickle"
		self.m_messageBar.message('state','I have finished reading and mapping the input files')
		self.m_messageBar.update()

	def f_importModelFile(self):
		"""
		Loads in a model file into the tree.
		"""
		ifile = askopenfilename(filetypes=[("model","*.model"),("All Files","*")])		
		if ifile:
			self.f_loadModelFile(ifile)
			self.m_rightFrame.pack_forget()
			self.m_mapAllBlocksToGui()
			self.m_messageBar.message('state','Opened '+ifile)
			self.m_rightFrame.pack(side=RIGHT,fill=BOTH,expand=1)

	def f_quitProgram(self):
		"""
		Do something...
		
		"""
		sys.exit(0)

	def f_openProjectFile(self):
		self.manageParameters.openProjectXMLfile(eraseList=1)

	def f_importProjectFile(self):
		self.manageParameters.openProjectXMLfile(eraseList=0)

	def f_saveProjectFile(self):
		self.manageParameters.saveProjectXMLfile(saveas=0)

	def f_copyProjectFile(self):
		self.manageParameters.saveProjectXMLfile(saveas=1)

	def f_copyXMLfile(self):
		self.manageParameters.copyXMLfile()

	def f_makeMenuBar(self,where):	
		"""
		Creates the menu bar for the main program.
		"""
		self.m_menuBalloon = Pmw.Balloon(where)
		self.m_menuBar = Pmw.MenuBar(where,hull_relief=RAISED,hull_borderwidth=1, balloon=self.m_menuBalloon)
		self.m_menuBar.pack(fill=X)
		self.m_menuBar.addmenu('File','Simple Commands')
	
		self.m_menuBar.addmenuitem('File', 'command','Load XML file', label='Load XML file', command = self.f_openProjectFile)
		self.m_menuBar.addmenuitem('File', 'command','Import XML file', label='Import XML file', command = self.f_importProjectFile)
		self.m_menuBar.addmenuitem('File', 'command','Save As XML file and reopen copy', label='Save As another XML', command = self.f_saveProjectFile)
		self.m_menuBar.addmenuitem('File', 'command','Save a Copy and keep working with this one.', label='Save Copy of this XML file',command = self.f_copyProjectFile)
		self.m_menuBar.addmenuitem('File', 'command','Copy an XML File to another file', label='Copy XML files',command = self.f_copyXMLfile)
		self.m_menuBar.addmenuitem('File', 'command','View an XML File in Mozilla', label='View this XML file',command = self.f_showMozilla)

		############################## These are for new models. #######################################
		#self.m_menuBar.addmenuitem('File', 'command','Save as XML set', label='Save XML set', command = self.f_testme)
		#self.m_menuBar.addmenuitem('File', 'command','Save Model', label='Save Model File', command = self.m_saveTheModelFile)
		#self.m_menuBar.addmenuitem('File', 'command','Close a file', label='Close', command = self.m_closeTheModelFile)
		#self.m_menuBar.addmenuitem('File', 'command','Re-read Time', label='Read Time', command = self.f_readTimeAgain)

		self.m_menuBar.addmenuitem('File', 'command','Quit', label='Quit', command = self.f_quitProgram)


		#self.m_menuBar.addmenu('Jobs','Simple Commands')
		#self.m_menuBar.addmenuitem('Jobs', 'command','Run a job', label='Run Job', command = self.f_runjob)


		self.m_menuBar.addmenu('Options','Options file')
		#a = lambda s=self,b=1: s.m_disableTimeInfo(b)
		#self.m_menuBar.addmenuitem('Options', 'command','Disable Rates', label='Enable Rates', command = a)
		#a = lambda s=self,b=0: s.m_disableTimeInfo(b)
		#self.m_menuBar.addmenuitem('Options', 'command','Enable Rates', label='Disable Rates', command = a)

		#a = lambda s=self: s.doNotPressThisButton()
		#self.m_menuBar.addmenuitem('Options', 'command','Dont Press', label='Dont Press', command = a)

		a = lambda s=self: s.selectEditor()
		self.m_menuBar.addmenuitem('Options', 'command','64bit Monitor jobs', label='64 bit Monitor', command = self.f_execJobMonitor)
		self.m_menuBar.addmenuitem('Options', 'command','Old Monitor jobs', label='Old Monitor', command = self.f_runJobMonitor)
		#self.m_menuBar.addmenuitem('Options', 'command','See Output files', label='Output Monitor', command = self.f_runTailMonitor)
		self.m_menuBar.addmenuitem('Options', 'command','Select Editor', label='Select Editor', command = a)

		# Command and label to use.
		self.toolDir = "/peasapps/ssd/test_lnx/scripts/Linux/"	
		self.toolCommands = {  
				"simreport300" : "SIMREPORT 300" ,
				"EclxGui400": "EXTRACT 400", 
				"run_SP400": "SURVEYPLOT 400", 
				"run_SP300": "SURVEYPLOT 300", 
				"simreport400" : "SIMREPORT 400" , 
				"simstat302" : "SIMSTAT 302" , 
				"simstat400" : "SIMSTAT 400" , 
				"simview400" : "SIMVIEW 400" , 
				"simviewecl" : "SIMVIEW ECL" , 
				#"gocad_start" : "GOCAD" , 
				"EclxGui": "EXTRACT 300", 
				#"geoview": "GEOVIEW", 
				"chears_ext": "CHEARS Extract",
				"geolog_mnif" : "GEOLOG MANIFA" , 
				"run_tecplot5" : "TECPLOT 5" , 
				"run_tecplot" : "TECPLOT 4" , 
				"tec61F1706" : "TECPLOT MANIFA" , 
				"gocad213" : "GOCAD MANIFA" , 
				#"rsDV" : "RS3D", 
				"SimStore" : "SimStore",
				"rsECL" : "ListECL" }

		self.m_menuBar.addmenu('Tools','Tools for viewing files',tearoff=1)
		#tkeys = self.toolCommands.keys()

		tkeys = [ "simreport400" , "simview400" , "simstat400" , "EclxGui400" , "run_SP400", 'separator',
				"simreport300" , "simviewecl" , "EclxGui", "simstat302" ,  "run_SP300", 'separator',
				"tec61F1706", 'geolog_mnif', 'gocad213', 'separator',
				"chears_ext", 'run_tecplot5', "run_tecplot" , "rsECL" ] #, "rsDV" , "SimStore" ] 

		for tkey in tkeys: 
			if tkey =='separator':	
				self.m_menuBar.addmenuitem('Tools','separator','separator')
			else:
				a = lambda s=self,b=tkey: s.m_startExternalProgram(b)
				tvalue = self.toolCommands[tkey]
				self.m_menuBar.addmenuitem('Tools', 'command','External file', label=tvalue, command = a)

		self.m_menuBar.addmenu('Special','Tools for viewing files',tearoff=1)
		a = lambda s=self,b='ECLbrowser': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='ECL browser', command = a)
		a = lambda s=self,b='PEXTRACT': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='P_EXTRACT', command = a)
		a = lambda s=self,b='wxSOS': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='P_SIMRPT64', command = a)
		#a = lambda s=self,b='SOSimRpt': s.m_startParallelSimReport(b)
		#self.m_menuBar.addmenuitem('Special', 'command','External file', label='SimRpt 32', command = a)
		a = lambda s=self,b='Text': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='Text Editor', command = a)
		a = lambda s=self,b='PVTSAT': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='PVT/SAT Viewer', command = a)
		a = lambda s=self,b='FlowTable': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='Flow Table', command = a)
		a = lambda s=self,b='Ripper': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='ECL Slicer', command = a)
		a = lambda s=self,b='RS3D': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='RS3D - 3D', command = a)
		a = lambda s=self,b='XYplotter': s.m_startParallelSimReport(b)
		self.m_menuBar.addmenuitem('Special', 'command','External file', label='XY Plotter', command = a)

		self.m_menuBar.addmenu('Help','Help with Commands',side='right')
		#self.m_menuBar.addmenuitem('Help', 'command','Help file', label='Help', command = self.f_unimplemented)
		self.m_menuBar.addmenuitem('Help', 'command','Contact Info', label='Contact', command = self.f_showContact)
		self.m_menuBar.addmenuitem('Help', 'command','Help file', label='Help', command = self.f_showHelp)
		self.m_menuBar.addmenuitem('Help', 'command','Guide Sheet', label='Guide', command = self.f_showGuide)
		self.m_menuBar.addmenuitem('Help', 'command','About the program', label='About', command = self.f_showAbout)


	def f_showMozilla(self):
		if os.fork() == 0:
			os.execl("/usr/bin/mozilla", "mozilla", self.manageParameters.projectsXMLfilename)

	def f_showHelp(self):
		if os.fork() == 0:
			os.execl("/usr/bin/xpdf", "xpdf", "/peasd/ssd/husainkb/template/guiManual.pdf")

	def f_showGuide(self):
		if os.fork() == 0:
			os.execl("/usr/X11R6/bin/xview", "xview", "/peasd/ssd/husainkb/template/pGUI_guide.gif")

	def f_showContact(self):
		self.helpWin = Toplevel()
		self.helpWin.title('Support: Kamran Husain 8747898')
		self.helpImg = PhotoImage(file="/peasd/ssd/husainkb/template/pguiSplash.gif")
		self.helpBtn = Label(self.helpWin,image=self.helpImg).pack(side=TOP,fill=BOTH,expand=1)
		self.helpWin.mainloop()


	def selectEditor(self):
		thisdir = os.getcwd()
		os.chdir('/usr/bin')
		ifile = askopenfilename(filetypes=[("All Files","*")])
		if ifile: self.manageParameters.userEditorCommand = ifile
		os.chdir(thisdir)
		#
		# I have to save this information somewhere.
		#

	def f_showAbout(self):
		showinfo('About','This version is written by \nKamran Husain, PEASD/SSD 874 7898\nSaudi Aramco\n' + myVersionString)

	def f_makeStatusBar(self,where):
		"""
		The status bar at the bottom of the window.
		"""
		self.m_progressBar = ProgressBar(where,min=0,max=100,value=0,doLabel=1,width=150,fillColor='blue',labelFormat='%d');
		self.m_progressBar.frame.pack(side=RIGHT,expand=0,pady=2,padx=5)
		self.m_messageBar = Pmw.MessageBar(where, entry_width=40,entry_relief=GROOVE,labelpos=W,label_text='Msgs')
		self.m_messageBar.pack(side=LEFT,fill=X,expand=1,padx=5,pady=2)

	def updateProgressBar(self,value=0,vlimit=100):
		"""
		Shell for the function that updates the progress bar.
		"""
		self.m_progressBar.updateProgress(value,vlimit)

	def f_runjob(self):
		"""
		Starts the run job command as an independant window.
		"""
		self.r = Tk()
		self.b = makeSubmitForm(self.r)

	def f_execJobMonitor(self):
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runMonitor.ksh")
		
	def f_runJobMonitor(self):
		self.rJobMon = Toplevel()   # Don't use Tk() since this handles events.
		self.rJobMon.option_add('*font',('courier',10,'bold'))
		self.rJobMon.geometry("%dx%d+0+0" %(600,600))
		self.rJobMon.title("PGUI job monitoring extravaganza") 
		self.jobMonitorApplication = pJobInfoFrame(self.rJobMon)
		self.rJobMon.mainloop()

	def f_runTailMonitor(self):
		self.rTailMon = Toplevel()   # Don't use Tk() since this handles events.
		self.rTailMon.option_add('*font',('courier',10,'bold'))
		self.rTailMon.geometry("%dx%d+0+0" %(500,600))
		self.rTailMon.title("PGUI output monitoring extravaganza") 
		self.tailMonitorApplication = pMonitorFrame(self.rTailMon)
		self.rTailMon.mainloop()


if __name__ == '__main__':
	setPlatformSpecificPaths()
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		filename = None
	root = Tk()
	root.title('POWERS GUI 64bit (aka Office) ' + myVersionString + ' Support: Kamran Husain 8747898' )

	try:
		root.option_readfile("/red/ssd/appl/khusain/64bit/srcs/optionDB")
	except:
		print "Using defaults"
		root.option_add("*font",'Times 10')
		root.option_add("*background",'gray')
		root.option_add("*foreground",'black')
		root.option_add("*Label*foreground",'#1F5977')
		root.option_add("*Label*background",'gray')
		root.option_add("*Frame*background",'gray')
		root.option_add("*Button*background",'#0D18BA')
		#root.option_add("*Button*foreground",'black')
		root.option_add("*Button.borderwidth",'2')

	try:
		tt = os.getenv('HOME') + "/powersdata/optionDB"
		root.option_readfile(tt)
		print "Using user optionDB" ,tt
	except:
		pass

	sendMessage('PowersGUI','INIT')
	#root.option_add("*font",'courier 18')
	root.geometry("%dx%d+0+0" %(1024,640))
	makeMainProgram(root,filename)
	root.mainloop()

