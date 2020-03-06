

from Tkinter import *
import Pmw
import sys
import os, pwd
import time
import string
import xml
from xml.dom import minidom

from tkSimpleDialog import * 
from tkMessageBox import * 
from tkFileDialog import *
from TableList import *
from pObject import *
from pMonitor import *
from pFlowTableFrame import *
from pPVTTables import *
from pSATTables import *
from pPVTframes import *
from pPBFutils import *
from pUsageLogger import sendMessage
import pUserIdInfoFrame 
from pChangeRestart import verifyCopyModelFile

def showTime(x):
	return strftime("%Y.%m.%d %H.%M ", localtime(x)) 

def visit(arg,dirname,files):
	"""
	arg is appended with pathnames. Send an empty list or a filled one.
	Only files with a *.model extension are included in the list
	"""
	for name in files: 
		fn,ext = os.path.splitext(name)
		#if ext in [ '.DATA', '.model'] :
		if ext in [ '.model'] :
			fullname = dirname + os.sep + name
			modelname = fn
			xlines = os.stat(fullname)
			#sz = strftime("%Y.%m.%d %H.%M ", localtime(xlines[-1])) + "%d " % xlines[6]  
			sz = showTime(xlines[-1]) + "(%dK)" % int(xlines[6] / 1024)
			arg.append((modelname,fullname,sz))

extractedExtensions = [".tu_xml",".CNTLF"]

def visitExtracted(arg,dirname,files):
	"""
	arg is a bidirectional array of arrays:  
		arg[0] is appended with pathnames. Send an empty list or a filled one.
		arg[1] must be filled with the model base name to look for.
		Only files with a *.tu_ndx or *.CNTLF  extension are included in the list
		Files with _mig or _mtb in their base name are ignored.
	"""
	aname = arg[1]  # The modelbase
	sfiles = [ aname + ef for ef in extractedExtensions ] 
	sfiles = map(str,sfiles)
	for name in files: 
		fn,ext = os.path.splitext(name)
		fmig = fn.find('_mig')
		fmtb = fn.find('_mtb')
		if fmig > -1 or fmtb > -1: continue
		if name in sfiles:
			fullname = dirname + os.sep + name
			xlines = os.stat(fullname)
			sz = showTime(xlines[-1]) + "(%dK)" % int(xlines[6] / 1024)
			arg[0].append(('EXTRACTED_FILE',fullname,sz))


def createRowEntry(fullname):
	basename = os.path.basename(fullname)
	modelname,ext = os.path.splitext(basename)
	xlines = os.stat(fullname)
	sz = showTime(xlines[-1]) + "(%dK)" % int(xlines[6] / 1024)
	return (modelname,fullname,sz)
	

#
# Constants for this file.
#
modelFileColumnIndex = 1
otherFileColumnIndex = 1
tableListBackground = 'gray'
externalChecker = 'python /red/ssd/appl/khusain/powers/GUI/pSyntaxCheck.py '
scriptBaseDir = '/red/ssd/appl/khusain/64bit/srcs/'
testchars = "".join(map(chr,range(32,127))+list('\n\r\t\b'))
nullchars = string.maketrans("","")    # Get identity table.


def istextfile(filename,blocksize=1024):
	if not os.path.exists(filename): return 1
	return istext(open(filename).read(blocksize))

def istext(s):
	if "\0" in s: return 0     # Nul characters imply not text
	if not s: return 1         # Empty file is text.
	t = s.translate(nullchars,testchars) # remove text characters.
	if len(t)/len(s) > 0.2: return 0     # more than 20% non-text chars, 
	return getType(s)


def getType(s):
	"""
	Guesses at the type of file from some of the contents.
	Type   File 
	1      Text only
	2      Flow Table
	3      PVT Table 
	4      SAT Table
	5      XML file 
	"""
	fXML1 = s.find('xml') 
	fXML2 = s.find('version') 
	if fXML1 > 0 and fXML2 > 0 and fXML2 > fXML1: return 5
	fBHP = s.find('BHP')
	fPRD = s.find('PRD')
	if fBHP > -1 and fPRD > -1: 
		#print "Flow table"; 
		return 2
	fLABELS = s.find('GRAPH_LABELS')
	fUNITS = s.find('GRAPH_UNITS')
	fBUBBLE = s.find('BUBBLE')
	fSTANDARD = s.find('STANDARD_DENSITY')
	if fLABELS > -1 and fUNITS > -1:
		if fBUBBLE > -1 or fSTANDARD > -1: 	
			#print "PVT table"; 
			return 3
		else: 
			#print "SAT table"; 
			return 4
	return 1


class selectUserFileDlg(Frame):
	def __init__(self,parent=None,usethis=None):
		Frame.__init__(self,parent)
		self.pack()
		self.modelManager = usethis
		self.selectedProjectName =  ''
		self.selectedFileName = ''
		self.filesToAdd = []
		self.usersdir = {}
		getFromPet2 = 0;
		try:
			xlines = open(scriptBaseDir + 'userInfo.txt','r').readlines()
			for xln in xlines: 
				username, homedir = xln.split(':')
				self.usersdir[username.strip()] = homedir.strip()
		except:
			self.usersdir = pUserIdInfoFrame.returnDefinedUserDirectory()
		self.listOfUsers = []

		for username in self.usersdir.keys():
			userdir =  self.usersdir[username]
			try:
				ms = os.chdir(userdir)
			except:
				continue
			filename = userdir + '/powersdata/projects.xml' 
			try:
				ms = os.stat(filename)
			except:
				continue
			self.listOfUsers.append(username)

		self.listOfUsers.sort()
		self.projList = {} 
		self.fileList = []
		self.ubBox = Frame(self)
		self.ubBox.pack(side=LEFT,fill=Y)


		self.cbUserList = Pmw.ScrolledListBox(self.ubBox,
					listbox_selectmode = SINGLE,
					labelpos = 'n' ,
					label_text = 'Office Users',
					items = self.listOfUsers,
					listbox_exportselection=0,
					usehullsize=1,hull_width=100,hull_height=100,
					selectioncommand=self.m_selectUserID)
		self.cbUserList.pack(side=LEFT,expand=1,fill=Y)

		#a = lambda s=self, b='List' : s.doUserFetch(b)
		#self.addFileBtn = Button(self.ubBox,text="Get User Projects",command=a)
		#self.addFileBtn.pack(side=BOTTOM,fill=X,expand=0)

		self.rbBox = Frame(self)
		self.rbBox.pack(side=RIGHT,fill=BOTH,expand=1)

		self.cbProjList = Pmw.ScrolledListBox(self.rbBox,
					listbox_selectmode = SINGLE,
					items = [], 
					labelpos = N, 
					label_text = 'Projects',
					listbox_exportselection=0,
					#usehullsize=1,hull_width=520,hull_height=100,
					selectioncommand = self.m_selectProjID)
		self.cbProjList.pack(side=TOP,expand=1,fill=BOTH)
		self.cbFileList = Pmw.ScrolledListBox(self.rbBox,
					listbox_selectmode = EXTENDED,
					items = [], 
					labelpos = N, 
					label_text = 'Files',
					listbox_exportselection=0,
					#usehullsize=1,hull_width=520,hull_height=100,
					selectioncommand = self.m_selectFileID)
		self.cbFileList.pack(side=TOP,expand=1,fill=BOTH)

		self.btnBox = Frame(self.rbBox)
		self.btnBox.pack(side=BOTTOM,fill=X,expand=1)
		a = lambda s=self, b='Add Files' : s.doAddFiles(b)
		self.addFileBtn = Button(self.btnBox,text="Add Files",command=a)
		self.addFileBtn.pack(side=LEFT,fill=X,expand=0)
		a = lambda s=self, b='Dismiss' : s.doQuit(b)
		self.dismissBtn = Button(self.btnBox,text="Dismiss",command=a)
		self.dismissBtn.pack(side=LEFT,fill=X,expand=0)

	def m_selectUserID(self):
		sel = self.cbUserList.getcurselection()
		if len(sel)< 1: return
		username = sel[0] 
		self.openUserProjectFile(username)

	def m_selectProjID(self):
		"""
		"""
		if len(self.projList) < 1:  return 
		projnames = self.projList.keys()
		#print "Selected project list....", , projnames
		listbox = self.cbProjList.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()				    # The index 
		if len(sel) == 0: return
		ndx = int(sel[0])
		self.selectedProjectName =  projnames[ndx]
		self.fileList = self.projList[self.selectedProjectName]
		self.cbFileList.setlist(self.fileList)

	def m_selectFileID(self):
		if len(self.fileList) < 1:  return 
		listbox = self.cbFileList.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()				    # The index 
		if len(sel) == 0: return
		self.filesToAdd = []
		for nm in sel:
			ndx = int(nm)
			self.filesToAdd.append(self.fileList[ndx])
		#print "Names of files selected to add == ", self.filesToAdd

	def doUserFetch(self,parm):
		txt = self.cbUserList.component('entry')
		username = txt.get()
		#print "User name = ", username
		self.openUserProjectFile(username)

	def openUserProjectFile(self,parm):
		#print "Open User Project File", parm
		username = parm
		userdir =  self.usersdir[username.strip()] + '/powersdata'
		try:
			ms = os.chdir(userdir)
		except:
			showwarning("Error","The user has has no powers gui data directory in \n" + userdir)
			return
		
		filename = userdir + '/projects.xml' 
		try:
			ms = os.stat(filename)
		except:
			showwarning("Error","The user has has no %s \nfile in their (%s) directory in \n" % (filename,userdir))
			return

		# 
		# Now read the projects file in a DOM tree and return just file names
		#
		#print "Reading ... ", filename
		#xtxt = open(filename,'r').read()
		#strdata = xml.sax.saxutils.escape(xtxt,{'"':'&quot',"'":'&apos;'})
		#dom = minidom.parseString(strdata)
		try:
			dom = minidom.parse(filename)
		except:
			return
		nodes = dom.getElementsByTagName('PROJECT')  # All the notes are read here.
		self.fileList=[]
		self.projList={}
		for nd in nodes:
			key = None
			val = None
			for chld in nd.childNodes:
				if chld.nodeName == 'NAME': 
					key = chld.childNodes[0].nodeValue
					if not self.projList.has_key(key):
						self.projList[key] = []
				if chld.nodeName == 'FILE': 
					if chld.hasChildNodes(): 
						val = chld.childNodes[0].nodeValue
						plist = self.projList[key]
						if not val in plist: self.projList[key].append(val)
		self.cbProjList.setlist(self.projList.keys())


	def doQuit(self,parm):
		#Frame.quit(self) will quit the manager!
		self.modelManager.userCaseQuit()

	def doAddFiles(self,parm):
		if len(self.filesToAdd) < 1: return 
		self.modelManager.addFilesByNameToProject(self.filesToAdd)


class pModelManagerFrame(Frame):
	def __init__(self,parent,masterObj):
		Frame.__init__(self,parent)
		self.pack(side=TOP,fill=BOTH,expand=1)
		self.justShowedModel = 1
		self.monWindow = None
		self.userDialog = None  # for user id selection..

		self.pop_model = Menu(self,tearoff=0)
		a = lambda s=self,n='vim' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='vim', command=a)
		a = lambda s=self,n='tail' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='tail', command=a)
		a = lambda s=self,n='saveas' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='save as', command=a)
		self.pop_model.add_separator()
		a = lambda s=self,n='diff' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='diff models', command=a)
		a = lambda s=self,n='include' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='show include', command=a)
		self.pop_model.add_separator()
		a = lambda s=self,n='delete' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='delete 1 file', command=a)
		a = lambda s=self,n='konqueror' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='file manager', command=a)
		self.pop_model.add_separator()

		a = lambda s=self,n='savesimstore' : s.popupmenuCmd(n)
		self.pop_model.add_command(label='to Simstore', command=a)


		uname = os.getenv('USER')
		if uname in ['tibanaa', 'husainkb']:
			a = lambda s=self,n='runsimstore' : s.popupmenuCmd(n)
			self.pop_model.add_command(label='Run Simstore', command=a)



		###################### INPUT TABLE MIDDLE BUTTON POPUP ####################
		self.pop1 = Menu(self,tearoff=0)
		a = lambda s=self,n='vim' : s.popupmenuCmd(n)
		self.pop1.add_command(label='vim', command=a)
		a = lambda s=self,n='tail' : s.popupmenuCmd(n)
		self.pop1.add_command(label='tail', command=a)
		a = lambda s=self,n='saveas' : s.popupmenuCmd(n)
		self.pop1.add_command(label='save as', command=a)
		self.pop1.add_separator()
		a = lambda s=self,n='include' : s.popupmenuCmd(n)
		self.pop1.add_command(label='show include', command=a)
		self.pop1.add_separator()
		a = lambda s=self,n='delete' : s.popupmenuCmd(n)
		self.pop1.add_command(label='delete 1 file', command=a)
		a = lambda s=self,n='konqueror' : s.popupmenuCmd(n)
		self.pop1.add_command(label='file manager', command=a)
		self.pop1.add_separator()

		a = lambda s=self,n='rsecl' : s.popupmenuCmd(n)
		self.pop1.add_command(label='listECL', command=a)
		a = lambda s=self,n='rssat1' : s.popupmenuCmd(n)
		self.pop1.add_command(label='PVT SAT New', command=a)
		a = lambda s=self,n='rssat2' : s.popupmenuCmd(n)
		self.pop1.add_command(label='PVT SAT Old', command=a)
		a = lambda s=self,n='rs3d' : s.popupmenuCmd(n)
		self.pop1.add_command(label='RS3D', command=a)
		a = lambda s=self,n='rsXY' : s.popupmenuCmd(n)
		self.pop1.add_command(label='RSXY', command=a)


		###################### OUTPUT TABLE MIDDLE BUTTON POPUP ####################
		self.pop_output = Menu(self,tearoff=0)
		a = lambda s=self,n='vim' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='vim', command=a)
		a = lambda s=self,n='tail' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='tail', command=a)
		a = lambda s=self,n='saveas' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='save as', command=a)
		self.pop_output.add_separator()
		a = lambda s=self,n='delete' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='delete 1 file', command=a)
		a = lambda s=self,n='konqueror' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='file manager', command=a)
		self.pop_output.add_separator()
		#a = lambda s=self,n='savesimstore' : s.popupmenuCmd(n)
		#self.pop_output.add_command(label='to Simstore', command=a)
		a = lambda s=self,n='rsecl' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='listECL', command=a)
		a = lambda s=self,n='extract' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='P-extract', command=a)
		a = lambda s=self,n='rs3d' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='RS3D', command=a)
		a = lambda s=self,n='rsXY' : s.popupmenuCmd(n)
		self.pop_output.add_command(label='RSXY', command=a)

		###################### EXTRACTED TABLE MIDDLE BUTTON POPUP ####################
		self.pop_extracted = Menu(self,tearoff=0)
		a = lambda s=self,n='simreport' : s.popupmenuCmd(n)
		self.pop_extracted.add_command(label='simreport', command=a)
		a = lambda s=self,n='vim' : s.popupmenuCmd(n)
		self.pop_extracted.add_command(label='vim', command=a)
		#a = lambda s=self,n='saveas' : s.popupmenuCmd(n)
		#self.pop_extracted.add_command(label='save as', command=a)
		self.pop_extracted.add_separator()
		a = lambda s=self,n='delete' : s.popupmenuCmd(n)
		self.pop_extracted.add_command(label='delete 1 file', command=a)
		a = lambda s=self,n='konqueror' : s.popupmenuCmd(n)
		self.pop_extracted.add_command(label='file manager', command=a)
		self.pop_extracted.add_separator()
		a = lambda s=self,n='mozilla' : s.popupmenuCmd(n)
		self.pop_extracted.add_command(label='Mozilla', command=a)

		if os.path.exists('/usr/X11R6/bin/gvim'):
			self.userEditorCommand = '/usr/X11R6/bin/gvim'
		else: 
			self.userEditorCommand = '/usr/bin/vim'
		self.userXtermCommand = '/usr/bin/xterm'
		self.userSimstoreCommand = '/peasapps/ssd/test_lnx/scripts/Linux/SimStoreE-linux'
		self.numNodes  = 32 
		self.use_node  = 'test'
		self.doExtract = 1
		self.parent = parent
		self.masterObject = masterObj
		self.monitorObject = None 
		#self.submitJobParms = None
		self.lastsort = '-decreasing' 
		self.guiEditor = None 
		self.projectsXMLdirectory = os.getenv('HOME') + os.sep + 'powersdata' 
		self.projectsXMLfilename  = self.projectsXMLdirectory + os.sep + 'projects.xml'
		self.notesXMLfilename     = self.projectsXMLdirectory + os.sep + 'notes.xml'
		self.fileNotes = {}
		self.listOfProjects = {}

		self.snapshotKeywords = ['XNODES','YNODES','ZNODES','TITLE','RESERVOIR_TYPE','PHASES','BINARY_DATA_DIRECTORY']
		#self.snapshotRequired = {}

		self.mainPane = Pmw.PanedWidget(self,orient=HORIZONTAL) 
		self.mainPane.pack(side=TOP,fill=BOTH,expand=1)

		self.mainPane.add('F1',size=.8)
		#self.mainPane.updatelayout()
		self.mainPane.add('F2',size=200)
		self.mainPane.add('F3',size=0)
		self.mainPane.configurepane('F3',size=1)
		self.m_mgmtFrame = Pmw.PanedWidget(self.mainPane.pane('F1'))
		self.m_mgmtFrame.pack(side=TOP,fill=BOTH,expand=1)
		self.m_saveBtnForm = Frame(self.mainPane.pane('F2'))
		self.m_saveBtnForm.pack(side=TOP,expand=0,fill='none')
		self.m_saveNotesBtn = Button(self.m_saveBtnForm,command=self.saveNotesOnFile,text='Save Note!')
		self.m_saveNotesBtn.pack(side=LEFT)
		self.m_notesWidget = Pmw.ScrolledText(self.mainPane.pane('F2'), borderframe=1,labelpos=N,label_text ='Notes',
				 	text_wrap='none',usehullsize=1,hull_width=10,hull_height=100)
		self.m_notesWidget.pack(side=TOP,fill=BOTH,expand=YES)
		
		#self.m_snapshotWidget = Pmw.ScrolledText(self.mainPane.pane('F2'), borderframe=1, #labelpos=N,label_text ='',
				 	#text_wrap='none',usehullsize=1,hull_width=10,hull_height=80)
		#self.m_snapshotWidget.pack(side=BOTTOM,fill=X,expand=0)

		#self.m_saveAllNotes = Button(self.m_saveBtnForm,text="Sync",command=self.flushDBM)
		#self.m_saveAllNotes.pack(side=RIGHT)

		self.m_mgmtFrame.add('dirFrame',min=100,size=300)
		self.m_mgmtFrame.add('modelFileFrame',min=100,size=200)
		self.lastWorkingDir  = scriptBaseDir + 'powers'
		self.lastProjectName = ''
		self.editableFiles = ['MODEL_FILE', 'INCLUDE_FILE','BINARY_FILE','TEXT_FILE',\
			'WELL_PERFS','WELL_RATES','RECURRENT_DATA','RESTART_INPUT', 'OUTPUT_FILE', 'INT_FILE', 'VERSION_INFO', 'EXTRACTED_FILE']
		self.outputFiles   = ['RESTART_OUTPUT', 'MAPS_OUTPUT' ]
		#
		self.m_leftFrame = Frame(self.m_mgmtFrame.pane('dirFrame'),width=150,height=100,relief=GROOVE)
		self.m_leftFrame.pack(side=LEFT,fill=BOTH,expand=1)

		self.m_rightFrame = Frame(self.m_mgmtFrame.pane('modelFileFrame'))
		self.m_rightFrame.pack(side=RIGHT,fill=BOTH,expand=1)
		#
		#  Add the list of jobs here.
		#
		self.tableOfModels = ScrolledTableList(self.m_leftFrame,  width=40,showseparators='yes',
			#stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, 
			columns=(12,"Case",40,"Location",40,"Info"), 
			labelcommand=self.m_sortModelsByColumn,
			selectbackground='lightblue',
			exportselection='no',
			selectmode='extended',
			selecttype='row')
			#editendcommand=self.m_editEndCommand)
		#self.tableOfModels.columnconfigure(0,editable='YES')
		self.tableOfModels.pack(side=RIGHT,expand=1,fill=BOTH)
		self.tableOfModels.addHorizontalBar()

		self.projectsFrame = Frame(self.m_leftFrame)
		self.projectsFrame.pack(side=LEFT)
		self.projectXMLlabel = Label(self.projectsFrame,text='',relief='ridge',bg='darkblue',fg='white')
		self.projectXMLlabel.pack(side=TOP,fill=X,anchor='n')
		
		self.addProjectBtn = Button(self.projectsFrame,text="Add Project",command=self.addProjectCB)
		self.addProjectBtn.pack(side=TOP,fill=X,anchor='n')
		self.delProjectBtn = Button(self.projectsFrame,text="Del Project",command=self.delProjectCB)
		self.delProjectBtn.pack(side=TOP,fill=X,anchor='n')
		self.addFilesToProjBtn = Button(self.projectsFrame,text="Add Case\nTo Project",command=self.addFilesToProjectCB)
		self.addFilesToProjBtn.pack(side=TOP,fill=X,anchor='n')
		self.delFilesToProjBtn = Button(self.projectsFrame,text="Del Case\nFrom Project",command=self.delFilesToProjectCB)
		self.delFilesToProjBtn.pack(side=TOP,fill=X,anchor='n')

		#self.projectXMLlblPath = Label(self.projectsFrame,justify='left')
		#self.projectXMLlblPath.pack(side=TOP,fill=X,anchor='n')

		skeys = self.listOfProjects.keys()
		skeys.sort()
		self.sl_projects = Pmw.ScrolledListBox(self.projectsFrame,
					listbox_selectmode = SINGLE,
					items = skeys,
					labelpos = N, 
					label_text = 'Projects',
					selectioncommand = self.selectProjectCB,
					# dblclickcommand = self.selectCommand,
					listbox_exportselection=0)
					#usehullsize=1, hull_width=80, hull_height=200) # Don't work.
		self.sl_projects.pack(side=TOP,fill=BOTH,expand=1)

		self.t_btnsFrame = Frame(self.m_leftFrame)
		self.t_btnsFrame.pack(side=LEFT,fill=Y)

		self.btnsFrame = Frame(self.t_btnsFrame)
		self.btnsFrame.pack(side=TOP,fill=Y,expand=1)

		self.tableOfModels.bind('<Double-Button-1>',self.eventTableSelect)
		#self.tableOfModels.bind('<Double-Button-2>',self.eventTableModel)
		self.tableOfModels.bind('<Button-2>',self.evh_btn2_ModelFile)
		self.tableOfModels.bind('<Double-Button-3>',self.eventTableModel)
		self.tableOfModels.bind('<ButtonRelease-1>',self.eventTableSelect)

		self.findModelsbtn = Button(self.btnsFrame,text="Import\nCases",command=self.scanDir)
		self.findModelsbtn.pack(side=TOP,fill=X)

		self.findModelsbtn = Button(self.btnsFrame,text="Import\nUser Cases",command=self.userCaseScan)
		self.findModelsbtn.pack(side=TOP,fill=X)

		self.submitModelsbtn = Button(self.btnsFrame,text="Submit",command=self.submitModelCB)
		self.submitModelsbtn.pack(side=TOP,fill=X)


		#self.stopModelsbtn = Button(self.btnsFrame,text="Soft Kill",command=self.stopModelCB)
		#self.stopModelsbtn.pack(side=TOP,fill=X)
		self.startXtermBtn = Button(self.btnsFrame,text="XTERM",command=self.startXtermCB)
		self.startXtermBtn.pack(side=TOP,fill=X)


		#Deprecated
		#self.guiModelsbtn = Button(self.btnsFrame,text="GUI",command=self.toguiCB)
		#self.guiModelsbtn.pack(side=TOP,fill=X)

		self.checkModelsbtn = Button(self.btnsFrame,text="Syntax",command=self.checkModelCB)
		self.checkModelsbtn.pack(side=TOP,fill=X)

		#self.circleOfTrust = ['baddouma', 'husainkb', 'lincx', 'dossmn0f', 'nahdiua']
		#uname = os.getenv('USER')
		#if uname in self.circleOfTrust: 
		self.batchsubmitModelsbtn = Button(self.btnsFrame,text="Batch",command=self.batchsubmitModelCB)
		self.batchsubmitModelsbtn.pack(side=TOP,fill=X)

		self.m_saveAllNotes = Button(self.btnsFrame,text="Save",command=self.flushDBM)
		self.m_saveAllNotes.pack(side=TOP,fill=X)

		a = lambda a=1:self.saveProjectXMLfile(saveas=a)
		self.m_saveAllNotes = Button(self.btnsFrame,text="Save As",command=a)
		self.m_saveAllNotes.pack(side=TOP,fill=X)

		#self.m_saveAllNotes = Button(self.btnsFrame,text="TEST",command=self.testKill)
		#self.m_saveAllNotes.pack(side=TOP,fill=X)

		self.editModelsbtn = Button(self.btnsFrame,text="Save &\nQuit",command=self.doQuit,bg='red',fg='white')
		self.editModelsbtn.pack(side=TOP,fill=X)

		self.nb= Pmw.NoteBook(self.m_rightFrame)
		#self.tabNames = ['Input Files', 'Output Files', 'Restart Files']
		self.tabNames = ['Input Files', 'Output Files']
		self.tabIncludes = self.nb.add('Input Files') 		     # From data directory
		self.tabOutput   = self.nb.add('Output Files') 		     # From output directory
		self.tabInformation  = self.nb.add('Information') 		     # From output directory
		self.tabExtracted = self.nb.add('Extracted')

		self.informationText = Pmw.ScrolledText(self.tabInformation, borderframe=1,labelpos=N,label_text ='Information',
				 	text_wrap='none')
					#,usehullsize=1,hull_width=10,hull_height=100)
		self.informationText.pack(side=TOP,fill=BOTH,expand=1)

		self.tableOfExtracted = ScrolledTableList(self.tabExtracted,width=40,showseparators='yes',
			#stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, 
			labelcommand=self.m_sortIncludeTablesByColumn,
			columns=(12,"TYPE",70,"Location",40,"Info"), 
			selectbackground='lightblue',
			exportselection='no',
			selecttype='row')
		self.tableOfExtracted.pack(side=RIGHT,expand=1,fill=BOTH)
		self.tableOfExtracted.addHorizontalBar()

		self.tableOfExtracted.bind('<Double-Button-1>',self.evh_btn1_ExtractedFile)
		self.tableOfExtracted.bind('<Button-2>',self.evh_btn2_ExtractedFile)
		self.tableOfExtracted.bind('<Double-Button-3>',self.evh_btn3_ExtractedFile)

		#for tbn in self.tabNames:
		#	tab = self.nb.tab(tbn)
		#	tab['background'] = 'gray16'
		#	tab['foreground'] = 'white'

		self.nb.pack(side=TOP,fill=BOTH,expand=1)

		self.tableOfIncludes = ScrolledTableList(self.tabIncludes,width=40,showseparators='yes',
			#stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, 
			labelcommand=self.m_sortIncludeTablesByColumn,
			columns=(12,"TYPE",70,"Location",40,"Info"), 
			selectbackground='lightblue',
			exportselection='no',
			selecttype='row')
		self.tableOfIncludes.pack(side=RIGHT,expand=1,fill=BOTH)
		self.tableOfIncludes.addHorizontalBar()
		
		self.tableOfIncludes.bind('<Double-Button-1>',self.evh_btn1_IncludeFile)
		self.tableOfIncludes.bind('<Button-2>',self.evh_btn2_IncludeFile)
		self.tableOfIncludes.bind('<Double-Button-3>',self.evh_btn3_IncludeFile)
		#self.tableOfIncludes.bind('<Button-1>',self.evh_btn1_IncludeFile)

		self.tableOfOutputs = ScrolledTableList(self.tabOutput,width=40,showseparators='yes',
			#stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, 
			columns=(12,"TYPE",70,"Location",40,"Info"), 
			selectbackground='lightblue',
			exportselection='no',
			labelcommand=self.m_sortOutputTablesByColumn,
			selecttype='row')
		self.tableOfOutputs.pack(side=RIGHT,expand=1,fill=BOTH)
		self.tableOfOutputs.addHorizontalBar()

		self.tableOfOutputs.bind('<Double-Button-1>',self.evh_btn1_OutputFile)
		self.tableOfOutputs.bind('<Button-2>',self.evh_btn2_OutputFile)
		self.tableOfOutputs.bind('<Double-Button-3>',self.evh_btn3_OutputFile)
		#self.tableOfOutputs.bind('<space>',self.evh_btn1_OutputFile)

		#self.tableOfRestarts = ScrolledTableList(self.tabRestart,width=40,showseparators='yes',
			##stripebackground = 'gray64', stripeforeground = 'gray12',
			#background=tableListBackground, 
			#columns=(12,"TYPE",50,"Location",40,"Info"), 
			#selecttype='cell')
		#self.tableOfRestarts.pack(side=RIGHT,expand=1,fill=BOTH)
		#self.tableOfRestarts.addHorizontalBar()
		#
		#self.tableOfRestarts.bind('<Double-Button-1>',self.evh_btn1_RestartFile)
		#self.tableOfRestarts.bind('<Button-2>',self.evh_btn2_RestartFile)
		#self.tableOfRestarts.bind('<Double-Button-3>',self.evh_btn3_RestartFile)

	def readNotesXMLfile(self):
		try:
			dom = minidom.parse(self.notesXMLfilename)
		except:
			return
		nodes = dom.getElementsByTagName('NOTE')  # All the notes are read here.
		self.fileNotes = {}
		for nd in nodes:
			key = None
			val = None
			for chld in nd.childNodes:
				if chld.nodeName == 'NAME': key = chld.childNodes[0].nodeValue
				if chld.nodeName == 'COMMENT': 
					if chld.hasChildNodes(): 
						val = chld.childNodes[0].nodeValue
					else:
						val = '' 
				if key <> None and val <> None:
					self.fileNotes[key] = val
					break

	def askSimstoreFilename(self,runAlso=0):
		ofile = asksaveasfilename(filetypes=[('Simstore file',"*.simstore"),("All Files",'*')],\
				initialfile=os.getenv('HOME') + '/simstore.simstore',
				title='Select a file to export to')
		if ofile: 
			self.writeSimstoreFile(ofile)
			if runAlso == 1: 
				if os.fork() == 0: 
					os.execl(self.userSimstoreCommand,"SimStoreE-linux","-x",ofile)
			
		
	def getListOfIncludes(self,fname):
		print "Getting ..", fname
		if istextfile(fname) == 0:   return []
		outlist = []
		try:
			xlines = open(fname,'r').readlines()
		except:
			xlines = []
		flag = 0
		for ln in xlines:
			ln = ln.strip()
			if flag == 1: 
				items = ln.split()
				flag = 0
				if len(items) > 1:
					rname = items[0]
					rname = rname.replace("""'""",'')
					rname = rname.replace('"','')
					outlist.append(rname)
				continue
			f = ln.find('INCLUDE_FILE')
			if f == 0:
				items = ln.split()
				if len(items) > 1:
					rname = items[1]
					rname = rname.replace("""'""",'')
					rname = rname.replace('"','')
					outlist.append(rname)
				continue
			f = ln.find('INCLUDE')
			if f == 0:
				print "found ...", ln
				items = ln.split()
				if len(items) < 2: 
					flag = 1
					continue
				rname = items[1]
				rname = rname.replace("""'""",'')
				rname = rname.replace('"','')
				outlist.append(rname)
				
		return outlist

	def writeSimstoreFile(self,fname):

		f,e = os.path.splitext(fname)
		if len(e) < 1: fname.append('.simstore')
		print " I am writing ...", fname	
		fd = open(fname,'w')
		fd.write('<?xml version="1.0" encoding="iso-8859-1" ?>\n')
		fd.write('<?xml-stylesheet type="text/xsl" href="/peasd/ssd/husainkb/template/simstore.xsl"?>\n')
		fd.write('<SIMSTORE>\n')

		# Collect the information in the first page.
		lines  =  self.tableOfIncludes.get(0,"end")
		fd.write('<INCLUSIONS>\n')
		for ln in lines: 
			items = map(str,ln)
			filename = items[1].strip()
			fd.write('<FILE type="%s">\n' % items[0].strip())
			fd.write('<NAME value="%s" />\n' % items[1].strip())
			fd.write('<DATE value="%s" />\n' % items[2].strip())
			fd.write('</FILE>\n')
			ilist = self.getListOfIncludes(filename)
			if len(ilist) > 0:
				for ifile in ilist: 
					fd.write('<FILE type="INCLUDE_FILE">\n')
					fd.write('<NAME value="%s" />\n' % ifile)
					slines = os.stat(ifile)
					fd.write('<DATE value="%s" />\n' % showTime(slines[-1]))
					fd.write('</FILE>\n')
		fd.write('</INCLUSIONS>\n')

		lines  =  self.tableOfOutputs.get(0,"end")
		fd.write('<OUTPUTS>\n')
		for ln in lines: 
			items = map(str,ln)
			fd.write('<FILE type="%s">\n' % items[0].strip())
			fd.write('<NAME value="%s" />\n' % items[1].strip())
			fd.write('<DATE value="%s" />\n' % items[2].strip())
			fd.write('</FILE>\n')
		fd.write('</OUTPUTS>\n')

		#
		# Actually, I have to check the outpu
		#
		fd.write('<INFORMATION>\n')
		xtxt = self.informationText.get().split('\n')
		for xln in xtxt: 
			items = xln.split(':')
			if len(items) >= 2: 
				keyword = items[0].strip()
				if keyword[0].isdigit(): keyword = keyword[3:20]
				keyword = keyword.replace(' ','_')
				keyword = keyword.replace('/','')
				keyword = keyword.replace('(','')
				keyword = keyword.replace(')','')
				keyword = keyword.replace('<','')
				keyword = keyword.replace('>','')
				keyword = keyword.replace(',','_')
				fd.write('<%s>' % keyword)
				value = "".join(items[1:])
				value = value.replace(' ','_')
				value = value.replace('/','')
				value = value.replace('(','')
				value = value.replace(')','')
				value = value.replace('<','')
				value = value.replace('>','')
				value = value.replace('&','and')
				fd.write('%s' % value)
				fd.write('</%s>\n' % keyword)

		fd.write('<RAWPAGE>\n')
		xtxt = self.informationText.get()
		#xtxt = xtxt.replace('<','')
		#xtxt = xtxt.replace('>','')
		#xtxt = xtxt.replace(',','_')
		#xtxt = xtxt.replace('&','and')

		strdata = xml.sax.saxutils.escape(xtxt,{'"':'&quot',"'":'&apos;'})
		fd.write(strdata)

		fd.write('</RAWPAGE>\n')
		fd.write('</INFORMATION>\n')

		fd.write('</SIMSTORE>\n')
		fd.close()

	def writeNotesXMLfile(self):
		fd = open(self.notesXMLfilename,'w')
		fd.write('<?xml version="1.0" encoding="iso-8859-1" ?>\n')
		fd.write('<?xml-stylesheet type="text/xsl" href="/peasd/ssd/husainkb/template/notes.xsl"?>\n')
		fd.write('<NOTES>\n')
		xout = []
		
		keys  = self.fileNotes.keys()
		for key in 	keys:
			xout.append('<NOTE>\n<NAME>%s</NAME>\n' % key)	
			strdata = xml.sax.saxutils.escape(self.fileNotes[key],{'"':'&quot',"'":'&apos;'})
			xout.append('<COMMENT>%s</COMMENT>\n' % strdata)
			xout.append('</NOTE>\n')
		fd.write("".join(xout))
		fd.write('</NOTES>\n')
		fd.close()
		try:
			os.chmod(self.notesXMLfilename,0666)
		except:
			print "Unable to set permissions on ", self.notesXMLfilename

	def flushDBM(self):
		r = self.writeProjectsFile()
		if r > -1: self.writeNotesXMLfile()

	def readProjectsFile(self,eraseList=1):
		self.projectXMLlabel['text']= os.path.basename(self.projectsXMLfilename)
		dirname =  os.path.dirname(self.projectsXMLfilename)
		pdir =  split(dirname,'/')
		f = dirname.find('powersdata')
		lbl = self.sl_projects.component('label')
		lbl['fg'] = 'white'
		lbl['bg'] = 'darkblue'
		if len(pdir) > 3 and f > 0:
			#self.projectXMLlblPath['text']= pdir[3]
			lbl['text'] = pdir[3]
		else:
			#self.projectXMLlblPath['text']= os.path.dirname(self.projectsXMLfilename)
			lbl['text'] = os.path.dirname(self.projectsXMLfilename)
		dom = minidom.parse(self.projectsXMLfilename)
		nodes = dom.getElementsByTagName('PROJECT')  # All the notes are read here.
		if eraseList == 1: self.listOfProjects = {}
		for nd in nodes:
			key = None
			val = None
			for chld in nd.childNodes:
				if chld.nodeName == 'NAME': 
					key = chld.childNodes[0].nodeValue
					if not self.listOfProjects.has_key(key):
						self.listOfProjects[key] = []
				if chld.nodeName == 'FILE': 
					if chld.hasChildNodes(): 
						val = chld.childNodes[0].nodeValue
						plist = self.listOfProjects[key]
						if not val in plist: self.listOfProjects[key].append(val)

		skeys = self.listOfProjects.keys()
		if len(skeys) < 1: 
			showwarning("Oops!"," The XML file you have read has no PROJECT info!!" + self.projectsXMLfilename)
			return -1
		return 0

	def writeProjectsFile(self):
		writeFail = 0
		try:
			fd = open(self.projectsXMLfilename,'w')
		except:
			writeFail = 1

		while writeFail == 1:
			showwarning("Oops!"," I cannot save to the file " + self.projectsXMLfilename + " ... try again ... ")
			safename = os.getenv('HOME') + os.sep + 'powersdata' + os.sep + 'projects.xml'  
			ofile = asksaveasfilename(filetypes=[('XML file',"*.xml"),("All Files",'*')],\
				initialfile=safename,title='Select a different name')
			if ofile:
				try:
					fd = open(ofile,'w')
					self.projectsXMLfilename = ofile
					self.projectsXMLdirectory = os.path.dirname(ofile)
					os.chdir(self.projectsXMLdirectory)
					self.notesXMLfilename    = self.projectsXMLdirectory + os.sep + 'notes.xml'
					writeFail = 0
				except:
					writeFail = 1
			else:
				showwarning("Oops!"," I did not save to the file " + self.projectsXMLfilename )
				return -1
				
		fd.write('<?xml version="1.0" encoding="iso-8859-1" ?>\n')
		fd.write('<?xml-stylesheet type="text/xsl" href="/peasd/ssd/husainkb/template/projects.xsl"?>\n')
		fd.write('<PROJECTS>\n')
		xout = []
		keys  = self.listOfProjects.keys()
		for key in 	keys:
			xout.append('<PROJECT>\n<NAME>%s</NAME>\n' % key)	
			for fn in self.listOfProjects[key]: xout.append('<FILE>%s</FILE>\n' % fn)
			xout.append('</PROJECT>\n')
		fd.write("".join(xout))
		fd.write('</PROJECTS>\n')
		fd.close()
		try:
			os.chmod(self.projectsXMLfilename,0666)
		except:
			print "Unable to set permissions on ", self.projectsXMLfilename
			return -1	
		return 0

	def doQuit(self):
		self.writeGUIstate(os.getcwd())
		r = self.writeProjectsFile()
		if r > -1: self.writeNotesXMLfile()
		sendMessage('PowersGUI','QUIT','ModelManager')
		sys.exit()

	def collectPBFinfo(self,filename):
		up = uPBFfile()
		up.openFile(filename)
		if up.fd == None: return [] 
		#print "Opening ...", filename
		ilines = up.getHeaderStrings(verbose=1)
		hdrs = 'NAME  Count  NX NY NZ Size  Min Max Ave'.split()
		fmtstr = "%20s %10s %5s %5s %5s %5s %10s %10s %10s\n"
		xlines = []
		xlines.append(fmtstr % tuple(hdrs))
		for x in ilines: xlines.append(fmtstr % tuple(x.split()))
		up.closeFile()
		return xlines

	def startXtermCB(self):
		if os.fork() == 0: 
			os.execl(self.userXtermCommand,"xterm")

	def eventRestartTableSelect(self,ev):
		if names == None: return
		name  = names[1].strip()
		if istextfile(name): 
			if os.fork() == 0: 
				os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand,name)
		else:
			showwarning("Oops!"," I cannot edit what appears to be a binary file: " + name)

	def evh_btn2_ModelFile(self,ev):
		self.justShowedModel = 1
		self.pop_model.tk_popup(ev.x_root,ev.y_root,"0")

	def evh_btn2_IncludeFile(self,ev):
		self.justShowedModel = 2
		self.pop1.tk_popup(ev.x_root,ev.y_root,"0")

	def evh_btn2_OutputFile(self,ev):
		self.justShowedModel = 3
		self.pop_output.tk_popup(ev.x_root,ev.y_root,"0")

	def evh_btn2_ExtractedFile(self,ev):
		self.justShowedModel = 4
		self.pop_extracted.tk_popup(ev.x_root,ev.y_root,"0")

	def evh_btn2_RestartFile(self,ev):
		self.justShowedModel = 5
		self.pop1.tk_popup(ev.x_root,ev.y_root,"0")

	def popupmenuCmd(self,parm):
		columnToUse = 1
		if self.justShowedModel == 1: 
			names =  self.tableOfModels.get("active")	
			columnToUse = modelFileColumnIndex
		elif self.justShowedModel == 2: 
			names =  self.tableOfIncludes.get("active")	
		elif self.justShowedModel == 3: 
			names =  self.tableOfOutputs.get("active")	
		elif self.justShowedModel == 4: 
			names =  self.tableOfExtracted.get("active")	
		#elif self.justShowedModel == 5: 
			#names =  self.tableOfRestarts.get("active")	
		else: 
			self.justShowedModel = 0
			return 
		name = str(names[columnToUse])
		name = name.strip()
		if parm == 'savesimstore': 
			self.askSimstoreFilename(0)
			return
		if parm == 'runsimstore': 
			self.askSimstoreFilename(1)
			return


		if parm == 'tail': 
			if istextfile(name): 
				if os.fork()==0:
					os.execl("/usr/bin/xterm","xterm", "-title", name, "-e", '/usr/bin/tail', '-f', name)
		if parm == 'vim': 
			if istextfile(name): 
				os.chdir(os.path.dirname(name))
				if os.fork() <> 0: 
					os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand,name)

		if parm == 'rs3d': 
			fname,ext = os.path.splitext(name.lower())
			if ext in ['.powers','.bin','.unrst','.init','.attri']: 
				if os.fork() == 0: 
					os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runRS3D.ksh",name)
			else:
				showwarning("Oops!"," Only .powers, .bin, .attri, .unrst or .init extensions are supported for binary file. " + name)

		if parm == 'rsXY': 
			fname,ext = os.path.splitext(name.lower())
			if ext in ['.powers','.bin','.unrst','.init','.attri']: 
				if os.fork() == 0: 
					os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runXY.ksh",name)
			else:
				showwarning("Oops!"," Only .powers, .bin, .attri, .unrst or .init extensions are supported for binary file. " + name)

		if parm == 'extract': 
			fname,ext = os.path.splitext(name.lower())
			if ext in ['.smspec','.SMSPEC']: 
				if os.fork() == 0:  # Child 
					os.execl(self.userXtermCommand,"xterm", "-e", "bash",scriptBaseDir + "parallelExtract.ksh",name,"/red/simdata/EXT400/%s" % os.getenv('USER'))
			else:
				showwarning("Oops!"," Only selected extensions are supported for extraction." + name)

		if parm == 'rssat2': 
			self.doBtn3handling(names)
			return 

		if parm == 'rssat1': 
			fname,ext = os.path.splitext(name)   # Lite 
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runPVT.ksh",name)
			return

		if parm == 'simreport': 
			fname,ext = os.path.splitext(name)
			if ext == '.tu_xml':
				tcmd = scripBaseDir + "runSimRpt.ksh"
				if os.fork() == 0: os.execl(tcmd,tcmd,name,name)
			if ext == '.CNTLF':
				tcmd = "/peasapps/ssd/test_lnx/scripts/Linux/simreport400"	
				if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])
				#if os.fork() == 0: os.execl(tcmd,tcmd)
				
		if parm == 'mozilla': 
			fname,ext = os.path.splitext(name)
			if ext == '.tu_xml':
				fname = 'file:///' + name
				if os.fork() == 0: os.execl('/usr/bin/mozilla',"mozilla", fname)

		if parm == 'rsecl': 
			fname,ext = os.path.splitext(name.lower())
			if ext in ['.unsmry','.smry','.init','.unrst','.grid']:
				if os.fork() == 0: 
					tcmd = "/peasapps/ssd/test_lnx/scripts/Linux/rsECL"
					os.execl(tcmd,"rsecl", name)
			else:
				showwarning("Oops!"," Only .unsmry or .smry, extensions are supported for binary file. " + name)
		if parm == 'diff': self.diffModelFiles()

		if parm == 'saveas': 
			print "I am trying to copy this file ", name 
			os.chdir(os.path.dirname(name))
			ofile = asksaveasfilename(filetypes=[("All Files","*")],initialfile=os.path.basename(name))
			if ofile:
				# Copy the file to the new name ...	
				fn,ext = os.path.splitext(ofile)
				if self.justShowedModel == 1 and ext <> ".model": ofile.append(".model")
				# This is where I have to modify the BINARY_DATA_DIRECTORY
				verifyCopyModelFile(name,ofile)
				# I add this line to the current project?
				self.lastWorkingDir = os.path.dirname(ofile)   # 
				os.chdir(self.lastWorkingDir)
				if self.justShowedModel == 1: 
					dirlist = createRowEntry(ofile)
					self.addOneFileToProject(dirlist)
					self.lastsort = '-increasing'   # The opposite
					self.m_sortModelsByColumn(self.tableOfModels,2)
				# -- showwarning("Oops!"," I cannot copy this file: " + name + " to " + ofile)
				return

		if parm == 'konqueror':
			pathname = os.path.dirname(name)
			if os.fork() == 0: 
				try:
					os.chdir(pathname)
					os.execl("/usr/bin/konqueror","konqueror", pathname)
				except:
					os.execl("/usr/bin/konqueror","konqueror")
		if parm == 'include':
			if istextfile(name) < 1: 
				showwarning("Oops!"," I cannot read a non-text file: " + name)
				return 
			try:
				xlines = open(name,'r').readlines() 
			except:
				showwarning("Oops!"," I cannot read the file: " + name)
				return
			outlist = []
			flag = 0
			for ln in xlines:
				ln = ln.strip()
				if flag == 1: 
					flag = 0
					items = ln.split()
					if len(items) > 0:
						fname = items[0]
						fname = fname.replace("""'""",'')
						fname = fname.replace('"','')
						outlist.append(fname)
						continue	
				f = ln.find('INCLUDE_FILE')
				if f == 0:
					items = ln.split()
					if len(items) > 1:
						fname = items[1]
						fname = fname.replace("""'""",'')
						fname = fname.replace('"','')
						outlist.append(fname)
					continue
				f = ln.find('INCLUDE')
				if f == 0:
					items = ln.split()
					if len(items) < 2:
						flag = 1
						continue
					if len(items) > 1:
						fname = items[1]
						fname = fname.replace("""'""",'')
						fname = fname.replace('"','')
						outlist.append(fname)
						
			if len(outlist) > 0: 
				self.selectIncludeDlg = Pmw.SelectionDialog(self.parent,
					buttons=('Open','Cancel'), defaultbutton='Open',
					scrolledlist_usehullsize = 1,
					scrolledlist_hull_width =  500,
					scrolledlist_hull_height =  400,
					scrolledlist_items=outlist,command=self.editSelectedInclude)
				self.selectIncludeDlg.activate()

		if parm == 'delete': 
			response = askyesno("Warning!","Shall I remove the following file %s ?" % name)
			if response == True: 
				try:
					os.remove(name)
				except: 
					showwarning("Oops!"," I cannot remove the file: " + name)
			#showwarning("OK!"," I have removed the file: " + name + "You now have to refresh your projects display")
			sel = self.sl_projects.getcurselection()
			if len(sel) > 0: self.showProjectEntries(str(sel[0]))


	def editSelectedInclude(self,parm):
		"""
		"""
		fname = None
		if parm == 'Open':
			sel = self.selectIncludeDlg.getcurselection()
			if len(sel) > 0: fname = sel[0]
		self.selectIncludeDlg.deactivate()
		if fname <> None: 
			if istextfile(fname) < 1: 
				showwarning("Oops!"," I cannot read a non-text file: " + fname)
			else:
				os.chdir(os.path.dirname(fname))
				if os.fork() <> 0: 
					os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand,fname)
			

	
	def evh_btn3_IncludeFile(self,ev):
		self.justShowedModel = 2
		names =  self.tableOfIncludes.get("active")	
		if names == None: return
		self.doBtn3handling(names)

	def evh_btn3_OutputFile(self,ev):
		self.justShowedModel = 3
		names =  self.tableOfOutputs.get("active")	
		if names == None: return
		self.doBtn3handling(names)
		
	def evh_btn3_ExtractedFile(self,ev):
		self.justShowedModel = 4
		names =  self.tableOfExtracted.get("active")	
		if names == None: return
		self.doBtn3handling(names)

	def evh_btn3_RestartFile(self,ev):
		pass
		#self.justShowedModel = 5
		#names =  self.tableOfRestarts.get("active")	
		#if names == None: return
		#self.doBtn3handling(names)

	def doBtn3handling(self,names):
		name = str(names[1])
		name = name.strip()
		if names[0] in self.editableFiles and istextfile(name) == 5:  # For XML files 
			if os.fork() == 0: 
				os.execl('/usr/bin/mozilla',"mozilla", name)
			return		
		if names[0] in self.editableFiles and istextfile(name) == 2:
			#self.rWindow = Toplevel()	
			#self.flow = frameFlowParms(self.rWindow)
			#self.flow.readFlowFile(useNew=1,incoming=name)
			#self.rWindow.mainloop()
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runFlow.ksh", name)
		if names[0] in self.editableFiles and istextfile(name) == 3:
			#self.rWindow = Toplevel()	
			#self.usePVT = pPVTTable()
			#self.usePVTfm = frameSATorPVTtableParms(self.rWindow,self.usePVT)
			#self.usePVTfm.pack(side=TOP,fill=BOTH,expand=1)
			#self.usePVTfm.m_readTable(name)
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runPVT.ksh", name)

		if names[0] in self.editableFiles and istextfile(name) == 4:
			#self.rWindow = Toplevel()	
			#self.useSAT = pSATTable()
			#self.useSATfm = frameSATorPVTtableParms(self.rWindow,self.useSAT)
			#self.useSATfm.pack(side=TOP,fill=BOTH,expand=1)
			#self.useSATfm.m_readTable(name)
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runPVT.ksh", name)


	def evh_btn1_IncludeFile(self,ev):
		self.justShowedModel = 2
		names =  self.tableOfIncludes.get("active")	
		if names == None: return
		self.editThisFile(names)

	def evh_btn1_OutputFile(self,ev):
		self.justShowedModel = 3
		names =  self.tableOfOutputs.get("active")	
		if names == None: return
		self.editThisFile(names)

	def evh_btn1_ExtractedFile(self,ev):
		self.justShowedModel = 4
		names =  self.tableOfExtracted.get("active")	
		if names == None: return
		self.editThisFile(names)

	def evh_btn1_RestartFile(self,ev):
		pass
		#self.justShowedModel = 5
		#names =  self.tableOfRestarts.get("active")	
		#if names == None: return
		#self.editThisFile(names)

	
	def editThisFile(self,names):
		"""
		Called from within the include, restart and output tabbed pages.
		"""
		typefile = names[0].strip()
		iname = str(names[modelFileColumnIndex])
		fullmodelfilename = str(iname.strip())

		if not self.fileNotes.has_key(str(fullmodelfilename)):
			self.fileNotes[str(fullmodelfilename)] = ''
			self.m_notesWidget.settext("")
		else: 	
			self.m_notesWidget.settext(self.fileNotes[str(fullmodelfilename)])

		if typefile in ['BINARY_FILE']:
			xlines = self.collectPBFinfo(fullmodelfilename)
			self.pDialog = Pmw.TextDialog(self.parent, scrolledtext_labelpos='n',title=fullmodelfilename,defaultbutton=0,label_text=fullmodelfilename) 
			self.pDialog.insert(END,"".join(xlines))
			return
		if names[0] in self.editableFiles and istextfile(fullmodelfilename) > 0:
			if os.fork() == 0: 
				os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand, fullmodelfilename)

	def setLastWorkingDir(self,d):
		self.scanDir(d)

	def toguiCB(self):
		names =  self.tableOfModels.get("active")	 # Get the model name location.
		name = str(names[modelFileColumnIndex])
		if self.guiEditor == None : return 
		self.guiEditor.f_loadInFile(name)

	def stopModelCB(self):
		"""
		"""
		names =  self.tableOfModels.get("active")	 # Get the model name location.
		name = str(names[modelFileColumnIndex])
		fname = name.strip() 
		fname = fname.replace(".model",".int")
		try:
			fd = open(fname,'w')
			fd.write('STOP\n')
			fd.close()
		except:
			pass
		showwarning("STOP!"," I have attempted to write a STOP in this file:\n " + fname + "\n You must delete it yourself")


	def diffModelFiles(self):
		rows =  self.tableOfModels.curselection()
		if len(rows) <> 2: 
			showwarning("STOP!","You can select a difference only between two model files"); 
			return
		row0 =  self.tableOfModels.get(rows[0]); name0 = str(row0[modelFileColumnIndex])
		row1 =  self.tableOfModels.get(rows[1]); name1 = str(row1[modelFileColumnIndex])
		print 'I am differencing..',name0
		print 'and ',name1
		if istextfile(name0) and istextfile(name1): 
			cmdstring = "/usr/bin/diff %s %s" % (name0,name1) 
			rsp = os.popen(cmdstring,'r')
			xlines = "".join(rsp.readlines())
			self.diffWindow = Pmw.TextDialog(self.parent, scrolledtext_labelpos='n',
					title="Difference",
					defaultbutton=0,
					buttons=('Close','Save'),command=self.diffCommandHandler, 
					label_text="%s vs. %s" % (name0,name1)) 
			self.diffWindow.insert(END,"".join(xlines))

	def diffCommandHandler(self,parm):
		if parm == 'Close':
			self.diffWindow.destroy()
			self.diffWindow = None
		if parm == 'Save':
			ofile = asksaveasfilename(filetypes=[("text file","*.txt"),("All Files","*"), ("All Files","*")])
			if ofile:
				print "I am writing to this file .......", ofile
				xstr = self.diffWindow.get()
				fd = open(ofile,'w')
				fd.write(xstr)
				fd.close()

	def batchsubmitModelCB(self):
		rows =  self.tableOfModels.curselection()
		if len(rows) < 1: return
		self.monWindow = Toplevel()
		self.monWindow.title('Submit a job')
		self.monSubmit = makeSubmitForm(self.monWindow,\
			modelName='',nodes=self.numNodes,\
			usenode=self.use_node,doExtract=self.doExtract,	\
			tellme=self.jobSubmissionHandler, obj=self, cancelbtn=1)
		#self.monSubmit.setDefaultModelFile(name)
		modelnames = []
		for i in rows: 
			row =  self.tableOfModels.get(i)
			name = str(row[modelFileColumnIndex])
			modelnames.append(name)
		self.monSubmit.runBatchCommand(modelnames)
		self.monWindow.destroy()
		self.monWindow = None

	def submitModelCB(self):
		names =  self.tableOfModels.get("active")	 # Get the model name location.
		name = str(names[modelFileColumnIndex])
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runSubmit.ksh",name)
		

	def submitModelCBxx(self):
		names =  self.tableOfModels.get("active")	 # Get the model name location.
		name = str(names[modelFileColumnIndex])
		if self.monWindow <> None: self.monWindow.destroy()
		self.monWindow = Toplevel()
		self.monWindow.title('Submit a job')
		self.monSubmit = makeSubmitForm(self.monWindow,\
			modelName=name,nodes=self.numNodes,\
			usenode=self.use_node,doExtract=self.doExtract,	\
			tellme=self.jobSubmissionHandler, obj=self, cancelbtn=1)
		self.monSubmit.setDefaultModelFile(name)
		self.monWindow.mainloop()

	def jobSubmissionHandler(self,obj,opcode,incoming):
		"""
		This is a kludge to set the file names for a batch job from the 
		The obj is myself, whereas the self in the submitJob object
		"""

		if opcode == 'PARMS':
			self.doExtract = int(incoming['EXTRACT'])
			self.use_node = incoming['USENODE'] 
			self.numNodes = int(incoming['NUMNODES'])
			self.writeGUIstate(self.lastWorkingDir)
			return
		# Default
		modelName,outputName,errName = incoming 
		name = outputName.strip()
		if len(name) < 1: 
			self.monWindow.destroy()
			self.monWindow = None
			return

		if self.monitorObject <> None: 
			self.monitorObject.modelFilename = modelName
			self.monitorObject.monitoredFilename = outputName
			self.monitorObject.commandFilename = errName
			self.monitorObject.f_showFileContents()
		self.monWindow.destroy()
		self.monWindow = None
		#
		# The output is from the script...
		#
		name = outputName.strip()
		if len(name) > 1:
			if os.fork() <> 0:
				print "Starting tail on ", outputName, "[", name , "]" 
				os.execl("/usr/bin/xterm","xterm", "-title", name, "-e", '/usr/bin/tail', '-f', name)

	def testKill(self):
		self.monWindow.destroy()
		self.monWindow = None

	def addProjectCB(self):
		pname = askstring("Enter Project name", 'Enter the name of the project')
		if pname == None: return
		pname = pname.strip()
		if len(pname) < 1: return 
		self.listOfProjects[pname] = []
		skeys = self.listOfProjects.keys()
		skeys.sort()
		self.sl_projects.setlist(skeys)

	def delProjectCB(self):
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project to delete please")
			return 
		name = self.sl_projects.getcurselection()[0]
		response = askyesno("Warning!","Shall I remove the following project %s ?" % name)
		if response <> True: return
		del self.listOfProjects[name]
		skeys = self.listOfProjects.keys()
		skeys.sort()
		self.sl_projects.setlist(skeys)

	def addOneFileToProject(self,dirlist):
		"""
		dirlist must of the form: name, fullpath, info
		"""
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project to add files to, please")
			return 
		pname = self.sl_projects.getcurselection()[0]
		project = self.listOfProjects[pname]	
		fname = str(dirlist[modelFileColumnIndex])
		if not fname in project: project.append(fname)
		self.showProjectEntries(pname)

	def addFilesToProjectCB(self):
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project to add files to, please")
			return 
		pname = self.sl_projects.getcurselection()[0]
		#print "add files to ", name
		project = self.listOfProjects[pname]	
		sel = self.tableOfModels.curselection()
		for m in sel: 
			dirlist = self.tableOfModels.get((m,))
			fname = str(dirlist[modelFileColumnIndex])
			if not fname in project: project.append(fname)
		#print "Project ", name , " has the following files" 
		#for m in project: print m
		self.showProjectEntries(pname)

	def addFilesByNameToProject(self,filenames):
		#print "I am adding these files to the project", filenames
		pname = self.sl_projects.getcurselection()[0]
		project = self.listOfProjects[pname]	
		for fname in filenames:
			if not fname in project: project.append(fname)
		self.showProjectEntries(pname)



	def delFilesToProjectCB(self):
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project to delete files from, please")
			return 
		pname = self.sl_projects.getcurselection()[0]
		#print "del files from ", name
		response = askyesno("Warning!","Shall I remove the selected files from your project?")
		if response <> True: return
		sel = self.tableOfModels.curselection()
		project = self.listOfProjects[pname]	
		for m in sel: 
			dirlist = self.tableOfModels.get((m,))
			fname = str(dirlist[modelFileColumnIndex])
			if fname in project: 
				findex = project.index(fname)
				del project[findex]
		self.showProjectEntries(pname)

	def selectProjectCB(self):
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project to delete files from, please")
			return 
		pname = self.sl_projects.getcurselection()[0]
		self.lastSelectedProject = pname
		self.showProjectEntries(pname)
		self.lastsort = '-increasing' 
		self.m_sortModelsByColumn(self.tableOfModels,2)

	def showProjectEntries(self,pname):
		self.lastProjectName = pname
		project = self.listOfProjects[pname]	
		self.retlist = []
		for fullname in project: 
			try:
				xlines = os.stat(fullname)
				basename = os.path.basename(fullname)
				modelname,ext = os.path.splitext(basename)
				sz = showTime(xlines[-1]) + "(%dK)" % int(xlines[6] / 1024)
				self.retlist.append((modelname,fullname,sz))
			except:
				pass 

		self.tableOfModels.clear()
		for i in self.retlist:
			self.tableOfModels.insert("end",i)
		self.writeGUIstate(self.lastWorkingDir)

	def editModelCB(self):
		names =  self.tableOfModels.get("active")	
		if os.fork() <> 0:
			name = str(names[modelFileColumnIndex])
			os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand, name.strip())

	def checkModelCB(self):
		names =  self.tableOfModels.get("active")	
		if os.fork() <> 0:
			name = str(names[modelFileColumnIndex])
			os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runSyntax.ksh",name)
			#os.system(externalChecker + name.strip())

	def saveNotesOnFile(self):
		sel = []
		if self.justShowedModel == 1: 
			sel =  self.tableOfModels.get("active")	
			fullmodelfilename = str(sel[modelFileColumnIndex])
		elif self.justShowedModel == 2: 
			sel =  self.tableOfIncludes.get("active")	
			fullmodelfilename = str(sel[otherFileColumnIndex])
		elif self.justShowedModel == 3: 
			sel =  self.tableOfOutputs.get("active")	
			fullmodelfilename = str(sel[otherFileColumnIndex])
		#elif self.justShowedModel == 4: 
			#sel =  self.tableOfRestarts.get("active")	
			#fullmodelfilename = str(sel[otherFileColumnIndex])
		if len(sel[modelFileColumnIndex]) < 1: return
		self.fileNotes[fullmodelfilename] = self.m_notesWidget.get()
		#print "sel = ", sel,fullmodelfilename, self.fileNotes[fullmodelfilename]
		self.fileNotes.keys()

	def eventTableModel(self,ev):
		self.justShowedModel = 1
		sel =  self.tableOfModels.get("active")	
		fullmodelfilename = sel[modelFileColumnIndex]

		#For future use
		#crx = self.tableOfModels.nearestcell(ev.x,ev.y)
		#icrx = int(crx.split(',')[1])

		if istextfile(fullmodelfilename): 
			if os.fork() <> 0: 
				os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand,fullmodelfilename)

	
	def eventTableSelect(self,ev):
		self.justShowedModel = 1
		sel =  self.tableOfModels.get("active")	
		fullmodelfilename = sel[modelFileColumnIndex]
		#print "Get information for ", fullmodelfilename
		#print "eventTableSelect fullmodelfilename = ", fullmodelfilename
		workpath,projectpath = deriveWorkpaths(fullmodelfilename)
		sector_datapath = None
		f = projectpath.find('/sector_data')
		if f>=0: sector_datapath = projectpath.replace('/sector_data','')

		try:
			xlines = open(fullmodelfilename,'r').readlines()
		except:	
			showwarning("Oops!"," I cannot open the file you have selected " + fullmodelfilename)
			return

		if not self.fileNotes.has_key(str(fullmodelfilename)):
			self.fileNotes[str(fullmodelfilename)] = ''
			self.m_notesWidget.settext("")
		else: 	
			self.m_notesWidget.settext(self.fileNotes[str(fullmodelfilename)])

		self.listOfIncludes = []
		self.listOfOutputs  = []
		self.listOfRestart  = []
		crx = self.tableOfModels.nearestcell(ev.x,ev.y)

		bindirpath = None
		modeldirname = os.path.dirname(fullmodelfilename)
		modeldirroot = modeldirname.replace('/data/','')
		justfilename = os.path.basename(fullmodelfilename)
		modelbase,ext = os.path.splitext(justfilename)
		self.listOfIncludes.append("MODEL_FILE: %s" % (fullmodelfilename))
		intmodelfilename = fullmodelfilename.replace('.model','.int')
		self.listOfIncludes.append("INT_FILE: %s" % (intmodelfilename))
		self.snapshotLines = [] 
		#self.snapshotRequired = {}
		#for snp in self.snapshotKeywords: self.snapshotRequired[snp] = 0
		self.snapshotRequired = {}
		for ln in xlines:	             # for lines in the model file.
			ln = ln.strip()              # Remove spaces 
			if len(ln) < 1: continue     # Ignore small lines
			if ln[0] in ['/','!','#']: continue    # Ignore comments
			for snp in self.snapshotKeywords:
				f = ln.find(snp)                   # Keyword found?
				if f >= 0: 
					self.snapshotLines.append(ln)
					#self.snapshotRequired[snp] = 1
			for inc  in self.outputFiles:          # Look for outputFileTypes
				f = ln.find(inc)                   # Keyword found?
				if f >= 0: 
					inames = ln.split()            # Has a value?
					if len(inames) < 2: continue
					iname = inames[1]
					inc_name = deriveIncludePath(iname,workpath,projectpath)
					try:
						xlines = os.stat(inc_name)
					except:
						continue
					fsize  = xlines[6] / 1024
					ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
					self.listOfOutputs.append(ostr)
					#self.listOfOutputs.append("%s: %s" % (inc,inc_name))


			f = ln.find('BINARY_DATA_DIRECTORY')
			self.binaryDataPathFound = 0
			if f >= 0: 
				iname = ln.split()[1]
				bindirpath = iname.replace("'",'') + '/' + modelbase
				self.binaryDataPathFound = 1

			#
			# Now check if there is an output directory (../output) and list 
			# its contents completely. 
			#
			for inc in self.editableFiles:
				f = ln.find(inc)
				if f >= 0: 
					inames = ln.split()
					if len(inames) < 2: 
						continue
					iname = inames[1]
					inc_name = deriveIncludePath(iname,workpath,projectpath)
					try:
						xlines = os.stat(inc_name)
						fsize  = xlines[6] / 1024
						ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
						self.listOfIncludes.append(ostr)
					except:
						pass
					#print "----> sector_data_path = ", sector_datapath
					#print "----> projectpath = ", projectpath
					if sector_datapath == None: continue
					inc_name = deriveIncludePath(iname,sector_datapath,projectpath)
					#print iname, "-->", inc_name
					try:
						xlines = os.stat(inc_name)
						fsize  = xlines[6] / 1024
						ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
						if not ostr in self.listOfIncludes: self.listOfIncludes.append(ostr)
					except:
						continue

					#fsize  = xlines[6] / 1024
					#ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
					#self.listOfIncludes.append(ostr)
					#self.listOfIncludes.append(ostr)
					#self.listOfIncludes.append("%s: %s :(%dK)" % (inc,inc_name,fsize))

		########################################################################################
		# Now set the list of output files.
		########################################################################################
		#
		#  If the binary directory path is set, then list the files in the bin dir path
		#
		if bindirpath <> None:
			tstr = bindirpath + os.sep + modelbase + ".output"
		else:
			tstr = modeldirroot + ".output"
		powersVersionString = ''
		try:
			xlines = open(tstr,'r').readlines()
			for xln in xlines: 
				f = xln.find('version:')
				if f>=0: 
					items = xln.split(':')
					powersVersionString = items[-1]
					break
	

		except:
			powersVersionString = 'Not run'

		ostr = "VERSION_INFO: %s : %s " % (tstr, powersVersionString)
		self.listOfOutputs.append(ostr)


		binrestartpath = []
		if bindirpath <> None:
			#print "bindirpath = ", bindirpath
			inc = 'OUTPUT_FILE'
			try:
				ofiles =  os.listdir(bindirpath)
			except: 
				ofiles = []
			dirs   = []
			for oname in ofiles:
				fullname = bindirpath + '/' + oname 
				if oname in ['data']: continue   # ignore the data directory
				if oname in ['restart']:         # Collect restart files
					binrestartpath.append(fullname)
					continue
				if os.path.isdir(fullname):      # Also sub directories 
					dirs.append(fullname)
					continue
				else:
					xlines = os.stat(fullname);
					fsize  = xlines[6] / 1024
					ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
				self.listOfOutputs.append(ostr)

			
			#
			# List the contents of the lower level directories too!
			#
			for ipath in dirs:
				ofiles =  os.listdir(ipath)
				for oname in ofiles:
					fullname = ipath + '/' + oname 
					if os.path.isdir(fullname): continue
					xlines = os.stat(fullname);
					fsize  = xlines[6] / 1024
					ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
					self.listOfOutputs.append(ostr)

		#
		try:
			inc = 'OUTPUT_FILE'
			fullname = projectpath + "/OUT_" + modelbase 
			print "fullname for OUT_", fullname
			xlines = os.stat(fullname);
			fsize  = xlines[6] / 1024
			ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			if not ostr in self.listOfOutputs: self.listOfOutputs.append(ostr)
		except:
			pass
		# List the contents of the project path as well.
		#
		try:
			ofiles =  os.listdir(projectpath + '/output')
		except:
			ofiles = []
		inc = 'OUTPUT_FILE'
		for oname in ofiles:
			f = oname.find(modelbase)
			if f < 0: continue
			fullname = projectpath + '/output/' + oname 
			xlines = os.stat(fullname)
			fsize  = xlines[6] / 1024
			ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			self.listOfOutputs.append(ostr)
		#
		# Finally, append any restart paths from this the bin
		#
		ofiles = []
		for rd in binrestartpath:
			try:
				for r in os.listdir(rd): 	
					ofiles.append(rd + os.sep + r)
			except:
				pass
		for fullname in ofiles:
			if os.path.isdir(fullname): continue
			xlines = os.stat(fullname)
			fsize  = xlines[6] / 1024
			ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			self.listOfOutputs.append(ostr)

		#
		# Append any restart paths from this directory: /red/restart/USER/MODEL
		#
		for rrdir in ['/red/restart','/red/restart1','/red/restart2','/red/restart3']:
			restartDir = rrdir + os.sep + os.getenv('USER') + os.sep +  modelbase 
			inc = 'OUTPUT_FILE'
			try:
				rnames = os.listdir(restartDir)
				for rname in rnames: 
					fullname = restartDir + os.sep + rname
					xlines = os.stat(fullname)
					fsize  = xlines[6] / 1024
					ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
					self.listOfOutputs.append(ostr)
			except:
				continue
		
		########################################################################################
		# Set data into the tabbed areas.
		########################################################################################
		self.tableOfOutputs.clear()
		informationFilename = ''
		model_information   = modelbase + '.information'
		for i in self.listOfOutputs: 
			il = tuple(i.split(':'))
			self.tableOfOutputs.insert("end",il)
			thisFile = str(il[modelFileColumnIndex]).strip()
			f = thisFile.find(model_information)
			if f > 0: 
				#print thisFile
				flen = len(thisFile) - f  
				#print flen, f, len(thisFile)
				if flen == len(model_information):
					#print "INFORMATION", thisFile
					informationFilename = thisFile

		self.tableOfIncludes.clear()
		for i in self.listOfIncludes: 
			il = tuple(i.split(':'))
			self.tableOfIncludes.insert("end",il)

		oslines = []
		for i in self.snapshotLines:
			ix = i.split()
			ix.insert(1,":")
			oslines.append("".join(ix))
		if self.binaryDataPathFound == 0: self.snapshotLines.append('BINARY_DATA_DIRECTORY not found in model file.')
		snapshotText = "\n".join(oslines)
		self.informationText.settext(snapshotText)
		#print informationFilename, " is the file ", modelbase
		if len(informationFilename)> 1:	
			try:
				ms = os.stat(informationFilename)
				self.informationText.clear()
				self.informationText.importfile(informationFilename)
			except:
				pass  


		#self.tableOfRestarts.clear()
		#for i in self.listOfRestart: 
			#il = tuple(i.split(':'))
			#self.tableOfRestarts.insert("end",il)

		icrx = int(crx.split(',')[1])
		#WORKS-->self.m_snapshotWidget.settext("\n".join(self.snapshotLines))
		#self.m_snapshotWidget.settext(snapshotText)

		#for tbn in self.tabNames:
		#	tab = self.nb.tab(tbn)
		#	tab['background'] = 'gray64'
		if icrx == 1: 
			self.nb.selectpage('Output Files')
			#tab = self.nb.tab('Output Files')
			#tab['background'] = 'lightblue'
		elif icrx == 2: 
			self.nb.selectpage('Information')
		else:
			self.nb.selectpage('Input Files')
			#tab = self.nb.tab('Input Files')
			#tab['background'] = 'lightblue'

		self.tableOfExtracted.clear()
		self.extractList = []

		lstat = os.stat(fullmodelfilename)
		thisuid   = lstat[4]
		userlists = pwd.getpwall()
		username = os.getenv('USER') 
		for ul in userlists: 
			if thisuid == ul[2]: username = ul[0]; break
		userExtractDir = '/red/simdata/EXT400/' + username 
		try:
			os.path.walk(userExtractDir,visitExtracted,[self.extractList,modelbase])
			for i in self.extractList: self.tableOfExtracted.insert("end",i)
		except:
			print "There was an exception at the end of the extracted file listing."
			pass
		########################################################################################
		# End of eventTableSelect function here.
		########################################################################################

	def forceopenProjectXMLfile(self,eraseList,initDir=None):
		if initDir == None:
			fromhere=os.path.dirname(self.projectsXMLfilename)
			fromfile=self.projectsXMLfilename
		else: 
			fromhere=initDir
			fromfile='projects.xml'
		ofile=fromhere + os.sep + fromfile
		self.openThisProjectFile(eraseList,ofile)

	def openProjectXMLfile(self,eraseList,initDir=None,justdoit=0):
		if initDir == None:
			fromhere=os.path.dirname(self.projectsXMLfilename)
			fromfile=self.projectsXMLfilename
		else: 
			fromhere=initDir
			fromfile='projects.xml'
		ofile = askopenfilename(filetypes=[("XML file","*.xml")],\
			initialdir=fromhere, \
			title='Enter project filename to read',\
			initialfile=fromfile)
		if ofile:
			self.openThisProjectFile(eraseList,ofile)
			return 1
		return 0

	def openThisProjectFile(self,eraseList,ofile):
		self.projectsXMLdirectory = os.path.dirname(ofile)
		os.chdir(self.projectsXMLdirectory)
		self.projectsXMLfilename = ofile 
		self.notesXMLfilename    = self.projectsXMLdirectory + os.sep + 'notes.xml'
		if os.path.exists(self.notesXMLfilename): self.readNotesXMLfile()
		self.readProjectsFile(eraseList)
		self.resetProjectsList()
		return 1

	def copyXMLfile(self):
		ifile = askopenfilename(filetypes=[("XML file","*.xml")],\
			defaultextension=".xml", title="Enter the name of the file to copy",\
			initialdir=os.path.dirname(self.projectsXMLfilename))
		if ifile: 
			ofile = asksaveasfilename(filetypes=[("XML file","*.xml")],\
				defaultextension='.xml', \
				title='Enter file name to write to',\
				initialdir=os.path.dirname(self.projectsXMLfilename))
			if ofile: 
				xlines = open(ifile,'r').readlines()
				fd = open(ofile,'w')
				for xln in xlines: fd.write(xln)
				fd.close()
			
	def saveProjectXMLfile(self,saveas=0):
		ofile = asksaveasfilename(filetypes=[("XML file","*.xml")],\
			defaultextension='.xml', \
			title='Enter file name to write to',\
			initialdir=os.path.dirname(self.projectsXMLfilename),\
			initialfile=self.projectsXMLfilename)
		if ofile:
			if saveas==1: 
				savename = self.projectsXMLfilename 
				savenote = self.notesXMLfilename    
			#print " I will save the project to " , ofile
			self.projectsXMLfilename = ofile
			self.projectsXMLdirectory = os.path.dirname(ofile)
			self.notesXMLfilename     = self.projectsXMLdirectory + os.sep + 'notes.xml'
			self.writeProjectsFile()
			self.writeNotesXMLfile()
			if saveas==1:                      # Restore Original 
				self.projectsXMLfilename = savename
				self.projectsXMLdirectory = os.path.dirname(savename)
				self.notesXMLfilename   = savenote 

	def userCaseScan(self):
		sel = self.sl_projects.getcurselection()
		if len(sel) < 1:
			showwarning("Oops!"," Select a project in your cases to add files to")
			return 
		self.userDialog = Toplevel() 
		self.userDialog.title("User Files") 
		self.userDialog.geometry("%dx%d+50+50" %(800,600))
		self.doThis = selectUserFileDlg(self.userDialog,usethis=self)
		self.doThis.pack(side=TOP,fill=BOTH,expand=1)
		#self.userDialog.mainloop()

	def userCaseQuit(self):
		if self.userDialog <> None: self.userDialog.destroy()
		self.userDialog = None

	def scanDir(self,here = None):
		if here == None: 
			here = askdirectory()
			if here == None: return 
		if len(here) < 1: return
		self.lastWorkingDir = here 
		os.chdir(self.lastWorkingDir)
		self.retlist = []
		os.path.walk(here,visit,self.retlist)
		self.tableOfModels.clear()
		for i in self.retlist:
			self.tableOfModels.insert("end",i)
		self.writeGUIstate(self.lastWorkingDir)
	
	def m_sortModelsByColumn(self,tbl,c):
		if self.lastsort == '-increasing': 
			self.lastsort = '-decreasing' 
		else:
			self.lastsort = '-increasing' 
		self.tableOfModels.sortbycolumn(c,self.lastsort)


	def m_sortIncludeTablesByColumn(self,tbl,c):
		if self.lastsort == '-increasing': 
			self.lastsort = '-decreasing' 
		else:
			self.lastsort = '-increasing' 
		self.tableOfIncludes.sortbycolumn(c,self.lastsort)

	def m_sortOutputTablesByColumn(self,tbl,c):
		if self.lastsort == '-increasing': 
			self.lastsort = '-decreasing' 
		else:
			self.lastsort = '-increasing' 
		self.tableOfOutputs.sortbycolumn(c,self.lastsort)

	def m_editEndCommand(self,tbl,row,col,txt):
		try:
			v = float(txt)
		except:
			tbl.rejectinput()
			return
		
		#print "You selected ...", txt
		#print "Row ", row
		#print "Col ", col
		#self.btn_replot['bg'] = 'red'
		#elf.btn_saveChanges['bg'] = 'red'
		return txt


	def writeGUIstate(self,where):
		#print "I will write about ", where
		#print "Where I am ", os.getcwd()
		filename = os.getenv('HOME') + os.sep + 'powersdata' + os.sep + 'manager.inf'
		#print "I will write to ", filename
		lastdir = 'LASTDIR : ' + where + '\n'
		fd=open(filename,'w')
		fd.write('#Saved for MODEL GUI - \n#' + ctime() + '\n')
		fd.write(lastdir); 
		fd.write('LASTPROJECT:%s\n' % self.lastProjectName)
		fd.write('PROJECTDIR:%s\n' % os.path.dirname(self.projectsXMLfilename))
		fd.write('PROJECTFILE:%s\n' % os.path.basename(self.projectsXMLfilename))
		fd.write('USERXTERM:%s\n' % self.userXtermCommand)
		fd.write('USEREDITOR:%s\n' % self.userEditorCommand)
		fd.write('NUMNODES:%d\n' % self.numNodes)
		fd.write('USENODE:%s\n' % self.use_node)
		fd.write('EXTRACT:%d\n' % self.doExtract)
		fd.close()

	def readGUIstate(self):
		if os.name == 'posix':
			self.repository = os.getenv('HOME')
			if self.repository == None:
				self.repository = "/peasd/ssd/husainkb/template"
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
		filename = self.repository + os.sep + 'manager.inf'

		############################################################################
		# VERY IMPORTANT # Set the defaultprojects path based on the directory now.
		############################################################################
		self.projectsXMLdirectory = os.getenv('HOME') + os.sep + 'powersdata' 
		self.projectsXMLbasename  = 'projects.xml'
		############################################################################
		self.lastSelectedProject = ''
		try:
			fd=open(filename,'r')
			xlines=fd.readlines()
			for ln in xlines:
				ln = ln.strip()
				if ln == None: continue
				if ln[0] == '#': continue
				items = ln.split(':')
				if len(items) == 2:
					token = items[0].strip()
					value = items[1].strip()
					#print "[%s][%s]" % (token,value)
					if token == 'LASTPROJECT': self.lastSelectedProject = value
					if token == 'PROJECTDIR' : self.projectsXMLdirectory = value
					if token == 'PROJECTFILE' : self.projectsXMLbasename = value
					if token == 'LASTDIR': 
						self.lastWorkingDir = value
						os.chdir(value)
					if token == 'READRATES': 
						self.processTimeInfo.set(int(value))
					if token == 'USERXTERM': 
						if os.path.exists(value): 
							self.userXtermCommand = value
						else:
							self.userXtermCommand = '/usr/bin/xterm'
					if token == 'USEREDITOR': 
						if os.path.exists(value): 
							self.userEditorCommand = value
						else:
							if os.path.exists('/usr/X11R6/bin/gvim'):
								self.userEditorCommand = '/usr/X11R6/bin/gvim'
							else: 
								self.userEditorCommand = '/usr/bin/vim'
					if token == 'NUMNODES': self.numNodes = int(value)
					if token == 'EXTRACT': self.doExtract = int(value)
					if token == 'USENODE': self.use_node = value
			fd.close()
		except:
			return

		############################################################################
		# VERY IMPORTANT # Set the defaultprojects path based on the directory now.
		############################################################################
		self.projectsXMLfilename = self.projectsXMLdirectory + os.sep + self.projectsXMLbasename
		############################################################################
		# VERY IMPORTANT # Set the defaultprojects path based on the directory now.
		############################################################################
		self.projectsXMLfilename = self.projectsXMLdirectory + os.sep + self.projectsXMLbasename
		self.notesXMLfilename    = self.projectsXMLdirectory + os.sep + 'notes.xml'
		############################################################################
		self.fileNotes = {}
		self.listOfProjects = {}
		if os.path.exists(self.notesXMLfilename): self.readNotesXMLfile()
		if os.path.exists(self.projectsXMLfilename): 
			self.readProjectsFile()
			self.resetProjectsList()

	def resetProjectsList(self):
		"""
		Once you have read the project, you can reset the projects list.
		"""
		#print "I am setting it here ...", self.projectsXMLfilename
		#print "I am reading here ..."   , self.projectsXMLfilename
		skeys = self.listOfProjects.keys()
		slist = map(str,skeys)
		slist.sort()
		self.sl_projects.setlist(slist)
		if self.lastSelectedProject in slist: self.showProjectInformation(slist)

	def showProjectInformation(self,slist):
		self.showProjectEntries(self.lastSelectedProject)
		self.lastsort = '-increasing' 
		self.m_sortModelsByColumn(self.tableOfModels,2)
		ndx = slist.index(self.lastSelectedProject)
		self.sl_projects.selection_set(ndx)
		self.sl_projects.activate(ndx)

	def setToFirstProject(self):
		skeys = self.listOfProjects.keys()
		slist = map(str,skeys)
		slist.sort()
		if len(slist) < 1: return
		self.lastSelectedProject = slist[0]
		self.showProjectInformation(slist)

	def handler_openUserDir(self,mainFrame,userdir):
		"""
		mainFrame The main program frame objet
		userDir   to open the file from
		"""
		self.forceopenProjectXMLfile(eraseList=1,initDir=userdir)
		mainFrame.nb.selectpage('Office')
		self.setToFirstProject()

	def handler_viewUserDir(self,mainFrame,userdir):
		re = self.openProjectXMLfile(eraseList=1,initDir=userdir)
		if re == 1: 
			mainFrame.nb.selectpage('Office')
			self.setToFirstProject()

	def handler_selectFileFromUserXML(self,mainFrame,userxmlfile):
		"""
		Show the list of projects in the xml file and let the user select from it.
		Once the list is selected add it to the current project file.
		"""
		pass

class makeManager:	
	def __init__(self,rootWindow,filename=None):
		self.m_rootWindow = rootWindow
		self.processTimeInfo = None
		self.nb= Pmw.NoteBook(self.m_rootWindow)
		self.tabManageParms = self.nb.add('Manage') 	
		self.tabSubmitParms = self.nb.add('Jobs')  
		self.tabMonitorParms = self.nb.add('Monitor')
		self.nb.pack(padx=5,pady=5,fill=BOTH,expand=1)

		self.ff = Frame(self.tabManageParms)
		self.ff.pack(side=TOP,fill=BOTH,expand=1)
		self.manageParameters = pModelManagerFrame(self.ff,self)
		self.manageParameters.readGUIstate()
		self.mpFrame = Pmw.PanedWidget(self.tabSubmitParms) #,orient=HORIZONTAL)
		self.mpFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.mpFrame.add('top',min=100,size=.7)
		self.mpFrame.add('bottom',min=100)
		self.jobInfoObject = pJobInfoFrame(self.mpFrame.pane('top'))

		#self.submitJobParms = makeSubmitForm(self.mpFrame.pane('bottom'),\
		#	tellme=self.jobSubmissionHandler,obj=self.manageParameters)
		#self.submitJobParms.setDefaultModelFile('')
		#self.manageParameters.submitJobParms = self.submitJobParms    # Keep a reference
#
		self.mobj = pMonitorFrame(self.tabMonitorParms)
		self.mobj.modelFilename = ''
		self.mobj.outputFilename = ''
		self.mobj.commandFilename = ''
		self.manageParameters.monitorObject = self.mobj    # Keep a reference

		self.jobInfoObject.setMonitorObject(self.mobj)

	def jobSubmissionHandler(self,obj,modelName,outputName,errName):
		"""
		This is a kludge to set the file names for a batch job from the 
		The obj is myself, whereas the self in the submitJob object
		"""
		obj.monitorObject.modelFilename = modelName
		obj.monitorObject.outputFilename = outputName
		obj.monitorObject.commandFilename = errName
		#print "I am setting ... ", modelName,outputName,errName


if __name__ == '__main__':
	root = Tk() 
	root.title('POWERS EDITING ENVIRONMENT DEC 26, 2005 - Kamran Husain 874 7898')
	f = makeManager(root)
	root.geometry("%dx%d+0+0" %(1024,640))
	root.mainloop()

