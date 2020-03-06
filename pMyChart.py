"""
 A very simple XY plotter.
 October 5, 2004 - Kamran - replacing the BLT calls with matplotlib
 July 13, 2003 - Kamran - Added limits format
 10/8/2003 Added histogram support for raw X value on axis.
 05/1/2003 Added barchart  support for raw X value on axis.
"""

###########################################################################

import Numeric
import matplotlib
matplotlib.use('TkAgg')


import os, sys

import matplotlib.pylab as mtlab
from matplotlib.numerix import arange, sin, pi
from matplotlib.axes import Subplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

###########################################################################
from Tkinter import *		# The Tk package
from tkSimpleDialog import * 
from tkMessageBox import * 
from tkFileDialog import *
import os
import tkFileDialog		 # To be able to ask for files
import Pmw				 # The Python MegaWidget package
import math				 # import the sin-function
import string
import sys
from pDateTime import Date 
from tkColorChooser import *
from copy import copy
import datetime

def askcolorstring(titlestr='Choose'):
	ret = askcolor(title="Choose Color")
	scolor = ret[0]
	if scolor == None: return None
	return '#%02X%02X%02X' % (scolor[0],scolor[1],scolor[2]) 

class myChart_simpleGraphSetup:
	"""
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

class myChart_pSimplePlotElement:
	def __init__(self, name):
		self.name = name
		self.title = name
		self.stype = None		# Plot type = histogram, barchart or default None.
		self.plotnumber  = 0
		self.axis  = None
		self.m_vector_x  = None
		self.m_vector_y  = None
		self.m_lineColor   = '#00FF00'
		self.m_symbol  = '-'
		self.m_lineWidth = 1.0
		self.m_lined = True

	def setdata(self,x,y,nm):
		self.m_vector_x  = x
		self.m_vector_y  = y
		self.name = nm


class myChart_pSimpleXYPlotter:
	def __init__(self,parent,filename=None,xcol=0,ycol=1,barchart=0):
		self.m_master = parent
		self.m_filename = filename
		self.m_xcol = xcol
		self.m_ycol = ycol
		self.m_dialog = None
		self.m_colBox = None
		self.m_symBox = None
		self.m_scoBox = None
		self.m_isolBox = None
		self.m_smtBox = None
		self.m_linBox = None
		self.m_plotType = 'plot'
		self.m_plotTitle = ''
		self.printString = "lpr -h -Plplex125ps" 

		self.mouseFormatStr = '%.2f,%.2f'
		self.lastGridSetting =  True
		
		self.m_tickFontColor = 'black'
		self.m_tickFontSize = 8.0
		self.m_tickFontRotation = -45.0

		self.m_plots   = []                               # My plots
		self.m_vector_x = []
		self.m_vector_y = []

		self.makeMenu(parent,barchart)
		self.dragging = 0			# For mouse handling.
		self.m_linewidth = 0
		self.m_pixels = 2
		self.m_color = 'blue'
		self.m_symbol = 'circle'
		self.m_marker = None
		self.m_backcolor = 'white'
		self.m_colorIndex = 0
		self.m_symbolIndex = 0 
		self.m_keyedColors = {'b':'#0000FF', 'r':'#FF0000', 'g':'#00FF00', 'm':'#FFFF00','c': '#FF00FF', 'k': '#000000', 'y': '#00FFFF' }
		self.m_colorsList = self.m_keyedColors.keys()
		self.m_symbolCodes = { 'dash-dot':'-.','dashed':'--','solid':'-','dotted':':','points':'.','circle':'o'} 
		self.m_symbolList = self.m_symbolCodes.values()
		##['-', 'o', '^', 'v', 'd', 'D', '+', 'X' ]
		self.miny2 = 0.
		self.maxy2 = 1.
		self.m_showGraphPaper = False
		##############################################################################
		# Default actions for histogram displays.
		##############################################################################
		self.m_isHistogram = 0
		self.m_histogramMin = 0.0
		self.m_histogramMax = 0.0
		self.m_histogramHit = 1
		self.m_histogramRange = 	self.m_histogramMax - self.m_histogramMin 
	        
		##############################################################################
		# Default time for starting your plots
		##############################################################################
		self.m_xaxisIsDate = 0
		self.m_startDate = Date()
		self.m_startDate.day = 1
		self.m_startDate.month = 1
		self.m_startDate.year = 0 
		self.m_y0 = 0
		self.m_y1 = 0
		self.m_x0 = 0
		self.m_x1 = 0
		self.img = None

	def getPlotNames(self):
		names = []
		for plt in self.m_plots:
			names.append(plt.name)
		return names

	def getPlotElement(self,nm):
		for plt in self.m_plots:
			if nm == plt.name: return plt
		return None
	
	################################################ DO NOT USE #############################
	def setAsHistogram(self,fname,xdata,bins):
		plt = None
		found = 0
		for plt in self.m_plots:
			if plt.name == fname: 
				found = 1
				break; 
		if found == 0:	
			plt = pSimplePlotElement(fname)         # Create a place holder. 
			self.m_color=self.m_colorsList[self.m_colorIndex]
			self.m_colorIndex = self.m_colorIndex + 1
			plt.m_lineColor = self.m_color
			if (self.m_colorIndex >= len(self.m_colorsList)): self.m_colorIndex = 0
			self.m_symbol = self.m_symbolList[self.m_symbolIndex]
			plt.m_symbol = self.m_symbol
			#self.m_symbolIndex = self.m_symbolIndex + 1
			#if (self.m_symbolIndex >= len(self.m_symbolList)): self.m_symbolIndex = 0
			self.m_plots.append(plt)                 
		plt.binCount = bins
		plt.setdata(xdata,xdata,fname)
		self.m_isHistogram = 1
		self.m_histogramMin = xdata.min()
		self.m_histogramMax = xdata.max()
		self.m_histogramRange = self.m_histogramMax - self.m_histogramMin 
		self.m_plotType = 'hist'
		self.redraw()
	
	def setTupleData(self,fname,xdata,ydata,useLeft=1):
		xarray = Numeric.array(xdata)
		yarray = Numeric.array(ydata)
		self.setData(fname,xarray,yarray)

	def setData(self,fname,xdata,ydata):
		"""
		We are getting arrays here. Convert them to 
		"""
		plt = None
		found = 0
		if self.m_plots == None: self.m_plots = []
		for plt in self.m_plots:
			if plt.name == fname: 
				found = 1
				break; 
		if found == 0:	
			plt = pSimplePlotElement(fname)						# Create a place holder. 
			self.m_color=self.m_colorsList[self.m_colorIndex]   # Get the color
			self.m_colorIndex = self.m_colorIndex + 1
			if (self.m_colorIndex >= len(self.m_colorsList)): 	self.m_colorIndex = 0
			kc = self.m_colorsList[self.m_colorIndex]
				#self.m_symbolIndex = self.m_symbolIndex + 1
				#if (self.m_symbolIndex >= len(self.m_symbolList)): self.m_symbolIndex = 0
				#self.m_symbol = self.m_symbolList[self.m_symbolIndex]
			#print "LOOK " , kc, self.m_keyedColors[kc], self.m_colorIndex
			plt.m_lineColor = self.m_keyedColors[kc]
			plt.m_symbol = self.m_symbol
			self.m_plots.append(plt)                 
		m_vector_x  = Numeric.array(xdata.tolist())
		m_vector_y  = Numeric.array(ydata.tolist())

		plt.setdata(m_vector_x,m_vector_y,fname)
		self.redraw()
		return 
		
	###################### TODO ######################################################
	#if os.name =='nt': self.m_g.legend_configure(font='Arial 8')

	def testThis(self):
		self.m_myFigure.clf()

	def setPlotToDraw(self,name,how=True):
		for plt in self.m_plots:
			if plt.name == name: 
				plt.m_lined = how;

	def clearPlots(self,all=1):
		for plt in self.m_plots:  
			plt.m_lined = False
		self.redraw()

	def setPlotTitle(self,title):
		self.m_plotTitle = title

	def setTitle(self,title):
		self.m_plotTitle = title
		self.m_Subplot.set_title(self.m_plotTitle)
		self.m_canvas.show()

	def setYtitle(self,title):
		self.m_Subplot.set_ylabel(title)
		self.m_canvas.show()

	def setXtitle(self,title):
		self.m_Subplot.set_xlabel(title)
		self.m_canvas.show()


	def showTheseOnly(self,listOfNames):
		#print "Marking ...", listOfNames				
		#for plt in self.m_plots:  print plt.name, plt.m_lined
		for plt in self.m_plots: 
			if plt.name in listOfNames:
				plt.m_lined = True
			else: 
				plt.m_lined = False

	def redraw(self,legend=True,location=-1):
		"""
		Get names of plots and plot individually.
		"""
		lines = self.m_Subplot.get_lines()    # get the current number of lines. 
		for plt in self.m_plots: 
			for line in lines:				# Catch any duplicate lines here. 
				nm = line.get_label()
				lenx = len(line.get_xdata())
				leny = len(line.get_ydata())
				if nm == plt.name and lenx == len(plt.m_vector_x) and leny == len(plt.m_vector_y) and plt.m_lined == True:
					line.set_xdata(plt.m_vector_x)
					line.set_ydata(plt.m_vector_y)


		self.m_Subplot.clear()     # This does not work.
		labels = []
		for plt in self.m_plots: 
			cp_vector_x = copy(plt.m_vector_x)
			cp_vector_y = copy(plt.m_vector_y)
			if plt.m_lined == False: continue
			#print "Actually plotting...", plt.name
			if self.m_plotType == 'loglog':
				cp_vector_x = copy(plt.m_vector_x)
				cp_vector_y = copy(plt.m_vector_y)
				self.m_Subplot.loglog(cp_vector_x,cp_vector_y,label=plt.name,color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				labels.append(plt.name)
			elif self.m_plotType == 'dates':
				self.m_Subplot.plot_date(cp_vector_x,cp_vector_y,label=plt.name,color=plt.m_lineColor,linestyle='-',linewidth=plt.m_lineWidth,marker='X')
				labels.append(plt.name)
			elif self.m_plotType == 'scatter':
				self.m_Subplot.scatter(cp_vector_x,cp_vector_y,marker='o',c=plt.m_lineColor)
				labels.append(plt.name)
			elif self.m_plotType == 'fill':
				self.m_Subplot.fill(cp_vector_x,cp_vector_y,plt.m_lineColor)
				self.m_Subplot.plot(cp_vector_x,cp_vector_y,label=plt.name,color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				labels.append(plt.name)
			elif self.m_plotType == 'semilogx':
				self.m_Subplot.semilogx(cp_vector_x,cp_vector_y,label=plt.name,color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				labels.append(plt.name)
			elif self.m_plotType == 'semilogy':
				self.m_Subplot.semilogy(cp_vector_x,cp_vector_y,label=plt.name,color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				labels.append(plt.name)
			elif self.m_plotType == 'hist':
				n,bins,patches = self.m_Subplot.hist(x=cp_vector_x,bins=plt.binCount)
				#matplotlib.pylab.set(patches,'facecolor',plt.m_lineColor)
				#print n, bins
				self.m_Subplot.plot(n,label=plt.name,color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				labels.append(plt.name)
			else:
				# ln = self.m_Subplot.plot(plt.m_vector_x,plt.m_vector_y,label=plt.name,
				#	color=plt.m_lineColor,linestyle=plt.m_symbol,linewidth=plt.m_lineWidth)
				try:
					if self.m_marker <> None: 
						ln = self.m_Subplot.plot(cp_vector_x,cp_vector_y,label=plt.name,\
						color=plt.m_lineColor,linewidth=plt.m_lineWidth, marker=self.m_marker)
					else:
						ln = self.m_Subplot.plot(cp_vector_x,cp_vector_y,label=plt.name,\
						color=plt.m_lineColor,linewidth=plt.m_lineWidth)
				except:
					self.resetZoom()
				#print ")))->:", plt.m_lineColor, plt.m_symbol
				labels.append(plt.name)

		if len(self.m_plots) < 1: 
			#print "I cannot seem to clear this figure..."
			return
		plt = self.m_plots[0] 
		#self.m_plotTitle = labels[0] + "..."
		if self.m_plotTitle <> None:
			if len(self.m_plotTitle) > 0: 
				self.m_Subplot.set_title(self.m_plotTitle)

		if legend and len(labels) > 0: 
			legend = self.m_Subplot.legend(labels)     # Create the legend. 
			if location <> -1: legend._loc = location  # Use only if explicitly specified.


		if self.m_showGraphPaper == True:
			#xmin,xmax = self.m_Subplot.get_xlim()
			#ymin,ymax = self.m_Subplot.get_ylim()
			#yr = arange(ymin,ymax,(ymax - ymin)/20)
			#self.m_Subplot.hlines(yr,ones((20))*xmin,ones((20))*xmax)
			#xr = arange(xmin,xmax,(xmax - xmin)/20)
			#self.m_Subplot.vlines(xr,ones((20))*ymin,ones((20))*ymax)
			self.m_Subplot.xaxis.grid(True,which='minor')
			self.m_Subplot.yaxis.grid(True,which='minor')

		#print "Here are the axis settings..."			
		ticklabels = self.m_Subplot.get_xticklabels()
		for lbl in ticklabels:
			lbl.set_fontsize(self.m_tickFontSize)
			lbl.set_rotation(self.m_tickFontRotation)
		ticklabels.extend(self.m_Subplot.get_yticklabels())

		for lbl in ticklabels:
			lbl.set_fontsize(self.m_tickFontSize)
			lbl.set_color(self.m_tickFontColor)
		v = self.useLimits.get()
		if v == 1: 
			sx0 = self.limit_X0.get() 
			sx1 = self.limit_X1.get() 
			if len(sx0) > 1 and len(sx1) > 1: 
				x0 = float(sx0)
				x1 = float(sx1)
				self.m_Subplot.set_xlim([x0,x1])
			sy0 = self.limit_Y0.get() 
			sy1 = self.limit_Y1.get() 
			if len(sy0) > 1 and len(sy1) > 1: 
				y0 = float(sy0)
				y1 = float(sy1)
				self.m_Subplot.set_ylim([y0,y1])
			self.m_canvas.show()
		else:		
			self.resetZoom()

		
	########################################################################
	def setCrMarker(self): self.setMarker('o')
	def setDmMarker(self): self.setMarker('d')
	def setSqMarker(self): self.setMarker('s')
	def setNoMarker(self): self.setMarker('X')

	def getSymbol(self):
		return self.m_symbol

	def setSymbol(self,s):
		self.m_symbol = s


	def getMarker(self):
		return self.m_marker

	def setMarker(self,markerType):
		"""
		Permissible values are o,s,d; Any other value will remove marker
		"""
		if markerType in ['o','d','s']: 
			self.m_marker = markerType
		else: 
			self.m_marker = None
		self.redraw()

	########################################################################
	def setXaxisAsTime(self,year=0,month=0,day=0):
		if year == 0: 
			self.m_startDate.year = year
			self.m_g.xaxis_configure(rotate=0,command='')
			return
		self.m_startDate.day = day
		self.m_startDate.month = month
		self.m_startDate.year = year
		#self.m_g.xaxis_configure(rotate=90,command=self.formatTickLabels)
		#self.m_g.xaxis_configure(stepsize=720.0,subdivisions=2)

	########################################################################
	def formatTickLabels(self,widget,value):
		#ss = float(value) 
		pDate = self.m_startDate + int(value)
		ss = "%d/%d/%d" % (pDate.day,pDate.month,pDate.year)
		return ss


	########################################################################
	# Make a dialog, and ask for a specified graph's color, linewidth etc.
	# This function is called when the graph is double-clicked.
	########################################################################
	def graphSetup(self):
		t = Toplevel()
		dlg = simpleGraphSetup(t,self)
						
						
	##########################################################################
	# shows a FileDialog, and opens the selected file. The file must be
	# a text file with each line on the form: 
	# <whitespace><number><whitespace><comma><whitespace><number><whitespace>\n
	##########################################################################

	def openFile(self):
		pass
	
		fname = tkFileDialog.Open().show()
		if fname <> "":
			file = open(fname, 'r')
		else:
			return

		self.m_vector_x  = []
		self.m_vector_y  = []
				
		for line in file.readlines():
			[x, y] = string.split(line)
			#print x,y
			self.m_vector_x.append(float(x))
			self.m_vector_y.append(float(y))
			
		self.m_graphName = "Graph :" + fname
		self.m_g.line_create(self.m_graphName, xdata=tuple(vector_x), 
					  ydata=tuple(vector_y), color=self.m_color, scalesymbols=1)
			
		#self.m_g.element_bind(self.m_graphName, sequence="<Double-Button-1>",  func=self.graphSetup)



	#########################################################################################
	# These apply to the specific plot being shown. For now, I am defaulting ro the first
	# plot in the list of plots. 
	##########################################################################################
	def getYtitle(self):
		if self.m_plots <> None: 
			xstr = askstring("Y Label", "->")
			if xstr <> None:
				self.m_Subplot.set_ylabel(xstr)
				self.m_canvas.show()


	def getXtitle(self):
		if self.m_plots <> None: 
			xstr = askstring("X Label", "->")
			if xstr <> None:
				self.m_Subplot.set_xlabel(xstr)
				self.m_canvas.show()

	def getTitle(self):
		if self.m_plots <> None: 
			xstr = askstring("Title", "->")
			if xstr <> None:
				self.m_Subplot.set_title(xstr)
				self.m_canvas.show()

	# Empties the plotting window
	def newFile(self):
		self.clearPlots()


	def chooseTickFontColor(self):
		scolor = askcolorstring("Choose Cross Color")
		if scolor <> None: 
			self.m_tickFontColor=scolor
			self.redraw()
		  
	def chooseBackground(self): 
		""" 
		This sets the background border ... <-- --> ...
		"""
		scolor = askcolorstring("Choose Cross Color")
		if scolor <> None: 
			self.m_myFigure.set_facecolor(scolor)
			self.m_canvas.show()

	def chooseAxisBackground(self):
		""" 
		This sets the inner chart border ... <-- --> ...
		"""
		scolor = askcolorstring("Color for inner chart...")
		if scolor <> None: 
			#print scolor, " is scolor"
			self.m_Subplot.set_axis_bgcolor(scolor)
			self.m_canvas.show()



	# Replots using default line width of 1. 
	def defaultLine(self,pixels=1,lw=1):
		lines = self.m_Subplot.get_lines()
		for line in lines:
			#line.set_linewidth(lw)
			#line.set_markersize(pixels)
			line.set_linestyle('-')
		self.m_canvas.show()
		  
	def defaultPoints(self,pixels=2,lw=0):
		pass   # Draw them again as scatter plots. 
		  
# Saves the plot as postscript file
	def postscript(self):
		ofile = asksaveasfilename(filetypes=[("Postscript","*.ps"),("All Files","*")])
		if ofile:
			self.m_canvas.print_figure(ofile, dpi=300)

	def doMinorGrid(self):
		self.m_showGraphPaper = not self.m_showGraphPaper
		self.redraw()

	########################################################################
	# 
	########################################################################	
	def setYAxisLimits(self):
		y0 = askfloat('Please enter lower limit',"Y0")
		if y0 == None: return 
		y1 = askfloat('Please enter upper limit',"Y1")
		if y1 == None: return 
		if y1 <= y0: 
			showwarning("Cannot set y1 lower than or equal to y0", "Error")
			return
		self.m_Subplot.set_ylim([y0,y1])
		self.m_canvas.show()

	def setXAxisLimits(self):
		x0 = askfloat('Please enter lower limit for X axis',"X0")
		if x0 == None: return 
		x1 = askfloat('Please enter upper limit for X axis',"X1")
		if x1 == None: return 
		if x1 <= x0: 
			showwarning("Cannot set x1 lower than or equal to x0", "Error")
			return
		self.m_Subplot.set_xlim([x0,x1])
		self.m_canvas.show()

	########################################################################
	# 
	########################################################################	
	def zoomIn(self):
		print "X limit", self.m_Subplot.get_xlim()
		print "Y limit", self.m_Subplot.get_ylim()

		x0,x1 = self.m_Subplot.get_xlim()
		y0,y1 = self.m_Subplot.get_ylim()
		r = (x1 - x0) / 4
		self.m_Subplot.set_xlim([x0 + r, x1 - r])
		r = (y1 - y0) / 4
		self.m_Subplot.set_ylim([y0 + r, y1 - r])
		print "X limit", self.m_Subplot.get_xlim()
		print "Y limit", self.m_Subplot.get_ylim()
		self.m_canvas.show()

	########################################################################
	# How do I force the replot and redraw on the screen.
	########################################################################	
	def resetZoom(self):
		if (self.m_plots) < 1: return 
		plt = self.m_plots[0]
		#x0 = plt.m_vector_x.min()
		#x1 = plt.m_vector_x.max()
		#y0 = plt.m_vector_y.min()
		#y1 = plt.m_vector_y.max()
		
		x0 = min(plt.m_vector_x)
		x1 = max(plt.m_vector_x)
		y0 = min(plt.m_vector_y)
		y1 = max(plt.m_vector_y)
		
		for plt in self.m_plots: 
			if plt.m_lined == False: continue
			if x0 > min(plt.m_vector_x): x0 = min(plt.m_vector_x)
			if x1 < max(plt.m_vector_x): x1 = max(plt.m_vector_x)
			if y0 > min(plt.m_vector_y): y0 = min(plt.m_vector_y)
			if y1 < max(plt.m_vector_y): y1 = max(plt.m_vector_y)

		if y0 == y1: y1 = y0 + 1
		self.m_Subplot.set_xlim([x0,x1])
		self.m_Subplot.set_ylim([y0,y1])
		self.m_canvas.show()


# The next functions configure the axes
	def showAxis(self): 
		"""
		Debug function: Dumps axis parameters.
		"""
		#print self.m_Subplot.get_xaxis()
		print dir(self.m_Subplot)
		print "X limit", self.m_Subplot.get_xlim()
		print "Y limit", self.m_Subplot.get_ylim()
		#for plt in self.m_plots: 
		#	print plt.name
		#	print plt.m_vector_x[:3]
		#	print plt.m_vector_y[:3]

		#state = int(self.m_g.axis_cget("x", 'hide'))
		#self.m_g.axis_configure(["x", "y"], hide = not state)
		self.m_canvas.show()

	
	def swapAxes(self):
		for plt in self.m_plots: 
			plt.m_vector_y,plt.m_vector_x = 	plt.m_vector_x,plt.m_vector_y
		self.redraw()

	def scatterPlot(self):
		self.m_plotType = 'scatter'
		self.redraw()

	def filled(self):
		self.m_plotType = 'fill'
		self.redraw()

	def plotdates(self):
		self.m_plotType = 'dates'
		self.redraw()
		
	def xlogScale(self):
		self.m_plotType = 'semilogx'
		self.redraw()
	
	def ylogScale(self):
		self.m_plotType = 'semilogy'
		self.redraw()

	def loglogScale(self):
		self.m_plotType = 'loglog'
		self.redraw()

	def nologScale(self):
		self.m_plotType = 'plot'
		self.redraw()

	def xdescending(self):
		state = int(self.m_g.axis_cget("x", 'descending'))
		self.m_g.xaxis_configure(descending = not state)

	def ydescending(self):
		state = int(self.m_g.axis_cget("y", 'descending'))
		self.m_g.yaxis_configure(descending = not state)

	def descending(self):
		state = int(self.m_g.axis_cget("x", 'descending'))
		self.m_g.axis_configure(["x", "y"], descending = not state)

	def xloose(self):
		state = int(self.m_g.axis_cget("x", 'loose'))
		self.m_g.xaxis_configure(loose = not state)

	def yloose(self):
		state = int(self.m_g.axis_cget("y", 'loose'))
		self.m_g.yaxis_configure(loose = not state)

	def showCrosshairs(self):
		hide = not int(self.m_g.crosshairs_cget('hide'))
		self.m_g.crosshairs_configure(hide = hide, dashes="1")
		if(hide):
			self.m_g.unbind("<Motion>")
		else:
			self.m_g.bind("<Motion>", self.m_mouseMove)
	  
	############################################################################	
	# The next functions configures the Grid
	############################################################################	
	def showGrid(self,useLast=True):	
		if useLast in [True,False]: self.lastGridSetting =  useLast
		self.m_Subplot.grid(self.lastGridSetting)
		self.m_canvas.show()

	def hideGrid(self):
		self.lastGridSetting =  False
		self.m_Subplot.grid(False)
		self.m_canvas.show()

	def showYgridLines(self,how=-11):
		xaxis = self.m_Subplot.get_xaxis()
		xaxis.grid(True)
		self.m_canvas.show()

	def showXgridLines(self):
		yaxis = self.m_Subplot.get_yaxis()
		yaxis.grid(True)
		self.m_canvas.show()

	def setGridColor(self,color):
		glines = self.m_Subplot.get_xgridlines()
		for gline in glines: gline.set_color(color)
		glines = self.m_Subplot.get_ygridlines()
		for gline in glines: gline.set_color(color)
		self.m_canvas.show()
	
	def redGrid(self):   self.setGridColor("r")
	def blueGrid(self):  self.setGridColor("b")
	def greenGrid(self): self.setGridColor("g")
	def blackGrid(self): self.setGridColor("k")

	def chooseGrid(self): 
		scolor = askcolorstring("Choose Grid Color")
		if scolor == None: return
		self.setGridColor(scolor)

	# The next functions configures the Legend. 
	# BUG There is no way to hide the legend??
	def showLegend(self, whence=1):
		legend = self.m_Subplot.get_legend()
		if legend == None: 
			self.redraw(legend=True,location=whence)
			return
		if whence in range(1,11): legend._loc = whence
		if whence == 11: 
			legend._loc = (1.0,0.5)
			# Adjust the width of the border ... how?
		self.m_canvas.draw()
		self.m_canvas.show()

	def testLegend(self,tup=(1.0,0.5)):
		legend = self.m_Subplot.get_legend()
		legend._loc = tup
		self.m_canvas.draw()
		self.m_canvas.show()

	def hideLegend(self):
		"""
		This function does not work, since I cannot seem to get rid of the legend once
		it is printed. 
		"""
		legend = self.m_Subplot.get_legend()   # Get the legend itself.
		if legend == None: 
			self.redraw(legend=True)
			return
		b = not legend.get_visible()		  # Get the state of the legend. 
		legend.set_visible(b)			      # Set the state. 
		self.redraw(legend=b)
		return 

		print dir(legend), legend._loc
		legend._loc += 1
		legend.draw_frame(b)
		print b
		lines = legend.get_lines()
		for ln in lines: ln.set_visible(b)
		lines = legend.get_texts()
		for ln in lines: ln.set_visible(b)
		self.m_canvas.draw()
		self.m_canvas.show()
	

	def m_myaddmenu(self,menuBar, owner, label, command):
		menuBar.addmenuitem(owner, 'command', '<help context>', 
						label = label, command = command)

	def m_mychkmenu(self,menuBar, owner, label, command):
		menuBar.addmenuitem(owner, 'checkbutton', '<help context>', 
			label = label, command = command, variable=IntVar())
	
	def saveasimage(self):
		ofile = asksaveasfilename(filetypes=[("PNG","*.png"),("All Files","*")])
		if ofile == None: return
		if ofile:
			self.m_canvas.print_figure(ofile, dpi=300)
		return 


	def setPrinterName(self):
		xstr = askstring("Printer Name (e.g. lplex125ps)", "Set Printer Name")
		if xstr <> None: self.printString = "lpr -P%s -h" % xstr

	def printImage(self):
		ofile = os.getenv('HOME') + os.sep + 'tempFile.ps'
		#self.m_canvas.print_figure(ofile, dpi=300)

		cnv = self.m_canvas.get_tk_widget()
		cnv.postscript(file=ofile,colormode='color',rotate='true',pagewidth='8i',pageheight='10i')
		os.system(self.printString + " " +  ofile)

		#if self.img == None:
		#	self.img = PhotoImage(name="image", master=self.m_master)
		#self.m_g.snap(self.img)           # take snapshot
		#self.img.write(ofile)  # and save it to file.

# Create and pack the MenuBar.		
	def makeMenu(self,master,barchart=0):
		self.m_menuBar = Pmw.MenuBar(master, hull_relief = 'raised', hull_borderwidth = 1)		
		self.m_menuBar.pack(fill = 'x')

# Make the File menu
		self.m_menuBar.addmenu('File', 'helptxt')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Setup', self.graphSetup)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Open...',	self.openFile)
		self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Set Printer ', self.setPrinterName)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Print ', self.printImage)
		self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Save as image', self.saveasimage)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Save as ps', self.postscript)
		self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Default Lines', self.defaultLine)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Default Points', self.defaultPoints)
		self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Read Text', self.doReadFile)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Show XY', self.dumpXY)

		#self.m_myaddmenu(self.m_menuBar, 'File', 'Quit',	  master.quit)

# Make the Axis menu				
		self.m_menuBar.addmenu('Axis', '')
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Line Axes', self.nologScale )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Scatter', self.scatterPlot)
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Zoom Reset',  self.resetZoom  )
		#self.m_myaddmenu(self.m_menuBar, 'Axis', 'Swap', self.swapAxes)
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'X is Date', self.plotdates)
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Filled', self.filled )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Dump Axis  ',  self.showAxis  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Set X limits',  self.setXAxisLimits  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Set Y limits',  self.setYAxisLimits  )
		#self.m_myaddmenu(self.m_menuBar, 'Axis', 'Zoom In X 2',  self.zoomIn  )
		#self.m_myaddmenu(self.m_menuBar, 'Axis', 'x logscale', self.xlogScale )
		#self.m_myaddmenu(self.m_menuBar, 'Axis', 'y logscale', self.ylogScale )
		#self.m_myaddmenu(self.m_menuBar, 'Axis', 'Log logscale', self.loglogScale )
		
# Make the Background menu				
		self.m_menuBar.addmenu('Options', '')
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set backgd color', self.chooseAxisBackground)
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set border color', self.chooseBackground)
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set ticks color', self.chooseTickFontColor)
		
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'descending', self.descending)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'x looseScale', self.xloose)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'y looseScale', self.yloose)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'hide',	  self.showAxis  )


# Make the Crosshairs menu

		#self.m_menuBar.addmenu('Crosshairs', '')
		#self.m_mychkmenu(self.m_menuBar, 'Crosshairs', 'show', self.showCrosshairs)
		#self.m_menuBar.addcascademenu('Crosshairs', 'Color', '')
		#self.m_myaddmenu(self.m_menuBar, 'Color', 'red',   self.redCross  )
		#self.m_myaddmenu(self.m_menuBar, 'Color', 'blue',  self.blueCross )
		#self.m_myaddmenu(self.m_menuBar, 'Color', 'green', self.greenCross)
		#self.m_myaddmenu(self.m_menuBar, 'Color', 'black', self.blackCross)
		#self.m_myaddmenu(self.m_menuBar, 'Choose', 'black', self.chooseCross)

# Make the Grid menu
		self.m_menuBar.addmenu('Grid', '')
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show', self.showGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'hide', self.hideGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show Horz', self.showXgridLines )
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show Vert', self.showYgridLines )
		#self.m_myaddmenu(self.m_menuBar, 'Grid', 'Minor', self.doMinorGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Main Title', self.getTitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'X Title', self.getXtitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Y Title', self.getYtitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Mouse Format Str', self.setMouseDecimalPlaces)
		self.m_menuBar.addcascademenu('Grid', 'Color ', '')
		self.m_myaddmenu(self.m_menuBar, 'Color ', 'red',   self.redGrid  )
		self.m_myaddmenu(self.m_menuBar, 'Color ', 'blue',  self.blueGrid )
		self.m_myaddmenu(self.m_menuBar, 'Color ', 'green', self.greenGrid)
		self.m_myaddmenu(self.m_menuBar, 'Color ', 'black', self.blackGrid)
		self.m_myaddmenu(self.m_menuBar, 'Color ', 'choose', self.chooseGrid)

	# Make the Legend menu
		self.m_menuBar.addmenu('Legend', '')
		self.m_menuBar.addcascademenu('Legend', 'Type', '')

		self.legendLocations = { 'Upper Right' : 1, 'Upper Left' :2, 'Lower Left' : 3, 'Lower Right' : 4, 
				'Center Left' : 6, 'Center Right': 7, 'Lower Center': 8, 'Upper Center': 9, 
				'Center': 10, 'Outside Rt': 11}
		#a = lambda s=self,x=0: s.hisegend(x)
		self.m_myaddmenu(self.m_menuBar, 'Legend', 'Hide/Show', self.hideLegend)
		# The following option does not work: 'Right' : 5,
		s = self.legendLocations.keys()
		s.sort()
		for i in s:
			t = self.legendLocations[i]
			a = lambda s=self,x=t: s.showLegend(x)
			self.m_myaddmenu(self.m_menuBar, 'Type', i, a)

		self.m_menuBar.addcascademenu('Legend', 'Marker ', '')
		self.m_myaddmenu(self.m_menuBar, 'Marker ', 'circle',   self.setCrMarker  )
		self.m_myaddmenu(self.m_menuBar, 'Marker ', 'diamond',  self.setDmMarker )
		self.m_myaddmenu(self.m_menuBar, 'Marker ', 'square', self.setSqMarker)
		self.m_myaddmenu(self.m_menuBar, 'Marker ', 'none', self.setNoMarker)

	######################################################################################
	# Make the graph area
	######################################################################################
		self.bottomFrame = Frame(self.m_master)
		self.bottomFrame.pack(side=BOTTOM,fill=X,expand=0)

		self.mouseText = Label(self.bottomFrame,width=20)
		self.mouseText.pack(side=LEFT,fill=X,expand=0)

		self.useLimits = IntVar()
		self.useLimits.set(0)
		self.ck_limit = Checkbutton(self.bottomFrame,text='Limit',anchor=W, variable=self.useLimits)
		self.ck_limit.pack(side=LEFT,expand=0)
		self.limit_X0 = Pmw.EntryField(self.bottomFrame,labelpos=W,label_text='X0')
		self.limit_X0.pack(side=LEFT,expand=0)
		self.limit_X1 = Pmw.EntryField(self.bottomFrame,labelpos=W,label_text='X1')
		self.limit_X1.pack(side=LEFT,expand=0)
		self.limit_Y0 = Pmw.EntryField(self.bottomFrame,labelpos=W,label_text='Y0')
		self.limit_Y0.pack(side=LEFT,expand=0)
		self.limit_Y1 = Pmw.EntryField(self.bottomFrame,labelpos=W,label_text='Y1')
		self.limit_Y1.pack(side=LEFT,expand=0)
		self.redrawBtn = Button(self.bottomFrame,text='Draw',command=self.redraw)
		self.redrawBtn.pack(side=LEFT,expand=0)


		self.m_canvas = None
		self.m_myFigure = Figure(figsize=(5,5),dpi=100)
		self.m_Subplot = self.m_myFigure.add_subplot(111)
		self.m_canvas = FigureCanvasTkAgg(self.m_myFigure,master=self.m_master)
		self.m_canvas.get_tk_widget().pack(side=TOP,expand=1, fill='both')
		self.m_canvas.mpl_connect('button_press_event',	self.mouseDown)
		self.m_canvas.mpl_connect('button_release_event',	self.mouseUp)
		self.m_canvas.mpl_connect('motion_notify_event',	self.mouseHandler)

	def mouseDown(self,event):
		self.dragging = 0
		if event.button == 2 :	
			self.resetZoom()
			return
		if event.inaxes and event.button == 1:
			self.dragging = 1
			self.m_x0 = event.xdata
			self.m_y0 = event.ydata
			#print "Dragging begin, ", event.xdata, event.ydata
			
	def mouseUp(self,event):
		if self.dragging:
			self.dragging = 0
			#print "Dragging done, ", event.xdata, event.ydata
			self.m_x1 = event.xdata
			self.m_y1 = event.ydata
			if (self.m_x0 <> self.m_x1) and (self.m_y0 <> self.m_y1):
				if (self.m_x0 > self.m_x1): self.m_x0,self.m_x1 = self.m_x1,self.m_x0
				if (self.m_y0 > self.m_y1): self.m_y0,self.m_y1 = self.m_y1,self.m_y0
				self.m_Subplot.set_xlim([self.m_x0,self.m_x1])
				self.m_Subplot.set_ylim([self.m_y0,self.m_y1])
				self.m_canvas.show()

				
	def setMouseDecimalPlaces(self):
		xstr = askinteger("Set Format string", "Enter number of decimal places")
		if xstr <> None:
			self.mouseFormatStr = '%.' + str(xstr) + 'f %.' + str(xstr) + 'f'
			
	def mouseHandler(self,event):
		if self.mouseFormatStr <> None:
			fmtstr = self.mouseFormatStr
		else:
			fmtstr = '%f %f'
		if event.inaxes:
			#outstr = fmtstr % (event.xdata,event.ydata)
			outstr = fmtstr % (float(event.x),float(event.y))
           	if self.m_plotType == 'dates':
				try:
					d1 = datetime.date.fromordinal(float(event.xdata))
					outstr = '%s %8.2f' % (d1.strftime('%Y-%m-%d'),event.ydata)
				except: 
					outstr = ""
		else: 
			outstr = fmtstr % (float(event.x),float(event.y))
		self.mouseText['text'] = outstr 
		
		

	def doReadFile(self):
		"""
		Reads in a csv file. Values must be floating point numbers.
		Blank lines or with hash as first character will be ignored. 
		First column Col 0 is X 
		Second column Col 1 is Y 
		"""
		ifile = askopenfilename(filetypes=[("txt","*.txt"),("All Files","*")])		
		if ifile:self.readFile(ifile)

	def readFile(self,filename,col1=0,col2=1):
		"""
		Reads in a csv file. Values must be floating point numbers.
		Blank lines or with hash as first character will be ignored. 
		col1 is the index for x axis. 
		col2 is the index for y axis. 
		"""
		file = open(sys.argv[1],'r')
		xdata = []
		ydata = []
		for line in file.readlines():
			if len(line) < 2:  continue
			if line[0] == '#': continue
			items = string.split(line) 
			k = len(items)
			if k < col2 or k < col1: continue
			x = items[col1]
			y = items[col2]
			xdata.append(float(x))
			ydata.append(float(y))
		self.setTupleData(filename,xdata,ydata)

	def dumpXY(self):
		"""
		For all elements, print out the values of x vs. y in a separate text dialog. 
		"""
		xstr  = ''
		for plt in self.m_plots: 
			if plt.m_lined == False: continue
			xstr = '#' + plt.name + "\n"
			for k in range(len(plt.m_vector_x)): 
				xstr = xstr + "%6.3f\t%6.3f\n" % (plt.m_vector_x[k], plt.m_vector_y[k])
			headerDialog = Pmw.TextDialog(self.m_master,scrolledtext_labelpos='n',\
				title=plt.name, defaultbutton=0,label_text="XY from "+plt.name)
			xx = headerDialog.component('scrolledtext')
			xx.settext(xstr)
			#headerDialog.configure(text_state='disabled')

	def setBarchartData(self,fname,xdata,ydata):
		self.m_vector_x  = xdata
		self.m_vector_y  = ydata
		self.m_graphName = fname 
		self.m_g.makeBar(self.m_graphName, self.m_vector_x, self.m_vector_y )

		self.m_g.legend_configure(hide = 0)
		self.m_g.xaxis_configure(subdivision=10, loose=1)
		self.m_g.yaxis_configure(subdivision=10, loose=1)
		self.m_g.grid_on() 



##########################################################################
# -------------------[ The test routine ]---------------------
##########################################################################

if __name__ == '__main__':
	if len(sys.argv) < 2: print "Usage: filename [xcol ycol] with columns as 1, 2, etc."; sys.exit(0)
	xcol = 0
	ycol = 1
	file = open(sys.argv[1],'r')
	if len(sys.argv) >= 4: 
		xcol = int(sys.argv[2]) 
		ycol = int(sys.argv[3]) 
	y2data = None
	if len(sys.argv) == 5: 
		y2col = int(sys.argv[4]) 
		y2data = []
	else:
		y2col = None
	xdata = []
	ydata = []
	for tline in file.readlines():
		if len(tline) < 1: continue
		tline = string.replace(tline, ',',' ')
		line = string.strip(tline)
		if not line[0] in string.digits: continue
		items = string.split(tline) 
		xdata.append(float(items[xcol]))
		ydata.append(float(items[ycol]))
		if y2col <> None:
			y2data.append(float(items[y2col]))
			
	root = Tk()				 # build Tk-environment
	ff = pSimpleXYPlotter(root)
	ff.setTupleData(sys.argv[1],ydata,xdata)
	if y2col <> None:
		ff.setTupleData("4"+sys.argv[1],y2data,xdata)
	root.mainloop()					# ...and wait for input
