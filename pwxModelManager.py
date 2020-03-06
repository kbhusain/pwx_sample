"""
Powers Office Version 2.0


"""
import pyexpat   # ABSOLUTELY CRITICAL IMPORT HERE
import os, sys, string, pwd
from time import *
import  wx
import wx.lib.dialogs
import wx.lib.foldpanelbar as fpb
import wx.lib.mixins.listctrl as listmix
import wx.gizmos as gizmos
import pwxImages 
from pwxFoldingOptions import *
from pwxUserIds import *
from pwxMMprojects import *
from pPBFutils import *
from pObject import deriveWorkpaths, deriveIncludePath
import xml
from xml.dom import minidom
from pChangeRestart import verifyCopyModelFile


def showTime(x): return strftime("%Y.%m.%d %H.%M ", localtime(x)) 

def visit(arg,dirname,files):
	"""
	arg is appended with pathnames. Send an empty list or a filled one.
	Only files with a *.model extension are included in the list
	"""
	for name in files: 
		fn,ext = os.path.splitext(name)
		if ext in [ '.model', '.DATA' ]:
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
	
"""
#
# Constants for this file.
#
"""
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

class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent,ID,pos=wx.DefaultPosition,\
		size=(-1,-1),style=wx.EXPAND):
		wx.ListCtrl.__init__(self,parent,ID,pos,size,style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class TestListCtrlPanel(wx.Panel,listmix.ColumnSorterMixin):
	def __init__(self, parent,ID,style=0):
		wx.Panel.__init__(self,parent,ID,style=wx.WANTS_CHARS)
		self.itemDataMap = None 
	
	def SetList(self,x): self.list = x
	def GetListCtrl(self): return self.list 
# ----------------------------------------------------------------------------
# Beginning Of Main Menu Items
# ----------------------------------------------------------------------------

class pwxModelManager(wx.Frame):
	def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
				 size=(700,650), style=wx.DEFAULT_FRAME_STYLE):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self._flags = 0
		self.SetIcon(GetMondrianIcon())
		self.SetTitle("Model Input Manager Kamran Husain ")

		self.makePaths(parent) 
		self.makeMenus()
		self.makePopupMenus()

		self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self.statusbar.SetStatusWidths([-4, -3])
		self.statusbar.SetStatusText("Kamran Husain - Nov 17 2006", 0)
		self.statusbar.SetStatusText("Welcome to the new office!", 1)

		self._leftWindow1 = wx.SashLayoutWindow(self, 101, wx.DefaultPosition,
												wx.Size(200, 1000), wx.NO_BORDER |
												wx.SW_3D | wx.CLIP_CHILDREN)
		self._leftWindow1.SetDefaultSize(wx.Size(220, 1000))
		self._leftWindow1.SetOrientation(wx.LAYOUT_VERTICAL)
		self._leftWindow1.SetAlignment(wx.LAYOUT_LEFT)
		self._leftWindow1.SetSashVisible(wx.SASH_RIGHT, True)
		self._leftWindow1.SetExtraBorderSize(10)

		self._pnl = 0

		# will occupy the space not used by the Layout Algorithm
		self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
		#------------------ The notebook code goes here ------------------------
		psizer = wx.BoxSizer(wx.VERTICAL)
		self.notebook_inputOutput =  wx.Notebook(self.remainingSpace, -1, style=wx.DOUBLE_BORDER)
		psizer.Add( self.notebook_inputOutput ,1, wx.TOP | wx.LEFT | wx.GROW )

		self.remainingSpace.SetSizer(psizer)
		

		self.notebook_1_pane_info = wx.Panel(self.notebook_inputOutput, -1)
		rsizer = wx.BoxSizer(wx.VERTICAL)
		self.text_ctrl_information = wx.TextCtrl(self.notebook_1_pane_info, -1, style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
		rsizer.Add(self.text_ctrl_information,1 ,wx.TOP | wx.LEFT | wx.GROW)
		self.notebook_1_pane_info.SetSizer(rsizer)

		self.notebook_1_pane_projectlist = wx.Panel(self.notebook_inputOutput, -1)
		self.treelist_ctrl_projectfiles = gizmos.TreeListCtrl(self.notebook_1_pane_projectlist, -1,
					style = wx.TR_DEFAULT_STYLE| wx.TR_FULL_ROW_HIGHLIGHT)
		rsizer = wx.BoxSizer(wx.VERTICAL)
		rsizer.Add(self.treelist_ctrl_projectfiles,1 ,wx.TOP | wx.LEFT | wx.GROW)
		self.notebook_1_pane_projectlist.SetSizer(rsizer)
		self.treelist_ctrl_pwindow = self.treelist_ctrl_projectfiles.GetMainWindow()
		
		self.treelist_ctrl_pwindow.Bind(wx.EVT_RIGHT_UP,self.handleProjectListUp)
		self.treelist_ctrl_pwindow.Bind(wx.EVT_MIDDLE_UP,self.handleProjectListMB)
		self.treelist_ctrl_pwindow.Bind(wx.EVT_LEFT_DCLICK,self.handleProjectListDB)

		self.treelist_ctrl_projectfiles.AddColumn('TYPE')
		self.treelist_ctrl_projectfiles.AddColumn('PATH')
		self.treelist_ctrl_projectfiles.AddColumn('DATE')
		self.treelist_ctrl_projectfiles.SetColumnWidth(0,100)
		self.treelist_ctrl_projectfiles.SetColumnWidth(1,400)

		self.notebook_inputOutput.AddPage(self.notebook_1_pane_projectlist, "Projects")
		#self.notebook_inputOutput.AddPage(self.notebook_1_pane_inputs, "Inputs")
		#self.notebook_inputOutput.AddPage(self.notebook_1_pane_outputs, "Outputs")
		#self.notebook_inputOutput.AddPage(self.notebook_1_pane_extract, "Extracts")
		self.notebook_inputOutput.AddPage(self.notebook_1_pane_info, "Information")
		
		self.ID_WINDOW_TOP = 100
		self.ID_WINDOW_LEFT1 = 101
		self.ID_WINDOW_RIGHT1 = 102
		self.ID_WINDOW_BOTTOM = 103
	
		self._leftWindow1.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnFoldPanelBarDrag,
							   id=100, id2=103)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.ReCreateFoldPanel(0)
	
	def showwarning(self, caption, message): wx.MessageBox(message,caption='MM:' + caption)

	def handleProjectListMB(self,evt):
		pos = evt.GetPosition() 
		item, flags, col = self.treelist_ctrl_projectfiles.HitTest(pos)
		if item:
			itemText = self.treelist_ctrl_projectfiles.GetItemText(item, col)
			if col == 1:  
				self.lastSelectedModelFileName  = itemText
				self.treelist_ctrl_projectfiles.PopupMenu(self.inModelPopupMenu)

	def handleProjectListDB(self,evt):
		"""
		This handles ALL double clicks. 
		"""
		pos = evt.GetPosition() 
		item, flags, col = self.treelist_ctrl_projectfiles.HitTest(pos)
		if item:
			if col == 0 and evt.GetButton() == 1: 
				itemText  = self.treelist_ctrl_projectfiles.GetItemText(item, 0)
				projectchild = self.treelist_projectnames.get(itemText,None)
				if projectchild <> None: 
					self.lastSelectedModelFileName = self.treelist_ctrl_projectfiles.GetItemText(item, 0)
					self.lastSelectedInputFileName = self.treelist_ctrl_projectfiles.GetItemText(item, 1)
					fname, ext = os.path.splitext(self.lastSelectedInputFileName)
					if ext == '.model': self.showModelFileDependancies()
			if col == 1 and evt.GetButton() == 1:
				fileType  = self.treelist_ctrl_projectfiles.GetItemText(item, 0)
				itemText  = self.treelist_ctrl_projectfiles.GetItemText(item, 1)
				if fileType in ['BINARY_FILE']:
					xlines = collectPBFinfo(itemText)
					dlg = wx.lib.dialogs.ScrolledMessageDialog(self,xlines,itemText)
					dlg.ShowModal()
				if istextfile(itemText) in [ 1, 2, 3, 4 ]:
					self.lastSelectedModelFileName  = itemText
					self.startTextEditor( self.lastSelectedModelFileName)
				
		evt.Skip()	
			
	def handleProjectListUp(self,evt):
		pos = evt.GetPosition() 
		item, flags, col = self.treelist_ctrl_projectfiles.HitTest(pos)
		if item:
			print "HIT", col, self.treelist_ctrl_projectfiles.GetItemText(item, col)
			if col == 1 and evt.GetButton() == 3: 
				name  = self.treelist_ctrl_projectfiles.GetItemText(item, col)
				self.doBtn3Handling(name)



	def doBtn3Handling(self,name):
		name = name.strip()
		if istextfile(name) == 5:  # For XML files 
			if os.fork() == 0: os.execl('/usr/bin/mozilla',"mozilla", name)
			return		
		if istextfile(name) == 2:
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runFlow.ksh", name)
			return
		if istextfile(name) in [4, 3]:
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runPVT.ksh", name)

	def makePopupMenus(self):
		"""
		When RMB is pressed 
		"""
		self.inModelPopupMenu = wx.Menu()
		item = self.inModelPopupMenu.Append(-1.,'vim');  self.Bind(wx.EVT_MENU,self.mpp_startVim,item)
		item = self.inModelPopupMenu.Append(-1.,'submit');  self.Bind(wx.EVT_MENU,self.mpp_submitJob,item)
		item = self.inModelPopupMenu.Append(-1.,'tail'); self.Bind(wx.EVT_MENU,self.mpp_tailFile,item)
		item = self.inModelPopupMenu.Append(-1.,'syntax');  self.Bind(wx.EVT_MENU,self.mpp_runSyntax,item)
		item = self.inModelPopupMenu.Append(-1.,'save as'); self.Bind(wx.EVT_MENU,self.mpp_saveTextAs,item)
		self.inModelPopupMenu.AppendSeparator() 
		item = self.inModelPopupMenu.Append(-1.,'diff'); self.Bind(wx.EVT_MENU,self.mpp_diffModels,item)
		item = self.inModelPopupMenu.Append(-1.,'inclusion'); self.Bind(wx.EVT_MENU,self.mpp_showInclusions,item)
		self.inModelPopupMenu.AppendSeparator() 
		item = self.inModelPopupMenu.Append(-1.,'xterm');  self.Bind(wx.EVT_MENU,self.mpp_startXterm,item)
		item = self.inModelPopupMenu.Append(-1.,'delete'); self.Bind(wx.EVT_MENU,self.mpp_deleteOneFile,item)
		item = self.inModelPopupMenu.Append(-1.,'file mgr'); self.Bind(wx.EVT_MENU,self.mpp_startKonquerer,item)

		self.inInputPopupMenu = wx.Menu()
		item = self.inModelPopupMenu.Append(-1.,'vim');  self.Bind(wx.EVT_MENU,self.ipp_startVim,item)
		item = self.inModelPopupMenu.Append(-1.,'tail'); self.Bind(wx.EVT_MENU,self.ipp_tailFile,item)



	def startXterm(self):
		if os.fork() == 0: os.execl(self.userXtermCommand,"xterm")


	def startTextEditor(self,name):
		if istextfile(name): 
			if os.fork() == 0: 
				os.execl(self.userXtermCommand,"xterm", "-e", self.userEditorCommand,name)
		else:
			self.showwarning("Oops!"," I cannot edit what appears to be a binary file: " + name)

	def startTail(self,name):
		if istextfile(name): 
			if os.fork()==0:
				os.execl("/usr/bin/xterm","xterm", "-title", name, "-e", '/usr/bin/tail', '-f', name)

	def copyFile(self,name):
		dlg = wx.FileDialog(self,"Save copy of file for extraction", defaultDir=os.path.dirname(name),
			style=wx.OPEN | wx.CHANGE_DIR,
			defaultFile = "*.*", 
			wildcard = "All Files |*.*")
		if dlg.ShowModal() == wx.ID_OK: 
			ofile = dlg.GetPath()
			fn,ext = os.path.splitext(ofile)
			if ext <> ".model":
				os.system("cp "+name+" "+ofile)
				return 
			verifyCopyModelFile(name,ofile)
			self.lastWorkingDir = os.path.dirname(ofile)   # 
			os.chdir(self.lastWorkingDir)
			dirlist = createRowEntry(ofile)
			self.addOneFileToProject(dirlist)  # Now somehow click the project list.
			
	def startKonquerer(self,name):
		pathname = os.path.dirname(name)
		if os.fork() == 0: 
			try:
				os.chdir(pathname)
				os.execl("/usr/bin/konqueror","konqueror", pathname)
			except:
				os.execl("/usr/bin/konqueror","konqueror")
	
	def runSubmitJob(self, name):
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runSubmit.ksh",name)
		
	#_____________________ For the menu _________________________________________________
	def mpp_startXterm(self,event): self.startXterm()
	def mpp_runSyntax(self,event): 
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", scriptBaseDir + "runSyntax.ksh",self.lastSelectedModelFileName)
	def mpp_submitJob(self,event): self.runSubmitJob( self.lastSelectedModelFileName)
	def mpp_startVim(self,event): self.startTextEditor( self.lastSelectedModelFileName)
	def mpp_tailFile(self,event): self.startTail( self.lastSelectedModelFileName)
	def mpp_saveTextAs(self,event): self.copyFile( self.lastSelectedModelFileName)
	def mpp_diffModels(self,event): pass
	def mpp_showInclusions(self,event): pass
	def mpp_deleteOneFile(self,event): pass
	def mpp_startKonquerer(self,event): self.startKonquerer(self.lastSelectedModelFileName)

	#_____________________ For the menu _________________________________________________
	def ipp_startVim(self,event): self.startTextEditor( self.lastSelectedInputFileName)
	def ipp_tailFile(self,event): self.startTail( self.lastSelectedInputFileName)

	def handle_inputFileLB(self,event):
		self.lastSelectedInputIndex = event.m_itemIndex
		item =  self.list_ctrl_inputFiles.GetItem(self.lastSelectedInputIndex,1)
		self.lastSelectedInputFileName  = item.GetText()

	def handle_inputFileRB(self,event):
		self.lastSelectedInputIndex = event.m_itemIndex
		item =  self.list_ctrl_inputFiles.GetItem(self.lastSelectedInputIndex,1)
		self.lastSelectedInputFileName  = item.GetText()
		


	def makePaths(self,parent):
		self.toolDir = "/peasapps/ssd/test_lnx/scripts/Linux/"	
		if os.path.exists('/usr/X11R6/bin/gvim'):
			self.userEditorCommand = '/usr/X11R6/bin/gvim'
		else: 
			self.userEditorCommand = '/usr/bin/vim'
		self.lastSelectedModelFileName = ''
		self.lastSelectedModelIndex = 0
		self.userXtermCommand = '/usr/bin/xterm'
		self.userSimstoreCommand = '/peasapps/ssd/test_lnx/scripts/Linux/SimStoreE-linux'
		self.parent = parent
		self.masterObject = self
		self.lastsort = '-decreasing' 
		self.guiEditor = None 
		self.projectsXMLdirectory = os.getenv('HOME') + os.sep + 'powersdata' 
		self.projectsXMLfilename  = self.projectsXMLdirectory + os.sep + 'projects.xml'
		self.notesXMLfilename     = self.projectsXMLdirectory + os.sep + 'notes.xml'
		self.fileNotes = {}
		self.listOfProjects = {}
		self.ds_inputFiles = mmgrDataSource([]) 
		self.ds_outputFiles = mmgrDataSource([])
		self.ds_extractFiles =  mmgrDataSource([])
		self.snapshotKeywords = ['XNODES','YNODES','ZNODES','TITLE','RESERVOIR_TYPE','PHASES','BINARY_DATA_DIRECTORY']
		
		self.lastProjectName = ''
		self.editableFiles = ['MODEL_FILE', 'INCLUDE_FILE','BINARY_FILE','TEXT_FILE',\
			'WELL_PERFS','WELL_RATES','RECURRENT_DATA','RESTART_INPUT', 'OUTPUT_FILE', 'INT_FILE', 'VERSION_INFO', 'EXTRACTED_FILE']
		self.outputFiles   = ['RESTART_OUTPUT', 'MAPS_OUTPUT' ]
	
	#def diffModelFiles(self):
	#	rows =  self.list_ctrl_modelFiles.GetSelection()
	#	if len(rows) <> 2: 
	#		showwarning("STOP!","You can select a difference only between two model files"); 
	#		return
	#	row0 =  self.tableOfModels.get(rows[0]); name0 = str(row0[modelFileColumnIndex])
	#	row1 =  self.tableOfModels.get(rows[1]); name1 = str(row1[modelFileColumnIndex])
	#	print 'I am differencing..',name0
	#	print 'and ',name1
	#	if istextfile(name0) and istextfile(name1): 
	#		cmdstring = "/usr/bin/diff %s %s" % (name0,name1) 
	#		rsp = os.popen(cmdstring,'r')
	#		xlines = "".join(rsp.readlines())
	#		self.diffWindow = Pmw.TextDialog(self.parent, scrolledtext_labelpos='n',
	#				title="Difference",
	#				defaultbutton=0,
	#				buttons=('Close','Save'),command=self.diffCommandHandler, 
	#				label_text="%s vs. %s" % (name0,name1)) 
	#		self.diffWindow.insert(END,"".join(xlines))


	def openThisProjectFile(self,eraseList,ofile):
		"""
		If eraseList == 0: you have an import 
		If eraseList == 1: you overwrite 
		"""
		self.projectsXMLdirectory = os.path.dirname(ofile)
		os.chdir(self.projectsXMLdirectory)
		self.projectsXMLfilename = ofile 
		self.notesXMLfilename    = self.projectsXMLdirectory + os.sep + 'notes.xml'
		if os.path.exists(self.notesXMLfilename): self.readNotesXMLfile()
		self.readProjectsFile(eraseList)
		self.resetProjectsList()
		return 1

	def copyXMLfile(self, ifile=None):
		ifile = None; ofile = None
		dlg = wx.FileDialog(self,"Open XML file for copy", defaultDir=os.getenv('HOME') + '/powersdata',
			style=wx.OPEN | wx.CHANGE_DIR,
			defaultFile = "*.xml", 
			wildcard = "XML (*.xml)|*.xml|All Files |*.*")
		if dlg.ShowModal() == wx.ID_OK: 
			ifile = dlg.GetPath()
		dlg.Destroy()
		if ifile: 
			dlg = wx.FileDialog(self,"Open XML file to write to", defaultDir=os.getenv('HOME') + '/powersdata',
				style=wx.SAVE | wx.CHANGE_DIR,
				defaultFile = "*.xml", 
				wildcard = "XML (*.xml)|*.xml|All Files |*.*")
			if dlg.ShowModal() == wx.ID_OK: 
				ofile = dlg.GetPath()
			dlg.Destroy()
		if ofile and ifile: 
			xlines = open(ifile,'r').readlines()
			fd = open(ofile,'w')
			for xln in xlines: fd.write(xln)
			fd.close()
			
	def saveProjectXMLfile(self,saveas):
		ofile = None
		dlg = wx.FileDialog(self,"Open XML file to write to", defaultDir=os.path.dirname(self.projectsXMLfilename),\
			style=wx.SAVE | wx.CHANGE_DIR,
			defaultFile = "*.xml", 
			wildcard = "XML (*.xml)|*.xml|All Files |*.*")
		if dlg.ShowModal() == wx.ID_OK: 
			ofile = dlg.GetPath()
		dlg.Destroy()
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
		
	def writeProjectsFile(self):
		writeFail = 0
		try:
			fd = open(self.projectsXMLfilename,'w')
		except:
			writeFail = 1

		while writeFail == 1:
			self.showwarning("Oops!"," I cannot save to the file " + self.projectsXMLfilename + " ... try again ... ")
			safename = os.getenv('HOME') + os.sep + 'powersdata' + os.sep + 'projects.xml'  
			#ofile = asksaveasfilename(filetypes=[('XML file',"*.xml"),("All Files",'*')],\
			#	initialfile=safename,title='Select a different name')
			dlg = wx.FileDialog(self,"Open XML file to write to", defaultDir=os.path.dirname(self.projectsXMLfilename),\
						style=wx.SAVE | wx.CHANGE_DIR, defaultFile = "*.xml", wildcard = "XML (*.xml)|*.xml|All Files |*.*")
			if dlg.ShowModal() == wx.ID_OK: 
				ofile = dlg.GetPath()
			dlg.Destroy()
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
				self.showwarning("Oops!"," I did not save to the file " + self.projectsXMLfilename )
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

	def readProjectsFile(self,eraseList=1):
		self._mgrProjects.SetXMLfilename(os.path.basename(self.projectsXMLfilename))
		dirname =  os.path.dirname(self.projectsXMLfilename)
		pdir =  dirname.split('/')
		f = dirname.find('powersdata')
		if len(pdir) > 3 and f > 0:
			self._mgrProjects.SetUserName(pdir[3])
		else:
			self._mgrProjects.SetUserName(self.projectsXMLfilename)
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

		return 0

	def resetProjectsList(self):
		"""
		Once you have read the project, you can reset the projects list.
		"""
		#print "I am setting it here ...", self.projectsXMLfilename
		#print "I am reading here ..."   , self.projectsXMLfilename
		skeys = self.listOfProjects.keys()
		slist = map(str,skeys)
		slist.sort()
		self._mgrProjects.SetProjectsList(slist)
		if self.lastSelectedProject in slist: self.showProjectInformation(slist)

	def handleAddCases(self,dlg,event):
		pname = self._mgrProjects.GetSelectedProject()
		if len(pname) < 1: 
			self.showwarning("Select a project to add the case to", "Error")
			return 

		dlg = wx.DirDialog(None,"Choose a directory to search in ", 
			defaultPath='/red/rsd/' + os.getenv('USER'), 
			style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		directory = None
		if dlg.ShowModal() == wx.ID_OK: directory = dlg.GetPath()
		dlg.Destroy()
		if directory == None: return
		self.lastWorkingDir = directory 
		os.chdir(self.lastWorkingDir)
		self.retlist = []
		os.path.walk(directory,visit,self.retlist)
		#pathsToUse = [ ":".join(x) for x in self.retlist ] 
		pathsToUse = [ x[1] for x in self.retlist ] 
		strings = []
		dlg = wx.MultiChoiceDialog(self,"Pick the models you want to add to the project", "Add Cases", pathsToUse)
		if dlg.ShowModal() == wx.ID_OK:
			selections = dlg.GetSelections()
			strings = [pathsToUse[x] for x in selections]
			project = self.listOfProjects[pname]
			project.extend(strings)
			self.resetProjectsList()
			self.listOfProjects[pname] = project
			self._mgrProjects.SetSelectedProject(pname) 
			self.handleShowProject(pname)
		dlg.Destroy()

	def handleSaveProject(self,dlg,event):
		r = self.writeProjectsFile()
		if r > -1: self.writeNotesXMLfile()

	def handleUserImport(self,dlg,event):
		self.userFrame = pwxUserImports(None, -1, "")
		self.userFrame.SetMaster = self
		self.userFrame.Show(True)
	
	def handleNewProject(self,dlg,event):
		pname = wx.GetTextFromUser('Enter Project Name', "Enter Name of new project, no spaces")
		if len(pname) < 1: return 
		pname = pname.strip()
		if self.listOfProjects.has_key(pname):
			self.showwarning(pname + "already exists", "Error")
			return
		self.listOfProjects[pname] = []
		self.resetProjectsList()

	def handleDelProject(self,dlg,event):
		pname = dlg.GetSelectedProject()
		retcode = wx.MessageBox("Delete project: " + pname, "Delete", wx.YES_NO | wx.ICON_QUESTION)
		if retcode <> wx.YES: return 
		del self.listOfProjects[name]
		self.resetProjectsList()

	def showProjectInformation(self,slist): 
		self.handleShowProject(self.lastSelectedProject)

	def handleShowProject(self,pname):
		self.lastProjectName = pname.strip()
		project = self.listOfProjects[pname]	
		retlist = {}
		k = 0
		for ucc in project: 
			try:
				fullname = str(ucc)
				xlines = os.stat(fullname)
				basename = os.path.basename(fullname)
				modelname,ext = os.path.splitext(basename)
				sz = showTime(xlines[-1]) + "(%dK)" % long(xlines[6] / 1024)
				retlist[k] = (modelname,fullname,sz)
				k = k + 1
			except:
				pass 
		self.text_ctrl_projectnotes.SetValue(self.fileNotes.get(self.lastProjectName,''))
		self.text_label_notekey.SetLabel(pname)
		
		self.treelist_ctrl_projectfiles.DeleteAllItems()
		self.treelist_projectroot = self.treelist_ctrl_projectfiles.AddRoot(pname)
		self.treelist_projectnames = {}
		skeys = retlist.keys()
		skeys.sort()
		for mykey in skeys:
			nm, fullname, sz = retlist[mykey]
			child = self.treelist_ctrl_projectfiles.AppendItem(self.treelist_projectroot, nm)
			self.treelist_ctrl_projectfiles.SetItemText(child,fullname,1)
			self.treelist_ctrl_projectfiles.SetItemText(child,sz,2)
			self.treelist_projectnames[nm]  = child
		self.treelist_ctrl_projectfiles.Expand(self.treelist_projectroot)
	



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
		#fd.write('NUMNODES:%d\n' % self.numNodes)
		#fd.write('USENODE:%s\n' % self.use_node)
		#fd.write('EXTRACT:%d\n' % self.doExtract)
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
					#if token == 'READRATES': self.processTimeInfo.set(int(value))
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
					#if token == 'NUMNODES': self.numNodes = int(value)
					#if token == 'EXTRACT': self.doExtract = int(value)
					#if token == 'USENODE': self.use_node = value
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

	def OnSize(self, event):
		wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
		event.Skip()

	def OnQuit(self, event):
		self.writeGUIstate(os.getcwd())
		r = self.writeProjectsFile()
		if r > -1: self.writeNotesXMLfile()
		sendMessage('PowersGUI','QUIT','pwxModelManager')
		self.Destroy()

	def OnAbout(self, event):
		msg = "Kamran Husain" + wx.VERSION_STRING + "!!"
		dlg = wx.MessageDialog(self, msg, "FoldPanelBar Extended Demo",
							   wx.OK | wx.ICON_INFORMATION)
		dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False, "Verdana"))
		dlg.ShowModal()
		dlg.Destroy()


	def OnToggleWindow(self, event):
		self._leftWindow1.Show(not self._leftWindow1.IsShown())
		# Leaves bits of itself behind sometimes
		wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
		self.remainingSpace.Refresh()
		event.Skip()
		

	def OnFoldPanelBarDrag(self, event):
		if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
			return
		if event.GetId() == self.ID_WINDOW_LEFT1:
			self._leftWindow1.SetDefaultSize(wx.Size(event.GetDragRect().width, 1000))
		# Leaves bits of itself behind sometimes
		wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
		self.remainingSpace.Refresh()
		event.Skip()
	   

	def ReCreateFoldPanel(self, fpb_flags):
		"""
		Call this ONLY ONCE!!!!
		"""
		self._leftWindow1.DestroyChildren()
		self._pnl = fpb.FoldPanelBar(self._leftWindow1, -1, wx.DefaultPosition,
									 wx.Size(-1,-1), fpb.FPB_DEFAULT_STYLE, fpb_flags)
		Images = wx.ImageList(16,16)
		Images.Add(GetExpandedIconBitmap())
		Images.Add(GetCollapsedIconBitmap())
		item = self._pnl.AddFoldPanel("Project Panel", collapsed=False,
									  foldIcons=Images)
		self._mgrProjects = mmgr_ProjectsPanel(item,-1)
		self._mgrProjects.setMaster(self)
		
		self._pnl.AddFoldPanelWindow(item, self._mgrProjects, fpb.FPB_ALIGN_WIDTH, 0, 20) 
		self._pnl.AddFoldPanelSeparator(item)
		item = self._pnl.AddFoldPanel("Commands", False, foldIcons=Images)
		self._mgrCommands = mmgr_CommandsPanel(item,-1)
		self._pnl.AddFoldPanelWindow(item, self._mgrCommands, fpb.FPB_ALIGN_WIDTH, 0, 20) 
		self._pnl.AddFoldPanelSeparator(item)
		cs = fpb.CaptionBarStyle()
		cs.SetCaptionStyle(fpb.CAPTIONBAR_RECTANGLE)
		item = self._pnl.AddFoldPanel("Notes", False, foldIcons=Images)
		self.text_ctrl_projectnotes = wx.TextCtrl(item, -1, "", style=wx.TE_MULTILINE | wx.TE_DONTWRAP)
		self.text_label_notekey = wx.StaticText(item,-1,'NOTE')
		self._pnl.AddFoldPanelWindow(item,self.text_label_notekey, fpb.FPB_ALIGN_WIDTH, 5, 20) 
		self._pnl.AddFoldPanelWindow(item, self.text_ctrl_projectnotes, 
									 fpb.FPB_ALIGN_WIDTH, fpb.FPB_DEFAULT_SPACING, 10)
		button2 = wx.Button(item, wx.NewId(), "Save Note")		
		self._pnl.AddFoldPanelWindow(item, button2) 
		button2.Bind(wx.EVT_BUTTON, self.cb_saveNote)
		#button2 = wx.Button(item, wx.NewId(), "Collapse All")		
		#self._pnl.AddFoldPanelWindow(item, button2) 
		#button2.Bind(wx.EVT_BUTTON, self.OnCollapseMe)
		self._leftWindow1.SizeWindows()

	def OnCollapseMe(self, event):
		for i in range(0, self._pnl.GetCount()):
			item = self._pnl.GetFoldPanel(i)
			self._pnl.Collapse(item)


	def makeMenus(self):
		self._mymenu = wx.MenuBar()
		self.SetMenuBar(self._mymenu)
		wxglade_tmp_menu = wx.Menu()
		self.mi_loadXML = wxglade_tmp_menu.Append(wx.NewId(), "Load XML ", "", wx.ITEM_NORMAL)
		self.mi_importXML = wxglade_tmp_menu.Append(wx.NewId(), "Import XML ", "", wx.ITEM_NORMAL)
		self.mi_saveas = wxglade_tmp_menu.Append(wx.NewId(), "Save as another XML", "", wx.ITEM_NORMAL)
		self.mi_savecopy = wxglade_tmp_menu.Append(wx.NewId(), "Save Copy of Projects", "", wx.ITEM_NORMAL)
		self.mi_quit = wxglade_tmp_menu.Append(wx.NewId(), "Quit", "", wx.ITEM_NORMAL)
		self._mymenu.Append(wxglade_tmp_menu, "File")
		wxglade_tmp_menu = wx.Menu()
		self.mi_jobmonitor = wxglade_tmp_menu.Append(wx.NewId(), "Job Monitor", "", wx.ITEM_NORMAL)
		self.mi_editor = wxglade_tmp_menu.Append(wx.NewId(), "Editor", "", wx.ITEM_NORMAL)
		self._mymenu.Append(wxglade_tmp_menu, "Options")
		wxglade_tmp_menu = wx.Menu()
		self.mi_simreport400 = wxglade_tmp_menu.Append(wx.NewId(), "Simreport 400", "", wx.ITEM_NORMAL)
		self.mi_simview400 = wxglade_tmp_menu.Append(wx.NewId(), "Simview 400", "", wx.ITEM_NORMAL)
		self.mi_simstat400 = wxglade_tmp_menu.Append(wx.NewId(), "Simstat400", "", wx.ITEM_NORMAL)
		self.mi_simextract400 = wxglade_tmp_menu.Append(wx.NewId(), "Extract 400", "", wx.ITEM_NORMAL)
		self.mi_simsurvey400 = wxglade_tmp_menu.Append(wx.NewId(), "SurveyPlot 400", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.AppendSeparator()
		self.mi_simreport300 = wxglade_tmp_menu.Append(wx.NewId(), "Simreport 300", "", wx.ITEM_NORMAL)
		#self.mi_simview300 = wxglade_tmp_menu.Append(wx.NewId(), "Simview 300", "", wx.ITEM_NORMAL)
		self.mi_simstat300 = wxglade_tmp_menu.Append(wx.NewId(), "Simstat300", "", wx.ITEM_NORMAL)
		self.mi_simextract300 = wxglade_tmp_menu.Append(wx.NewId(), "Extract 300", "", wx.ITEM_NORMAL)
		self.mi_simsurvey300 = wxglade_tmp_menu.Append(wx.NewId(), "SurveyPlot 300", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.AppendSeparator()
		self.mi_tecplot_manifa = wxglade_tmp_menu.Append(wx.NewId(), "TECPLOT MANIFA", "", wx.ITEM_NORMAL)
		self.mi_geolog_manifa = wxglade_tmp_menu.Append(wx.NewId(), "GEOLOG MANIFA", "", wx.ITEM_NORMAL)
		self.mi_gocad_manifa = wxglade_tmp_menu.Append(wx.NewId(), "GOCAD MANIFA", "", wx.ITEM_NORMAL)
		self.mi_tecplot_5 = wxglade_tmp_menu.Append(wx.NewId(), "TECPLOT 5", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.Append(wx.NewId(), "TECPLOT 5", "", wx.ITEM_NORMAL)
		self._mymenu.Append(wxglade_tmp_menu, "Tools")
		wxglade_tmp_menu = wx.Menu(style=wx.MENU_TEAROFF)
		self.mi_eclbrowser = wxglade_tmp_menu.Append(wx.NewId(), "ECL browser", "", wx.ITEM_NORMAL)
		self.mi_jobmonitor2 = wxglade_tmp_menu.Append(wx.NewId(), "Job Monitor", "", wx.ITEM_NORMAL)
		self.mi_eclextractor = wxglade_tmp_menu.Append(wx.NewId(), "ECL extractor", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.AppendSeparator()
		self.mi_psimreport = wxglade_tmp_menu.Append(wx.NewId(), "New Simreport", "", wx.ITEM_NORMAL)
		self.mi_pvtviewer = wxglade_tmp_menu.Append(wx.NewId(), "PVT or SAT Viewer", "", wx.ITEM_NORMAL)
		self.mi_flowtable = wxglade_tmp_menu.Append(wx.NewId(), "Flow Table Viewer", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.AppendSeparator()
		self.mi_runscite = wxglade_tmp_menu.Append(wx.NewId(), "Scite Text", "", wx.ITEM_NORMAL)
		self.mi_eclslicer = wxglade_tmp_menu.Append(wx.NewId(), "ECL slicer", "", wx.ITEM_NORMAL)
		self.mi_rs3d = wxglade_tmp_menu.Append(wx.NewId(), "RS3D", "", wx.ITEM_NORMAL)
		self.mi_xyplotter = wxglade_tmp_menu.Append(wx.NewId(), "XY Plotter", "", wx.ITEM_NORMAL)
		self._mymenu.Append(wxglade_tmp_menu, "Power Tools")

		self.__set_properties()
		self.__do_layout()

		self.Bind( wx.EVT_MENU, self.mf_loadprojectxml, self.mi_loadXML)
		self.Bind( wx.EVT_MENU, self.mf_import_xmlfiles, self.mi_importXML)
		self.Bind( wx.EVT_MENU, self.mf_saveasprojectxmlfile, self.mi_saveas)
		self.Bind( wx.EVT_MENU, self.mf_savecopyofprojects, self.mi_savecopy)
		self.Bind( wx.EVT_MENU, self.mf_quit, self.mi_quit)
		self.Bind( wx.EVT_MENU, self.mf_selectEditor, self.mi_editor)
		self.Bind( wx.EVT_MENU, self.mf_simreport400, self.mi_simreport400)
		self.Bind( wx.EVT_MENU, self.mf_simview400, self.mi_simview400)
		self.Bind( wx.EVT_MENU, self.mf_simstat400, self.mi_simstat400)
		self.Bind( wx.EVT_MENU, self.mf_extract400, self.mi_simextract400)
		self.Bind( wx.EVT_MENU, self.mf_surveyplot400, self.mi_simsurvey400)
		self.Bind( wx.EVT_MENU, self.mf_simreport300, self.mi_simreport300)
		#self.Bind( wx.EVT_MENU, self.mf_simview300, self.mi_simview300)
		self.Bind( wx.EVT_MENU, self.mf_simstat300, self.mi_simstat300)
		self.Bind( wx.EVT_MENU, self.mf_extract300, self.mi_simextract300)
		self.Bind( wx.EVT_MENU, self.mf_surveyplot300, self.mi_simsurvey300)
		self.Bind( wx.EVT_MENU, self.mf_tecplot_manifa, self.mi_tecplot_manifa)
		self.Bind( wx.EVT_MENU, self.mf_geologmanifa, self.mi_geolog_manifa)
		self.Bind( wx.EVT_MENU, self.mf_gocadmanifa, self.mi_gocad_manifa)
		self.Bind( wx.EVT_MENU, self.mf_tecplot5, self.mi_tecplot_5)
		self.Bind( wx.EVT_MENU, self.mf_eclbrowser, self.mi_eclbrowser)
		self.Bind( wx.EVT_MENU, self.mf_eclextractor, self.mi_eclextractor)
		self.Bind( wx.EVT_MENU, self.mf_parallelsimreport, self.mi_psimreport)
		self.Bind( wx.EVT_MENU, self.mf_pvtviewer, self.mi_pvtviewer)
		self.Bind( wx.EVT_MENU, self.mf_flowtable, self.mi_flowtable)
		self.Bind( wx.EVT_MENU, self.mf_runscite, self.mi_runscite)
		self.Bind( wx.EVT_MENU, self.mf_eclslicer, self.mi_eclslicer)
		self.Bind( wx.EVT_MENU, self.mf_runrs3d, self.mi_rs3d)
		self.Bind( wx.EVT_MENU, self.mf_xyplotter, self.mi_xyplotter)
		self.Bind( wx.EVT_MENU, self.mf_jobmonitor, self.mi_jobmonitor)
		self.Bind( wx.EVT_MENU, self.mf_jobmonitor, self.mi_jobmonitor2)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: mmMenuBar.__set_properties
		pass
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: mmMenuBar.__do_layout
		pass
		# end wxGlade

	def mf_loadprojectxml(self, event): # wxGlade: mmMenuBar.<event_handler>
		print "Event handler `mf_loadprojectxml' not implemented!"
		event.Skip()

	def mf_import_xmlfiles(self, event): # wxGlade: mmMenuBar.<event_handler>
		r = self.writeProjectsFile()
		if r > -1: self.writeNotesXMLfile()

	def mf_saveasprojectxmlfile(self, event): # wxGlade: mmMenuBar.<event_handler>
		self.saveProjectXMLfile(self,saveas=1)

	def mf_savecopyofprojects(self, event): # wxGlade: mmMenuBar.<event_handler>
		self.saveProjectXMLfile(self,saveas=0)

	def mf_quit(self, event): # wxGlade: mmMenuBar.<event_handler>
		self.Destroy()

	def mf_selectEditor(self, event): # wxGlade: mmMenuBar.<event_handler>
		print "Event handler `mf_selectEditor' not implemented!"
		event.Skip()

	def mf_simreport400(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'simreport400' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_simview400(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'simview400' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_simstat400(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'simstat302' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_extract400(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'EclxGui400' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_surveyplot400(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'run_SP400' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_simreport300(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'simreport300' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_simview300(self, event): # wxGlade: mmMenuBar.<event_handler>
		print "Event handler `mf_simview300' not implemented!"
		event.Skip()

	def mf_simstat300(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'simstat302' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_extract300(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'EclxGui' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_surveyplot300(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + 'run_SP400' 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_tecplot_manifa(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + "tec61F1706" 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_geologmanifa(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + "geolog_mnif" 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_gocadmanifa(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + "gocad213" 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_tecplot5(self, event): # wxGlade: mmMenuBar.<event_handler>
		tcmd = self.toolDir + "run_tecplot5" 
		if os.fork() == 0: os.execv(tcmd,['%s' % tcmd ])

	def mf_eclbrowser(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runECLbrowser.ksh")

	def mf_jobmonitor(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runMonitor.ksh")

	def mf_eclextractor(self, event): # wxGlade: mmMenuBar.<event_handler>
		dlg = wx.FileDialog(self,"Open SMSPEC file for extraction", defaultDir='/red/simdata/EXT400/' + os.getenv('USER'),
			style=wx.OPEN | wx.CHANGE_DIR,
			defaultFile = "*.smspec", 
			wildcard = "SMSPEC (*.smspec)|*.inc|SMSPEC |*.SMSPEC|All Files |*.*")
		if dlg.ShowModal() == wx.ID_OK: 
			ifile = dlg.GetPath()
			dlg.Destroy()
			bname, ext = os.path.splitext(ifile)
			print "Extract with ", bname, ext
			if os.fork() == 0: 
				os.execl('/bin/bash',"/bin/bash", \
						"/red/ssd/appl/khusain/64bit/srcs/extractWithPython.ksh", \
						bname, ext, "/red/simdata/EXT400/" + os.getenv('USER'))
		dlg.Destroy()

	def mf_parallelsimreport(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runSimRpt2.ksh")

	def mf_pvtviewer(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runPVT.ksh")

	def mf_flowtable(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runFlow.ksh")

	def mf_runscite(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/red/ssd/appl/khusain/64bit/srcs/scite/bin/SciTE',"SciTE")

	def mf_eclslicer(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runRipper.ksh")

	def mf_runrs3d(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/runRS3D.ksh")

	def mf_xyplotter(self, event): # wxGlade: mmMenuBar.<event_handler>
		if os.fork() == 0: 
			os.execl('/bin/bash',"/bin/bash", "/red/ssd/appl/khusain/64bit/srcs/runXYplotter.ksh")

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
		
	def showModelFileDependancies(self):
		"""
		This is the work horse routine for listing files from within model files.
		"""
		fullmodelfilename = self.lastSelectedInputFileName 
		workpath,projectpath = deriveWorkpaths(fullmodelfilename)
		sector_datapath = None
		f = projectpath.find('/sector_data')
		if f>=0: sector_datapath = projectpath.replace('/sector_data','')
		try:
			xlines = open(fullmodelfilename,'r').readlines()
		except:	
			self.showwarning("Oops!"," I cannot open the file you have selected " + fullmodelfilename)
			return
		self.text_ctrl_projectnotes.SetValue(self.fileNotes.get(fullmodelfilename,''))

		self.listOfIncludes = []    # For model file 
		self.listOfOutputs  = []    # from output directory
		self.listOfRestart  = []    # from the simdata directory

		bindirpath = None                                         # Not set by user
		modeldirname = os.path.dirname(fullmodelfilename)         # for data file
		modeldirroot = modeldirname.replace('/data/','')          # For powers
		justfilename = os.path.basename(fullmodelfilename)        # name + ext
		modelbase,ext = os.path.splitext(justfilename)
		self.listOfIncludes.append(("MODEL_FILE", fullmodelfilename, " - "))
		intmodelfilename = fullmodelfilename.replace('.model','.int')
		self.listOfIncludes.append(("INT_FILE",intmodelfilename,"-"))

		#--------------------------------- Create output file list ---
		self.snapshotLines = [] 
		self.snapshotRequired = {}
		for ln in xlines:	             # for lines in the model file.
			ln = ln.strip()              # Remove spaces 
			if len(ln) < 1: continue     # Ignore small lines
			if ln[0] in ['/','!','#']: continue    # Ignore comments
			for snp in self.snapshotKeywords:
				f = ln.find(snp)                   # Keep line with snapshot information
				if f >= 0: self.snapshotLines.append(ln)
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
					#ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
					ostr = (inc,inc_name, showTime(xlines[-1]) + "(%dK)" % fsize)
					self.listOfOutputs.append(ostr)

			# -------------- IF BINARY_DATA_DIRECTORY found, use it
			f = ln.find('BINARY_DATA_DIRECTORY')
			self.binaryDataPathFound = 0
			if f >= 0: 
				iname = ln.split()[1]
				bindirpath = iname.replace("'",'') + '/' + modelbase
				self.binaryDataPathFound = 1

			# -------------------------------------------------------------------------------
			# Now check if there is an output directory (../output) and list 
			# its contents completely. 
			# -------------------------------------------------------------------------------
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
						#ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
						ostr = (inc,inc_name, showTime(xlines[-1]) + "(%dK)" % fsize)
						self.listOfIncludes.append(ostr)
					except:
						pass
					#print "----> sector_data_path = ", sector_datapath
					#print "----> projectpath = ", projectpath
					if sector_datapath == None: continue
					inc_name = deriveIncludePath(iname,sector_datapath,projectpath)
					try:
						xlines = os.stat(inc_name)
						fsize  = xlines[6] / 1024
						#ostr = "%s: %s : " % (inc,inc_name) + showTime(xlines[-1]) + "(%dK)" % fsize
						ostr = (inc,inc_name, showTime(xlines[-1]) + "(%dK)" % fsize)
						if not ostr in self.listOfIncludes: self.listOfIncludes.append(ostr)
					except:
						continue

		########################################################################################
		# Now set the list of output files.
		#  If the binary directory path is set, then list the files in the bin dir path
		########################################################################################
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
					powersVersionString = items[-1].strip()
					break
		except:
			powersVersionString = 'Not run'

		self.listOfOutputs.append(("VERSION_INFO", tstr, powersVersionString))

		binrestartpath = []
		if bindirpath <> None:
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
					#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
					ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
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
					#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
					ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
					self.listOfOutputs.append(ostr)

		#
		try:
			inc = 'OUTPUT_FILE'
			fullname = projectpath + "/OUT_" + modelbase 
			print "fullname for OUT_", fullname
			xlines = os.stat(fullname);
			fsize  = xlines[6] / 1024
			#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
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
			#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
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
			#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
			ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
			self.listOfOutputs.append(ostr)

		#
		# Append any restart paths from this directory: /red/restart/USER/MODEL
		#
		for rrdir in ['/red/restart/','/red/restart1/','/red/restart2/','/red/restart3/']:
			restartDir = rrdir + os.getenv('USER') + os.sep +  modelbase 
			inc = 'OUTPUT_FILE'
			try:
				rnames = os.listdir(restartDir)
				for rname in rnames: 
					fullname = restartDir + os.sep + rname
					xlines = os.stat(fullname)
					fsize  = xlines[6] / 1024
					#ostr = "%s: %s : " % (inc,fullname) + showTime(xlines[-1]) + "(%dK)" % fsize
					ostr = (inc,fullname, showTime(xlines[-1]) + "(%dK)" % fsize)
					self.listOfOutputs.append(ostr)
			except:
				continue
	
		#self.ds_outputFiles.SetData(self.listOfOutputs)
		#self.list_ctrl_outputFiles.SetItemCount(self.ds_outputFiles.GetCount())
		informationFilename = ''
		model_information   = modelbase + '.information'
		for k,i in enumerate(self.listOfOutputs):
			thisFile = str(i[1]).strip()
			f = thisFile.find(model_information)
			if f >= 0: 
				flen = len(thisFile) - f  
				if flen == len(model_information): 
					informationFilename = thisFile
					break

		#self.ds_inputFiles.SetData(self.listOfIncludes)
		#self.list_ctrl_inputFiles.SetItemCount(self.ds_inputFiles.GetCount())

		oslines = []
		if len(informationFilename)> 1:	
			try:
				ms = os.stat(informationFilename)
				self.informationText.clear()
				oslines = open(informationFilename).readlines()
			except:
				oslines = []
		if len(oslines) < 1: 
			for i in self.snapshotLines:
				ix = i.split()
				ix.insert(1,":")
				oslines.append("".join(ix))
		if self.binaryDataPathFound == 0: 
			self.snapshotLines.append('BINARY_DATA_DIRECTORY not found in model file.')
		snapshotText = "\n".join(oslines)
		self.text_ctrl_information.SetValue(snapshotText)

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
		except:
			print "There was an exception at the end of the extracted file listing."
			pass


		#self.ds_extractFiles.SetData(self.extractList)
		#self.list_ctrl_extractFiles.SetItemCount(self.ds_inputFiles.GetCount())
		#for w in [self.list_ctrl_inputFiles, self.list_ctrl_outputFiles, self.list_ctrl_extractFiles]:
		#	w.SetColumnWidth(0,120)
		#	w.SetColumnWidth(1,350)
		#	w.SetColumnWidth(2,200)

		projectchild = self.treelist_projectnames.get(modelbase,None)
		if projectchild == None:
			print "No child found", modelbase, self.treelist_projectnames.keys()
			return
		self.treelist_ctrl_projectfiles.DeleteChildren(projectchild)
		inputchild = self.treelist_ctrl_projectfiles.AppendItem(projectchild, 'INPUTS')
		outputchild = self.treelist_ctrl_projectfiles.AppendItem(projectchild, 'OUTPUTS')
		extractchild = self.treelist_ctrl_projectfiles.AppendItem(projectchild, 'EXTRACTS')

		for item in self.listOfIncludes:
			child = self.treelist_ctrl_projectfiles.AppendItem(inputchild, item[0])
			self.treelist_ctrl_projectfiles.SetItemText(child, item[1], 1)
			self.treelist_ctrl_projectfiles.SetItemText(child, item[2], 2)
		for item in self.listOfOutputs:
			child = self.treelist_ctrl_projectfiles.AppendItem(outputchild, item[0])
			self.treelist_ctrl_projectfiles.SetItemText(child, item[1], 1)
			self.treelist_ctrl_projectfiles.SetItemText(child, item[2], 2)
		for item in self.extractList:
			child = self.treelist_ctrl_projectfiles.AppendItem(extractchild, item[0])
			self.treelist_ctrl_projectfiles.SetItemText(child, item[1], 1)
			self.treelist_ctrl_projectfiles.SetItemText(child, item[2], 2)
		self.treelist_ctrl_projectfiles.Expand(child)


		########################################################################################
		# End of eventTableSelect function here.
		########################################################################################


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

	def cb_saveNote(self,event):
		notekey = self.text_label_notekey.GetLabel()
		notes   = self.text_ctrl_projectnotes.GetValue()
		self.fileNotes[notekey] = notes
		self.writeNotesXMLfile()

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

	def CreateMenuBar(self):
		FoldPanelBarTest_Quit = wx.NewId()
		FoldPanelBarTest_About = wx.NewId()
		FoldPanelBarTest_Horizontal = wx.NewId()
		FoldPanelBarTest_Vertical = wx.NewId()
		
		menuFile = wx.Menu()
		menuFile.Append(FoldPanelBarTest_Horizontal, "&Horizontal\tAlt-H")
		menuFile.Append(FoldPanelBarTest_Vertical, "&Vertical\tAlt-V")
		menuFile.AppendSeparator()
		menuFile.Append(FoldPanelBarTest_Quit, "E&xit\tAlt-X", "Quit This Program")

		helpMenu = wx.Menu()
		helpMenu.Append(FoldPanelBarTest_About, "&About...\tF1", "Show About Dialog")

		self.FoldPanelBarTest_Vertical = FoldPanelBarTest_Vertical
		self.FoldPanelBarTest_Horizontal = FoldPanelBarTest_Horizontal

		self.Bind(wx.EVT_MENU, self.OnQuit, id=FoldPanelBarTest_Quit)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=FoldPanelBarTest_About)
		self.Bind(wx.EVT_MENU, self.OnOrientation, id=FoldPanelBarTest_Horizontal)
		self.Bind(wx.EVT_MENU, self.OnOrientation, id=FoldPanelBarTest_Vertical)

		value = wx.MenuBar()
		value.Append(menuFile, "&File")
		value.Append(helpMenu, "&Help")

		return value


	def OnOrientation(self, event):
		self.CreateFoldBar(event.GetId() == self.FoldPanelBarTest_Vertical)


	def OnQuit(self, event):
		# True is to force the frame to close
		self.Close(True)


	def OnAbout(self, event):

		msg = "This is the about dialog of the FoldPanelBarTest application.\n\n" + \
			  "Welcome To wxPython " + wx.VERSION_STRING + "!!"
		dlg = wx.MessageDialog(self, msg, "About FoldPanelBarTest",
							   wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()


	def OnCollapseMe(self, event):

		item = self.pnl.GetFoldPanel(0)
		self.pnl.Collapse(item)

	def OnExpandMe(self, event):

		self.pnl.Expand(self.pnl.GetFoldPanel(0))
		self.pnl.Collapse(self.pnl.GetFoldPanel(1))


	
# ----------------------------------------------------------------------------
# NotCollapsed Implementation
# ----------------------------------------------------------------------------

		# end wxGlade

if __name__ == '__main__':
	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	frame_1 = pwxModelManager(None, -1, "")
	frame_1.readGUIstate()
	app.SetTopWindow(frame_1)
	frame_1.Show()
	app.MainLoop()

