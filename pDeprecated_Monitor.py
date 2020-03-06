
"""
Code for frame with monitor command. I require the root window.

Added code to filter in keywords on the input. I have to explain the use
for them to get the full functionality.

"""
from Tkinter import *
import Pmw
from tkMessageBox import showwarning 
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
from pObject import *
from copy import copy
import sys
import os


class pMonitorFrame(Frame): 
	def __init__(self,parent): 
		self.parent = parent
		self.m_listOfMonitorID = []                                        # Jobs being monitored.
		self.outputTextList  = []

		self.outputFilename  = ''
		self.modelFilename  = ''
		self.errorFilename  = ''
		self.commandFilename = ''
		self.errFilename = None
		self.timerID  = [None,None]
		self.timerInterval = [3000, 3000]
		self.timerBtn = [None,None]

		self.listOfNodes = ['@plcc','@plcd','@plce','@plcf','@plcg','@plci']
		x1 = []
		x2 = []
		for xstr in self.listOfNodes: 
			x1.append('qstat -a %s;' % xstr)
			x2.append('qstat -a %s -u $USER;' % xstr)
		self.allQstatString = "".join(x1)
		self.userQstatString = "".join(x2)

		self.doTailOnly = IntVar()
		self.doTailOnly.set(1)

		self.monitorFrame = Frame(self.parent)
		self.monitorFrame.pack(side=TOP,expand=1,fill=BOTH)

		self.monitorTopFrame = Pmw.PanedWidget(self.monitorFrame) #,orient=HORIZONTAL)
		self.monitorTopFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.monitorTopFrame.add('top',min=100,size=.4)
		self.monitorTopFrame.add('bottom',min=100)

		####################################################################################
		# The top frame where job monitor information is placed.
		####################################################################################
		self.jobCommandsForm = Frame(self.monitorTopFrame.pane('top'),relief=GROOVE)
		self.jobCommandsForm.pack(side=LEFT,fill=Y,expand=0)
		#
		# Add the commands to monitor jobs here. Vertically.
		# 
		a = lambda s=self,b='ALL': s.f_monitorqstat(b)
		self.getAllJobsBtn = Button(self.jobCommandsForm,text="All jobs",command=a)
		self.getAllJobsBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-f': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="Job Status",command=a)
		self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		self.txtStatusID = Pmw.ComboBox(self.jobCommandsForm,
					listbox_selectmode = SINGLE,
					label_text = 'Job ID',
					labelpos = 'w' ,
					scrolledlist_items = [],
					listbox_exportselection=0,
					dropdown=1) 
					#selectioncommand = self.m_selectJobID)

		#self.txtStatusID = Pmw.ComboBox(self.jobCommandsForm,
			#labelpos=W,label_text='ID')
		#self.txtStatusID.pack(side=TOP,fill=X,expand=0)

		#self.setListOfAllJobs() 
		a = lambda s=self,b='-u': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="My Jobs",command=a)
		self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-d': self.f_deleteJob()
		self.delQueBtn = Button(self.jobCommandsForm,text="Kill Job", command=a)
		self.delQueBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-q': s.f_monitorqstat(b)
		self.getAllJobsBtn = Button(self.jobCommandsForm,text="Quota",command=a)
		self.getAllJobsBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self: self.f_timerControl(0)
		self.timerBtn[0] = Button(self.jobCommandsForm,text="REFRESH",bg='blue',fg='white',command=a)
		self.timerBtn[0].pack(side=TOP,fill=X,expand=0)
	
		# On the top frames, this is  text frame for the output. 
	
		self.monitorListBox = Pmw.ScrolledListBox(self.monitorTopFrame.pane('top'),
					listbox_selectmode = SINGLE,
					items = [], 
					labelpos = N, 
					label_text = 'Status Tables',
					listbox_exportselection=0,
					selectioncommand = self.m_selectJobID)
		self.monitorListBox.pack(side=RIGHT,expand=1,fill=BOTH)
		self.monitorText = Pmw.ScrolledText(self.monitorTopFrame.pane('top'))
			#labelpos=N,label_text='From qstat',
			#usehullsize =1, hull_width=500, hull_height=20)
		self.monitorText.pack(side=RIGHT,expand=1,fill=BOTH)
		self.monitorListBox.pack_forget()


		####################################################################################
		# The bottom frame where job monitor information is placed.
		####################################################################################
		self.errorFileText = Pmw.ScrolledText(self.monitorTopFrame.pane('bottom'),labelpos=N,label_text='Output',
			usehullsize =1, hull_width=150, hull_height=20)
		self.errorFileText.pack(side=TOP,expand=1,fill=BOTH)

		####################################################################################
		# The bottom frame where commands pertaining to monitoring are placed.
		####################################################################################
		#
		# Create a button box here, with frame information
		#
		self.statBtnFrame = Frame(self.monitorFrame)
		self.statBtnFrame.pack(side=BOTTOM,fill=X,expand=0)


		####################################################################################
		# 
		####################################################################################

		self.yesTail = Radiobutton(self.statBtnFrame,text='Tail',value=1,variable=self.doTailOnly)
		self.noTail = Radiobutton(self.statBtnFrame,text='Full',value=0,variable=self.doTailOnly)
		self.yesTail.pack(side=LEFT)
		self.noTail.pack(side=LEFT)

		a = lambda s=self: self.f_timerControl(1)
		self.timerBtn[1] = Button(self.statBtnFrame,text="Auto",bg='blue',fg='white',command=a)
		self.timerBtn[1].pack(side=LEFT,expand=0)

		self.typeOfFiles =  ['error','script','output'] 

		self.filterText = Pmw.EntryField(self.statBtnFrame, labelpos=W,label_text='Filter')
		self.filterText.pack(side=LEFT,fill=X,expand=0)

		a = lambda s=self,b='full': self.f_readInTextFile(b) 
		self.readTextFileBtn = Button(self.statBtnFrame,text="Read File", command=a)
		self.readTextFileBtn.pack(side=LEFT,anchor=E)

		self.typeOfFileBox = Pmw.ComboBox(self.statBtnFrame,
					listbox_selectmode = SINGLE,
					scrolledlist_items = self.typeOfFiles,
					labelpos = W ,
					label_text = 'File:',
					listbox_exportselection=0,
					dropdown=1, 
					selectioncommand=self.f_outfileTypeSelection)
		self.typeOfFileBox.pack(side=LEFT,expand=1,fill=BOTH)

		self.modelText = Pmw.EntryField(self.statBtnFrame, labelpos=W,label_text='Data')
		self.modelText.pack(side=LEFT,fill=X,expand=0)

		a = lambda s=self: self.f_startTECPlot()
		self.tecPlotBtn = Button(self.statBtnFrame,text="TECPLOT",command=a)
		self.tecPlotBtn.pack(side=LEFT,fill=X,expand=0)

	def f_startTECPlot(self): 
		self.errorFileText.settext("I will start  for all warnings here ... ")
		pid = os.fork()
		print "out of fork", pid
		if pid > 0: 
			#os.execv(os.P_NOWAIT,'/peasapps/ssd/test_lnx/scripts/Linux/rs60Load')
			#os.execv('/usr/bin/vim',[''])
			os.execv('/peasapps/ssd/test_lnx/scripts/Linux/rs60Load',[''])


	#def f_showWarnings(self,how):
		#if not how in  [ '-e','-w' ]: return
		#if len(self.errFilename) < 1: return
		#self.errorFileText.clear()
		#if len(self.errFilename) < 0: 
			#if how == '-w': self.errorFileText.settext("I will show text for all warnings from an output file here ... ")
			#if how == '-e': self.errorFileText.settext("I will show text for all errors from an output file here ... ")
			#return
		#xlines = open(self.errFilename).readlines()
		#if how == '-w': xout = [x for x in xlines if x.find('arning') > -1 ] 
		#if how == '-e': xout = [x for x in xlines if x.find('rror') > -1 ] 
		#self.errorFileText.settext("".join(xout))

	def f_deleteJob(self):
		x = self.txtStatusID.get() 
		if len(x) < 1: return
		useCommand = 'qdel ' +  x
		id = os.popen(useCommand)
		xstr = id.readlines()
		id.close()
		self.f_monitorqstat('ALL')

	def f_deleteJobViaDlg(self):
		self.deleteDialog = Pmw.ComboBoxDialog(self.parent,title="Delete Job", 
			buttons=('OK','CANCEL'), defaultbutton='OK', 
			combobox_labelpos=N,label_text='Which one?',
			scrolledlist_items=self.m_listOfMonitorID)
		self.deleteDialog.tkraise(); 
		result = self.deleteDialog.activate()
		useCommand = 'qdel ' +  self.deleteDialog.get()
		id = os.popen(useCommand)
		xstr = id.readlines()
		id.close()
		self.f_monitorqstat('ALL')

	# I could use an array for this.
	# Timer control for the top frame. ..
	#
	def f_timerControl(self,ndx):
		if self.timerID[ndx]   == None:
			self.timerInterval[ndx] = 2000
			self.timerID[ndx] = self.parent.after(self.timerInterval[ndx],self.timerEvent,ndx)
			thisBtn = self.timerBtn[ndx]
			thisBtn['text'] = 'STOP'
			thisBtn['bg'] = 'red'
		else:
			self.timerInterval[ndx] = 0
			thisBtn = self.timerBtn[ndx]
			thisBtn['text'] = 'REFRESH'
			thisBtn['bg'] = 'blue'
			self.parent.after_cancel(self.timerID[ndx])
			self.timerID[ndx] = None

	def timerEvent(self,ndx):
		if self.timerInterval[ndx] <= 0: 
			if self.timerID[ndx] <> None: self.parent.after_cancel(self.timerID[ndx])
			self.timerID[ndx] = None
			thisBtn = self.timerBtn[ndx]
			thisBtn['text'] = 'REFRESH'
			thisBtn['bg'] = 'blue'
			return 
		if ndx == 0: self.f_monitorqstat('ALL')
		if ndx == 1: self.f_showErrorFileContents()
		self.timerID[ndx] = self.parent.after(self.timerInterval[ndx],self.timerEvent,ndx)

	def f_outfileTypeSelection(self,how): 
		print how
		listbox = self.typeOfFileBox.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if len(sel) == 0: return
		ndx = int(sel[0])
		word = self.typeOfFiles[ndx]
		self.f_monitorTextFile(word)

	def f_monitorTextFile(self,b): 
		"""
		Calls sima monitors status command and displays the results in a window.
		"""
		self.errorFileText.clear()
		if b == 'error' : self.errFilename = self.modelFilename.replace('.error','.err')
		if b == 'output': self.errFilename = self.outputFilename
		if b == 'script': self.errFilename = self.commandFilename
		if len(self.errFilename) < 1: 
			self.errorFileText.settext('I need a way of determining the output filename from the job...' )
			ifile = askopenfilename(filetypes=[("output","*.txt"),  ("All Files","*")])
			if ifile:
				self.errFilename = ifile
				if b == 'error' : self.errorFilename = ifile
				if b == 'output': self.outputFilename = ifile
				if b == 'script': self.commandFilename = ifile
				self.f_showErrorFileContents()
			return 
		
		self.f_showErrorFileContents()
		self.errorFileText.yview_moveto(1.0)

	def f_showErrorFileContents(self):
		doTail = self.doTailOnly.get()  
		ftxt = self.filterText.get()
		ftxt = ftxt.strip()
		if len(ftxt) < 1:  
			if doTail == 1:
				self.errorFileText.settext(self.readTail(self.errFilename))
			else:
			 	self.errorFileText.importfile(self.errFilename)
		else: 
			print "Using filter", ftxt, " doTail ", doTail, " on ", self.errFilename
			if doTail == 1:
				xlines = self.readTail(self.errFilename,asList=1) 
			else:
				xlines = open(self.errFilename).readlines()
			xout = [ x for x in xlines if x.find(ftxt) >= 0 ] 
			print "%d line from %d\n" % (len(xout), len(xlines))
			self.errorFileText.settext("".join(xout))


	def f_readInTextFile(self,b): 
		ifile = askopenfilename(filetypes=[("output","*.txt"),  ("All Files","*")])
		if ifile: 
			self.errFilename = ifile
			self.f_showErrorFileContents()
			

	def f_monitorqstat(self,how='ALL'):
		"""
		Calls sima monitors status command and displays the results in a window.
		"""

		if how == '-q': useCommand = '/red/ssd/appl/powers/bin/myquota'
		if how == '-f': 
			x = self.txtStatusID.get() 
			if len(x) < 1: return
			useCommand = 'qstat -f ' + self.txtStatusID.get()
		if how == '-d': 
			x = self.txtStatusID.get() 
			if len(x) < 1: return
			useCommand = 'qdel ' + self.txtStatusID.get()
		if how == 'ALL': useCommand = self.allQstatString
		if how == '-u': useCommand = self.userQstatString

		self.outputTextList  = []
		id = os.popen(useCommand)
		xstr = id.readlines()
		id.close()

		if how in ['ALL', '-u']: 
			self.outputTextList  = map(string.strip,xstr)
			self.monitorListBox.setlist(self.outputTextList)
			self.monitorText.pack_forget()
			self.monitorListBox.pack(side=RIGHT,expand=1,fill=BOTH)
		else:
			self.outputTextList  = xstr
			self.monitorText.settext(''.join(xstr))
			self.monitorListBox.pack_forget()
			self.monitorText.pack(side=RIGHT,expand=1,fill=BOTH)
		self.setListOfAllJobs(xstr) 

	def m_selectJobID(self):
		"""
		"""
		if len(self.outputTextList) < 1:  return 
		listbox = self.monitorListBox.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()							  # The index 
		if len(sel) == 0: return
		ndx = int(sel[0])
		words = split(self.outputTextList[ndx])
		if len(words) < 1: return
		jobid = words[0]
		f=jobid[0] 
		d=jobid.find('.')
		if f in string.digits and d > 1: 
			self.txtStatusID.setentry(jobid)

	def setListOfAllJobs(self,istr=[]):
		if len(istr) < 1:
			useCommand = self.allQstatString
			id = os.popen(useCommand)
			xstr = id.readlines()
			id.close()
		else: 
			xstr = istr
		self.m_listOfMonitorID = []
		for ln in xstr:
			if len(ln) < 10: continue
			if not ln[0] in string.digits: continue
			#f = ln.find('.')
			items = ln.split()
			self.m_listOfMonitorID.append(items[0])
		self.txtStatusID.setlist(self.m_listOfMonitorID)

	def readTail(self,filename,asList=0):
		try:
			fd = open(filename,'rb')
			fd.seek(-2048,2)
			xlines = fd.readlines()
			fd.close()
			if asList == 1: 
				return xlines
			else: 
				return "".join(xlines)
		except:
			return "Cannot open %s\n" % filename

if __name__ == '__main__':
	root =Tk()
	root.option_add('*font',('courier',10,'bold'))
	root.title("Kamran Husain's own job monitoring extravaganza")
	f = pMonitorFrame(root)
	root.mainloop()
