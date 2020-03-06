
import  wx
import wx.lib.foldpanelbar as fpb

class mmgrDataSource:
	def __init__(self,mytuple3): self.data = mytuple3
	def SetData(self,data): self.data = data
	def GetColumnHeaders(self): return ('TYPE','Path', 'Time')
	def GetCount(self): return len(self.data)
	def GetItem(self,i): return self.data[i]
	def UpdateCache(self,start,end): pass

class mmgrVirtualList(wx.ListCtrl):
	def __init__(self,parent,datasource):
		wx.ListCtrl.__init__(self,parent,style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VIRTUAL)
		self.dataSource = datasource
		self.Bind(wx.EVT_LIST_CACHE_HINT,self.DoCacheItems)
		self.SetItemCount(datasource.GetCount())
		columns = datasource.GetColumnHeaders()
		for col, text in enumerate(columns): self.InsertColumn(col,text)

	def DoCacheItems(self,evt):
		self.dataSource.UpdateCache(evt.GetCacheFrom(),evt.GetCacheTo())
	
	def OnGetItemText(self,item,col):
		data = self.dataSource.GetItem(item)
		if col >= len(data):return ''
		return data[col]
	
	def OnGetItemAttr(self,item): return None
	def OnGetItemImage(self,item): return 0 

	def ResizeColumns(self):
		#clen = range(len(self.dataSource.GetColumnHeaders()))
		print "Setting column width"
		clen = range(3)
		for i in clen: self.SetColumnWidth(i,wx.LIST_AUTOSIZE)

		
class mmgr_ProjectsPanel(wx.Panel):
	def __init__(self, *args, **kwds):
		# begin wxGlade: pwxMMprojects.__init__
		#kwds["style"] = wx.DEFAULT_FRAME_STYLE
		self.master = None
		wx.Panel.__init__(self, *args, **kwds)
		self.sizer_9_staticbox = wx.StaticBox(self, -1, "Operations")
		self.sizer_10_staticbox = wx.StaticBox(self, -1, "Projects")
		self.label_xmlfilename = wx.StaticText(self, -1, "projects.xml", style=wx.ALIGN_LEFT)
		self.list_box_projectNames = wx.ListBox(self, -1, choices=[], style=wx.LB_SINGLE)
		self.label_filler = wx.StaticText(self, -1, " for ", style=wx.ALIGN_RIGHT)
		self.label_username = wx.StaticText(self, -1, "label_1", style=wx.ALIGN_RIGHT)
		self.button_new_project = wx.Button(self, -1, "New Prj")
		self.button_del_project = wx.Button(self, -1, "Del Prj")
		self.button_addCaseToProject = wx.Button(self, -1, "Add Case")
		self.button_delCaseToProject = wx.Button(self, -1, "Del Case")
		self.button_import_user = wx.Button(self, -1, "User")
		self.button_save_project = wx.Button(self, -1, "Save")

		self.__set_properties()
		self.__do_layout()
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: pwxMMprojects.__set_properties
		# self.SetTitle("frame_2")
		pass
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: pwxMMprojects.__do_layout
		sizer_7 = wx.BoxSizer(wx.VERTICAL)
		sizer_8 = wx.BoxSizer(wx.VERTICAL)
		sizer_9 = wx.StaticBoxSizer(self.sizer_9_staticbox, wx.VERTICAL)
		sizer_10 = wx.StaticBoxSizer(self.sizer_10_staticbox, wx.VERTICAL)
		sizer_90 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_90.Add(self.label_xmlfilename, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
		sizer_90.Add(self.label_filler, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
		sizer_90.Add(self.label_username, 0, wx.EXPAND|wx.ADJUST_MINSIZE|wx.ALIGN_RIGHT, 0)
		sizer_10.Add(sizer_90, 0, wx.ADJUST_MINSIZE, 0)
		sizer_10.Add(self.list_box_projectNames, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_8.Add(sizer_10, 1, wx.EXPAND, 0)
		sizer_91 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_91.Add(self.button_new_project, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_91.Add(self.button_del_project, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_9.Add(sizer_91,1,wx.EXPAND,0)
		sizer_92 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_92.Add(self.button_addCaseToProject, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_92.Add(self.button_delCaseToProject, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_9.Add(sizer_92,1,wx.EXPAND | wx.ADJUST_MINSIZE,0)
		sizer_93 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_93.Add(self.button_import_user, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_93.Add(self.button_save_project, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_9.Add(sizer_93,1,wx.EXPAND | wx.ADJUST_MINSIZE,0)
		sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)
		sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)
		self.SetAutoLayout(True)
		self.SetSizer(sizer_7)
		sizer_7.Fit(self)
		sizer_7.SetSizeHints(self)
		self.Layout()
		# end wxGlade

		self.Bind( wx.EVT_BUTTON, self.cb_userImport, self.button_import_user)
		self.Bind( wx.EVT_BUTTON, self.cb_newProject, self.button_new_project)
		self.Bind( wx.EVT_BUTTON, self.cb_delProject, self.button_del_project)
		self.Bind( wx.EVT_BUTTON, self.cb_addCaseProject, self.button_addCaseToProject)
		self.Bind( wx.EVT_BUTTON, self.cb_delCaseProject, self.button_delCaseToProject)
		self.Bind( wx.EVT_LISTBOX, self.cb_showProject, self.list_box_projectNames)
		self.Bind( wx.EVT_BUTTON, self.cb_saveProject, self.button_save_project)

	def	cb_userImport(self,event): self.master.handleUserImport(self,event)
	def	cb_saveProject(self,event): self.master.handleSaveProject(self,event)
	def	cb_newProject(self,event): self.master.handleNewProject(self,event)
	def	cb_delProject(self,event): self.master.handleDelProject(self,event)
	def	cb_addCaseProject(self,event): self.master.handleAddCases(self,event)
	def	cb_delCaseProject(self,event): self.master.handleDelCases(self,event)
	def	cb_showProject(self,event): 
		pname = self.list_box_projectNames.GetStringSelection()
		self.master.handleShowProject(pname)

	def SetXMLfilename(self, name): self.label_xmlfilename.SetLabel(name)
	def SetUserName (self, name): self.label_username.SetLabel(name)
	def GetSelectedProject(self): return self.list_box_projectNames.GetStringSelection()
	def SetSelectedProject(self,name):  self.list_box_projectNames.SetStringSelection(name)
	def SetProjectsList(self,names): self.list_box_projectNames.Set(names)
	def setMaster(self, master): self.master = master



class NotCollapsed(wx.Frame):
	def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
				 size=(400,300), style=wx.DEFAULT_FRAME_STYLE):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		
		self.SetIcon(GetMondrianIcon())
		self.SetMenuBar(self.CreateMenuBar())

		self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self.statusbar.SetStatusWidths([-4, -3])
		self.statusbar.SetStatusText("Kamran Husain ", 0)
		self.statusbar.SetStatusText("Welcome to wxPython!", 1)

		pnl = fpb.FoldPanelBar(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
						   fpb.FPB_DEFAULT_STYLE | fpb.FPB_VERTICAL)

		item = pnl.AddFoldPanel("Test Me", collapsed=False)
		
		button1 = wx.Button(item, wx.ID_ANY, "Collapse Me")
		
		pnl.AddFoldPanelWindow(item, button1, fpb.FPB_ALIGN_LEFT)
		pnl.AddFoldPanelSeparator(item)
		
		button1.Bind(wx.EVT_BUTTON, self.OnCollapseMe)

		item = pnl.AddFoldPanel("Test Me Too!", collapsed=True)
		button2 = wx.Button(item, wx.ID_ANY, "Expand First One")
		pnl.AddFoldPanelWindow(item, button2, fpb.FPB_ALIGN_LEFT)
		pnl.AddFoldPanelSeparator(item)

		button2.Bind(wx.EVT_BUTTON, self.OnExpandMe)
		
		newfoldpanel = FoldTestPanel(item, wx.ID_ANY)
		pnl.AddFoldPanelWindow(item, newfoldpanel)

		pnl.AddFoldPanelSeparator(item)

		pnl.AddFoldPanelWindow(item, wx.TextCtrl(item, wx.ID_ANY, "Comment"),
							   fpb.FPB_ALIGN_LEFT, fpb.FPB_DEFAULT_SPACING, 20)

		item = pnl.AddFoldPanel("Some Opinions ...", collapsed=False)
		pnl.AddFoldPanelWindow(item, wx.CheckBox(item, wx.ID_ANY, "I Like This"))
		pnl.AddFoldPanelWindow(item, wx.CheckBox(item, wx.ID_ANY, "And Also This"))
		pnl.AddFoldPanelWindow(item, wx.CheckBox(item, wx.ID_ANY, "And Gimme This Too"))

		pnl.AddFoldPanelSeparator(item)

		pnl.AddFoldPanelWindow(item, wx.CheckBox(item, wx.ID_ANY, "Check This Too If You Like"))
		pnl.AddFoldPanelWindow(item, wx.CheckBox(item, wx.ID_ANY, "What About This"))

		item = pnl.AddFoldPanel("Choose One ...", collapsed=False)
		pnl.AddFoldPanelWindow(item, wx.StaticText(item, wx.ID_ANY, "Enter Your Comment"))
		pnl.AddFoldPanelWindow(item, wx.TextCtrl(item, wx.ID_ANY, "Comment"),
							   fpb.FPB_ALIGN_WIDTH, fpb.FPB_DEFAULT_SPACING, 20, 20)
		self.pnl = pnl


	def CreateMenuBar(self):

		FoldPanelBarTest_Quit = wx.NewId()
		FoldPanelBarTest_About = wx.NewId()
		
		menuFile = wx.Menu()
		menuFile.Append(FoldPanelBarTest_Quit, "E&xit\tAlt-X", "Quit This Program")

		helpMenu = wx.Menu()
		helpMenu.Append(FoldPanelBarTest_About, "&About...\tF1", "Show About Dialog")

		self.Bind(wx.EVT_MENU, self.OnQuit, id=FoldPanelBarTest_Quit)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=FoldPanelBarTest_About)

		value = wx.MenuBar()
		value.Append(menuFile, "&File")
		value.Append(helpMenu, "&Help")

		return value


	# Event Handlers

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

"""
For commands ...
"""

class mmgr_CommandsPanel(wx.Panel):
	def __init__(self, *args, **kwds):
		#kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Panel.__init__(self, *args, **kwds)
		self.sizer_11_staticbox = wx.StaticBox(self, -1, "Commands")
		#self.button_batch = wx.Button(self, -1, "Batch")
		self.button_save_all = wx.Button(self, -1, "Save All")
		self.button_save_and_quit = wx.Button(self, -1, "Save And Quit")
		self.button_save_as = wx.Button(self, -1, "Save As ...")

		self.__set_properties()
		self.__do_layout()
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: MMFrameCmds.__set_properties
		#self.SetTitle("frame_mm_frameCmds")
		# end wxGlade
		pass

	def __do_layout(self):
		# begin wxGlade: MMFrameCmds.__do_layout
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_11 = wx.StaticBoxSizer(self.sizer_11_staticbox, wx.VERTICAL)
		#sizer_11.Add(self.button_batch, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_11.Add(self.button_save_all, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_11.Add(self.button_save_and_quit, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_11.Add(self.button_save_as, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		
		sizer_1.Add(sizer_11, 1, wx.EXPAND, 0)
		self.SetAutoLayout(True)
		self.SetSizer(sizer_1)
		sizer_1.Fit(self)
		sizer_1.SetSizeHints(self)
		self.Layout()
