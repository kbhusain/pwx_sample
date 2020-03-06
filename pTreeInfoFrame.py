
"""
This file contains the code to display and information displayed from 
a tree constructed with the cPerfFile object. 

"""
from Tkinter import *
import Pmw
from tkMessageBox import showwarning, askyesno
from tkSimpleDialog import askstring
from tkFileDialog import *
import string 
from pModifiableList import *
from pObject import *
import Tree 
import cPerfParser 
import cRateParser 
from TableList import *
import os

class MyDateInfoTreeNode(Tree.Node):
	def __init__(self,*args,**kw_args):
		apply(Tree.Node.__init__, (self,)+args,kw_args)
		self.widget.tag_bind(self.label,'<1>',self.printMe) 

	def printMe(self,event):
		#print "Hello ... from a label", self.get_label(), self.full_id()
		full_id =  self.full_id()
		if len(full_id) == 1:     # A well has been selected.
			dName = full_id[1]    # The date selected.
			self.callback_parms.lastWell = daWell
			self.callback_parms.lastDate = dt
			for dt in self.callback_parms.myObject.allDates.values():            # Get the date name
				if dt.getDate().find(dName) == 0: 
					self.callback_parms.f_showDate(dt)   # Using the object for frame
			return
		if len(full_id) == 3:     # A well has been selected.
			dName = full_id[1]    # The date selected.
			wName = full_id[2]    # The well in the date
			for dt in self.callback_parms.myObject.allDates.values():            # Get the date name
				if dt.getDate().find(dName) == 0: 
					if dt.Wells.has_key(wName):
						daWell = dt.Wells[wName]
						#print "daWell has ", len(daWell.perforations), " perforations"
						self.callback_parms.lastPerf = None
						self.callback_parms.lastWell = daWell
						self.callback_parms.lastDate = dt
						self.callback_parms.f_showWell(daWell)   # Using the object for frame
			return

		if len(full_id) <> 4: return    # Only if a perforation has been selected.
		dName = full_id[1]    # The date selected.
		wName = full_id[2]    # The well in the date
		pName = full_id[3]    # The well in the date
		for dt in self.callback_parms.myObject.allDates.values():            # Get the date name
			if dt.getDate().find(dName) == 0: 
				if dt.Wells.has_key(wName):
					daWell = dt.Wells[wName]
					for perf in daWell.perforations:
						if pName == perf.getPerfName():
							self.callback_parms.lastWell = daWell
							self.callback_parms.lastDate = dt
							self.callback_parms.f_showPerf(perf)   # Using the object for frame
							return


class frameDateInfoParameters(Frame):
	"""
	This is used to create the frame for hte `
	"""
	def __init__(self,master,rateObject=None):
		Frame.__init__(self,master)
		self.pack(expand=YES,fill=BOTH)
		self.frm_tree = Frame(self)
		self.frm_tree.pack(side=LEFT,fill=BOTH,expand=1)
		self.m_treeBrowser = None 
		# if rateObject <> None:  self.mapObjToGui(rateObject):
	
		self.frm_details = Frame(self);

		self.well_icon = PhotoImage(data='R0lGODlhDwAPAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/\n/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm\nAABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/\nMwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm\nZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/\nmTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm\nzGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/\n/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ\nAJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA\nM8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ\nZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A\nmf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z\nzP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///yH5BAEAABAALAAAAAAPAA8A\nAAhUAJcIHEiwoMGDCBMSRKFwoB8UfhouSYUiVcNUD/1YTOjnH4p/ERFqzIgRYap/HlGWLIgRI8SW\nBkMuYShQI0s+pvigwInTT86fKIIKHcoz59CjSAMCADs=')

		self.closed_icon = PhotoImage(data='R0lGODlhDwAPAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/\n/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm\nAABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/\nMwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm\nZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/\nmTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm\nzGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/\n/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ\nAJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA\nM8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ\nZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A\nmf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z\nzP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAADwAPAAAIWgAfCBxI\nsKDBgwIJKFzIkOEDAqn8RJwosSIBAAQeLNDIcePAixBTCRSZqqRJkA9Iplwp8iFGljBLusxIUqbK\nmTZjlkS5sWdHjSAbClUI4AGAo0iTJkXItOnAgAA7')

		self.open_icon = PhotoImage(data='R0lGODlhDwAPAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/\n/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm\nAABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/\nMwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm\nZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/\nmTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm\nzGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/\n/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ\nAJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA\nM8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ\nZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A\nmf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z\nzP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAADwAPAAAIUAAfCBxI\nsKDBgwP9pFLIcKFDhQ8WHgTwAIBEPwgJpopY8UGCBB0pUsSIMaPAjRspfgzZkaTJkxxVgqRIkOTG\njH4oPtzZkCaAn0CDAn1J9GBAADs=')


		self.headerLabel =  Label(self.frm_details,text="ID")
		self.headerLabel.pack(side=TOP,fill=X,expand=0)

		self.parametersTable = TableList(self.frm_details,  width=40,
			background='white', columns=(16,"Parameter",16,"Value"), selecttype='cell')
		self.parametersTable.columnconfigure(1,editable='YES')
		self.parametersTable.pack(side=TOP,expand=1)

		self.perfColumns  = []                            # for showing items in perforations 
		for x in cPerfAllowedKeywords:           # allow all allowed values
			self.perfColumns.append(8)                    # allow upto 8 characters
			self.perfColumns.append(x)                    # for each character

		self.perforationsTable = ScrolledTableList(self.frm_details,         # Only if table is needed
			background='white', columns=tuple(self.perfColumns))             # and in the middle of the dialog
		for x in range(len(cPerfAllowedKeywords)):                  # Make the whole thing editable
			self.perforationsTable.columnconfigure(x,editable='YES')         # pack it and show it
		self.perforationsTable.pack(side=TOP,fill=BOTH,expand=1)
		self.perforationsTable.pack_forget()
		
		###################################################################################
		# You must handle both Well and Perforation saves.
		###################################################################################
		self.btnSaveWell = Button(self.frm_details,text="Save Values", command=self.f_saveValues)
		self.btnSaveWell.pack(side=TOP,expand=0)

		###################################################################################
		#self.buttonBox = Pmw.ButtonBox(self.frm_details,labelpos='n',label_text='TODO Actions', orient='vertical')
		###################################################################################
		self.buttonBox = Pmw.ButtonBox(self.frm_details,labelpos='n',label_text='TODO Actions')
		self.buttonBox.pack(side=BOTTOM,fill=X, expand=0,padx=0,pady=0)
		self.buttonBox.add('ADD DATE',command = lambda s=self :  s.m_addDate());
		self.buttonBox.add('DEL DATE',command = lambda s=self :  s.m_deleteDate());
		self.buttonBox.add('ADD WELL',command = lambda s=self :  s.m_addWell());
		self.buttonBox.add('DEL WELL',command = lambda s=self :  s.m_deleteWell());
		self.buttonBox.add('ADD PERF',command = lambda s=self :  s.m_addWell());
		self.buttonBox.add('DEL PERF',command = lambda s=self :  s.m_deleteWell());

		self.frm_details.pack(side=RIGHT,expand=1,fill=BOTH,pady=10)

		self.lastDate = None
		self.lastWell = None
		self.lastPerf = None

	############################################################################
	# Tree manipulation functions
	############################################################################
	def m_addDate(self):
		if self.lastDate == None: return
		print "I will add a new date after " , index

	def m_deleteDate(self):
		if self.lastDate <> None: 
			print "I will delete a Date here."
			self.lastDate = None

	def m_addWell(self):
		print "I will add a Well here."

	def m_deleteWell(self):
		if self.lastWell <> None: 
			print "I will delete a Well here."
			self.lastWell = None

	def mapObjToGui(self,perfObject,forceTheIssue=0):
		self.myObject = perfObject
		if self.m_treeBrowser == None: 
			self.m_treeBrowser = Tree.Tree(master=self.frm_tree, 
				root_id = os.sep,  root_label='Dates', 
				get_contents_callback=self.get_contents,
				callback_parms=self,
				width=150, 
				expanded_icon=self.closed_icon, 
				collapsed_icon=self.open_icon, 
				regular_icon=self.well_icon, 

				node_class=MyDateInfoTreeNode)
			self.m_treeBrowser.pack(side=LEFT,fill=BOTH,expand=1,padx=0) 
			self.sb=Scrollbar(self.frm_tree)
			self.sb.pack(side=RIGHT,fill=Y,expand=1,padx=0)
			self.m_treeBrowser.configure(yscrollcommand=self.sb.set)
			self.sb.configure(command=self.m_treeBrowser.yview)
		self.m_treeBrowser.root.expand()

	def get_contents(self,another,node): 
		path=apply(os.path.join, node.full_id())    # Get the main name.
		if path == '/':                             # root node.
			mydates = self.myObject.allDates.keys()
			mydates.sort()
			for kk in mydates:
				dt = self.myObject.allDates[kk]
				full=os.path.join(path, dt.getDate())
				node.widget.add_node(name=dt.getDate(), id=dt.getDate(), flag=1)
			return			
		ids = node.full_id()                         # Second level only
		myDateString = ids[1]                      # If this is a date 
		if len(ids) == 2: 
			for dt in self.myObject.allDates.values():                    # Get the date name
				if dt.getDate().find(myDateString) == 0: 
					wells = dt.Wells.keys()
					wells.sort()
					for well in wells:
						node.widget.add_node(name=well,id=well,flag=1) # Add it in there
			return
		if len(ids) == 3: 
			thisWellString = ids[2]                              # If this is a well 
			for dt in self.myObject.allDates.values():                    # Get the date name
				if dt.getDate().find(myDateString) == 0:	 # Get the well on this date  

					print "This well string = [%s]", (thisWellString) 
					print "dt.Wells = ", len(dt.Wells)           

					well = dt.Wells[thisWellString]              # as an object. 
					for perf in well.perforations:               # List the perfs here
						xstr = perf.getPerfName()                # with the ID string
						node.widget.add_node(name=xstr,id=xstr,flag=0) # Add it in the tree

	def mapGuiToObj(self,rateObject):
		pass 

	def f_enmasseSetValue(self):
		""" 
		Untested code
		"""
		if self.lastPerf <> None and self.lastWell <> None: 
			reply = askyesno('Whoa!',"Are you sure you want to set the non-empty entries for all other Perfs in this well?")
			sz = self.parametersTable.size()
			for r in range(sz):
				parm = self.parametersTable.get(r)
				self.lastWell.setKeywordValue(parm[0],parm[1])
				if parm[1] <> '': 
					for perf in self.lastWell.perforations:
						perf.setKeywordValue(txt,parm[1])   # Validate here @@@@!!!!LOOK I AM NOT DOING IT HERE 

	def f_saveValues(self):
		#
		# Collect the stuff from the form on frm_item and plunk it into the well or perforation
		#
		if self.lastPerf == None: 
			if self.lastWell == None: 
				print "There is no last Perf nor a well" 
				return 
			sz = self.parametersTable.size()
			for r in range(sz):
				parm = self.parametersTable.get(r)
				self.lastWell.setKeywordValue(parm[0],parm[1])

			return 
		sz = self.parametersTable.size()
		for r in range(sz):
			parm = self.parametersTable.get(r)
			self.lastPerf.setKeywordValue(parm[0],parm[1])

	def f_showDate(self,kk):
		self.headerLabel['text'] = kk.getDate()
		self.parametersTable.clear()
		self.lastPerf = None;
		self.lastWell = None;
		self.perforationsTable.pack_forget()

	def f_showPerf(self,kk):
		self.headerLabel['text'] = kk.getPerfName()
		self.parametersTable.clear()
		for txt in cPerfAllowedKeywords:
			y = kk.getKeywordValue(txt)   #
			self.parametersTable.insert("end",(txt,y))
		self.lastPerf = kk;
		self.perforationsTable.clear()
		self.perforationsTable.pack_forget()

	def f_saveDate(self):
		pass

	def f_showWell(self,kk):
		self.headerLabel['text'] = kk.getWellName()
		self.parametersTable.clear()
		dummy = cRateParser.cRateFile()
		for txt in dummy.aAllowedWellKeywords:   # You preserved the key when you store it.
			y = kk.getKeywordValue(txt)   #
			self.parametersTable.insert("end",(txt,y))
		self.lastWell = kk;
		self.lastPerf = None;   # Explicitly force the issue.
		self.perforationsTable.pack(fill=BOTH,expand=1)
		self.perforationsTable.clear()
		for kk in self.lastWell.perforations: 
			rowData = []
			for txt in cPerfAllowedKeywords:
				y = kk.getKeywordValue(txt)   #
				rowData.append(y)
			self.perforationsTable.insert("end",tuple(rowData))

