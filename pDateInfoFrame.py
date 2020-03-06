
"""
This file contains the dialog items for the use in the Rates, Perfs and Recurrent
data.
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
import cRecurrentParser 
from TableList import *
from pDialogKeyword import *
import os


tableListBackground = 'gray'

##########################################################################################
# Create a frame and put a list of Wells in there. Clicking on a well will show another
# list of dates where the well is used.
##########################################################################################
class frameListOfWells(Frame):
	def __init__(self,parent,parserObject=None):   # The parser object is cModelParser
		Frame.__init__(self,parent)
		self.parent = parent
		self.pack(expand=YES,fill=X)
		self.parserObject = parserObject              # Use this object 
		self.lastWellName = ''    					  # So nothing is displayed first
		self.lastDate = None                          # Last date entry selected
		self.lastWell = None                          # Last Well entry selected
		self.lastPerf = None                          # Last Perforation  entry 
		self.lastPseudoItem = None                    # Last pseudo item selected
		self.DeleteDialog = None 					  # To rid of the display
		self.showAccumulated = IntVar()		# Whether showing accumulated or snapshot. 
		self.showAccumulated.set(1)         # By default show accumulated.
		if parserObject <> None: 
			self.listOfWellNames  = self.parserObject.allWellNames.keys() # Only the names
			self.listOfWellNames.sort()
			self.listOfAllDates  = self.parserObject.allDatesArray.keys()  # Only the names
			self.listOfAllDates.sort()
		else: 
			self.listOfWellNames = []
			self.listOfAllDates  = []

		self.listOfGroups = []             # Per Date. OR Accumulated?
		self.listOfInjectors = []          # Per Date. OR Accumulated?
		self.listOfProducers = []          # Per Date. OR Accumulated?
		self.listOfWellsPerDate = []

		self.workingCollection = None 
		self.listOfRigs = []
		self.listOfGroupRules = []
		self.m_makeListOfWells(self)

	def makeWellActionButtons(self,where):
		self.frm_details = Frame(where)
		self.frm_details.pack(side=LEFT,fill=Y,expand=0)

		self.buttonBox1 = Frame(self.frm_details,relief='sunken')
		self.buttonBox1.pack(side=LEFT,fill=Y,expand=0)
		btn1 = Button(self.buttonBox1,text='+DATE',command = lambda s=self :  s.m_addDate());btn1.pack(side=TOP,fill=X,expand=0)
		btn1 = Button(self.buttonBox1,text='-DATE',command = lambda s=self :  s.m_deleteDate());btn1.pack(side=TOP,fill=X,expand=0)
		btn1 = Button(self.buttonBox1,text='+WELL',command = lambda s=self :  s.m_addWell());btn1.pack(side=TOP,fill=X,expand=0)
		self.buttonBox2 = Frame(self.frm_details,relief='sunken')
		self.buttonBox2.pack(side=LEFT,fill=Y,expand=0)
		btn1 = Button(self.buttonBox2,text='+PERF',command = lambda s=self :  s.m_addPerf());btn1.pack(side=TOP,fill=X,expand=0)
		btn1 = Button(self.buttonBox2,text='-PERF',command = lambda s=self :  s.m_deletePerf());btn1.pack(side=TOP,fill=X,expand=0)
		btn1 = Button(self.buttonBox2,text='-WELL',command = lambda s=self :  s.m_deleteOneWell());btn1.pack(side=TOP,fill=X,expand=0)
	
		#self.buttonBox1.add('-DATE',command = lambda s=self :  s.m_deleteDate());
		#self.buttonBox1.add('+WELL',command = lambda s=self :  s.m_addWell());


		#self.buttonBox1 = Pmw.ButtonBox(self.frm_details,labelpos='n',label_text='TODO',orient=VERTICAL)
		#self.buttonBox1.pack(side=LEFT,fill=X, expand=0,padx=0,pady=0)
		##self.buttonBox.add('SAVE CHGS',command = lambda s=self :  s.m_saveValues());
		#self.buttonBox1.add('+DATE',command = lambda s=self :  s.m_addDate());
		##self.buttonBox1.add('-DATE',command = lambda s=self :  s.m_deleteDate());
		##self.buttonBox1.add('+WELL',command = lambda s=self :  s.m_addWell());
		#self.buttonBox2 = Pmw.ButtonBox(self.frm_details,labelpos='n',label_text='TODO',orient=VERTICAL)
		#self.buttonBox2.pack(side=LEFT,fill=X, expand=0,padx=0,pady=0)
		#self.buttonBox2.add('+PERF',command = lambda s=self :  s.m_addPerf());
		#self.buttonBox2.add('-PERF',command = lambda s=self :  s.m_delPerf());
		#self.buttonBox2.add('-WELL',command = lambda s=self :  s.m_deleteOneWell());
#

	def m_makeListOfWells(self,where):
		"""
		Internal function
		Makes three panes. One for the main window area, and 
		the other two panes are called Group and Rules 
		"""
		self.mainPane = Pmw.PanedWidget(where,orient=HORIZONTAL)
		self.mainPane.pack(side=TOP,fill=BOTH,expand=1)
		self.mainPane.add('F1',min=500)
		self.mainPane.add('F2')

		self.leftPane = Pmw.PanedWidget(self.mainPane.pane('F1'))
		self.leftPane.add('top',min=400)
		self.leftPane.add('bottom')
		self.leftPane.pack(side=TOP,fill=BOTH,expand=1)

		##################################################################################
		#  For the well and perforation information 
		##################################################################################
		self.f1 = self.leftPane.pane('top')
		self.dateWellFrame = Frame(self.f1,height=10,relief='raised',borderwidth=3)
		self.dateWellFrame.pack(side=TOP,fill=X,expand=1)
		self.masterList = Pmw.ComboBox(self.dateWellFrame,
					#listbox_selectmode = SINGLE,
					label_text = 'DATE',
					labelpos = 'w' ,
					scrolledlist_items = [],
					listbox_exportselection=0,
					dropdown=1,
					selectioncommand = self.m_selectMaster)
		self.masterList.pack(side=LEFT,fill=X,expand=0)
		ef = self.masterList.component('entryfield')
		te = ef.component('entry')
		te['width']=12
		self.wellsList = Pmw.ComboBox(self.dateWellFrame,
					#listbox_selectmode = SINGLE,
					scrolledlist_items = self.listOfWellsPerDate, 
					labelpos = W, 
					label_text = 'Wells',
					dropdown=1,
					listbox_width=10,
					listbox_exportselection=0,
					selectioncommand = self.m_selectSubListItem)
		self.wellsList.pack(side=LEFT,expand=NO)
		ef = self.wellsList.component('entryfield')
		te = ef.component('entry')
		te['width']=10
		self.sourceLabel = Label(self.dateWellFrame, text='WHENCE')
		self.sourceLabel.pack(side=LEFT,expand=0)
		self.ck_accumulate = Checkbutton(self.dateWellFrame,text='Accumulate',anchor=W, variable=self.showAccumulated)
		self.ck_accumulate.pack(side=RIGHT,expand=0)

		self.f2 = Frame(self.f1);
		self.f2.pack(side=TOP,fill=BOTH,expand=1);

		##################################################################################
		#  For the group rules, pseudo, rigs and other information
		##################################################################################
		self.nb= Pmw.NoteBook(self.leftPane.pane('bottom'))
		self.tabRigsParms = self.nb.add('Rigs') 		     # For general parameters.
		self.tabRulesParms = self.nb.add('Group Rules')	     # For general parameters.
		self.tabInitKeywordsParms = self.nb.add('Initial')
		self.tabDateKeywordsParms = self.nb.add('At Date') 		
		self.tabAccKeywordsParms  = self.nb.add('Effective') 		
		self.nb.pack(side=BOTTOM,expand=1,fill=BOTH)

		self.rulesText = Pmw.ScrolledText(self.tabRulesParms,borderframe=1,
				labelpos=N,label_text ='Rules', text_wrap='none')
		self.rulesText.pack(side=BOTTOM,fill=BOTH,expand=1)

		self.rigsText = Pmw.ScrolledText(self.tabRigsParms,borderframe=1,
				labelpos=N,label_text ='Rigs', text_wrap='none')
		self.rigsText.pack(side=BOTTOM,fill=BOTH,expand=1)

		self.initKeywordsParms = ScrolledTableList(self.tabInitKeywordsParms,  width=40,showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=(32,"Parameter",16,"Value"), selecttype='cell')
		self.initKeywordsParms.columnconfigure(1,editable='YES')
		self.initKeywordsParms.pack(side=LEFT,expand=1,fill=BOTH)

		self.dateKeywordsParms = ScrolledTableList(self.tabDateKeywordsParms,  width=40,showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=(32,"Parameter",16,"Value"), selecttype='cell')
		self.dateKeywordsParms.columnconfigure(1,editable='YES')
		self.dateKeywordsParms.pack(side=LEFT,expand=1,fill=BOTH)

		self.accKeywordsParms = ScrolledTableList(self.tabAccKeywordsParms,  width=40,showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=(32,"Parameter",16,"Value"), selecttype='cell')
		self.accKeywordsParms.columnconfigure(1,editable='YES')
		self.accKeywordsParms.pack(side=LEFT,expand=1,fill=BOTH)

		##################################################################################
		#  For the group rules, pseudo, rigs and other information
		##################################################################################
		self.tabGroupParms = self.mainPane.pane('F2')

		self.searchReplaceForm = Frame(self.mainPane.pane('F2'))
		self.searchReplaceForm.pack(side=TOP,fill=X,expand=0)

		btn1 = Button(self.searchReplaceForm,text='Go', command= lambda s=self, b='Case' :  s.m_replaceText(b))
		btn1.pack(side=LEFT,fill=X,expand=0)
		self.searchGroupText = Pmw.EntryField(self.searchReplaceForm,labelpos=W,label_text="Replace",validate=None,value='')
		self.searchGroupText.pack(side=LEFT)
		self.replaceGroupText = Pmw.EntryField(self.searchReplaceForm,labelpos=W,label_text="With",validate=None,value='')
		self.replaceGroupText.pack(side=LEFT)
		

		self.frameGroupInfo = Frame(self.tabGroupParms) 
		self.frameGroupInfo.pack(side=LEFT,fill=BOTH,expand=1);
		self.grpList = Pmw.ScrolledListBox(self.frameGroupInfo,
					listbox_selectmode = SINGLE,
					items = self.listOfGroups, 
					labelpos = N, 
					label_text = 'Groups',
					listbox_exportselection=0,
					selectioncommand = self.m_selectGroup,
					usehullsize=1, hull_width=50, hull_height=150)
		self.grpList.pack(side=TOP,fill=X,expand=YES)
					
		self.Groups_buttonBox = Frame(self.frameGroupInfo,relief='sunken')
		self.Groups_buttonBox.pack(side=TOP)
		btn1 = Button(self.Groups_buttonBox,text='+Gp',command = lambda s=self, b='GROUP' :  s.m_addToCollection(b))
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1 = Button(self.Groups_buttonBox,text='-Gp',command = lambda s=self, b='GROUP' :  s.m_delFromCollection(b));
		btn1.pack(side=LEFT,fill=X,expand=0)
		#self.Groups_buttonBox.add('E',command = lambda s=self :  s.m_editGroup());

		self.injList = Pmw.ScrolledListBox(self.frameGroupInfo,
					listbox_selectmode = SINGLE,
					items = self.listOfInjectors, 
					labelpos = N, 
					label_text = 'Injectors',
					listbox_exportselection=0,
					selectioncommand = self.m_selectInjector,
					usehullsize=1, hull_width=50, hull_height=150)
		self.injList.pack(side=TOP,fill=X,expand=YES)

		self.Inj_buttonBox = Frame(self.frameGroupInfo,relief='sunken')
		self.Inj_buttonBox.pack(side=TOP)
		btn1 = Button(self.Inj_buttonBox,text='+Inj',command = lambda s=self, b='INJECTOR' :  s.m_addToCollection(b))
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1 = Button(self.Inj_buttonBox,text='-Inj',command = lambda s=self, b='INJECTOR' :  s.m_delFromCollection(b));
		btn1.pack(side=LEFT,fill=X,expand=0)
		#self.Inj_buttonBox.add('E',command = lambda s=self :  s.m_editInjector());

		self.prdList = Pmw.ScrolledListBox(self.frameGroupInfo,
					listbox_selectmode = SINGLE,
					items = self.listOfProducers, 
					labelpos = N, 
					label_text = 'Producers',
					listbox_exportselection=0,
					selectioncommand = self.m_selectProducer,
					usehullsize=1, hull_width=50, hull_height=150)
		self.prdList.pack(side=TOP,fill=X,expand=YES)

		self.Prd_buttonBox = Frame(self.frameGroupInfo,relief='sunken')
		self.Prd_buttonBox.pack(side=TOP)
		btn1 = Button(self.Prd_buttonBox,text='+Prd',command = lambda s=self, b='PRODUCER' :  s.m_addToCollection(b))
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1 = Button(self.Prd_buttonBox,text='-Prd',command = lambda s=self, b='PRODUCER' :  s.m_delFromCollection(b));
		btn1.pack(side=LEFT,fill=X,expand=0)
		#self.Prd_buttonBox.add('E',command = lambda s=self :  s.m_editProducer());

		self.frameWellPlusPsuedo = Frame(self.tabGroupParms)
		self.frameWellPlusPsuedo.pack(side=RIGHT,fill=BOTH,expand=0)
		### Show wells on the top
		self.fWellsPerGroup = Frame(self.frameWellPlusPsuedo)	
		self.fWellsPerGroup.pack(side=TOP,fill=BOTH,expand=1)
		self.listWellsPerGroup = Pmw.ScrolledListBox(self.fWellsPerGroup,
					listbox_selectmode = SINGLE,
					items = [],
					labelpos = N, 
					label_text = 'Wells',
					listbox_exportselection=0,
					selectioncommand = self.m_selectGroupWell,
					usehullsize=1, hull_width=50, hull_height=150)
		self.listWellsPerGroup.pack(side=TOP,fill=BOTH,expand=YES)
		self.Wpg_buttonBox = Frame(self.fWellsPerGroup,relief='sunken')
		self.Wpg_buttonBox.pack(side=TOP)
		btn1 = Button(self.Wpg_buttonBox,text='+Well',command = lambda s=self :  s.m_addItemToCollection())
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1 = Button(self.Wpg_buttonBox,text='-Well',command = lambda s=self :  s.m_delItemFromCollection());
		btn1.pack(side=LEFT,fill=X,expand=0)

		### Now, show 
		self.framePS = Frame(self.frameWellPlusPsuedo)
		self.framePS.pack(side=BOTTOM,expand=0,fill=X)
		self.listPseudoForDate = Pmw.ScrolledListBox(self.framePS,
					listbox_selectmode = SINGLE,
					items = [],
					labelpos = N, 
					label_text = 'Pseudo',
					listbox_exportselection=0,
					selectioncommand = self.m_selectPseudoForDate,
					usehullsize=1, hull_width=50, hull_height=50)
		self.listPseudoForDate.pack(side=BOTTOM,fill=BOTH,expand=YES)
		self.pseudoParmsTable = ScrolledTableList(self.framePS,  width=50, height=5,showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=(16,"Parameter",16,"Value"), selecttype='cell')
		self.pseudoParmsTable.columnconfigure(1,editable='YES')
		self.pseudoParmsTable.pack(side=BOTTOM,expand=1,fill=BOTH)
		self.Groups_buttonBox = Frame(self.framePS)
		self.Groups_buttonBox.pack(side=BOTTOM)
		btn1=Button(self.Groups_buttonBox,text='+Psd',command = lambda s=self, b='ADD' :  s.m_addPseudoToDate(b))
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1=Button(self.Groups_buttonBox,text='-Psd',command = lambda s=self, b='DEL' :  s.m_delPseudoToDate(b));
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1=Button(self.Groups_buttonBox,text='+Key',command = lambda s=self, b='ADD_PS_KEY' :  s.m_addPseudoKeyword(b));
		btn1.pack(side=LEFT,fill=X,expand=0)
		btn1=Button(self.Groups_buttonBox,text='-Key',command = lambda s=self, b='DEL_PS_KEY' :  s.m_delPseudoKeyword(b));
		btn1.pack(side=LEFT,fill=X,expand=0)

		##
		## The Well Parameters are shown in this dialog.
		##
		self.tabWellParms = Frame(self.f2)
		self.tabWellParms.pack(side=LEFT,expand=1,fill=BOTH)
		self.f5 = Frame(self.tabWellParms);             # for Perforations + well info
		self.f5.pack(side=TOP,fill=BOTH,expand=1);      # on the left

		self.f4 = Frame(self.f5)                        #  for setting values
		self.f4.pack(side=TOP,fill=BOTH,expand=1);      # 

		self.wellButtonFrame = Frame(self.f4)
		self.wellButtonFrame.pack(side=LEFT,fill=Y,expand=NO)
		self.makeWellActionButtons(self.wellButtonFrame)

		self.setValuesForm = Frame(self.f4)
		self.setValuesForm.pack(side=LEFT,fill=BOTH,expand=1);

		self.listOfColumns = Pmw.ComboBox(self.setValuesForm, labelpos=W, label_text='Column', 
				listheight=120, dropdown=1, scrolledlist_items=cPerfAllowedKeywords)
		e = self.listOfColumns.component('entryfield')
		t = e.component('entry')
		t['width'] = 16
		self.listOfColumns.pack(side=TOP)

		self.valueEntry = Pmw.EntryField(self.setValuesForm,labelpos=W,label_text="Set", validate=None,value=0)
		self.valueEntry.pack(side=TOP)

		self.valueEntryInc = Pmw.EntryField(self.setValuesForm,labelpos=W,label_text="Inc", validate=None,value=0)
		self.valueEntryInc.pack(side=TOP)

		self.smallBtnForm = Frame(self.setValuesForm)
		self.smallBtnForm.pack(side=TOP)
		a = lambda s=self,b='Clr' : s.setPerfColumn(b)
		self.setButton = Button(self.smallBtnForm,text='Clr',command=a)
		self.setButton.pack(side=LEFT)
		a = lambda s=self,b='Set' : s.setPerfColumn(b)
		self.setButton = Button(self.smallBtnForm,text='Set',command=a)
		self.setButton.pack(side=LEFT)
		a = lambda s=self,b='Inc' : s.setPerfColumn(b)
		self.setButton = Button(self.smallBtnForm,text='Inc',command=a)
		self.setButton.pack(side=LEFT)
		a = lambda s=self,b='Mul' : s.setPerfColumn(b)
		self.setButton = Button(self.smallBtnForm,text='Mul',command=a)
		self.setButton.pack(side=LEFT)

		self.small2BtnForm = Frame(self.setValuesForm)
		self.small2BtnForm.pack(side=TOP)

		self.saveButton = Button(self.small2BtnForm,text='Save',command=self.m_saveValues)
		self.saveButton.pack(side=LEFT)

		self.wellPseudoStatus = IntVar()
		self.wellPseudoStatus.set(0)
		self.wellPseudoCheckBtn = Checkbutton(self.small2BtnForm,text='Pseudo', anchor=W, variable=self.wellPseudoStatus)
		self.wellPseudoCheckBtn.pack(side=LEFT,expand=0)

		self.parametersTable = ScrolledTableList(self.f4,  width=32,showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=(16,"Parameter",16,"Value"), selecttype='cell')
		self.parametersTable.columnconfigure(1,editable='YES')
		self.parametersTable.pack(side=LEFT,expand=1,fill=BOTH)
		self.perfColumns  = []                            # for showing items in Perforations 
		for x in cPerfAllowedKeywords:           # allow all allowed values
			self.perfColumns.append(5)                    # allow upto 8 characters
			self.perfColumns.append(x)                    # for each character

		self.tableForPerforations = ScrolledTableList(self.f5,        showseparators='yes',
			stripebackground = 'gray64', stripeforeground = 'gray12',
			background=tableListBackground, columns=tuple(self.perfColumns))        # and in the middle of the dialog
		for x in range(len(cPerfAllowedKeywords)):             # Make the whole thing editable
			self.tableForPerforations.columnconfigure(x,editable='YES')    # pack it and show it
		self.tableForPerforations.addHorizontalBar()
		self.tableForPerforations.pack(side=BOTTOM,fill=BOTH,expand=1)

		self.lastDate = None
		self.lastWell = None
		self.lastPerf = None

	def m_replaceText(self,how):
		oldText = self.searchGroupText.get() 
		newText = self.replaceGroupText.get()
		print 'Attempting replacement', oldText, " with ", newText
		self.lastDateName = self.masterList.get()
		if not self.parserObject.allDatesArray.has_key(self.lastDateName): 
			showwarning('Wrong Date','Select a date or type in a correct format')
			return 
		dte = self.parserObject.allDatesArray[self.lastDateName]
		if len(oldText) == 0: return 
		dte.replaceTextInCollections(oldText,newText)
		self.listWellsPerGroup.setlist([])
		self.updateCollectionDisplay(dte)

	def m_selectPseudoForDate(self):
		"""
		Get the index for the pseudo Item in question
		"""
		self.lastPseudoItem = None 
		listbox = self.listPseudoForDate.component('listbox')
		sel = listbox.curselection()				# The selection
		if (len(sel) < 1): return None              # Bail if empty
		ndx = int(sel[0])                          	# The index of the selection
		name = listbox.get(ndx)
		if self.lastDate == None:
			print "Line 327, pDateInfo, m_selectPseudoItemForDate, No date..."
			return None
		ps = self.lastDate.getPseudoItem(name)
		self.pseudoParmsTable.clear()
		if ps == None: return None
		self.lastPseudoItem = ps 
		self.m_showPseudoEntries()

	def m_showPseudoEntries(self):
		"""
		Not tested. 
		"""
		ps = self.lastPseudoItem 
		sk = ps.getKeywords()
		sk.sort()
		for k in sk:
			v = ps.getKeywordValue(k)
			self.pseudoParmsTable.insert("end",(k,v))
		return ps

	def m_addPseudoToDate(self,collectionName):
		return

	def m_delPseudoToDate(self,collectionName):
		"""
		Removes a pseudo item from a pDate object
		"""
		listbox = self.listPseudoForDate.component('listbox')
		sel = listbox.curselection()				# The selection
		if (len(sel) < 1): return None              # Bail if empty
		ndx = int(sel[0])                          	# The index of the selection
		name = listbox.get(ndx)
		if self.lastDate == None:
			print "Line 327, pDateInfo, m_selectPseudoItemForDate, No date..."
			return None

	def m_addPseudoKeyword(self,collectionName):
		"""
		Ask the user what keyword,value he wants to add to the pseudo object selected.
		If the answers are not NONE, they are added to the currently selected PSEUDO. 
		"""
		ps = self.m_selectPseudoForDate()
		if ps == None: return 

		pp = doKeywordQuery(self.parent)
		pp.useDictionary(ps.getKeywords())
		pp.askQuery()
		print pp.keywd, pp.value, pp.dict
		for k in pp.keys():
			v = pp[k]
			self.lastPseudoItem[k] = v
		self.m_showPseudoEntries()

	def m_delPseudoKeyword(self,collectionName):
		"""
		Deletes a row from the selection table
		"""
		if self.lastPseudoItem == None: return 
		cursel = self.pseudoParmsTable.curselection()
		if len(cursel) < 1: return
		self.pseudoParmsTable.delete(cursel)
		self.m_showPseudoEntries()

	def m_addToCollection(self,collectionName):
		"""
		Present the list of current groups. 
		"""
		self.lastDateName = self.masterList.get()
		if not self.parserObject.allDatesArray.has_key(self.lastDateName): 
			showwarning('Wrong Date','Select a date or type in a correct format')
			return 
		dte = self.parserObject.allDatesArray[self.lastDateName]
		# Now get the list of groups
		useThis = dte.getCollection(collectionName)   # Get the groups...
		dialog = Pmw.ComboBoxDialog(self,title='Add '+ collectionName, 
				buttons=('OK','Cancel'), defaultbutton='OK',
				combobox_labelpos=N,label_text='Add ' + collectionName,
				scrolledlist_items = useThis, listbox_width=30)
		dialog.tkraise()
		result = dialog.activate()	
		if result=='OK': dte.addCollection(collectionName,dialog.get())
		self.updateCollectionDisplay(dte)

	def cb_delCollectionCommand(self,dte,collectionName):
		if self.DeleteDialog == None: return
		sels =  self.DeleteDialog.getcurselection()	 # Get user selection
		if len(sels) == 0: 
			self.DeleteDialog.deactivate()	             # Hide the display
			self.DeleteDialog = None 					 # Get rid of memory
			return                    # Check if something selected.
		dte.delCollection(collectionName,sels[0])    # Add new collection
		self.DeleteDialog.deactivate()	             # Hide the display
		self.updateCollectionDisplay(dte)            # Update visuals 
		self.DeleteDialog = None 					 # Get rid of memory

	def m_delFromCollection(self,collectionType):
		self.lastDateName = self.masterList.get()
		if not self.parserObject.allDatesArray.has_key(self.lastDateName): 
			showwarning('Wrong Date','Select a date or type in a correct format')
			return 
		dte = self.parserObject.allDatesArray[self.lastDateName]
		useThis = dte.getCollection(collectionType)   # Get the groups...
		self.DeleteDialog = Pmw.SelectionDialog(self,title='Delete '+ collectionType, 
				buttons=('OK','Cancel'), defaultbutton='OK',
				command=lambda s=self, d=dte, nm=collectionType: self.cb_delCollectionCommand(d,nm), 
				scrolledlist_items = useThis, listbox_width=30)
		self.DeleteDialog.tkraise()
		self.DeleteDialog.activate()	

	def m_addItemToCollection(self):
		"""
		We have to determine if we are adding wells here or group names. 
		There is no way to tell since it's the same list. The call back
		for the list being set has to first search the names of wells 
		then the name of <> .
		"""
		if self.workingCollection == None: return 
		collectionType, collectionName = self.workingCollection
		dte = self.parserObject.allDatesArray[self.lastDateName]
		useThis = dte.getNamedCollection(collectionType,collectionName)
		dialog = Pmw.ComboBoxDialog(self,title='Add '+ collectionType + ' to ' + collectionName, 
				buttons=('OK','Cancel'), defaultbutton='OK',
				combobox_labelpos=N,label_text='Add ', 
				scrolledlist_items = useThis, listbox_width=30)
		dialog.tkraise()
		result = dialog.activate()	
		if result=='OK': dte.addToCollection(collectionType,collectionName,dialog.get())
		self.updateCollectionDisplay(dte)

	def cb_delItemFromCollectionCommand(self,dte,collectionType,collectionName):
		if self.DeleteDialog == None: return
		sels =  self.DeleteDialog.getcurselection()	 # Get user selection
		if len(sels) == 0: return                    # Check if something selected.
		dte.delItemFromCollection(collectionType,collectionName,sels[0])    # Add new collection
		self.DeleteDialog.deactivate()	             # Hide the display
		self.updateCollectionDisplay(dte)            # Update visuals 
		self.DeleteDialog = None 					 # Get rid of memory

	def m_delItemFromCollection(self):
		if self.workingCollection == None: return 
		collectionType, name = self.workingCollection
		dte = self.parserObject.allDatesArray[self.lastDateName]
		useThis = dte.getNamedCollection(Identifier,name)
		self.DeleteDialog = Pmw.SelectionDialog(self,title='Delete '+ collectionType, 
				buttons=('OK','Cancel'), defaultbutton='OK',
				command=lambda s=self,d=dte,ty=collectionType,nm=name: self.cb_delItemFromCollectionCommand(d,ty,nm), 
				scrolledlist_items = useThis, listbox_width=30)
		self.DeleteDialog.tkraise()
		self.DeleteDialog.activate()	
		

	def m_selectGroupedItem(self,theList,Identifier):
		"""
		This function is called when a grouped item is selected. 
		"""
		listbox = theList.component('listbox') # Get the list of items. 
		sel = listbox.curselection()				# The selection
		if (len(sel) < 1): return 
		ndx = int(sel[0])                          	# The index of the selection
		name = listbox.get(ndx)                		# The name  

		############################################################################
		# Now, I have to cycle through the dates till I get the latest one with
		# information about the group. Then I can show the date. 
		############################################################################

		dte = self.parserObject.allDatesArray[self.lastDateName]


		acc = self.showAccumulated.get() 
		supto  = dte.getDate()            # For the date to accumulate to 
		col_list = []
		acc = self.showAccumulated.get()
		for dkey in self.listOfAllDates:
			tdate = self.parserObject.allDatesArray[dkey]  # get the date object.
			if acc == 0: 
				tdate = dte
			else:
				sd = tdate.getDate()                           # It's string.
				if sd > supto: break                           # Only upto last date selected.
			col = tdate.getCollectionNames(Identifier)      #  The collection.
			lst = tdate.getNamedCollection(Identifier,name) # 
			if lst <> None: 
				for t in lst: 
					col_list.append(t)
			if acc == 0: break
		self.listWellsPerGroup.setlist(col_list)
		lbl = self.listWellsPerGroup.component('label')
		lbl['text'] = Identifier + " in " + name

		#dte = self.parserObject.allDatesArray[self.lastDateName]
		#col = dte.getCollectionNames(Identifier)      #  The collection.
		#lst = dte.getNamedCollection(Identifier,name) # 
		#self.listWellsPerGroup.setlist(lst)
		#lbl = self.listWellsPerGroup.component('label')
		#lbl['text'] = Identifier + " in " + name
		return (Identifier,name)

		# Here NOTE the collection you have just identified ... and the type....
		# This will be used to add wells or injectors, etc.
	
	def m_selectGroup(self):
		self.workingCollection = self.m_selectGroupedItem(self.grpList,'GROUP')

	def m_selectInjector(self):
		self.workingCollection = self.m_selectGroupedItem(self.injList,'INJECTOR')

	def m_selectProducer(self):
		self.workingCollection = self.m_selectGroupedItem(self.prdList,'PRODUCER')

	def updateCollectionDisplay(self,dte):
		"""
		Given a date, you should be able to move forward in time from 
		the start of dates. I have to iterate from
		"""
		if dte <> None: 
			supto  = dte.getDate()            # For the date to accumulate to 
			#
			# Set the pseudo for this page.
			#
			acc = self.showAccumulated.get()
			self.listOfGroups = []
			self.listOfInjectors = []
			self.listOfProducers = []
			for dkey in self.listOfAllDates:
				if acc == 0: 
					tdate = self.parserObject.allDatesArray[dkey]  # get the date object.
					sd = tdate.getDate()                           # It's string.
					if sd > supto: break                           # Only upto last date selected.
				else: 
					tdate = dte
				a = tdate.getCollection('GROUP')
				if len(a) > 0: 
					for i in a: 
						if not i in self.listOfGroups: self.listOfGroups.append(i)
				a = tdate.getCollection('INJECTOR')
				if len(a) > 0: 
					for i in a: 
						if not i in self.listOfInjectors: self.listOfInjectors.append(i)
				#self.listOfProducers = dte.getCollection('PRODUCER')
				a = tdate.getCollection('PRODUCER')
				if len(a) > 0: 
					for i in a: 
						if not i in self.listOfProducers: self.listOfProducers.append(i)
				self.grpList.setlist(self.listOfGroups)
				self.injList.setlist(self.listOfInjectors)
				self.prdList.setlist(self.listOfProducers)
				if acc == 0: break;
		else:	
			self.grpList.setlist([])
			self.injList.setlist([])
			self.prdList.setlist([])
		self.workingCollection = None
		
	def m_selectMaster(self,parm):
		"""
		Called when an item in master list of dates is selected.
		"""
		#print "Master =" , parm
		if self.parserObject == None: return

		listbox = self.masterList.component('scrolledlist') # Get the list of items. 
		sel = listbox.curselection()				   # The index 
		if len(sel) < 1: return
		ndx = int(sel[0])

		listbox = self.wellsList.component('scrolledlist') # Clear the list of subitem
		listbox.setlist([])                       #

		masterLabel = self.masterList.component('label') # for the title
		subLabel = self.wellsList.component('label') # for the title
		#
		# This masterList is showing all dates.
		#
		#----> self.lastDateName = self.listOfAllDates[ndx]
		self.lastDateName = self.masterList.get()
		if not self.parserObject.allDatesArray.has_key(self.lastDateName): 
			showwarning('Wrong Date','Select a date or type in a correct format')
			return 
		dte = self.parserObject.allDatesArray[self.lastDateName]
		self.listOfRigs = dte.allRigs                 # pObject.py
		self.listOfGroupRules = dte.groupRules        # Items
		#--> This gets modifications only ---> #--> self.listOfWellsPerDate = dte.Wells.keys()
		self.listOfWellsPerDate = dte.existingWells
		self.listOfWellsPerDate.sort()
		listbox = self.wellsList.component('scrolledlist') # Clear the list of subitem
		listbox.setlist(self.listOfWellsPerDate)
		self.updateCollectionDisplay(dte)                # Set the lists too!
		masterLabel['text'] = self.lastDateName
		#print "Line 429: ", self.lastWellName, subLabel['text']
		if (subLabel['text'] <>  'Wells'): 
			self.lastWellName = subLabel['text']
			self.showInfoForLastWell()

		self.listWellsPerGroup.setlist([])             # List any pseudo items for this date.
		self.listPseudoForDate.setlist(dte.pseudoItems.keys())
		self.pseudoParmsTable.clear()

		#self.parametersTable.clear()
		#self.tableForPerforations.clear()
		self.sourceLabel['text'] = dte.getSource()

		#
		# Populate from the initial date value from Recurrent Parser.
		#
		acc = {}
		self.initKeywordsParms.clear()                # allow upto 8 characters
		
		if self.parserObject.recurrentFileObject <> None:
			rp = self.parserObject.recurrentFileObject
			sk = rp.aAllowedKeywords
			
			sk.sort()
			for txt in sk:
				y = rp.keywordHolder.getKeywordValue(txt)    #
				acc[txt] = y
				self.initKeywordsParms.insert("end",(txt,y))

		self.dateKeywordsParms.clear()                # allow upto 8 characters
		sk = dte.getKeywords()
		sk.sort()
		for txt in sk:
			y = dte.getKeywordValue(txt)              #
			acc[txt] = y                              # Accumulate
			self.dateKeywordsParms.insert("end",(txt,y))

		#
		# Accumulative keywords from recurrent file.
		#
		self.accKeywordsParms.clear()                # allow upto 8 characters
		sk = acc.keys()
		sk.sort()
		for txt in sk:
			self.accKeywordsParms.insert("end",(txt,acc[txt]))

		self.listOfRigs = dte.allRigs                 # pObject.py
		self.listOfGroupRules = dte.groupRules        # Items
		if len(self.listOfRigs) > 0:
			xstr = []
			for rig in self.listOfRigs:
				xstr.append(rig.getEditableString())
			self.rigsText.settext("".join(xstr))
		else:
			self.rigsText.settext("")
		#
		# Get the editable string per group rule and print it.
		#
		if len(self.listOfGroupRules) > 0:
			xstr = []
			for g in self.listOfGroupRules:
				xstr.append(g.getEditableString())
			self.rulesText.settext("".join(xstr))
		else:
			self.rulesText.settext("")

		### End of function for m_selectMaster ###

	def m_selectGroupWell(self):
		"""
		This is called to set wells  from a group. 
		"""
		if self.workingCollection == None: return 
		collectionType, collectionName = self.workingCollection
		if collectionType == 'GROUP':
			#
			# The list of names are for groups... do nothing
			#
			return
		# In this case, you have injectors or producers. 
		listbox = self.listWellsPerGroup.component('listbox')
		sel = listbox.curselection()				# The selection
		if (len(sel) < 1): return                   # Bail if empty
		ndx = int(sel[0])                          	# The index of the selection
		name = listbox.get(ndx)
		ef = self.wellsList.component('entryfield')
		ef.setentry(name)
		self.m_selectSubListItem(name)


	def m_selectSubListItem(self,name):  
		if self.parserObject == None: return
		subLabel = self.wellsList.component('label') # for the title
		self.lastWellName = name                            # Check if date exists.
		if not self.parserObject.allDatesArray.has_key(self.lastDateName): return  
		subLabel['text'] = self.lastWellName
		self.showInfoForLastWell()

	def showInfoForLastWell(self):
		"""
		Shows accumulated information for well up to last date or at current date
		The value shown is determined by the showAccumulated Tkinter Variable.
		Note: The string for self.lastDateName and self.lastWellName must be set.

		"""
		well = cWellObject()
		well.setID(self.lastWellName)
		dte = self.parserObject.allDatesArray[self.lastDateName]
		supto  = dte.getDate()
		acc = self.showAccumulated.get()                   # 
		for dkey in self.listOfAllDates:
			tdate = self.parserObject.allDatesArray[dkey]  # get the date object.
			if acc == 0: 
				tdate = dte
			else:
				sd = tdate.getDate()                           # It's string.
				if sd > supto: break                           # Only upto last date selected.
			if tdate.Wells.has_key(self.lastWellName):         # Merge the data
				getwell = tdate.Wells[self.lastWellName] # The last modification is tracked.
				if getwell.isPseudo == 0:  			   # Merge only if well is not pseudo
					well.mergeData(getwell)              # The lastest is accumulated.
				else: 
					well = copy.copy(getwell)            # Overwrite any accumulations
			if acc == 0: break
		self.f_showWell(well)

	def f_showWell(self,thisWell):
		"""
		self.lastWell is set here.
		"""
		self.parametersTable.clear()
		for txt in cRateParser.sRateFileAllowedKeywords:
			y = thisWell.getKeywordValue(txt)    #
			self.parametersTable.insert("end",(txt,y))
		self.lastWell = thisWell;
		self.wellPseudoStatus.set(thisWell.isPseudo)  # for pseudo wells 
		self.showPerforationsForWell()                # for last well

	def mapObjToGui(self,modelParser): # Not the object
		self.parserObject = modelParser    # The parser object is cModelParser
		self.listOfWellNames  = self.parserObject.allWellNames.keys()  # Just the names please 
		self.listOfWellNames.sort()
		self.listOfAllDates  = self.parserObject.allDatesArray.keys()  # Just the names please 
		self.listOfAllDates.sort()
		self.lastDateName = ''
		self.lastWellName = ''
		listbox = self.masterList.component('scrolledlist') # Clear the list of subitem
		listbox.setlist(self.listOfAllDates)
		self.wellsList.setlist([])
	
	def setPerfColumn(self,action):
		if self.lastWell == None: 
			showwarning("Please select a well before you try to set the values in a column.")
			return
		selColumn = self.listOfColumns.get()
		#print " .._",  selColumn 
		if not selColumn in cPerfAllowedKeywords: return 
		column = cPerfAllowedKeywords.index(selColumn)  # This will be column index.
		if action == 'Clr':
			for tp in self.lastWell.perforations.values():
				tp.setKeywordValue(selColumn,'')
		elif action in [ 'Set', 'Inc', 'Mul' ]: 
			try:
				fval = float(self.valueEntry.get())
				incval = float(self.valueEntryInc.get())
			except:
				showwarning("Please use numeric values for this command....")
				return
			fmtstr = '%f'
			ival = int(fval)
			if (fval-ival) == 0: 
				fmtstr = '%d'
				fval = int(self.valueEntry.get())
				incval = int(self.valueEntryInc.get())
			skeys = self.lastWell.perforations.keys()
			skeys.sort()
			for key in skeys:
					tp = self.lastWell.perforations[key]
					sval = fmtstr % fval
					tp.setKeywordValue(selColumn,sval)
					if action == 'Inc': fval = fval + incval 
					if action == 'Mul': fval = fval * incval
		self.showPerforationsForWell()

	def mapGuiToObj(self,simulatorparms):   # place holder
		pass

	############################################################################
	# Tree manipulation functions
	############################################################################
	def m_addDate(self):
		dname = askstring("Date","Enter the date as YYYY-MM-DD. The MM must be 01,02,..,12. DD must 01,02, etc. as fit for month")
		if len(dname) <> 10: 
			showwarning("Ooops", "Invalid date format for input")
			return
		if self.parserObject.allDatesArray.has_key(dname):
			showwarning("Ooops", "The requested date " + dname + " already exists in the system")
			return
		masterLabel = self.masterList.component('label') # for the title
		masterLabel['text'] = dname                              # Set the master label to new date
		self.lastDate =  cDateObject(0)
		self.parserObject.allDatesArray[dname]=self.lastDate   
		self.lastDate.setDate(dname)

		# 
		# 
		#
		self.listOfAllDates  = self.parserObject.allDatesArray.keys()  # Just the names please 
		self.listOfAllDates.sort()
		self.masterList.setlist(self.listOfAllDates)
		self.lastDateName = dname
		self.listOfWellsPerDate = []
		self.wellsList.setlist([])
		masterLabel['text'] = self.lastDateName
		self.parametersTable.clear()                                  
		self.pseudoParmsTable.clear()                                  
		self.tableForPerforations.clear()                                  


	def m_deleteDate(self):
		reply = askyesno('Confirm!',"Are you sure you want to delete the date?")
		if reply <> True: return
		masterLabel = self.masterList.component('label') # for the title
		dname = masterLabel['text'] 
		if not self.parserObject.allDatesArray.has_key(dname): return 
		self.lastDate = None
		self.parametersTable.clear()                                  
		self.tableForPerforations.clear()                                  
		del(self.parserObject.allDatesArray[dname])

	def m_addWell(self):
		r =  self.showAccumulated.get()
		if r == 1: 
			showwarning("Turn off accumulated flag","Cannot add well in accumulated mode")
			return
		masterLabel = self.masterList.component('label') # for the title
		nm = masterLabel['text'] 
		if nm == 'Choose': 
			showwarning("Ooops", "Please select the BYDATE option before adding a well")
			return
		self.lastDate = self.parserObject.allDatesArray[nm]
		wname = askstring("WELLNAME","Enter an 8 character well name")
		if wname == None: return 
		if len(wname) <> 8: 
			showwarning("Ooops", "The name must be exactly 8 characters long")
			return
		self.lastWell = self.lastDate.addWell(wname)
		self.lastDate.existingWells.append(wname)
		self.lastDate.existingWells.sort()
		self.listOfWellsPerDate = self.lastDate.Wells.keys()
		self.listOfWellsPerDate.sort()
		self.wellsList.setlist(self.listOfWellsPerDate)
		self.tableForPerforations.clear()                                  

	def m_deleteOneWell(self):
		showwarning("Functionality not defined. ","Unable to determine where to delete well. \
		Cannot delete in Rates or Perfs or even Recurrent..... To be defined.");
		return
		
		r =  self.showAccumulated.get()
		if r == 1: 
			showwarning("Turn off accumulated flag","Cannot delete in accumulated mode")
			return
		r = self.m_resetDateAndWell()   # self.lastWell and self.lastDate are set.
		if r == 0: return
		nm = self.lastWell.getWellName()                     # Get name of well
		reply = askyesno('Confirm!',"Are you sure you want to delete " + nm + "?")
		if reply == True:
			del self.lastDate.Wells[nm]                          # Remove from this date.
			self.listOfWellsPerDate = self.lastDate.Wells.keys() # Get new name of wells
			self.listOfWellsPerDate.sort()                       # sort it.
			self.wellsList.setlist(self.listOfWellsPerDate)      # Clear perforations
			self.tableForPerforations.clear()                                  
			self.lastWell = None
			self.listOfWellNames.remove(nm)


	def m_addPerf(self):
		if self.lastWell == None: 
			showwarning("Ooops", "Please select a well before you try to add or delete a perforation")
			return 
		self.lastWell.addAnotherPerforation()
		self.showPerforationsForWell()

	def m_resetDateAndWell(self):
		mLabel = self.wellsList.component('label') # for the title
		dLabel = self.masterList.component('label') # for the title
		dname = dLabel['text']
		wname = mLabel['text']		
		try:
			self.lastDate = self.parserObject.allDatesArray[dname]
			self.lastWell = self.lastDate.Wells[wname]
		except:
			showwarning('Error', "Select a well and date ")
			return 0
		if self.lastWell == None: 
			showwarning('Error', "Unable to find date ")
			return 0
		if self.lastWell == None: 
			showwarning('Error', "Unable to find well")
			return 0
		return 1


	def m_delPerf(self):
		r = self.m_resetDateAndWell() 
		if r == 0: return 
		rsel =  self.tableForPerforations.curselection()
		if len(rsel) < 0: return
		rownumber = rsel[0] 
		print "You have selected ", rsel  , "Row number = ", rownumber
		reply = askyesno('Confirm!',"Are you sure you want to delete the perforation line?")
		if reply <> True: return
		rsel =  self.tableForPerforations.delete(rsel)          # Remove from table.
		self.lastWell.clearPerforations()                       # Remove all from well
		self.m_savePerforationsForWell(self.lastWell)           # Take a snapshot of the table
		self.showPerforationsForWell()

	def showPerforationsForWell(self,tp=None):
		self.tableForPerforations.clear()		    # start with clean slate
		self.lastPerf = tp;                         # Save this for later. 
		tkeys = self.lastWell.perforations.keys()   # Get the keywords for perforations
		tkeys.sort()                                # Sort them alphabetically
		for tk in tkeys:                            # For each perforation
			tp =  self.lastWell.perforations[tk]
			rowData = []
			for txt in cPerfAllowedKeywords:
				y = tp.getKeywordValue(txt)   #
				rowData.append(y)
			self.tableForPerforations.insert("end",tuple(rowData))

	def f_enmasseSetValue(self):
		""" 
		Untested code -  I have to set a column of date here
		"""
		if self.lastPerf <> None and self.lastWell <> None: 
			reply = askyesno('Whoa!',"Are you sure you want to set the non-empty entries for all other Perfs in this well?")
			sz = self.parametersTable.size()
			for r in range(sz):
				parm = self.parametersTable.get(r)
				self.lastWell.setKeywordValue(parm[0],parm[1])
				if parm[1] <> '': 
					for perf in self.lastWell.perforations.values():
						perf.setKeywordValue(txt,parm[1])   # Validate here @@@@!!!!LOOK I AM NOT DOING IT HERE 

	def m_saveValues(self):
		"""
		Collect the stuff from the form on frm_item and plunk it into the well or perforation
		"""
		r = self.m_resetDateAndWell() 
		if r == 0: return 
		sz = self.parametersTable.size()
		for r in range(sz):
			parm = self.parametersTable.get(r)
			self.lastWell.setKeywordValue(parm[0],parm[1])
		self.m_savePerforationsForWell(self.lastWell)

	def m_savePerforationsForWell(self,wp):
		"""
		The wp is a pointer to a well object.
		"""
		sz = self.tableForPerforations.size()
		print "Size in m_savePerforationsForWell", sz, self.lastWell.getKeywordValue('NAME')
		colValues = {}
		for r in range(sz):                                   # For each row. 
			parm = self.tableForPerforations.get(r)           # Get the row.
			i = 0 
			for x in cPerfAllowedKeywords:           # Get the columns
				colValues[x] = parm[i]
				i += 1
			tp = cPerfObject(None)
			for key in colValues.keys(): 
				tp.setKeywordValue(key,colValues[key])
			tp.setPerfName()
			wp.addPerforation(tp) 

