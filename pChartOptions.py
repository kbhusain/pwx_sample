
from Tkinter import *
from tkFileDialog import *
from tkSimpleDialog import *
import Pmw
from pMathUtils import *
from tkMessageBox import *
import os
import matplotlib.pylab as mtlab
from matplotlib.numerix import arange, sin, pi
from matplotlib.axes import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.dates import date2num, num2date
from matplotlib.widgets import Cursor
from copy import copy

LINETYPES = ['-','--','-.',':',' ']
COLORTYPES= ['#0000FF','#00FF00','#FF0000','#FF00FF','#FFFF00','#FF00FF','#000000']
MARKERTYPES = [' ','+','o',',','.','1','2','3','4','<','>','D','H','^','v','p','h','_','|']

def askcolorstring(titlestr='Choose'):
	ret = askcolor(title="Choose Color")
	scolor = ret[0]
	if scolor == None: return None
	return '#%02X%02X%02X' % (scolor[0],scolor[1],scolor[2]) 

		
def xml_saveLineParameters(dparms,basename=None):
	"""
	Writes in os.getenv('HOME') + os.sep + '/powersdata/simplots.xml' 
	These are parameters that are specific to the type of lines, etc.
	"""
	fname = ''
	if os.name =='nt': 
		try:
			os.mkdir('D:/powersdata')
		except:
			pass
		if basename == None: 
			fname = 'd:/powersdata/simplots.parms'
		else: 
			fname = basename
	else: 
		if basename == None: 
			fname = os.getenv('HOME') + '/powersdata/simplots.parms'
		else:
			fname = basename 
	# Now try to write to it. 		
	try:
		nfd = open(fname, 'w')
	except:
		print " I cannot save %s the defaults file" % fname
		return
		
			
	nfd.write('<?xml version="1.0" encoding="iso-8859-1" standalone="yes" ?>\n')
	nfd.write('<SIMPLOTS>\n')
	nfd.write('<PLOTPARMS>\n')
	skeys = dparms.keys()
	for k in skeys: 
		if k == 'LINEPARAMETERS': continue
		nfd.write('<%s value="%s" />\n' % (k,dparms[k]))
	nfd.write('</PLOTPARMS>\n')
	lineParameters = dparms['LINEPARAMETERS']
	nfd.write('<LINEPARMS count="%s">\n' % len(lineParameters))
	for xln in lineParameters: 
		x0 = tuple(xln)
		xstr ='<LINEPARM index="%s" linestyle="%s" linecolor="%s" linewidth="%s" marker="%s" markercolor="%s" markersize="%d"/>\n' % x0 
		nfd.write(xstr)
	nfd.write('</LINEPARMS>\n')
	nfd.write('</SIMPLOTS>\n')
	nfd.close()

	############################ Handlers for buttons ###################################
def xml_readLineParameters(basename=None):
	"""
	Looks in os.getenv('HOME') + os.sep + '/powersdata/simplots.xml' for resource file.
	"""
	fname = ''
	if os.name =='nt': 
		try:
			os.mkdir('D:/powersdata')
		except:
			pass
		if basename == None: 
			fname = 'd:/powersdata/simplots.xml'
		else:
			fname =  basename 
	else: 
		if basename == None: 
			fname = os.getenv('HOME') + '/powersdata/simplots.xml'
		else:
			fname =  basename 
		
	try:
		nfd = open(fname,'r')
	except:
		return None
	try:
		dom = minidom.parse(fname)
	except:
		return None

	lineTypes = LINETYPES 
	colors    = COLORTYPES
	markerTypes = MARKERTYPES
		
	dparms = {} 
	lineParameters = []
	self.maxLines = 12
	for i in range(self.maxLines):
		j = i % len(self.markerTypes) 
		k = i % len(self.colors)
		# index, width, colors,lnw, marker, markerColor, markerSize  
		lineParameters.append([i+1,'-', colors[k],1, 'o', colors[k],1])
	
	dparms['LINEPARAMETERS'] = lineParameters 
	nodes = dom.getElementsByTagName('PLOTPARMS')  # All the notes are read here.
	for nd in nodes: 
		for chld in nd.childNodes:
			dparms[chld.nodeName] = str(nd.getAttribute('value'))
	nodes = dom.getElementsByTagName('LINEPARMS')  # All the notes are read here.
	for nd in nodes: 
		for chld in nd.childNodes:
			k = 0
			if chld.nodeName == 'LINEPARM': 
				ls = chld.getAttribute('linestyle')
				id = int(chld.getAttribute('index'))
				lc = chld.getAttribute('linecolor')
				lw = int(chld.getAttribute('linewidth'))
				mk = chld.getAttribute('marker')
				mc = chld.getAttribute('markercolor')
				ms = int(chld.getAttribute('markersize'))
				lineParameters[k]  = [id,ls,lc,lw,mk,mc,ms]
				k = k + 1
	return dparms
		
################################################################################################################
# Chart option setting dialog as one class.
################################################################################################################
class chartOptions(Frame):
	"""
	Class to handle setting the lines etc. for plots.
	The incoming object must have a Tk() in chartOptsDlg or a frame.

	Only the number of lines in question should be displayed.

	"""
	def __init__(self,obj,ftouse,linenames):
		Frame.__init__(self,ftouse)
		self.lineNames = linenames
		self.lineParmBtns    = [ ]
		self.lineParameters   = [ ]
		self.obj = obj
		self.cellForm = self
		self.showGrid=False
		self.borderColor = 'white'
		self.faceColor   = 'white'
		self.legendLocation = 1
		
		self.generalFrame = Frame(self.cellForm)
		self.generalFrame.pack(side=TOP,fill=X,expand=0)
		self.gridLineStyle = '-'
		self.gridOptions = Pmw.OptionMenu(self.generalFrame,labelpos=W,\
			label_text='Grid', 
			command= self.handleGridOption,
			items=('None - Hide','- Lines','-- Dashed','-. DashDot',': Dotted'))
		self.gridOptions.pack(side=LEFT,expand=0)

		
		self.legendLocations = { 'None' : 0 , ' Upper Right' : 1, ' Upper Left' :2, 'Lower Left' : 3, 'Lower Right' : 4, 
				 'Center Left' : 6, 'Center Right': 7, 'Lower Center': 8, ' Upper Center': 9, 
				'Center': 10, 'Outside Rt': 11}
		skeys = self.legendLocations.keys()
		skeys.sort()
		self.legendOptions = Pmw.OptionMenu(self.generalFrame,labelpos=W,\
			label_text='Legend Location', 
			command= self.handleLegendOption,
			items=skeys)
		self.legendOptions.pack(side=LEFT,expand=0)
	
		
		#self.borderColorBtn = Button(self.generalFrame,bg=self.borderColor,fg='blue',text='Border')
		#self.borderColorBtn.pack(side=RIGHT)
		#self.borderColorBtn['command'] = lambda s=self,b=self.borderColorBtn: s.setBtnColor(b)
		#self.faceColorBtn = Button(self.generalFrame,bg=self.faceColor,fg='blue',text='Face')
		#self.faceColorBtn.pack(side=RIGHT)
		#self.faceColorBtn['command'] = lambda s=self,b=self.faceColorBtn: s.setBtnColor(b)
		self.lineParameters = obj.lineParameters
		if len(self.lineNames) == 0:
			self.lineNames = [ "Ln %d" % (i+1) for i in range(self.obj.maxLines) ]
			self.maxLines = self.obj.maxLines
		else:
			self.maxLines = len(self.lineNames)
		self.colors = self.obj.colors
		self.markerTypes = self.obj.markerTypes
		self.lineTypes = self.obj.lineTypes
		markerw = range(1,11) 
		linew   = range(0,11) 

		##########################################################################
		# Only show the number of lines you have to.
		##########################################################################
		for i in range(self.maxLines):
			k = i % len(self.colors) 
			self.myLineParmFrame = Frame(self.cellForm)
			lbl = Label(self.myLineParmFrame ,text=self.lineNames[i])
			lbl.pack(side=LEFT,expand=0)	
			lnStyleOpts = Pmw.OptionMenu(self.myLineParmFrame,labelpos=W,\
					label_text='Style', menubutton_width = 16, items=self.lineTypes)
			lnStyleOpts.pack(side=LEFT,expand=0)
			lnClrBtn = Button(self.myLineParmFrame,text='Color',fg='white',bg=self.colors[k])
			lnClrBtn['command'] = lambda s=self,b=lnClrBtn: s.setBtnColor(b)
			lnClrBtn.pack(side=LEFT)
			lnWdOpts = Pmw.OptionMenu(self.myLineParmFrame,labelpos=W,\
					label_text='Line Wd', menubutton_width = 8, items=map(str,linew))
			lnWdOpts.pack(side=LEFT)
			markerOpts = Pmw.OptionMenu(self.myLineParmFrame,labelpos=W,\
					label_text='Marker', 
					menubutton_width = 8, 
					items=self.markerTypes)
			markerOpts.pack(side=LEFT,expand=0)
			markerColorBtn = Button(self.myLineParmFrame,text='Color',fg='white',bg=self.colors[k])
			markerColorBtn.pack(side=LEFT)
			markerColorBtn['command'] = lambda s=self,b=markerColorBtn: s.setBtnColor(b)
			mszOpts = Pmw.OptionMenu(self.myLineParmFrame,labelpos=W,\
					label_text='Marker Sz', menubutton_width = 8, items=map(str,markerw))
			mszOpts.pack(side=LEFT)
			self.lineParmBtns.append([lbl,lnStyleOpts,lnClrBtn,lnWdOpts,markerOpts,markerColorBtn,mszOpts])
			self.myLineParmFrame.pack(side=TOP)

		self.cellBtnForm = Frame(self.cellForm)
		self.applyLineOptsBtn = Button(self.cellBtnForm,text='Apply and Save', \
			command=self.handleApplyButton, fg='white', bg='blue')
		self.applyLineOptsBtn.pack(side=LEFT)
		self.saveLineOptsBtn = Button(self.cellBtnForm,text='Save', command=self.handleSaveButton)
		self.saveLineOptsBtn.pack(side=RIGHT)
		self.readLineOptsBtn = Button(self.cellBtnForm,text='Read From', command=self.handleReadFromButton)
		self.readLineOptsBtn.pack(side=RIGHT)
		self.readLineOptsBtn = Button(self.cellBtnForm,text='Read Default', command=self.handleReadButton)
		self.readLineOptsBtn.pack(side=RIGHT)
		self.cellBtnForm.pack(side=TOP,fill=X,expand=1)
		self.cellForm.pack(side=TOP,fill=BOTH,expand=1)

		#
		# Put the legend here.
		#
		lblText = """
		Lines  : - solid;  -- dashed; -. dash-dot; : dotted; . points;
		Markers: . points; o circles; ^ triangle up; v triangle down; < left; > right;
		Markers: s square; + plus sign; x cross; D diamond; 1,2,3,4 tripod symbols;
		Markers: H or h hexagon; p pentagon; | vertical lines
		**Note** Marker symbols have to be >= size 7 to show some shapes
		"""
		markDescLabel=Label(self.cellForm,text=lblText,justify='left')
		markDescLabel.pack(side=BOTTOM,fill=X,expand=0)
	
		
		
		
	def setBtnColor(self,btn):
		ret = askcolorstring('Set Color')		
		if ret == None: return 
		btn['bg'] = ret

	def handleLegendOption(self,parm):
		self.legendLocation = self.legendLocations.get(parm,1)
		
		
		
	def handleGridOption(self,parm):
		items = parm.split()
		if items[0] == 'None': 
			self.showGrid=False
			self.gridLineStyle = '-'
		else: 
			self.showGrid=True
			self.gridLineStyle = items[0]

	def handleSaveButton(self):
		ofile = asksaveasfilename(filetypes=[("Parameters","*.parms"),("All Files","*")])
		if ofile: self.saveLineParameters(ofile)

	def handleReadFromButton(self): 		
		ifile = askopenfilename(filetypes=[("Parameters","*.parms"),("All Files","*")])		
		if ifile: 
			self.readLineParameters(ifile)
			self.applyReadOptions(self.obj.lineParameters)
		
	def handleReadButton(self):
		self.readLineParameters()
		self.applyReadOptions(self.obj.lineParameters)

	def applyReadOptions(self,lineParameters):	
		self.lineParameters = copy(lineParameters)
		id = 0 
		for parms in self.lineParameters:
			#id = parms[0] - 1
			try:
				lbl,lnStyleOpts,lnClrBtn,lnWdOpts,markerOpts,markerColorBtn,mszOpts  \
					=  self.lineParmBtns[id]
			except:
				continue
			print parms
			lnStyleOpts.invoke(self.lineTypes.index(parms[1]))
			lnClrBtn['bg'] = parms[2]
			lnWdOpts.invoke(str(parms[3]))
			markerOpts.invoke(self.markerTypes.index(parms[4]))
			markerColorBtn['bg'] = parms[5]
			mszOpts.invoke(str(parms[6]))
			self.lineParmBtns[id] = [lbl,lnStyleOpts,lnClrBtn,lnWdOpts,markerOpts,markerColorBtn,mszOpts]
			id = id + 1 

		self.showGrid = self.obj.showGrid
		self.gridLineStyle = self.obj.gridLineStyle 

	def handleApplyButton(self,save=1):
		"""
		#
		# Collect parameters from self.myLineParmBtns and put them in self.lineParameters
		# self.lineParmBtns.append([lbl,lnStyleOpts,lnClrBtn,markerOpts,markerColorBtn,lnWdOpts])
		# self.lineParameters.append([i+1, '-', self.colors[k],lw,self.markerTypes[j], self.colors[k],mw])
		#
		"""
		#self.faceColor = self.faceColorBtn['bg']
		#self.borderColor = self.borderColorBtn['bg']
		self.obj.showGrid      = self.showGrid
		self.obj.gridLineStyle = self.gridLineStyle 
		#self.obj.borderColor = self.borderColor 
		#self.obj.faceColor = self.obj.faceColor
		self.obj.legendLocation = self.legendLocation
		self.lineParameters = []
		for i in range(self.maxLines):
			ilabel, lnOpts,lnClrBtn,lnWdOpts,mkOpts,mkClrBtn, mkSzOpts = self.lineParmBtns[i]
			ls = lnOpts.getvalue()
			lc = lnClrBtn['bg']
			lw = int(lnWdOpts.getvalue())
			mt = mkOpts.getvalue()
			mc = mkClrBtn['bg']
			ms = int(mkSzOpts.getvalue())
			#print lineStyle, lineColor, markerStyle, markerColor, lineWidth
			self.lineParameters.append([i+1,ls,lc,lw,mt,mc,ms])
		self.obj.lineParameters = copy(self.lineParameters)   # Reflect to master object.
		self.obj.applyLineParameters();                       # Save to master object only.
		if save == 1: 
			dparms = self.mapObjToLineParms()
			xml_saveLineParameters(dparms)
		self.obj.m_canvas.draw(); 
		self.obj.m_canvas.show()
				
	def mapObjToLineParms(self):
		dparms = {}
		dparms['LINEPARAMETERS']= self.lineParameters
		dparms['SHOWGRID'] 		= self.showGrid
		dparms['GRIDLINESTYLE'] = self.gridLineStyle 
		dparms['BORDERCOLOR']   = self.borderColor
		dparms['FACECOLOR']     = self.faceColor
		dparms['LEGENDLOCATION'] = str(self.legendLocation)
		return dparms; 
		
	def mapLineParmsToObj(self,dparms):
		p = dparms.get('LINEPARAMETERS',None) 
		if p <> None: self.lineparameters = p 
		self.showGrid = dparms.get('SHOWGRID',1)
		self.gridLineStyle  = dparms.get('GRIDLINESTYLE',' ')
		self.borderColor = dparms.get('BORDERCOLOR','#FFFFFF')   
		self.faceColor = dparms.get('FACECOLOR','#FFFFFF')
		self.legendLocation = dparms.get('LEGENDLOCATION','1')
		if self.obj <> None: 
			self.obj.borderColor = self.borderColor 
			self.obj.faceColor = self.obj.faceColor
			self.obj.showGrid = self.showGrid
			self.obj.gridLineStyle = self.gridLineStyle
			self.obj.legendLocation = int(self.legendLocation)
		
	def saveLineParameters(self,fname=None):
		dparms = self.mapObjToLineParms()
		xml_saveLineParameters(dparms,fname)
		
	def readLineParameters(self):
		dparms = xml_readLineParameters()
		if dparms <> None:		self.mapObjToLineParms(dparms)
				

class simpleGraphSetup:
	"""
	This dialog is similar to the line setup..
	The following items will be set: 
		Line color
		Line width
		Symbol Type (for line style)
	"""
	def __init__(self,master,obj): 
		self.applied = 0
		self.master = master
		self.m_df = Frame(self.master)
		self.m_df.pack()
		self.m_theplot = obj
		self.m_elNames  = self.m_theplot.getPlotNames()
		self.m_selectedTraceLabel = Label(self.m_df,text='Select Trace')
		self.m_selectedTraceLabel.pack(side=TOP,fill=X,expand=1)

		self.m_elName = Pmw.ComboBox(self.m_df, scrolledlist_items=self.m_elNames,
                                   entry_width=12, entry_state="disabled",
                                   selectioncommand = self.ripple)
		self.m_elName.pack(fill = 'both', expand = 1, padx = 8, pady = 8)

		############### Line Color ##################
		frm_1 = Frame(self.m_df)
		frm_1.pack(fill=NONE,expand=1)
		a = lambda s=self,x=0: s.setLineColor(x)
		self.m_colorSelect = Button(frm_1,text="Line Color Dialog", command=a)
		self.m_colorSelect.pack(side=LEFT,fill=X,expand=1,padx=8,pady=8)
		self.m_selectedColorLabel = Label(frm_1,background='blue',text='...')
		self.m_selectedColorLabel.pack(side=RIGHT,fill=NONE,expand=1)
		############### Line Width ##################
		#self.m_linBox = self.cBox(self.m_df, 'Line thickness:', (0, 1, 2, 3, 4))
		frm_1 = Frame(self.m_df)
		frm_1.pack(fill=NONE,expand=1)
		self.m_linBox = Pmw.Counter(frm_1,label_text='Line Width',labelpos=W,entryfield_value='1.0',datatype={'counter':'real'},
			entryfield_validate={'validator':'real','min':'0','max':10}, increment=0.2)
		self.m_linBox.pack(side=TOP,fill=BOTH,expand=1)
		############### Symbols ##################
		self.m_symBox = self.cBox(self.m_df, 'Symbols:', self.m_theplot.m_symbolCodes.keys())

		frm_1 = Frame(self.m_df)
		frm_1.pack(fill=NONE,expand=1)
		self.m_bOK = Button(frm_1,text='OK', command = self.close)
		self.m_bOK.pack(side=LEFT,fill=NONE,expand=1)
		self.m_bApply = Button(frm_1,text='Apply', command = self.apply)
		self.m_bApply.pack(side=RIGHT,fill=NONE,expand=1)
		##self.m_bXHide = Button(self.m_df,text='Hide', command = self.hideMe)
		##self.m_bXHide.pack(side=BOTTOM,fill=BOTH,expand=1)

		##self.m_bXShow = Button(self.m_df,text='Show', command = self.ShowMe)
		##self.m_bXShow.pack(side=BOTTOM,fill=BOTH,expand=1)


	def setLineColor(self,c=1):
		ret = askcolorstring("Choose Color")
		if ret <> None: self.m_selectedColorLabel['bg'] = ret

	def cBox(self,f, label, items):
		box = Pmw.ComboBox(f, label_text = label, labelpos = 'w', scrolledlist_items = items)
		box.pack(fill = 'both', expand = 1, padx = 8, pady = 8)
		return box

	def close(self):
		"""
		The applied flag is set to 0 explicitly.
		"""
		self.applied = 0

	def ripple(self,value):
		elName = value
		element = self.m_theplot.getPlotElement(value)
		

		#print "Element symbol =[", element.m_symbol,"]"
		print "keys = ",		self.m_theplot.m_symbolCodes.keys()
		for k in self.m_theplot.m_symbolCodes.keys():
			if k == element.m_symbol:
				self.m_symBox.selectitem(k)
				b = self.m_symBox.component('entryfield') 
				b.setentry(k)
				#print "Setting ...", k
		
		#self.m_scoBox.selectitem(self.m_g.element_cget(elName, "fill"))
		#b = self.m_scoBox.component('entryfield')
		#b.setentry(self.m_g.element_cget(elName, "fill"))
		#self.m_isolBox.selectitem(self.m_g.element_cget(elName, "outline"))
		#b = self.m_isolBox.component('entryfield')
		#b.setentry(self.m_g.element_cget(elName, "outline"))
		#self.m_smtBox.selectitem(self.m_g.element_cget(elName, "smooth"))

		b = self.m_linBox.component('entryfield')
		b.setentry(str(element.m_lineWidth))
		
		#b = self.m_pixBox.component('entryfield')
		#b.setentry(self.m_g.element_cget(elName, "pixels"))
		b =None

	def hideMe(self):
		elName = self.m_elName.get()
		if (elName <> 'None'):
			self.m_g.element_configure(elName,hide=1)

	def showMe(self):
		elName = self.m_elName.get()
		if (elName <> 'None'):
			self.m_g.element_configure(elName,hide=0)

	def apply(self):
		self.applied = 0
		elName = self.m_elName.get()
		element = self.m_theplot.getPlotElement(elName)
		if (elName <> None):
			# Get color from the
			element.m_lineColor = self.m_selectedColorLabel['bg']
			kc = self.m_symBox.get()
			element.m_symbol = self.m_theplot.m_symbolCodes[kc] 
			#print "LOOOK ", kc, self.m_theplot.m_symbolCodes[kc], element.m_symbol
			element.m_lineWidth = float(self.m_linBox.get())
			self.applied = 1
			self.m_theplot.redraw()

