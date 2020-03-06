
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
import re
from pSubmitJob import *

class pJobInfoFrame(Frame):
	def __init__(self,parent): 
		Frame.__init__(self,parent)
		self.pack(side=TOP,expand=YES,fill=BOTH)
		self.parent = parent
		self.m_listOfMonitorID = []   # Jobs being monitored.
		self.timerID       = None
		self.timerInterval = 3000
		self.timerBtn      = None 
		self.outputfilename = ''
		self.monitorObject  = None
		self.listOfNodes = ['@plcd','@plce','@plcf','@plcg','@plch', '@plci','@plcl','@plcm']
		x1 = []
		x2 = []
		for xstr in self.listOfNodes: 
			x1.append('qstat -a %s;' % xstr)
			x2.append('qstat -a %s -u $USER;' % xstr)
		self.allQstatString = "".join(x1)
		self.userQstatString = "".join(x2)
		self.serialString = "qstat -a @sima -u $USER | grep serial ; qstat -a @simc -u $USER | grep serial"
	 	self.monitorPageObject = None 
		self.jobid_pattern = r'^\d+\.'
		self.regex = re.compile(self.jobid_pattern)

		####################################################################################
		# The top frame where job monitor information is placed.
		####################################################################################
		self.jobCommandsForm = Frame(self,relief=GROOVE)
		self.jobCommandsForm.pack(side=LEFT,fill=Y,expand=0)
		####################################################################################
		# Add the commands to monitor jobs here. Vertically.
		####################################################################################
		a = lambda s=self,b='ALL': s.f_monitorqstat(b)
		self.getAllJobsBtn = Button(self.jobCommandsForm,text="All jobs",command=a)
		self.getAllJobsBtn.pack(side=TOP,fill=X,expand=0)


		a = lambda s=self,b='-J': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="Monitor",command=a)
		#self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		# Don't pack the invisible object below. I use it as a temporary place holder.
		self.lastJobID = ''
		self.txtStatusID = Pmw.ComboBox(self.jobCommandsForm,
					listbox_selectmode = SINGLE,
					label_text = 'Job ID',
					labelpos = 'w' ,
					scrolledlist_items = [],
					listbox_exportselection=0,
					dropdown=1) 
		#Don't pack it...
		#self.txtStatusID.pack(side=TOP,fill=X,expand=0)

		#self.setListOfAllJobs() 
		a = lambda s=self,b='-u': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="My Jobs",command=a)
		self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-f': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="Job Status",command=a)
		self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-s': s.f_monitorqstat(b)
		self.getFullStatBtn = Button(self.jobCommandsForm,text="Serial",command=a)
		self.getFullStatBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-d': self.f_deleteJob()
		self.delQueBtn = Button(self.jobCommandsForm,text="Kill Job", command=a)
		self.delQueBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self,b='-q': s.f_monitorqstat(b)
		self.getAllJobsBtn = Button(self.jobCommandsForm,text="Quota",command=a)
		self.getAllJobsBtn.pack(side=TOP,fill=X,expand=0)

		a = lambda s=self: self.f_timerControl()
		self.timerBtn = Button(self.jobCommandsForm,text="START\nTimer",bg='blue',fg='white',command=a)
		self.timerBtn.pack(side=TOP,fill=X,expand=0)
	
		# On the top frames, this is  text frame for the output. 

		self.jobInfoListFrame= Frame(self)
		self.jobInfoListFrame.pack(side=RIGHT,expand=1,fill=BOTH)
	
		#a = lambda s=self,b='-J': s.f_monitorqstat(b)
		a = lambda s=self,b='-J': s.dblClickHandler(b)
		self.monitorListBox = Pmw.ScrolledListBox(self.jobInfoListFrame,
					listbox_selectmode = SINGLE,
					items = [], 
					labelpos = N, 
					label_text = 'Status Tables',
					listbox_exportselection=0,
					#dblclickcommand  = a, 
					
					selectioncommand = self.m_selectJobID)
		self.monitorListBox.pack(side=RIGHT,expand=1,fill=BOTH)
		self.monitorText = Pmw.ScrolledText(self.jobInfoListFrame)
		self.monitorText.pack(side=RIGHT,expand=1,fill=BOTH)
		self.monitorListBox.pack_forget()

	def f_deleteJob(self):
		#x = self.txtStatusID.get() 
		x = self.lastJobID
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


	def f_timerControl(self):
		if self.timerID   == None:
			self.timerInterval = 3000
			self.timerID = self.parent.after(self.timerInterval,self.timerEvent)
			thisBtn = self.timerBtn
			thisBtn['text'] = 'STOP\nTimer'
			thisBtn['bg'] = 'red'
		else:
			self.timerInterval = 0
			thisBtn = self.timerBtn
			thisBtn['text'] = 'START\nTimer'
			thisBtn['bg'] = 'blue'
			self.parent.after_cancel(self.timerID)
			self.timerID = None

	def timerEvent(self):
		if self.timerInterval <= 0: 
			if self.timerID <> None: self.parent.after_cancel(self.timerID)
			self.timerID = None
			thisBtn = self.timerBtn
			thisBtn['text'] = 'START\nTimer'
			thisBtn['bg'] = 'blue'
			return 
		self.f_monitorqstat('ALL')
		self.timerID = self.parent.after(self.timerInterval,self.timerEvent)

	def dblClickHandler(self,parm):
		self.m_selectJobID()       # Get the farging job id from selection 
		self.f_monitorqstat(parm)
		
	def f_monitorqstat(self,how='ALL'):
		"""
		Calls simc monitors status command and displays the results in a window.
		"""
		if how == '-q': useCommand = '/red/ssd/appl/powers/bin/myquota'
		if how in ['-J', '-f']: 
			x = self.lastJobID
			if len(x) < 1: return
			useCommand = 'qstat -f ' + x
		if how == '-d': 
			#
			# Hmm. How do I know which job this is? 
			#
			self.m_selectJobID() 
			x = self.lastJobID
			if len(x) < 1: return
			print "I am killing ...", self.lastJobID
			useCommand = 'qdel ' + x
		if how == 'ALL': useCommand = self.allQstatString
		if how == '-u': useCommand = self.userQstatString
		if how == '-s': useCommand = self.serialString 

		self.outputTextList  = []
		id = os.popen(useCommand)
		xstr = id.readlines()
		id.close()

		if how in ['ALL', '-u','-s']: 
			self.outputTextList  = map(string.strip,xstr)
			self.monitorListBox.setlist(self.outputTextList)
			self.monitorText.pack_forget()
			self.monitorListBox.pack(side=RIGHT,expand=1,fill=BOTH)
		elif how in ['-J']:
			try:	
				bls = "".join(xstr)
				bls = bls.replace('\n',' ')
				fl = 'Output_Path ='
				fs = bls.find(fl) + len(fl)
				fe = bls.find('Priority =')
				xi = bls[fs:fe].strip()
				fc = xi.find(':') + 1
				self.outputfilename = xi[fc:]
				self.outputfilename = self.outputfilename.replace("\t",'')
				self.outputfilename = self.outputfilename.replace(" ",'')
				self.outputfilename = self.outputfilename
			except:
				self.outputfilename = ''
			#print "...monitor =[", self.outputfilename, ']'
			if len(self.outputfilename) > 0 and self.monitorObject <> None: 
				self.monitorObject.monitoredFilename = self.outputfilename.strip()
				self.monitorObject.f_showFileContents()
				if self.monitorPageObject <> None: 
					self.monitorPageObject.switchToMonitor()
		else:
			self.outputTextList  = xstr
			self.monitorText.settext(''.join(xstr))
			self.monitorListBox.pack_forget()
			self.monitorText.pack(side=RIGHT,expand=1,fill=BOTH)
		#self.setListOfAllJobs(xstr) 

	def setMonitorObject(self,obj):
		self.monitorObject = obj


	def m_selectJobID(self):
		"""
		Uses the list box component to select the jobid to monitor.
		"""
		listbox = self.monitorListBox.component('listbox')  # Get the list of items. 
		sel = listbox.curselection()					    # The index 
		if len(sel) == 0: return
		ndx = int(sel[0])
		allwords = self.monitorListBox.get()
		match = self.regex.match(allwords[ndx])
		if match: 
			self.lastJobID = allwords[ndx].split()[0]
		else:
			self.lastJobID = ''

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
			match = self.regex.match(ln)
			#if len(ln) < 10: continue
			#if not ln[0] in string.digits: continue
			if match:
				items = ln.split()
				self.m_listOfMonitorID.append(items[0])


class pMonitorFrame(Frame): 
	def __init__(self,parent): 
		Frame.__init__(self,parent)
		self.pack(expand=YES,fill=BOTH,side=TOP)
		self.parent = parent
		self.m_listOfMonitorID = []                                        # Jobs being monitored.
		self.outputTextList  = []

		self.modelFilename   = ''
		self.commandFilename = ''
		self.monitoredFilename = None
		self.timerID  = None
		self.timerInterval = 3000
		self.timerBtn = None
		self.doTailOnly = IntVar()
		self.doTailOnly.set(1)
		####################################################################################
		# The bottom frame where job monitor information is placed.
		####################################################################################
		self.monitorFrame = Frame(self)
		self.monitorFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.errorFileText = Pmw.ScrolledText(self.monitorFrame,labelpos=N,label_text='  ',
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

		a = lambda s=self: self.f_timerControl()
		self.timerBtn = Button(self.statBtnFrame,text="START\nTimer",bg='blue',fg='white',command=a)
		self.timerBtn.pack(side=LEFT,expand=0)

		a = lambda s=self: self.f_showFileContents()
		self.timerBtn = Button(self.statBtnFrame,text="Refresh",bg='blue',fg='white',command=a)
		self.timerBtn.pack(side=LEFT,expand=0)

		self.filterText = Pmw.EntryField(self.statBtnFrame, labelpos=W,label_text='Filter')
		self.filterText.pack(side=LEFT,fill=X,expand=0)

		a = lambda s=self,b='full': self.f_readInTextFile(b) 
		self.readTextFileBtn = Button(self.statBtnFrame,text="Show Here", command=a)
		self.readTextFileBtn.pack(side=LEFT,anchor=E)

		a = lambda s=self: self.f_startTailXterm()
		self.tailTextBth = Button(self.statBtnFrame,text="XTerm Tail", command=a)
		self.tailTextBth.pack(side=LEFT,anchor=E)

		self.modelText = Pmw.EntryField(self.statBtnFrame, labelpos=W,label_text='File:')
		self.modelText.pack(side=LEFT,fill=X,expand=1)


	def f_startTailXterm(self):
		ifile = askopenfilename(filetypes=[("All Files","*")])
		if ifile: 
			if os.fork()==0:
				os.execl("/usr/bin/xterm","xterm", "-title", ifile, "-e", '/usr/bin/tail', '-f', ifile)

	#def f_showWarnings(self,how):
		#if not how in  [ '-e','-w' ]: return
		#if len(self.monitoredFilename) < 1: return
		#self.errorFileText.clear()
		#if len(self.monitoredFilename) < 0: 
			#if how == '-w': self.errorFileText.settext("I will show text for all warnings from an output file here ... ")
			#if how == '-e': self.errorFileText.settext("I will show text for all errors from an output file here ... ")
			#return
		#xlines = open(self.monitoredFilename).readlines()
		#if how == '-w': xout = [x for x in xlines if x.find('arning') > -1 ] 
		#if how == '-e': xout = [x for x in xlines if x.find('rror') > -1 ] 
		#self.errorFileText.settext("".join(xout))


	def f_timerControl(self):
		if self.timerID   == None:
			self.timerInterval = 3000
			self.timerID = self.parent.after(self.timerInterval,self.timerEvent)
			thisBtn = self.timerBtn
			thisBtn['text'] = 'STOP\nTimer'
			thisBtn['bg'] = 'red'
		else:
			self.timerInterval = 0
			thisBtn = self.timerBtn
			thisBtn['text'] = 'START\nTimer'
			thisBtn['bg'] = 'blue'
			self.parent.after_cancel(self.timerID)
			self.timerID = None

	def timerEvent(self):
		if self.timerInterval <= 0: 
			if self.timerID <> None: self.parent.after_cancel(self.timerID)
			self.timerID = None
			thisBtn = self.timerBtn
			thisBtn['text'] = 'START\nTimer'
			thisBtn['bg'] = 'blue'
			return 
		self.f_showFileContents()
		self.errorFileText.yview_moveto(1.0)
		self.timerID = self.parent.after(self.timerInterval,self.timerEvent)

	def f_showFileContents(self):
		doTail = self.doTailOnly.get()   # If you have to do tail
		ftxt = self.filterText.get()     # If you have to filter
		ftxt = ftxt.strip()              # Get contents of filter
		if len(ftxt) < 1:                # No filter
			if doTail == 1:
				self.errorFileText.settext(self.readTail(self.monitoredFilename))
			else:
			 	self.errorFileText.importfile(self.monitoredFilename)
		else: 
			print "Using filter", ftxt, " doTail ", doTail, " on ", self.monitoredFilename
			if doTail == 1:
				xlines = self.readTail(self.monitoredFilename,asList=1) 
			else:
				xlines = open(self.monitoredFilename).readlines()
			xout = [ x for x in xlines if x.find(ftxt) >= 0 ] 
			print "%d line from %d\n" % (len(xout), len(xlines))
			self.errorFileText.settext("".join(xout))
		self.modelText.setentry(self.monitoredFilename)

	def f_readInTextFile(self,b): 
		ifile = askopenfilename(filetypes=[("All Files","*")])
		if ifile: 
			self.monitoredFilename = ifile
			self.f_showFileContents()
			self.modelText.setentry(self.monitoredFilename)
			
	def readTail(self,filename,asList=0):
		try:
			items = os.stat(filename)
			sz = int(items[6]) 
			if sz > 2048: sz = 2048
			sz *= -1
			fd = open(filename,'rb')
			fd.seek(sz,2)
			xlines = fd.readlines()
			fd.close()
			if asList == 1: 
				return xlines
			else: 
				return "".join(xlines)
		except:
			return "Cannot open [%s]\n" % filename


class pMonitorApplication(Frame):
	def __init__(self,master): 
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=BOTH)
		self.parent = master
		self.mpFrame = Pmw.PanedWidget(self.parent) #,orient=HORIZONTAL)
		self.mpFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.mpFrame.add('top')
		self.mpFrame.add('middle')
		self.mpFrame.add('bottom')
		self.submitObject  = makeSubmitForm(self.mpFrame.pane('top'))
		self.jobObject     = pJobInfoFrame(self.mpFrame.pane('middle'))
		self.monitorObject = pMonitorFrame(self.mpFrame.pane('bottom'))



if __name__ == '__main__':
	root =Tk()
	root.option_add('*font',('courier',10,'bold'))
	root.geometry("%dx%d+0+0" %(1024,640))
	root.title("Kamran's own job monitoring extravaganza")
	f = pJobInfoFrame(root)
	root.mainloop()

if __name__ == '__pain__':
	root =Tk()
	root.option_add('*font',('courier',10,'bold'))
	root.title("PGUI job monitoring extravaganza")
	f = pMonitorApplication(root)
	root.mainloop()
