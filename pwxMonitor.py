"""
This monitors jobs in all our clusters.
"""
import wx
import string 
#from pObject import *
from copy import copy
import os, sys, re

##########################################################################################
# The main form for the application  ... 
##########################################################################################
class pwxJobInfoFrame(wx.Frame):
	def __init__(self,parent,id,caption=""):
		wx.Frame.__init__(self,parent=None,id=-1)
		self.m_master     = parent		# The master frame.

		self.msizer = wx.BoxSizer(wx.HORIZONTAL)      # For the main frame. 
		self.m_controlPanel = pwxControlPanel(self,-1)
		self.m_displayPanel = pwxMonitoredPanel(self,-1)
		self.msizer.Add(self.m_controlPanel, 0, wx.ALL )
		self.msizer.Add(self.m_displayPanel, 1, wx.ALL | wx.GROW)
		self.SetSizer(self.msizer)
		self.Fit()

		self.m_listOfMonitorID = []   # Jobs being monitored.
		self.lastJobID     = ''
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
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER,self.onTimer,self.timer)

	def onTimer(self,event):
		self.f_monitorqstat('All Jobs')

	def startTimer(self):
		self.timer.Start(3000)

	def stopTimer(self):
		self.timer.Stop()

	def f_monitorqstat(self,how='All Jobs'):
		"""
		Calls simc monitors status command and displays the results in a window.
		"""
		useCommand = ''
		if how == 'Quota': useCommand = '/red/ssd/appl/powers/bin/myquota'
		if how == 'All Jobs': useCommand = self.allQstatString
		if how == 'My Jobs' : useCommand = self.userQstatString
		if how == 'Serial'  : useCommand = self.serialString 
		if how in ['Detailed', 'Kill Job']: 
			ln = self.m_displayPanel.getSelectedText()
			match = self.regex.match(ln)
			if match: 
				self.lastJobID = ln.split()[0] 
				if how == 'Detailed': useCommand = 'qstat -f ' + self.lastJobID 
				if how == 'Kill Job': useCommand = 'qdel ' + self.lastJobID 
		if len(useCommand) < 1: return 
	
		id = os.popen(useCommand)
		xstr = id.readlines()
		id.close()
		self.outputTextList = xstr
		
		self.m_displayPanel.setOutputString(self.outputTextList)
		if how in ['Detailed']:
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
		
class pwxControlPanel(wx.Panel):
	def __init__(self,parent,id=-1):
		"""
		This is where the tables will be listed. 
		"""
		wx.Panel.__init__(self,parent,id)
		self.masterframe  = parent                       # The calling class, not the pvt table.
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		# Create your elements first
		self.m_allJobsBtn = wx.Button(self,-1,'All Jobs')
		self.m_myJobsBtn = wx.Button(self,-1, 'My Jobs')
		self.m_oneJobBtn = wx.Button(self,-1, 'Detailed')
		self.m_serialBtn = wx.Button(self,-1, 'Serial')
		self.m_deleteBtn = wx.Button(self,-1, 'Kill Job')
		self.m_quotaBtn  = wx.Button(self,-1, 'Quota')
		self.m_startTimerBtn = wx.Button(self,-1, 'Timer')
		# Do the bindings here.
		self.Bind(wx.EVT_BUTTON,self.processRequest,self.m_allJobsBtn)
		self.Bind(wx.EVT_BUTTON,self.processRequest,self.m_oneJobBtn)
		self.Bind(wx.EVT_BUTTON,self.processRequest,self.m_myJobsBtn)
		self.Bind(wx.EVT_BUTTON,self.processRequest,self.m_quotaBtn)
		self.Bind(wx.EVT_BUTTON,self.processRequest,self.m_deleteBtn)
		self.Bind(wx.EVT_BUTTON,self.startTimer,self.m_startTimerBtn)

		# Add stuff to the sizer. 
		self.sizer.Add(self.m_allJobsBtn, 0, wx.TOP) 
		self.sizer.Add(self.m_myJobsBtn , 0, wx.TOP) 
		self.sizer.Add(self.m_deleteBtn , 0, wx.TOP) 
		self.sizer.Add(self.m_serialBtn , 0, wx.TOP) 
		self.sizer.Add(self.m_quotaBtn , 0, wx.TOP) 
		self.sizer.Add(self.m_oneJobBtn , 0, wx.TOP) 
		self.sizer.Add(self.m_startTimerBtn , 0, wx.TOP) 
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)

	def startTimer(self,event):
		xstr = event.GetEventObject().GetLabel()
		ctrl = event.GetEventObject()
		if xstr == 'Timer':
			self.masterframe.startTimer()
			ctrl.SetLabel('Stop')
		else:
			self.masterframe.stopTimer()
			ctrl.SetLabel('Timer')

	def processRequest(self,event): 
		xstr = event.GetEventObject().GetLabel()
		self.masterframe.f_monitorqstat(xstr)

class pwxMonitoredPanel(wx.Panel):
	def __init__(self,parent,id=-1):
		"""
		This is where the tables will be listed. 
		"""
		wx.Panel.__init__(self,parent,id)
		self.masterframe  = parent       # The calling class
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.textOutput = wx.TextCtrl(self,-1,'This is a\ntest', size=(600,500),style=wx.TE_MULTILINE)
		self.sizer.Add(self.textOutput,1,wx.ALL|wx.GROW) 
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		
		self.font = wx.Font(10,wx.FONTFAMILY_TELETYPE,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
		self.font.SetFaceName('Courier')
		self.font.SetUnderlined(1)
		self.textOutput.SetFont(self.font)


	def setOutputString(self,xstr):
		self.textOutput.SetValue("".join(xstr))

	def getSelectedText(self):
		return self.textOutput.GetStringSelection()


##########################################################################
# The main application goes here. 
##########################################################################
class MyApp(wx.App):
	def OnInit(self):
		self.fame = pwxJobInfoFrame(None,-1,'Job Information Viewer')
		self.fame.Show()
		self.SetTopWindow(self.fame)
		return True

if __name__ == '__main__': 
	#setPlatformSpecificPaths()
	root = MyApp()
	root.MainLoop()					# ...and wait for input
	
