"""
TODO: 
	1. Allow for marker type, color and size from menu
	2. Allow for line size from menu
	3. Print to file or printer
	4. Configurable popup menus 

"""

###########################################################################

import os, sys
import numarray
import matplotlib
from matplotlib.numerix import arange, sin, pi
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx

import matplotlib.pylab as mtlab
from matplotlib.numerix import arange, sin, pi
from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, FuncFormatter
from matplotlib.dates import date2num, num2date, YearLocator, MonthLocator, DateFormatter

###########################################################################

import math				  # import the sin-function
import string
import sys
import time, datetime
from copy import copy
from pwxShowGridData import *

from pwxChartOpts import *

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


class pCompletionFormatter(FuncFormatter):
	def __init__(self, func):
		FuncFormatter.__init__(self,func)
		self._nx = 10
		self._ny = 20
		self._nz = 30
		self._nxy = self._nx * self._ny

	def setDimensions(self,nx,ny,nz):
		self._nx = nx 
		self._ny = ny
		self._nz = nz
		self._nxy = self._nx * self._ny


	def format_data(self,value):
		k = int(value / self._nxy)
		j = int(value - (k * self._nxy))/ self._nx
		i = int(value - (k * self._nxy) - j * self._nx)
		xstr = "[%d,%d,%d]" % (i,j,k)
		return xstr


def completionFormatFunction(x,pos,arv=None):
	print 'completionFormat ', x, pos,arv
	return '[%d]' % pos

		
class pSimplePlotElement:
	def __init__(self, name):
		self.name = name        # As shown in label
		self.stype = None		# Plot type = histogram, barchart or default None.
		self.parmid = 0         # Index into
		self.axis  = None       # The main axis to which I am associated.
		self.m_vector_x  = None # Pointers only
		self.m_vector_y  = None # Pointers only
		self.m_plotType  = 'plot'
		self.m_lined = False
		self.binCount = 100
		self.lineType = None
		self.m_xlabels = None 

	def set_x_labels(self,labels):
		self.m_xlabels = copy(labels)

	def setdata(self,x,y,nm,linetype=None):
		self.m_vector_x  = x
		self.m_vector_y  = y
		self.name = nm
		self.lineType = linetype 

class pwxPlotHolder(wx.Frame):
	def __init__(self,parent,id,caption="",filename=None,style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self,parent=None,title=caption,id=-1,style=style)
		self.m_master = parent
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.m_plotThaing = pwxSimpleXYPlotter(self,id,caption,filename)
		self.sizer.Add(self.m_plotThaing, 1, wx.TOP | wx.LEFT | wx.GROW)
		self.SetSizer(self.sizer)
		self.Fit()

	def getChartObject(self):
		return self.m_plotThaing


class pwxSimpleXYPlotter(wx.Panel):
	def __init__(self,parent,id,caption="",filename=None):
		wx.Panel.__init__(self,parent,id)
		self.m_master = parent
		self.m_filename = filename
		self.lineParmsDialog = None
		self.xyInitialization()                               # Initialization
		self.m_myFigure = Figure() # DONT USE figsize=(3,3),dpi=300)   # Set the appropriately
		self.m_firstAxes = None
		self.m_canvas = FigureCanvas(self,-1,self.m_myFigure)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.m_canvas, 1, wx.LEFT| wx.TOP | wx.GROW)
		self.statusbar = wx.StatusBar(self)
		self.statusbar.SetFieldsCount(2)
		self.sizer.Add(self.statusbar, 0 , wx.GROW)
		self.SetSizer(self.sizer)
		self.Fit()
		self.makeMenu(self,None)   # This has to go somewhere on this panel and not the frame.

		###########################################################################
		# You can use the event directly from the Figure class here.
		###########################################################################
		self.m_canvas.mpl_connect('motion_notify_event',	self.mouseMovementHandler)  
		self.m_canvas.mpl_connect('button_press_event',	    self.mousePressHandler)     
		self.m_canvas.mpl_connect('button_release_event',	self.mouseReleaseHandler)   
		self.m_canvas.mpl_connect('key_press_event',	self.keyPressHandler)   

	def setStatusBar(self,sbar):
		self.statusbar = sbar;

	def xyInitialization(self):
		self.m_xcol = 0
		self.m_ycol = 1
		self.m_plotType = 'plot'              # Default x vs. y plot
		self.m_plotTitle = ''                 # No titles 
		self.printString = 'rsh applsrv2 "/usr/ucb/lpr -h -P lplex125ps"' 
		self.printerName = 'lplex125ps'
		self.showColorBar = 0 
		self.showAllThree = True 
		self.colorFormatString = "#%02X%02X%02X"

		###########################################################################
		# END OF NEW
		###########################################################################
		self.mouseFormatStr = '%.2f,%.2f'              # For tracking the mouse.
		self.gridSetting       = True                     # Default 
		self.legendLocation = 1
		self.legendLocations = { 'Upper Right' : 1, 'Upper Left' :2, 'Lower Left' : 3, 'Lower Right' : 4, 
				 'Center Left' : 6, 'Center Right': 7, 
				 'Center Upper': 8, 'Center Lower': 9, 'Center Middle': 10 } 
		self.legendObj = None
		self.lineTypes = LINETYPES 
		self.colors    = COLORTYPES
		self.markerTypes = MARKERTYPES
		self.xlabel = ''
		self.ylabel = ''
		self.selectLineIndex = -1;

		###########################################################################
		# Start of items required for options....
		###########################################################################
		self.borderColor    = '#FFFFFF' 
		self.faceColor      = '#FFFFFF'
		self.gridLineStyle  = '-'
		self.lineParameters = [ ]
		
		# End of items required for options....
		
		self.maxLines = 12
		for i in range(self.maxLines):
			j = i % len(self.markerTypes) 
			k = i % len(self.colors)
			# index, width, colors,lnw, marker, markerColor, markerSize  
			self.lineParameters.append([i+1,'-', self.colors[k],1, self.markerTypes[0], self.colors[k],1])

		dparms = xml_readLineParameters()
		if dparms <> None:	self.mapObjToLineParms(dparms)

		######################################################################################
		# Make the graph area
		######################################################################################
		self.m_tickFontColor = 'black'
		self.m_tickFontSize = 8.0
		self.m_tickFontRotation = 45.0
		self.m_plots   = []                               # My plots
		self.m_vector_x = []
		self.m_vector_y = []
		self.image_ny = 0 
		self.image_nx = 0
		self.imageAction = 'X-Y'
		self.horizontalLayout = 1
		self.cvector = None
		self.dvector = None
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
		self.pshowGrid = 1
		self.gridLineStyle = '.'
		self.borderColor = 'white'
		self.faceColor = 'white'
	         
		##############################################################################
		# Default time for starting your plots
		##############################################################################
		self.m_xaxisIsDate = 0
		self.m_startDate = datetime.date(1,1,1)
		self.m_y0 = 0
		self.m_y1 = 0
		self.m_x0 = 0
		self.m_x1 = 0
		self.img = None

		print "Done with xy initialization"

	def mapObjToLineParms(self):
		dparms = {}
		dparms['LINEPARAMETERS']= self.lineparameters; 
		dparms['SHOWGRID'] 		= self.pshowGrid
		dparms['GRIDLINESTYLE'] = self.gridLineStyle 
		dparms['BORDERCOLOR']   = self.borderColor
		dparms['FACECOLOR']     = self.faceColor; 
		return dparms; 
		
	def mapLineParmsToObj(self,dparms):
		p = dparms.get('LINEPARAMETERS',None) 
		if p <> None: self.lineparameters = p 
		self.pshowGrid = dparms.get('SHOWGRID',1)
		self.gridLineStyle  = dparms.get('GRIDLINESTYLE',' ')
		self.borderColor = dparms.get('BORDERCOLOR','#FFFFFF')   
		self.faceColor = dparms.get('FACECOLOR','#FFFFFF')
		
	def saveLineParameters(self):
		dparms = self.mapObjToLineParms()
		xml_saveLineParameters(dparms)
		
	def readLineParameters(self):
		dparms = xml_readLineParameters()
		if dparms <> None:	self.mapObjToLineParms(dparms)
		
	def setLayout(self,how):
		self.horizontalLayout = how 
		
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
	

	def findPlot(self,fname,makeit=1):
		if self.m_plots == None:
			plt = pSimplePlotElement(fname)						# Create a place holder. 
			self.m_plots = [plt]
			return plt
		for plt in self.m_plots:
			if plt.name == fname: return plt 
		if makeit == 0: return None
		plt = pSimplePlotElement(fname)						# Create a place holder. 
		self.m_plots.append(plt)                 
		return plt

	def setPlotType(self,name,ptype,**kwparms):
		plt = self.findPlot(name,makeit=0)
		if plt == None: return 
		print "Setting plot type = ", ptype, ' for ', name
		plt.plotType = ptype
		if ptype == 'completion':
			plt.m_xlabels = kwparms['xlabels']
			print plt.m_xlabels


	def setTupleData(self,fname,xdata,ydata,useLeft=1,linetype=None,xlabels=None):
		"""
		We are getting tuples and must convert to numarray arrays here. 
		"""
		plt = self.findPlot(fname)
		m_vector_x  = numarray.asarray(xdata)
		m_vector_y  = numarray.asarray(ydata)
		print fname
		print "X TUPLE", type(m_vector_x), len(m_vector_x), m_vector_x[:5]
		print "Y TUPLE", type(m_vector_y), len(m_vector_y), m_vector_y[:5]
		plt.setdata(m_vector_x,m_vector_y,fname,linetype)
		if xlabels <> None: plt.set_x_labels(xlabels)
		self.redraw()
		#self.setData(fname,xdata,ydata)

	def setnumarrayData(self,fname,xdata,ydata,useLeft=1,xlabels=None):
		"""
		We are getting numarray arrays here. 
		"""
		plt = self.findPlot(fname)
		plt.setdata(xdata,ydata,fname) # Set directly
		if xlabels <> None: plt.set_x_labels(xlabels)
		self.redraw()                  

	def setData(self,fname,xdata,ydata,linetype=None,xlabels=None):
		"""
		We are getting generic lists or  arrays here. 
		"""
		plt = self.findPlot(fname)
		m_vector_x  = numarray.asarray(xdata)
		m_vector_y  = numarray.asarray(ydata)
		plt.setdata(m_vector_x,m_vector_y,fname,linetype)
		if xlabels <> None: plt.set_x_labels(xlabels)
		self.redraw()
		
	###################### TODO ######################################################
	#if os.name =='nt': self.m_g.legend_configure(font='Arial 8')

	def applyLineParameters(self):
		ax = self.m_firstAxes
		setp( ax.get_xgridlines(), linestyle=self.gridLineStyle)
		setp( ax.get_ygridlines(), linestyle=self.gridLineStyle)
		glines = ax.get_lines()
		k = 0 
		for ln in glines:
			k = k % len(self.lineParameters)
			lbl, lns, lineColor, lnw, markerType, markerColor, markerSize = self.lineParameters[k] 
			ln.set_linestyle(lns)
			ln.set_color(lineColor)
			ln.set_linewidth(lnw)
			ln.set_marker(markerType)
			ln.set_markerfacecolor(markerColor)
			ln.set_markersize(markerSize)
			k = k + 1
		self.redraw()

	def testThis(self,m=None):
		self.clearPlots()
		#self.m_myFigure.clf()
		#self.m_canvas.Refresh()

	def setPlotToDraw(self,name,how=True):
		for plt in self.m_plots:
			if plt.name == name: 
				plt.m_lined = how;

	def clearData(self,all=1):
		if self.m_myFigure == None: return 
		#x = self.m_myFigure.get_axes()
		#for a in x: self.m_myFigure.delaxes(a)
		for plt in self.m_plots:  del plt
		self.m_plots = []
		self.m_myFigure.clf()
		self.m_canvas.Refresh()

	def clearPlots(self,all=1):
		if self.m_myFigure == None: return 
		x = self.m_myFigure.get_axes()
		for a in x: self.m_myFigure.delaxes(a)
		for plt in self.m_plots:  del plt
		self.m_plots = []
		self.m_myFigure.clf()
		self.m_canvas.Refresh()

	def setTitle(self,title=None):
		if title <> None: self.m_plotTitle = title
		self.forceTitle()

	def getPlotTitle(self): return self.m_plotTitle 
		
	def forceTitle(self):
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_title(self.m_plotTitle)
			self.m_canvas.Refresh()
			self.redraw()

	def setYlabel(self,ylabel):
		self.ylabel = ylabel

	def setXlabel(self,xlabel):
		self.xlabel = xlabel

	def setYtitle(self,title):
		self.ylabel = title
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_ylabel(title)
			#self.m_canvas.Refresh()
			self.redraw()

	def setXtitle(self,title):
		self.xlabel = title
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_xlabel(title)
			#self.m_canvas.Refresh()
			self.redraw()

	def showTheseOnly(self,listOfNames):
		#print "Marking ...", listOfNames				
		#for plt in self.m_plots:  print plt.name, plt.m_lined
		for plt in self.m_plots: 
			if plt.name in listOfNames:
				plt.m_lined = True
			else: 
				plt.m_lined = False

	def forceMarkerType(self,markerType='o',markerSize=2):
		for k in range(len(self.lineParameters)): 
			item =  self.lineParameters[k]
			# lbl, lns, lineColor, lineWidth, markerType, markerColor, mSize 
			item[-1] = markerSize
			item[-3] = markerType
			self.lineParameters[k] = item
				
	def setDifferenceDisplay(self,how):
		"""
		if how == True: show x,y,f(x,y) 
		else show show f(x,y)
		"""
		self.showAllThree = how

	def toggleAllThree(self,event=None):
		self.showAllThree = not self.showAllThree
		self.redraw()
				
	def redraw(self):
		"""
		
		"""
		x = self.m_myFigure.get_axes()
		for a in x: self.m_myFigure.delaxes(a)
		#print "I using the Y label now : [", self.ylabel , "]"
		self.m_myFigure.clf()
		left, width = 0.1, 0.8                # For display area
		self.plotht = 0.8
		r1 = [left, 0.1, width, self.plotht - 0.05]
		if self.m_plotType <> 'image': 
			self.m_firstAxes = self.m_myFigure.add_axes(r1,label='firstAxes')
		labels = []
		j = 0                                  # Counts which line to use.
		#print "MPLOTS = ", len(self.m_plots)
		pltCounter = 0 
		for plt in self.m_plots: 
			cp_vector_x = plt.m_vector_x  # Why am I copying again?
			cp_vector_y = plt.m_vector_y
			#if plt.m_lined == False: continue
			#print "Plot ", plt.name, plt.m_plotType, plt.m_vector_y
			###############################################################################
			# Now use the lineparameters function
			###############################################################################
			k = j % len(self.lineParameters)
			self.lineParameters[k][0] = plt.name
			lbl, lns, lineColor, lineWidth, markerType, markerColor, mSize = self.lineParameters[k] 
			j = j + 1
			yearSpan = 0
			if self.m_plotType == 'plot': 
				function = self.m_firstAxes.plot
				if plt.lineType <> None: lns = plt.lineType
			elif self.m_plotType == 'image': 
				function = None;
				#print "Type of vector = " , type(plt.m_vector_x)
				self.avector = numarray.asarray(plt.m_vector_x)
				self.bvector = numarray.asarray(plt.m_vector_y)
				print "Dimensions", self.image_nx, self.image_ny, len(self.avector)
				self.avector.shape = self.image_ny, self.image_nx
				self.bvector.shape = self.image_ny, self.image_nx
				#x = self.m_myFigure.get_axes()
				#for a in x: self.m_myFigure.delaxes(a)
				#self.m_myFigure.clf()
				cb = None
				thisAspect = float(self.image_ny)  /float( self.image_nx )
				if self.imageAction in ['X-Y','Average','maximum','minimum']: 
					if self.imageAction == 'X-Y':
						self.evector = self.avector - self.bvector
					elif self.imageAction == 'maximum':
						self.evector = numarray.maximum(self.avector , self.bvector)
					elif self.imageAction == 'minimum':
						self.evector = numarray.minimum(self.avector , self.bvector)
					else: 
						self.evector = (self.avector + self.bvector) /2 
					self.m_myFigure.set_label(plt.name)
					if self.horizontalLayout == 0:
						layout = [311,312,313]
						r0 = (0.1,0.0,0.8,0.38) 
						r1 = (0.1,0.3,0.8,0.38) 
						r2 = (0.1,0.6,0.8,0.38) 
						thisAspect = float(self.image_ny)  /float( self.image_nx )
						print "VERTICAL", thisAspect
					else: 
						layout = [131,132,133]
						r0 = (0.0,0.1,0.38,0.8) 
						r1 = (0.3,0.1,0.38,0.8) 
						r2 = (0.6,0.1,0.38,0.8) 
						thisAspect = float(self.image_nx)  / float(self.image_ny )
						print "HORIZONTAL", thisAspect
					useAxes = 1
					if self.showAllThree:
						if useAxes == 0: 
							subplot0 = self.m_myFigure.add_subplot(layout[0])
							subplot1= self.m_myFigure.add_subplot(layout[1])
							subplot2 = self.m_myFigure.add_subplot(layout[2])
						else:
							subplot0 = self.m_myFigure.add_axes(r0)
							subplot1 = self.m_myFigure.add_axes(r1)
							subplot2 = self.m_myFigure.add_axes(r2)
						self.cb0 = subplot0.imshow(self.avector,cmap=cm.jet,aspect=thisAspect)
						self.cb1 = subplot1.imshow(self.bvector,cmap=cm.jet,aspect=thisAspect)
						self.cb2 = subplot2.imshow(self.evector,cmap=cm.jet,aspect=thisAspect)
					else:
						subplot2 = self.m_myFigure.add_subplot(111)
						self.cb2 = subplot2.imshow(self.evector,cmap=cm.jet)
					subplot1.set_xlabel(plt.name)
						#self.m_myFigure.colorbar(cb2,cax=cax,orientation='horizontal')
					#self.m_myFigure.subplots_adjust(left=0.1,right=0.9,bottom=0.1,top=0.9)
					cb0 = subplot0.imshow(self.avector,cmap=cm.jet) 
					cb1 = subplot1.imshow(self.bvector,cmap=cm.jet)
					cb2 = subplot2.imshow(self.evector,cmap=cm.jet)
					if self.showColorBar == 1: 
						cax = self.m_myFigure.add_axes([0.1,0.1,20,2])
						if self.image_ny < self.image_nx: 
							axx = self.m_myFigure.colorbar(cb2,cax=cax,orientation='vertical')
							print "HERE1"
							cax.set_position([0.1,0.1,10,44])
						else:	
							axx = self.m_myFigure.colorbar(cb2,cax=cax,orientation='horizontal')
							print "HERE2"
							cax.set_position([0.1,0.9,44,5])
				elif self.imageAction == 'Y': 
					subplot = self.m_myFigure.add_subplot(111)
					thisAspect1 = float(self.m_myFigure.get_figheight())  /float( self.m_myFigure.get_figwidth() )
					thisAspect2 = float(self.m_myFigure.get_figwidth())  /float( self.m_myFigure.get_figheight() )
					self.cb1 = subplot.imshow(self.avector,cmap=cm.jet,aspect=thisAspect2)
					self.m_myFigure.colorbar(self.cb1,orientation='vertical')	
					subplot.set_xlabel(plt.name)
				else: # 'X'
					subplot = self.m_myFigure.add_subplot(111)
					thisAspect1 = float(self.m_myFigure.get_figheight())  /float( self.m_myFigure.get_figwidth() )
					thisAspect2 = float(self.m_myFigure.get_figwidth())  /float( self.m_myFigure.get_figheight() )
					print "ASPECT = ", thisAspect1, thisAspect2
					self.cb1 = subplot.imshow(self.avector,cmap=cm.jet,aspect=thisAspect1)
					self.m_myFigure.colorbar(self.cb1,orientation='vertical')	
					subplot.set_xlabel(plt.name)
				self.m_firstAxes = self.m_myFigure.get_axes()[0]
			elif self.m_plotType == 'dates': 
				function = self.m_firstAxes.plot_date
				yearSpan = (cp_vector_x[-1] - cp_vector_x[0]) / 365.25
			elif self.m_plotType == 'loglog': function = self.m_firstAxes.loglog
			elif self.m_plotType == 'scatter': 
				if len(markerType)< 1: markerType = 'o'
				if not markerType in ['s','o','^','>','v','<','d','p','h','8']: markerType = 'o'
				self.m_firstAxes.scatter(cp_vector_x,cp_vector_y,label=plt.name, marker=markerType, c=lineColor)
				function = None
			elif self.m_plotType == 'fill':
				a1 = numarray.array([plt.m_vector_x[-1], plt.m_vector_x[0]],'f')
				cp_vector_x = numarray.concatenate((plt.m_vector_x,a1))
				a2 = numarray.array([plt.m_vector_y[0], plt.m_vector_y[0]],'f')
				cp_vector_y = numarray.concatenate((plt.m_vector_y,a2))
				print cp_vector_x
				print cp_vector_y
				self.m_firstAxes.fill(cp_vector_x,cp_vector_y,lineColor)
				function = None
			elif self.m_plotType == 'semilogx': function = self.m_firstAxes.semilogx
			elif self.m_plotType == 'semilogy': function = self.m_firstAxes.semilogy
			elif self.m_plotType == 'hist': 
				n,bins,patches = self.m_firstAxes.hist(x=cp_vector_y,bins=plt.binCount)
				function = None
				self.m_firstAxes.plot(n,label=plt.name,
					color=lineColor, 
					linestyle=lns, 
					linewidth=lineWidth)

			#######################################################################
			#
			#######################################################################
			#if self.selectLineIndex == pltCounter: lineWidth = 4
				
			if function <> None:
				function(cp_vector_x,cp_vector_y,label=plt.name,
					color=lineColor, 
					linestyle=lns, 
					linewidth=lineWidth, 
					marker=markerType, 
					markerfacecolor=markerColor, 
					markersize=mSize)
			labels.append(plt.name)
			pltCounter += 1

		for a in self.m_myFigure.get_axes(): a.grid(self.gridSetting)

		
		if len(self.m_plots) < 1: return
		plt = self.m_plots[0] 
		if self.m_plotTitle <> None:
			if len(self.m_plotTitle) > 0: 
				self.m_firstAxes.set_title(self.m_plotTitle)

		self.resetLegend()
		print "770: Setting limits", plt.m_plotType, plt.m_xlabels ,plt.name
	
		self.m_firstAxes.set_xlabel(self.xlabel)
		self.m_firstAxes.set_ylabel(self.ylabel)
		if self.m_showGraphPaper == True:
			self.m_firstAxes.xaxis.grid(True,which='minor')
			self.m_firstAxes.yaxis.grid(True,which='minor')

		self.setTickLabels(yearSpan)
		self.resetZoom()

	def setTickLabels(self,yearSpan):

		if self.m_plotType == 'dates':
			if yearSpan < 5: 
				major = DateFormatter("%b-%Y")
				self.m_firstAxes.xaxis.set_major_formatter(major)
				self.m_firstAxes.xaxis.set_major_locator(MonthLocator(interval=3))
			else:
				major = DateFormatter("%Y")
				self.m_firstAxes.xaxis.set_major_formatter(major)
				self.m_firstAxes.xaxis.set_major_locator(YearLocator(4))

		plt = self.m_plots[0] 
		if self.m_plotType == 'plot' and plt.m_xlabels <> None:
				print "----> 796:", plt.m_xlabels
				self.m_firstAxes.set_xticklabels(plt.m_xlabels)

		x = self.m_myFigure.get_axes()
		for a in x: 	
			ticklabels = a.get_xticklabels()
			for lbl in ticklabels: 
				lbl.set_rotation(self.m_tickFontRotation)
			ticklabels.extend(a.get_yticklabels())
			for lbl in ticklabels: 
				lbl.set_fontsize(self.m_tickFontSize)

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
			self.m_g.xaxis_configure(rotate=90,command='')
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
						 
						 

	#########################################################################################
	# These apply to the specific plot being shown. For now, I am defaulting to the first
	# plot in the list of plots. 
	##########################################################################################
	def getYtitle(self,event=None):
		if self.m_plots == None: return
		dlg = wx.TextEntryDialog(None,'Enter the text for the Y axis', 'Y axis', style=wx.OK|wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			xstr = dlg.GetValue()
			self.m_firstAxes.set_ylabel(xstr)
			self.m_canvas.Refresh()
		dlg.Destroy()

	def getXtitle(self,event=None):
		if self.m_plots == None: return
		dlg = wx.TextEntryDialog(None,'Enter the text for the X axis', 'X axis', style=wx.OK|wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			xstr = dlg.GetValue()
			self.m_firstAxes.set_xlabel(xstr)
			self.m_canvas.Refresh()
		dlg.Destroy()

	def getTitle(self,event=None):
		if self.m_plots == None: return
		dlg = wx.TextEntryDialog(None,'Enter the text for the X axis', 'X axis', style=wx.OK|wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			xstr = dlg.GetValue()
			self.m_firstAxes.set_title(xstr)
			self.m_canvas.Refresh()
		dlg.Destroy()

	def chooseTickFontColor(self,event=None):
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			scolor=dlg.GetColourData().GetColour()
			acolor= self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
			self.m_tickFontColor=acolor
			self.redraw()
		dlg.Destroy()

		   
	def chooseLineColor(self,event=None): 
		if self.selectLineIndex < 0 : return
		axes = self.m_myFigure.get_axes()
		lines = axes[0].get_lines()
		xlen = len(lines)
		if xlen < 1: return 
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			k = self.selectLineIndex
			scolor=dlg.GetColourData().GetColour()
			acolor= self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
			xline = lines[k]
			xline.set_color(acolor)
			self.lineParameters[k][2] = acolor 
			self.m_canvas.Refresh()
		dlg.Destroy()
	
	def chooseBackground(self,event=None): 
		""" 
		This sets the background border ... <-- --> ...
		"""
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			scolor=dlg.GetColourData().GetColour()
			acolor= self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
			self.m_myFigure.set_facecolor(acolor)
			self.m_canvas.Refresh()
		dlg.Destroy()

	def chooseAxisBackground(self,event=None):
		""" 
		This sets the inner chart border ... <-- --> ...
		"""
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			scolor=dlg.GetColourData().GetColour()
			acolor= self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
			self.m_firstAxes.set_axis_bgcolor(acolor)
			self.m_canvas.Refresh()
		dlg.Destroy()

	# Replots using default line width of 1. 
	def defaultLine(self,pixels=1,lw=1):
		lines = self.m_firstAxes.get_lines()
		for line in lines:
			line.set_linewidth(lw)
			#line.set_markersize(pixels)
			line.set_linestyle('-')
		self.m_canvas.Refresh()
		   
	def defaultPoints(self,pixels=2,lw=0):
		pass   # Draw them again as scatter plots. 
		   
# Saves the plot as postscript file
	def postscript(self,event):
		#ofile = asksaveasfilename(filetypes=[("Postscript","*.ps"),("All Files","*")])
		dlg = wx.FileDialog(self,'Save to Postscript...', os.getcwd(), style=wx.SAVE|wx.OVERWRITE_PROMPT,
						wildcard='Postscript (*.ps)|*.ps |All Files (*.*) |*.*')
		if dlg.ShowModal() == wx.ID_OK:
			ofile = dlg.GetPath()
			self.m_canvas.print_figure(ofile, dpi=300)

	def doMinorGrid(self):
		self.m_showGraphPaper = not self.m_showGraphPaper
		self.redraw()

	########################################################################
	# 
	########################################################################	
	def setYaxisLimits(self,event=None):
		if self.m_plots == None: return
		self.setAxisLimits('Y')

	def setXaxisLimits(self,event=None):
		if self.m_plots == None: return
		self.setAxisLimits('X')

	def setAxisLimits(self,where):
		dlg = wx.TextEntryDialog(None,'Enter the lower limit as a float for the %s axis' % where, '%s axis' % where, style=wx.OK|wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				y0 = float(dlg.GetValue())
			except:
				dlg.Destroy()
				return
		dlg.Destroy()
		dlg = wx.TextEntryDialog(None,'Enter the upper limit as a float for the %s axis' % where, '%s axis' % where, style=wx.OK|wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				y1 = float(dlg.GetValue())
			except:
				dlg.Destroy()
				return
		dlg.Destroy()

		if y1 <= y0: 
			return
		if where == 'Y': self.m_firstAxes.set_ylim([y0,y1])
		if where == 'X': self.m_firstAxes.set_xlim([y0,y1])
		self.m_canvas.Refresh()

	########################################################################
	#  Untested.
	########################################################################	
	def zoomIn(self):
		"""
		Untested routine.
		"""
		print "X limit", self.m_firstAxes.get_xlim()
		print "Y limit", self.m_firstAxes.get_ylim()

		x0,x1 = self.m_firstAxes.get_xlim()
		y0,y1 = self.m_firstAxes.get_ylim()
		r = (x1 - x0) / 4
		self.m_firstAxes.set_xlim([x0 + r, x1 - r])
		r = (y1 - y0) / 4
		self.m_firstAxes.set_ylim([y0 + r, y1 - r])
		print "X limit", self.m_firstAxes.get_xlim()
		print "Y limit", self.m_firstAxes.get_ylim()
		self.m_canvas.Refresh()

	########################################################################
	# How do I force the replot and redraw on the screen.
	########################################################################	
	def resetZoom(self,event=None):
		"""
		Resets the axes to the best fit possible.
		"""
		if (self.m_plots) < 1: return 
		if self.m_plotType == 'image': 
			x = self.m_myFigure.get_axes()
			print "Setting limits...", self.image_nx, self.image_ny
			for a in x: 	
				a.set_xlim([0,self.image_nx])
				a.set_ylim([0,self.image_ny])
			self.m_canvas.Refresh()
			return
		
		plt = self.m_plots[0]
		x0 = min(plt.m_vector_x.flat)
		x1 = max(plt.m_vector_x.flat)
		y0 = min(plt.m_vector_y.flat)
		y1 = max(plt.m_vector_y.flat)
		
		for plt in self.m_plots: 
			#if plt.m_lined == False: continue
			if x0 > min(plt.m_vector_x.flat): x0 = min(plt.m_vector_x.flat)
			if x1 < max(plt.m_vector_x.flat): x1 = max(plt.m_vector_x.flat)
			if y0 > min(plt.m_vector_y.flat): y0 = min(plt.m_vector_y.flat)
			if y1 < max(plt.m_vector_y.flat): y1 = max(plt.m_vector_y.flat)
		self.m_firstAxes.set_xlim([x0,x1])
		self.m_firstAxes.set_ylim([y0,y1])
		self.m_canvas.Refresh()


# The next functions configure the axes
	def showAxis(self,event=None): 
		"""
		Debug function: Dumps axis parameters.
		"""
		#print self.m_firstAxes.get_xaxis()
		print dir(self.m_firstAxes)
		print "X limit", self.m_firstAxes.get_xlim()
		print "Y limit", self.m_firstAxes.get_ylim()
		#for plt in self.m_plots: 
		#	print plt.name
		#	print plt.m_vector_x[:3]
		#	print plt.m_vector_y[:3]

		#state = int(self.m_g.axis_cget("x", 'hide'))
		#self.m_g.axis_configure(["x", "y"], hide = not state)
		self.m_canvas.Refresh()
	
	def swapAxes(self,event=None):
		for plt in self.m_plots: 
			plt.m_vector_y,plt.m_vector_x =	plt.m_vector_x,plt.m_vector_y
		self.redraw()

	def scatterPlot(self,event=None):
		self.m_plotType = 'scatter'
		self.redraw()

	def histogramY(self,event=None):
		self.m_plotType = 'hist'
		self.redraw()

	def plotDates(self,event=None):
		self.m_plotType = 'dates'
		self.redraw()

	def filled(self,event=None):
		self.m_plotType = 'fill'
		self.redraw()

	def xlogScale(self,event=None):
		self.m_plotType = 'semilogx'
		self.redraw()
	
	def ylogScale(self,event=None):
		self.m_plotType = 'semilogy'
		self.redraw()

	def loglogScale(self,event=None):
		self.m_plotType = 'loglog'
		self.redraw()

	def nologScale(self,event=None):
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

	#def showCrosshairs(self):
		#hide = not int(self.m_g.crosshairs_cget('hide'))
		#self.m_g.crosshairs_configure(hide = hide, dashes="1")
		#if(hide):
			#self.m_g.unbind("<Motion>")
		#else:
			#self.m_g.bind("<Motion>", self.m_mouseMove)
	   
	############################################################################	
	# The next functions configures the Grid
	############################################################################	
	def f_showGrid(self,event=None):	
		self.m_firstAxes.grid(True)
		self.m_canvas.Refresh()

	def f_hideGrid(self,event=None):
		self.m_firstAxes.grid(False)
		self.m_canvas.Refresh()

	def showYgridLines(self,event=None):
		xaxis = self.m_firstAxes.get_xaxis()
		xaxis.grid(True)
		self.m_canvas.Refresh()

	def showXgridLines(self,event=None):
		yaxis = self.m_firstAxes.get_yaxis()
		yaxis.grid(True)
		self.m_canvas.Refresh()

	def setGridColor(self,how):
		glines = self.m_firstAxes.get_xgridlines()
		for gline in glines: gline.set_color(color)
		glines = self.m_firstAxes.get_ygridlines()
		for gline in glines: gline.set_color(color)
		self.m_canvas.Refresh()
	
	def redGrid(self,event=None):   self.setGridColor("r")
	def blueGrid(self,event=None):  self.setGridColor("b")
	def greenGrid(self,event=None): self.setGridColor("g")
	def blackGrid(self,event=None): self.setGridColor("k")

	def chooseGrid(self,event=None): 
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			scolor=dlg.GetColourData().GetColour()
			acolor= self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
			self.setGridColor(acolor)
		dlg.Destroy()

	# The next functions configures the Legend. 
	# BUG There is no way to hide the legend??
	def showLegend(self, event):
		self.legendLocation += 1
		if self.legendLocation > 10: self.legendLocation = 0
		self.redraw()

	def hideLegend(self,event):
		"""
		This function does not work, since I cannot seem to get rid of the legend once
		it is shown
		"""
		self.legendLocation = 0
		self.redraw()


	#def m_myaddmenu(self,menuBar, owner, label, command):
	#	menuBar.addmenuitem(owner, 'command', '<help context>', label = label, command = command)

	#def m_mychkmenu(self,menuBar, owner, label, command):
	#	menuBar.addmenuitem(owner, 'checkbutton', '<help context>', 
	#		label = label, command = command, variable=IntVar())
	
	def saveasimage(self,event):
		dlg = wx.FileDialog(self,'Save to Postscript...', os.getcwd(), style=wx.SAVE|wx.OVERWRITE_PROMPT,
				defaultFile="*.ps", 		
				wildcard='Postscript (*.ps)|*.ps|All Files (*.*) |*.*')
		if dlg.ShowModal() == wx.ID_OK:
			ofile = dlg.GetPath()
			self.m_canvas.print_figure(ofile, dpi=300)
		return 

	def setPrinterName(self,event):
		xstr = wx.GetTextFromUser("UNIX Printer Name (e.g. lplex125ps)", "Set Printer Name")
		if len(xstr) > 0: self.printString = 'rsh applsrv2 "/usr/ucb/lpr -h -P %s "' % xstr

	def printImage(self,event):
		self.m_canvas.Printer_Init()
		self.m_canvas.Printer_Preview()
		self.redraw()
		
# Create and pack the MenuBar.		
	def makeMenu(self,master,barchart=0):
		###########################################################################
		# This should be a series of classes for replication in pMultiplePlots.
		###########################################################################

		self.inaxesPopupMenu = wx.Menu()
		item = self.inaxesPopupMenu.Append(-1.,'Chart Color')
		self.Bind(wx.EVT_MENU,self.setChartColor,item)
		item = self.inaxesPopupMenu.Append(-1.,'Show Options')
		self.Bind(wx.EVT_MENU,self.toggleGrid,item)
		item = self.inaxesPopupMenu.Append(-1.,'Reset Zoom')
		self.Bind(wx.EVT_MENU,self.resetZoom,item)

		self.inborderPopupMenu = wx.Menu()
		item = self.inborderPopupMenu.Append(-1.,'Border Color')
		self.Bind(wx.EVT_MENU,self.setBorderColor,item)
		item = self.inborderPopupMenu.Append(-1.,'Toggle Grid')
		self.Bind(wx.EVT_MENU,self.toggleGrid,item)
		item = self.inborderPopupMenu.Append(-1.,'Reset Zoom')
		self.Bind(wx.EVT_MENU,self.resetZoom,item)

		################################ Make the File menu
		self.filemenu = wx.Menu()
		#btn = filemenu.Append(-1,"Setup"); self.Bind(wx.EVT_MENU, self.graphSetup, btn)  
		if os.name == 'posix': 
			#btn = self.filemenu.Append(-1,"Set Printer");  self.Bind(wx.EVT_MENU, self.setPrinterName, btn)
			btn = self.filemenu.Append(-1,"Print Image");  self.Bind(wx.EVT_MENU, self.printImage, btn)
		self.filemenu.AppendSeparator() 
		#btn = self.filemenu.Append(-1,"Save Image");  self.Bind(wx.EVT_MENU, self.saveasimage, btn)
		btn = self.filemenu.Append(-1,"PostScript");  self.Bind(wx.EVT_MENU, self.postscript, btn)
		self.filemenu.AppendSeparator() 
		btn = self.filemenu.Append(-1,"Read File");  self.Bind(wx.EVT_MENU, self.doReadFile, btn)
		btn = self.filemenu.Append(-1,"Show X Y ");  self.Bind(wx.EVT_MENU, self.dumpXY, btn)
		self.inaxesPopupMenu.AppendMenu(-1,'File',self.filemenu)

		self.gridmenu = wx.Menu()
		btn = self.gridmenu.Append(-1,"Show Grid"); self.Bind(wx.EVT_MENU, self.f_showGrid, btn)
		btn = self.gridmenu.Append(-1,"Hide Grid"); self.Bind(wx.EVT_MENU, self.f_hideGrid, btn)
		btn = self.gridmenu.Append(-1,"Show Horz"); self.Bind(wx.EVT_MENU, self.showXgridLines, btn)
		btn = self.gridmenu.Append(-1,"Show Vert"); self.Bind(wx.EVT_MENU, self.showYgridLines, btn)
		#btn = self.gridmenu.Append(-1,"Mouse Format Str"); self.Bind(wx.EVT_MENU, self.getYtitle, btn)
		self.inborderPopupMenu.AppendMenu(-1,'Grid',self.gridmenu)

		
		################################ Make the Axis menu
		self.axismenu = wx.Menu()
		btn = self.axismenu.Append(-1,"Zoom Reset"); self.Bind(wx.EVT_MENU, self.resetZoom, btn)
		btn = self.axismenu.Append(-1,"Main Title"); self.Bind(wx.EVT_MENU, self.getTitle, btn)
		btn = self.axismenu.Append(-1,"X Title"); self.Bind(wx.EVT_MENU, self.getXtitle, btn)
		btn = self.axismenu.Append(-1,"Y Title"); self.Bind(wx.EVT_MENU, self.getYtitle, btn)
		btn = self.axismenu.Append(-1,"Linear Scale");  self.Bind(wx.EVT_MENU, self.nologScale, btn)
		btn = self.axismenu.Append(-1,"X as dates"); self.Bind(wx.EVT_MENU, self.plotDates, btn)
		btn = self.axismenu.Append(-1,"Scatter Plot");  self.Bind(wx.EVT_MENU, self.scatterPlot, btn)
		btn = self.axismenu.Append(-1,"SwapAxes ");  self.Bind(wx.EVT_MENU, self.swapAxes, btn)
		btn = self.axismenu.Append(-1,"Swap XY"); self.Bind(wx.EVT_MENU, self.swapAxes, btn)
		btn = self.axismenu.Append(-1,"Filled"); self.Bind(wx.EVT_MENU, self.filled, btn)
		btn = self.axismenu.Append(-1,"X logscale"); self.Bind(wx.EVT_MENU, self.xlogScale, btn)
		btn = self.axismenu.Append(-1,"Y logscale"); self.Bind(wx.EVT_MENU, self.ylogScale, btn)
		btn = self.axismenu.Append(-1,"X limits"); self.Bind(wx.EVT_MENU, self.setXaxisLimits, btn)
		btn = self.axismenu.Append(-1,"Y limits"); self.Bind(wx.EVT_MENU, self.setYaxisLimits, btn)
		#btn = axismenu.Append(-1,"Log logscale"); self.Bind(wx.EVT_MENU, self.loglogScale, btn)
		#btn = axismenu.Append(-1,"Debug"); self.Bind(wx.EVT_MENU, self.showAxis, btn)
		self.inaxesPopupMenu.AppendMenu(-1,'Axis', self.axismenu)

		################################ Make the Axis menu
		self.optionmenu = wx.Menu()
		btn = self.optionmenu.Append(-1,"Background Color"); self.Bind(wx.EVT_MENU, self.chooseAxisBackground, btn)
		btn = self.optionmenu.Append(-1,"Border Color"); self.Bind(wx.EVT_MENU, self.chooseBackground, btn)
		btn = self.optionmenu.Append(-1,"Line Color"); self.Bind(wx.EVT_MENU, self.chooseLineColor, btn)
		#btn = self.optionmenu.Append(-1,"Comparative Display"); self.Bind(wx.EVT_MENU, self.toggleAllThree, btn)
		#btn = self.optionmenu.Append(-1,"Tick Font Color"); self.Bind(wx.EVT_MENU, self.chooseTickFontColor, btn)
		self.inaxesPopupMenu.AppendMenu(-1,'Colors',self.optionmenu)

		self.legendmenu = wx.Menu()
		btn = self.legendmenu.Append(-1,'Show'); self.Bind(wx.EVT_MENU, self.showLegend, btn)
		btn = self.legendmenu.Append(-1,'Hide'); self.Bind(wx.EVT_MENU, self.hideLegend, btn)
		self.inaxesPopupMenu.AppendMenu(-1,'Legend',self.legendmenu)


	####################################### HANDLERS 
	def mousePressHandler(self,event):
		"""
		Shows many different menus based on the location and
		button pressed. 
		"""
		#print dir(event)
		#print dir(event.guiEvent)
		#print event.button
		
		if event.button == 1 :
			self.dragging = 1 
			self.m_x0 = event.xdata
			self.m_y0 = event.ydata
			return 


		if event.button == 3:
			pos = (event.x,event.y)
			if event.inaxes: 
				self.m_canvas.PopupMenu(self.inaxesPopupMenu)
			else:
				self.m_canvas.PopupMenu(self.inborderPopupMenu)
		

	def resetLegend(self):
		lines=[]
		labels = []
		a = self.m_firstAxes
		lnx = a.get_lines()
		for ln in lnx:
			lbl = ln.get_label()
			if not lbl in labels:
				lines.append(ln)
				labels.append(lbl)
		figure = self.m_firstAxes.get_figure()
		if self.legendLocation > 0: 
			self.legendObj = figure.legend(lines,labels,self.legendLocation)
		if self.legendLocation < 0 or len(labels) < 1: 
			self.legendObj.set_visible(False)


	def toggleGrid(self,event):
		self.gridSetting = not self.gridSetting
		#for a in self.m_myFigure.get_axes(): a.grid(self.gridSetting)
		self.m_firstAxes.grid(self.gridSetting)
		self.m_canvas.Refresh()

	def setBorderColor(self,event):
		self.setDisplayAction('Border')

	def setChartColor(self,event):
		self.setDisplayAction('Chart')

	def setDisplayAction(self,displayAction):
		"""
		Handler to be called from within the popup menu on the charts dialog.
		"""
		if displayAction == 'Grid'   : 	
			self.gridSetting = not self.gridSetting
			for a in self.m_myFigure.get_axes(): a.grid(self.gridSetting)
			self.m_canvas.draw() 
			self.m_canvas.Refresh()
		if displayAction in ['Chart', 'Border']:	
			dlg = wx.ColourDialog(None)
			if dlg.ShowModal() == wx.ID_OK:
				if displayAction == 'Border':	
					scolor=dlg.GetColourData().GetColour()
					self.borderColor = self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
					self.m_myFigure.set_facecolor(self.borderColor)
				else:
					scolor=dlg.GetColourData().GetColour()
					self.faceColor = self.colorFormatString % (scolor.Red(),scolor.Green(),scolor.Blue())
					self.m_firstAxes.set_axis_bgcolor(self.faceColor)
			dlg.Destroy()
			self.m_canvas.Refresh()

				
	def setMouseDecimalPlaces(self,event=None):
		xstr = askinteger("Set Format string", "Enter number of decimal places")
		if xstr <> None:
			self.mouseFormatStr = '%.' + str(xstr) + 'f %.' + str(xstr) + 'f'


	def keyPressHandler(self,event):
		print "1341 - event.key = ", event.key
		if event.key == ' ': 
			self.selectLineIndex = -1 
			if self.statusbar <> None: 
				self.statusbar.SetStatusText("No Line selected",1)
			self.redraw()
			self.lineParmsDialog.Destroy()
			self.lineParmsDialog = None
		if event.key in ['m', 'p']: 
			#self.m_canvas.Printer_Init()
			#self.m_canvas.Printer_Setup()
			#self.m_canvas.Printer_Print()
			#self.redraw()
			print self.m_figure.getdpi()
			print self.m_figure.get_figheight()
			print self.m_figure.getfigurewidth()
			return 
		if event.key == 'l': 
			self.showLegend(None)
			return 
		if event.key == 's': 
			lines = event.inaxes.get_lines()
			xlen = len(lines)
			if xlen < 1: return 
			self.selectLineIndex += 1 
			self.selectLineIndex = self.selectLineIndex % xlen
			if self.statusbar <> None: 
				self.statusbar.SetStatusText("Line %d" % self.selectLineIndex,1)
			self.redraw()	
			if self.lineParmsDialog == None: self.makeParametersDialog()
			k = self.selectLineIndex
			print self.lineParameters[k]
			self.lineParmsDialog.setMaster(self,k)
			self.lineParmsDialog.setParameters(self.lineParameters[k])
			self.lineParmsDialog.Show()


	def handleDeadLineParms(self,who):
		if who.lineParmsDialog <> None: 
			self.lineParmsDialog.Destroy()
		self.lineParmsDialog = None

	def setLineParameters(self,who,where,parms): 
		who.lineParameters[where] = parms
		self.redraw()

	def makeParametersDialog(self):	
		self.lineParmsDialog = pwxChartParms(None, -1, "")
		# lbl, lns, lineColor, lineWidth, markerType, markerColor, mSize = dlg.getParameters()
		
	def mouseMovementHandler(self,event):
		if self.mouseFormatStr <> None:
			fmtstr = self.mouseFormatStr
		else:
			fmtstr = '%f %f'
		if len(self.mouseFormatStr) < 1: fmtstr = '%f %f'
		if event.inaxes:
			#if 1:
			try:
				if self.m_plotType == 'image': 
					x = int(event.xdata)
					y = int(event.ydata)
					images = event.inaxes.get_images()
					v = len(images)
					lbl = event.inaxes.get_label()
					if len(images) > 0: 
						data   = images[0].get_array()
						v = data[y][x]
						outstr = "%f,%f,%f" % (v,x,y)
					else:
						outstr = "%s,%f,%f" % (lbl,x,y)
				elif self.m_plotType == 'dates': 
					if event.xdata > 0: 
						idt = num2date(int(event.xdata))
						outstr = "%s,%f" % (idt.strftime("%Y-%m-%d"),event.ydata)
					else: 
						outstr= "x=%f, y=%f" % (event.xdata, event.ydata)
				else: 
					idt = str(event.xdata)
					outstr= "x=%f, y=%f" % (event.xdata, event.ydata)

			except:
				outstr= "x=%f, y=%f" , event.xdata, event.ydata
		else: 
			outstr = ""
		if self.statusbar <> None: self.statusbar.SetStatusText(outstr ,0)
		
	def mouseReleaseHandler(self,event):
		if event.button == 1:
			if self.dragging:
				self.dragging = 0 #print "Dragging done, ", event.xdata, event.ydata
				if event.inaxes == None: return
				self.m_x1 = event.xdata
				self.m_y1 = event.ydata
				dx = abs(self.m_x0 - self.m_x1) 
				dy = abs(self.m_y0 - self.m_y1)
				if dx < 2 and dy < 2: 
					self.resetZoom()
					return 
				if (self.m_x0 <> self.m_x1) and (self.m_y0 <> self.m_y1):
					if (self.m_x0 > self.m_x1): self.m_x0,self.m_x1 = self.m_x1,self.m_x0
					if (self.m_y0 > self.m_y1): self.m_y0,self.m_y1 = self.m_y1,self.m_y0
					#xlim = self.m_x0, self.m_x1 
					#ylim = self.m_y0, self.m_y1 
					#dR = 0.0
					#p1 = 0.0
					#p0 = 0.0
					#try:
					#	ax.set_xlim(xlim)
					#except:
					#	showwarning("Please drag within one axes.")
					#	return
					#ax.set_ylim(ylim)
					x = self.m_myFigure.get_axes()
					for a in x: 	
						a.set_xlim([self.m_x0,self.m_x1])
						a.set_ylim([self.m_y0,self.m_y1])
					#self.m_firstAxes.set_xlim([self.m_x0,self.m_x1])
					#self.m_firstAxes.set_ylim([self.m_y0,self.m_y1])
					self.m_canvas.draw() 
					self.m_canvas.Refresh()

	##########################################################################
	def openFile(self):
		"""
		shows a FileDialog, and return the selected file name. 
		"""
		dlg = wx.FileDialog(self,"Read XY data", os.getcwd(),style=wx.OPEN,
			wildcard = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*")
		fname = None
		if dlg.ShowModal() == wx.ID_OK: fname = dlg.GetPath()
		dlg.Destroy()
		return fname
			
	##########################################################################
	def doReadFile(self,event):
		"""
		Reads in a csv file. Values must be floating point numbers.
		Blank lines or with hash as first character will be ignored. 
		First column Col 0 is X 
		Second column Col 1 is Y 
		The file must be a text file with each line on the form: 
		<whitespace><number><whitespace><comma><whitespace><number><whitespace>\n
		"""
		ifile = self.openFile() 
		if ifile <> None:self.readFile(ifile)

	##########################################################################
	def readFile(self,filename,col1=0,col2=1):
		"""
		Reads in a csv file. Values must be floating point numbers.
		Blank lines or with hash as first character will be ignored. 
		col1 is the index for x axis. 
		col2 is the index for y axis. 
		"""
		file = open(filename,'r')
		xlines = file.readlines()
		file.close()
		print xlines
		self.useCSVdata(os.path.basename(filename),xlines,col1,col2)

	##########################################################################
	def useCSVdata(self,title,csvdata,col1=0,col2=1,how=' '):
		xdata = []
		ydata = []
		for line in csvdata:
			if len(line) < 2:  continue
			if line[0] == '#': continue
			items = string.split(line,how) 
			k = len(items)
			if k < col2 or k < col1: continue
			x = items[col1]
			y = items[col2]
			xdata.append(float(x))
			ydata.append(float(y))
		self.setData(title,xdata,ydata)

	##########################################################################
	def dumpXY(self,event):
		"""
		For all elements, print out the values of x vs. y in a separate text dialog. 
		"""
		for plt in self.m_plots: 
			xstr = '#' + plt.name + "\n"
			pp = wx.PySimpleApp() 
			ff = MyGridDataFrame(title=xstr)
			dd = (plt.m_vector_x, plt.m_vector_y)
			ff.setData(len(plt.m_vector_x),2,dd,None,['x','y'])
			ff.Show()
			ff.MainLoop()

	##########################################################################
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
# The main application goes here. 
##########################################################################
class MyApp(wx.App):
	def OnInit(self):
		self.fame = pwxPlotHolder(None,-1,"Hello")
		self.fame.Show()
		self.SetTopWindow(self.fame)
		return True

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
		if len(line) < 1: continue
		if line[0] == '#': continue
		if not line[0] in string.digits: continue
		items = string.split(tline) 
		xdata.append(float(items[xcol]))
		ydata.append(float(items[ycol]))
		if y2col <> None:
			y2data.append(float(items[y2col]))
			
	
	root = MyApp()
	root.fame.m_plotThaing.setTupleData(sys.argv[1],xdata,ydata)
	root.MainLoop()					# ...and wait for input
