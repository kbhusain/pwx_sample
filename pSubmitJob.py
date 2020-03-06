 
import sys, os
from Tkinter import *
import Pmw
from tkMessageBox import showwarning, askyesno, showerror
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
import copy
from pCalDlg import *
from pObject import *

class makeSubmitForm(Frame):
	def __init__(self,master,modelName=None,tellme=None,obj=None,nodes=32,usenode='test',doExtract=1,cancelbtn=0):
		Frame.__init__(self,master)
		self.pack(side=TOP,expand=YES,fill=BOTH,anchor='n')
		self.parent = master
		self.modelName = modelName 
		self.outputFilename = ''
		self.errorFilename  = ''
		self.tellMaster = tellme
		self.masterObj  = obj
		self.incomingCommand = None
		self.circleOfTrust = ['baddouma', 'husainkb', 'lincx', 'fazaaam', 'dialdiha', 'dossmn0f', 'nahdiua']
		uname = os.getenv('USER')
		self.trustedUser = True
		#if uname in self.circleOfTrust: self.trustedUser  = True
		#
		# Configuration parameters
		#
		self.numNodes = nodes                   # PARM_NUMNODES
		self.use_node = usenode
		self.defaultModelName = ''
		self.commandFilename = ''
		self.jclCommandHandler = None
		self.plccString = 'powers@plcpbs'
		self.plccAllowed = ['powers@plcpbs']  + [ 'parallel@plc'+ i for i in 'defghilm']

	####################################### START OF JOB STRING 
		self.jobString = """#!/bin/sh
#PBS -l nodes=PARM_NUMNODES,walltime=180:00:00
#PBS -N PARM_10MODEL
#PBS -o PARM_SETBINDIRPATH/PARM_10MODEL.out
#PBS -e PARM_SETBINDIRPATH/PARM_10MODEL.err
#TIMEDRUN
#PBS -S /bin/csh
#PBS -M PARM_USER@exchange.aramco.com.sa
#PBS -m ae 
##PBS -q powers@plcpbs
#PBS -q PARM_PLCWHERE

OUTPUTDIR=PARM_SETBINDIRPATH  

MODEL=PARM_MODEL
EX='/red/ssd/appl/powers/PARM_SYSTEM/powers_lnx'
if [ ! -d PARM_PATH ]
then 
mkdir PARM_PATH
fi 

if [ ! -d PARM_PATH/binary ]
then 
mkdir PARM_PATH/binary
fi 

if [ ! -d PARM_PATH/output ]
then 
mkdir PARM_PATH/output
fi 

if [ ! -d PARM_PATH/restart ]
then 
mkdir PARM_PATH/restart
fi 

ONLYIFBINDIRFOUND

if [ ! -d PARM_PATH/data ]
then 
mkdir PARM_PATH/data
fi 


cd    $OUTPUTDIR
touch ${MODEL}.output
mpirun.ch_gm -np PARM_DOUBLECPU -machinefile $PBS_NODEFILE $EX data/${MODEL}.model > ${MODEL}.output


"""

		self.linkToBinDir = "ln -s PARM_MODELPATH $OUTPUTDIR/PARM_SECTORDATA\n"

	####################################### START OF MYEXTRACT STRING 
	# bash /red/ssd/appl/khusain/parallelExtract.ksh PARM_SETBINDIRPATH/PARM_MODEL.smspec PARM_SETBINDIRPATH &
		self.myExtraction = """  
echo "#!/bin/bash" > PARM_MODEL.tu
echo "/red/ssd/appl/khusain/64bit/srcs/extractWithPython.ksh PARM_SETBINDIRPATH/PARM_MODEL .smspec /red/simdata/EXT400/${USER}" >> PARM_MODEL.tu
/bin/bash PARM_MODEL.tu
"""

		self.my32bitExtraction = """ 
echo "#!/bin/bash" > PARM_MODEL.tu
echo "rsh sima '/red/ssd/appl/khusain/parallelPOWERS.ksh PARM_SETBINDIRPATH/PARM_MODEL .smspec /red/simdata/EXT400/${USER}'" >> PARM_MODEL.tu
/bin/bash PARM_MODEL.tu
"""
	####################################### END OF MYEXTRACT STRING 

		self.myExtr2 = """
echo "PARM_P_EXT bash /red/ssd/appl/khusain/parallelExtract.ksh PARM_SETBINDIRPATH/PARM_MODEL.smspec /red/simdata/EXT400/${USER}" >> PARM_MODEL.EXT
echo "PARM_P_EXT bash /red/ssd/appl/khusain/parallelExtract.ksh PARM_SETBINDIRPATH/PARM_MODEL_mig.smspec /red/simdata/EXT400/${USER}" >> PARM_MODEL.EXT
echo "PARM_P_EXT bash /red/ssd/appl/khusain/parallelExtract.ksh PARM_SETBINDIRPATH/PARM_MODEL_mtb.smspec /red/simdata/EXT400/${USER}" >> PARM_MODEL.EXT
"""
	####################################### START OF ECL EXTRACT STRING 
		self.extractString=""" 
echo "#!/bin/sh" > PARM_MODEL.EXT
echo "#PBS -S /bin/csh" >> PARM_MODEL.EXT
echo "#PBS -N 'a"$PBS_JOBID"'" >> PARM_MODEL.EXT
echo "#PBS -l nodes=1,walltime=8:00:00" >> PARM_MODEL.EXT
echo "#PBS -q serial@simc" >> PARM_MODEL.EXT
echo "/peasapps/ssd/test_lnx/scripts/Linux/PARM_EXTRACTION PARM_MODEL POWERS PARM_SETBINDIRPATH PARM_MODEL" >> PARM_MODEL.EXT
qsub PARM_MODEL.EXT
rsh simc "mv PARM_COMMAND_SCRIPT  PARM_SETBINDIRPATH"
"""

	####################################### END OF JOB STRING 

		self.form1 = Frame(self) 
		self.form1.pack(side=TOP,fill=X,expand=1)

		self.form2 = Frame(self.form1)
		self.form2.pack(side=TOP,fill=X,expand=1)

		self.modelPathEntry = Pmw.EntryField(self.form2, labelpos=W,label_text='PATH', validate=None)
		self.modelPathEntry.pack(side=TOP,fill=X,expand=1)

		self.modelNameEntry = Pmw.EntryField(self.form2, labelpos=W,label_text='MODEL', validate=None)
		self.modelNameEntry.pack(side=LEFT,fill=X,expand=1)

		self.modelButton = Button(self.form2,text="...", command=self.getModel)
		self.modelButton.pack(side=RIGHT,expand =0)

		#self.numNodesEntry = Pmw.EntryField(self.form1,\
				#labelpos=W,label_text='No. Nodes', validate={'validator':'integer','minstrict':0},value=10)

		self.parametersForm = Frame(self.form1,relief='ridge',borderwidth=3)
		self.parametersForm.pack(side=TOP,expand=0,anchor='w')

		self.numNodesEntry = Pmw.Counter(self.parametersForm,
				labelpos=W,label_text='No. Nodes', 
				entry_width = 5, entryfield_value = self.numNodes, 
				entryfield_validate={'validator':'integer','min':1, 'max':128})
		self.numNodesEntry.pack(side=LEFT,expand=0)

		self.plccForm = Frame(self.form1,relief='ridge',borderwidth=3)
		self.plccForm.pack(side=TOP,expand=0,anchor='w')

		self.plccButton  = Pmw.RadioSelect(self.plccForm,labelpos=W,label_text='System:',frame_relief=RIDGE,
			command=self.selectedSimulator,frame_border=2, buttontype='radiobutton')
		self.plccButton.pack(side=LEFT,fill=X,expand=0)
		self.plccButton.add("prod")
		self.plccButton.add("test")
		self.plccButton.invoke(self.use_node)


		self.systemForm = Frame(self.plccForm,relief='ridge',borderwidth=3)
		self.systemForm.pack(side=TOP,expand=0,anchor='w')

		self.systemString = Pmw.ComboBox(self.systemForm,
					listbox_selectmode = SINGLE,
					label_text = 'Use PLC System ',
					labelpos = 'w' ,
					scrolledlist_items = self.plccAllowed,
					listbox_exportselection=0)
		self.systemString.pack(side=TOP,expand=1,anchor='w')
		self.systemString.setentry(self.plccString)

		self.extractionForm = Frame(self.form1,relief='ridge',borderwidth=3)
		self.extractionForm.pack(side=TOP,expand=1,anchor='w')
		self.doExtraction = IntVar() 
		self.doExtraction.set(doExtract)
		for txt,val in [('Dont Extract',0),('Extract 400',1),('Extract 300 (unsupported)',2),('64 bit extract',3)]:
			self.checkExtraction = Radiobutton(self.extractionForm,text=txt, anchor=W, variable=self.doExtraction,value=val)
			self.checkExtraction.pack(side=LEFT,expand=0)

		#self.checkExtraction = Checkbutton(self.btnsForm,text='Also Extract', anchor=W, variable=self.doExtraction)
		#self.checkExtraction.pack(side=LEFT,expand=0)


		self.timedForm = Frame(self.form1,relief='ridge',borderwidth=3)
		self.timedForm.pack(side=TOP,expand=1,anchor='w')

		self.dateForm = Frame(self.timedForm)
		self.dateForm.pack(side=TOP,expand=1,anchor='w')
		self.doTimedRun = IntVar()
		self.doTimedRun.set(0)
		self.runLaterBtn = Checkbutton(self.dateForm,text='Run at Time', anchor=W, variable=self.doTimedRun)
		self.runLaterBtn.pack(side=LEFT,expand=0)

		self.runAtDate = Pmw.EntryField(self.dateForm,labelpos='w',label_text='YYYY/MM/DD', 
			value=strftime('%Y/%m/%d',localtime(time())),
			validate={'validator':'date','format':'ymd'},
			)
		et = self.runAtDate.component('entry')['width']=10
		self.runAtDate.pack(side=LEFT,expand=0)

		self.calendarbtn = Button(self.dateForm,text="Calendar", command=self.showCalendar)
		self.calendarbtn.pack(side=LEFT,anchor=E)   # Set the command on the where and what!

		self.date_2_Form = Frame(self.timedForm)
		self.date_2_Form.pack(side=TOP,expand=1,anchor='w')

		self.runAtHour = Pmw.Counter(self.date_2_Form,labelpos='w',label_text='Hour', 
			entryfield_value=strftime('%k',localtime(time())),
			entryfield_validate={'validator':'integer', 'min': 0, 'max':23},
			)

		ef = self.runAtHour.component('entryfield')
		et = ef.component('entry')['width']=2
		self.runAtHour.pack(side=LEFT,expand=0)
		self.runAtMinute = Pmw.Counter(self.date_2_Form,labelpos='w',label_text='Minute', 
			entryfield_value=strftime('%M',localtime(time())),
			#entryfield_command=
			entryfield_validate={'validator':'integer', 'min': 0, 'max':59},
			)
		ef = self.runAtMinute.component('entryfield')
		et = ef.component('entry')['width']=2
		self.runAtMinute.pack(side=LEFT,expand=0)

		self.btnsForm = Frame(self.form1)
		self.btnsForm.pack(side=TOP,expand=0,anchor='e')

		self.writeButton = Button(self.btnsForm,text="Submit Job", command=self.runCommand)
		self.writeButton.pack(side=LEFT,anchor=E)   # Set the command on the where and what!

		self.showCmdBtn = Button(self.btnsForm,text="Show JCL", command=self.showCommand)
		self.showCmdBtn.pack(side=LEFT,anchor=E)   # Set the command on the where and what!

		self.saveParmsBtn = Button(self.btnsForm,text="Save Parms", command=self.writeStatusToDisk)
		self.saveParmsBtn.pack(side=LEFT,anchor=E)   # Set the command on the where and what!

		if cancelbtn == True:
			self.cancelButton = Button(self.btnsForm,text="Cancel", command=self.cancelBtn)
			self.cancelButton.pack(side=LEFT,anchor=E)   # Set the command on the where and what!

	def setDefaultModelFile(self,mstr):
		if mstr <> None:
			self.defaultModelName = mstr
			self.modelPathEntry.setentry(os.path.dirname(mstr))
			self.modelNameEntry.setentry(os.path.basename(mstr))

	def createCommandShell(self,cmd,dirName,modelname):
		usethis = modelname.replace('.model','')
		try:
			fname = dirName + os.sep + '%s.ksh' % usethis
			fd = open(fname,'w')
			fd.write(cmd)
			cmd = cmd.replace('PARM_COMMAND_SCRIPT',fname)    # IMPORTANT
			#fd.write("#LOOK \nmv " + fname + " $OUTPUTDIR\n")  # Move yourself to the output directory
			fd.close()
		except:		
			fname = os.getenv('HOME') + os.sep + 'powersdata' +  os.sep + '%s.ksh' % usethis
			fd = open(fname,'w')
			cmd = cmd.replace('PARM_COMMAND_SCRIPT',fname)    # IMPORTANT
			fd.write(cmd)
			#fd.write("#LOOK \nmv " + fname + " $OUTPUTDIR\n")  # Move yourself to the output directory
			fd.close()
		return fname

	
	def showCalendar(self):
		items = localtime()
		self.myCalendar  = makeMyCalendar(self.parent,self,items[0],items[1],items[2]) # y,m,d
		#if self.myCalendar.ok == 1: 

	def handleCalendar(self):
		xstr = '%4d/%02d/%02d' % (self.myCalendar.y,self.myCalendar.m,self.myCalendar.d)
		self.runAtDate.setentry(xstr)

	def writeStatusToDisk(self):
		"""
		Writes the status to disk for remembering key simulation parameters. 
		The file is $HOME/powersdata/manager.inf. 
		Caution: This file is used by a lot of other programs so be careful when modifying the 
		contents of the manager.inf file.
		"""
		managerfilename = os.getenv('HOME') + os.sep + 'powersdata' + os.sep + 'manager.inf'
		xlines = open(managerfilename,'r').readlines()
		olines = []
		parms = {}
		parms['NUMNODES'] =  self.numNodesEntry.get()
		parms['USENODE'] =  self.use_node
		parms['EXTRACT'] =  self.doExtraction.get()

		for xln in xlines: 
			f = xln.find('NUMNODES')
			if f >= 0:
				items = xln.split(':')
				xstr = 'NUMNODES:%s\n' % self.numNodesEntry.get()
				olines.append(xstr)
				continue
			f = xln.find('USENODE')
			if f >= 0:
				items = xln.split(':')
				xstr = 'USENODE:%s\n' % self.use_node
				olines.append(xstr)
				continue
			f = xln.find('EXTRACT')
			if f >= 0:
				items = xln.split(':')
				xstr = 'EXTRACT:%d\n' % self.doExtraction.get()
				olines.append(xstr)
				continue
			olines.append(xln)	
		fd = open(managerfilename,'w')
		for xln in olines: fd.write(xln)
		fd.close()

		if self.tellMaster <> None: self.tellMaster(self.masterObj,'PARMS',parms)

	def runJCLcommand(self):
		# KLUDGE
		cmd = self.incomingCommand
		if len(cmd) < 1: 
			showwarning('Caution','Attempted to submit the job for an invalid model')
			return 
		self.runPowersNow(cmd)
		return

	def runCommand(self,incoming=None):
		cmd = self.getCommandString()
		if len(cmd) < 1: 
			showwarning('Caution','Attempted to submit the job for an invalid model')
			return 
		self.runPowersNow(cmd)
		return

	def runBatchCommand(self,modelNames):
		x = self.tellMaster              # Preserve state
		self.tellMaster = None           # Forget about notifying master
		for name in modelNames:
			cmd = self.getCommandString(name)  # You have the command
			if len(self.outputFilename) > 0: 
				dirName = os.path.dirname(self.outputFilename)
			else:
				dirName = os.getenv('HOME') + '/powersdata/' 
			self.commandFilename = self.createCommandShell(cmd,dirName,os.path.basename(name))
			print "dirName = ", dirName, " and ", name, " and ", self.commandFilename
			os.system('qsub ' + self.commandFilename)
			self.writeStatusToDisk()
		self.tellMaster = x

	def runPowersNow(self,cmd,showDialog=True):
		#
		# Create a temprory file, write contents of cmd to the file 
		#

		# self.kornShellFileName = '/red/restart/' + os.getenv('USER') + os.sep + modelName + ".ksh"
		self.commandFilename = ''
		b = self.modelNameEntry.component('entry')
		modelname = self.modelNameEntry.get()
		dirName   = self.modelPathEntry.get()
		if len(self.outputFilename) > 0: 
			print "dirName = ", dirName, " and ", self.outputFilename
			dirName = os.path.dirname(self.outputFilename)
		self.commandFilename = self.createCommandShell(cmd,dirName,modelname)
		print "pSubmitJob: runPowersNow: command filename ", self.commandFilename
		os.system('qsub ' + self.commandFilename)
		self.writeStatusToDisk()
		if showDialog == True:
			showwarning('Caution','Attempted to submit the job per your request. Check monitor')
		if self.tellMaster <> None: 
			self.tellMaster(self.masterObj,'OBJS',[self.defaultModelName,self.outputFilename,self.errorFilename])


	def showCommand(self):
		cmd = self.getCommandString()
		if len(cmd) < 1: 
			showwarning('Caution','Attempted to submit the job for an invalid model')
			return 
		self.incomingCommand = None
		self.jclCommandHandler = Pmw.TextDialog(self.parent, scrolledtext_labelpos='n', title='JCL Command',\
			label_text='BE CAREFUL! I do NOT check for syntax errors with any edits to this JCL!',
			defaultbutton=0,buttons=('Close','Submit','Save','Clear','Read'),command=self.commandHandler)
		self.jclCommandHandler.settext(cmd)

	def commandHandler(self,parm):
		self.incomingCommand = None
		#print parm, dir(self)
		if parm == 'Clear':
			self.jclCommandHandler.clear()
			return

		if parm == 'Read':
			ifile = askopenfilename(filetypes=[("ksh","*.ksh"),("All Files","*")])		
			if ifile:
				self.jclCommandHandler.clear()
				self.jclCommandHandler.importfile(ifile)
				self.jclCommandHandler.activate()
			return
		if parm == 'Save': 
			xstr = self.jclCommandHandler.get()
			xlns = xstr.split('\n')
			initialdir = os.getcwd()
			mfile = '' 
			for xln in xlns: 
				f = xln.find('MODEL=')
				if f>=0 and len(mfile) < 1:  
					items=xln.split('=')
					mfile = items[1] + ".ksh"
				f = xln.find('OUTPUTDIR=')
				if f >=0:
					f = xln.find('=')
					initialDir = xln[f+1:]
					initialDir = initialDir.strip()
					
			ofile = asksaveasfilename(filetypes=[("shell script","*.ksh"),("All Files","*"), ("shell script","*.sh"),("All Files","*")],
					initialdir=initialDir,initialfile=mfile)
			if ofile:
				print "I am writing to this file .......", ofile
				xstr = self.jclCommandHandler.get()
				fd = open(ofile,'w')
				fd.write(xstr)
				fd.close()
			return 
		if parm == 'Submit': 
			self.incomingCommand = self.jclCommandHandler.get()
		self.jclCommandHandler.destroy()
		if parm == 'Submit': 
			if self.incomingCommand <> None:
				self.runJCLcommand()
		self.jclCommandHandler = None
		#if parm == 'Submit': showwarning('Caution','Attempted to submit the job per your request. Check monitor')

	def getCommandString(self,incoming=None):
		doit = self.doExtraction.get()
		if doit > 0: 
			retstr = '' + self.jobString + '\n' + self.extractString 
		else: 
			retstr = '' + self.jobString

		if self.trustedUser == True: retstr += '' + self.myExtraction 

		if incoming == None: 
			fullName = self.modelPathEntry.get() + os.sep + self.modelNameEntry.get()
			modelName = self.modelNameEntry.get()
			if modelName == '': 
				fullName = self.defaultModelName 
			else:
				self.defaultModelName = fullName
		else: 
			fullName = incoming;
		
		self.plccString = self.systemString.get()
		#
		# Now derive the name completely independantly of the model
		#
		fullName = fullName.strip()
		if len(fullName) < 1: return  ''

		modelName = os.path.basename(fullName)
		modelName = modelName.replace(".model",'')                # Create modelname 

		dirName = os.path.dirname(fullName)
		dirName = dirName.replace('/data','')                     # Replace data completely
		modeldirName = os.path.dirname(fullName)                  # 
		#modeldirName = modeldirName.replace('/data','')           # Get rid of data!
		
		foundBinDir = 0
		self.kornShellFileName = '/red/restart/' + os.getenv('USER') + os.sep + modelName + ".ksh"
		xlines = open(fullName,'r').readlines()
		for iln in xlines:
			ln = iln.strip()
			if len(ln) < 5 : continue
			if ln[0] == '#': continue
			f = ln.find('BINARY_DATA_DIRECTORY')
			if f >= 0: 
				items = ln.split()
				binDataDir  = items[1].replace("'",'')            # Get raw string 
				dirName = binDataDir + '/' + modelName            # Use this instead
				self.kornShellFileName = dirName + ".ksh"
				foundBinDir = 1
				break;


		self.doublecpu = 1
		fcpu = self.plccString[-1]
		if fcpu in ['h','i','l','m']: self.doublecpu = 2

		self.outputFilename = '%s/%s.output' % (dirName,modelName)
		#self.errorFilename  = dirName + '/' + modelName[:9] + '.err'
		retstr = retstr.replace('ONLYIFBINDIRFOUND', self.linkToBinDir)
		if foundBinDir == 1: 
			retstr = retstr.replace('PARM_SETBINDIRPATH', dirName)
			retstr = retstr.replace('PARM_BINDIRPATH',binDataDir)
		else:
			#print "modeldirName = ", modeldirName 
			#print "fullName = ", fullName
			# retstr = retstr.replace('PARM_SETBINDIRPATH', modeldirName)
			dirName = '/red/restart/' + os.getenv('USER') + os.sep + modelName
			retstr = retstr.replace('PARM_SETBINDIRPATH', dirName)
			retstr = retstr.replace('PARM_BINDIRPATH',modeldirName)
		retstr = retstr.replace('PARM_PATH',dirName)
		retstr = retstr.replace('PARM_MODELPATH',modeldirName)
		retstr = retstr.replace('PARM_MODEL',modelName)
		retstr = retstr.replace('PARM_10MODEL',modelName[:9])
		retstr = retstr.replace('PARM_NUMNODES',self.numNodesEntry.get())
		retstr = retstr.replace('PARM_DOUBLECPU','%d' % (int(self.numNodesEntry.get()) * self.doublecpu))
		retstr = retstr.replace('PARM_SYSTEM',self.use_node)
		retstr = retstr.replace('PARM_PLCWHERE',self.plccString)
		retstr = retstr.replace('PARM_USER',os.getenv('USER'))
		################################################################################
		# EXCEPTIONS
		# If the model exists in sector_data then don't append data to the link.
		#
		f = modeldirName.find('sector_data')
		if f >= 0: 
			retstr = retstr.replace('sector_data/data','sector_data')
			retstr = retstr.replace('PARM_SECTORDATA','sector_data')
		else:
			retstr = retstr.replace('PARM_SECTORDATA','data')
		doit = self.doExtraction.get()
		if doit == 1: retstr = retstr.replace('PARM_EXTRACTION','autoext_400')
		if doit == 2: retstr = retstr.replace('PARM_EXTRACTION','autoext_300')
		if doit == 3: 
			retstr = retstr.replace('PARM_EXTRACTION','autoext_a64_mtb')
			retstr = retstr.replace('serial@simc','parallel@simb')

		#f = retstr.find('PARM_P_EXT')
		#if f > 0: 
			#print "Looking at PARM_P_EXT"
			#if self.trustedUser == True: 
				#retstr = retstr.replace('PARM_P_EXT',' ')
			#else:
				#retstr = retstr.replace('PARM_P_EXT','#')
		################################################################################

		tr= self.doTimedRun.get()
		hourAt = int(self.runAtHour.get())
		minAt =  int(self.runAtMinute.get())
		if tr == 0:
			timedString = '##PBS -a %s%02d%02d' % (self.runAtDate.get(),hourAt,minAt)
		else: 
			timedString = 'PBS -a %s%02d%02d' % (self.runAtDate.get(),hourAt,minAt)
		timedString = timedString.replace('/','')
		retstr = retstr.replace('TIMEDRUN',timedString)
		return retstr


	def cancelBtn(self):
		if self.tellMaster <> None: 
			self.tellMaster(self.masterObj,'OBJS',[self.defaultModelName,"",""])
		

	def selectedSimulator(self,parm):
		self.use_node = 'test'
		if parm == 'prod':  self.use_node = 'prod'

	def getModel(self):
		ifile = askopenfilename(filetypes=[("model","*.model"),("All Files","*")])		
		if ifile: 
			if ifile[0] <> '/':
				fullpath = os.getcwd() + os.sep + ifile
			else:
				fullpath = ifile
			self.modelNameEntry.setentry(os.path.basename(fullpath))
			self.modelPathEntry.setentry(os.path.dirname(fullpath))


if __name__ == '__main__':
	r = Tk()
	b = makeSubmitForm(r)
	r.mainloop()

