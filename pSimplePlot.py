"""
 A very simple XY plotter.
 October 5, 2004 - Kamran - replacing the BLT calls with matplotlib
 July 13, 2003 - Kamran - Added limits format
 10/8/2003 Added histogram support for raw X value on axis.
 05/1/2003 Added barchart  support for raw X value on axis.
 Added the ability to use axes instead of the Plot
"""

###########################################################################

import numarray
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
from matplotlib.dates import date2num, num2date, YearLocator, MonthLocator, DateFormatter

###########################################################################
from Tkinter import *		# The Tk package
from tkSimpleDialog import * 
from tkMessageBox import * 
from tkFileDialog import *
import os
import tkFileDialog		  # To be able to ask for files
import Pmw				  # The Python MegaWidget package
import math				  # import the sin-function
import string
import sys
import time, datetime
from tkColorChooser import *
from copy import copy
from pChartOptions import *

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

	def setdata(self,x,y,nm,linetype=None):
		self.m_vector_x  = x
		self.m_vector_y  = y
		self.name = nm
		self.lineType = linetype 

class pSimpleXYPlotter:
	def __init__(self,parent,filename=None,xcol=0,ycol=1,barchart=0):
		self.m_master = parent
		self.m_filename = filename
		self.m_xcol = xcol
		self.m_ycol = ycol
		self.m_plotType = 'plot'              # Default x vs. y plot
		self.m_plotTitle = ''                 # No titles 
		self.printString = "lpr -h -Plplex125ps" 
		self.showColorBar = 0 
		self.showAllThree = True 

		###########################################################################
		# END OF NEW
		###########################################################################
		self.mouseFormatStr = '%.2f,%.2f'              # For tracking the mouse.
		self.gridSetting       = True                     # Default 
		self.legendLocation = 1
		self.legendLocations = { 'Upper Right' : 1, 'Upper Left' :2, 'Lower Left' : 3, 'Lower Right' : 4, 
				 'Center Left' : 6, 'Center Right': 7, 'Lower Center': 8, 'Upper Center': 9, 
				'Center': 10, 'Outside Rt': 11}
		self.legendObj = None
		self.lineTypes = LINETYPES 
		self.colors    = COLORTYPES
		self.markerTypes = MARKERTYPES
		self.xlabel = ''
		self.ylabel = ''

		#
		# Start of items required for options....
		#
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
			
		self.makeMenu(self.m_master,barchart)

		self.mouseText = Label(self.m_master,height=1)
		self.mouseText.pack(side=TOP,fill=X,expand=0)

		self.m_myFigure = Figure() # figsize=(5,5),dpi=200)   # Set the appropriately
		self.m_firstAxes = None
		self.m_canvas = FigureCanvasTkAgg(self.m_myFigure,master=self.m_master)
		self.m_canvas.get_tk_widget().pack(side=TOP,expand=1, fill='both')
		
		if os.name <>'nt': 	self.m_canvas.get_tk_widget()['cursor'] = 'crosshair'
		self.m_canvas.mpl_connect('motion_notify_event',	self.mouseMovementHandler) # NO clicks here.
		self.m_canvas.mpl_connect('button_press_event',	    self.mousePressHandler)    # Only movement.
		self.m_canvas.mpl_connect('button_release_event',	self.mouseReleaseHandler)
		###########################################################################
		# END OF NEW
		###########################################################################

		self.m_tickFontColor = 'black'
		self.m_tickFontSize = 8.0
		self.m_tickFontRotation = 45.0

		self.m_plots   = []                               # My plots
		self.m_vector_x = []
		self.m_vector_y = []


	######################################################################################
	# Make the graph area
	######################################################################################
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

	def mapObjToLineParms(self):
		dparms = {}
		dparms['LINEPARAMETERS']= self.lineparameters; 
		dparms['SHOWGRID'] 		= self.showGrid
		dparms['GRIDLINESTYLE'] = self.gridLineStyle 
		dparms['BORDERCOLOR']   = self.borderColor
		dparms['FACECOLOR']     = self.faceColor; 
		return dparms; 
		
	def mapLineParmsToObj(self,dparms):
		p = dparms.get('LINEPARAMETERS',None) 
		if p <> None: self.lineparameters = p 
		self.showGrid = dparms.get('SHOWGRID',1)
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
	

	def findPlot(self,fname):
		plt = None
		if self.m_plots == None:
			plt = pSimplePlotElement(fname)						# Create a place holder. 
			self.m_plots = [plt]
			return plt
		for plt in self.m_plots:
			if plt.name == fname: return plt 
		plt = pSimplePlotElement(fname)						# Create a place holder. 
		self.m_plots.append(plt)                 
		return plt

	def setTupleData(self,fname,xdata,ydata,useLeft=1,linetype=None):
		"""
		We are getting tuples and must convert to numarray arrays here. 
		"""
		plt = self.findPlot(fname)
		m_vector_x  = numarray.asarray(xdata)
		m_vector_y  = numarray.asarray(ydata)
		print "X TUPLE", type(m_vector_x), len(m_vector_x), m_vector_x[:5]
		print "Y TUPLE", type(m_vector_y), len(m_vector_y), m_vector_y[:5]
		plt.setdata(m_vector_x,m_vector_y,fname,linetype)
		self.redraw()
		#self.setData(fname,xdata,ydata)

	def setnumarrayData(self,fname,xdata,ydata,useLeft=1):
		"""
		We are getting numarray arrays here. 
		"""
		plt = self.findPlot(fname)
		plt.setdata(xdata,ydata,fname) # Set directly
		self.redraw()                  

	def setData(self,fname,xdata,ydata,linetype=None):
		"""
		We are getting generic lists or  arrays here. 
		"""
		plt = self.findPlot(fname)
		m_vector_x  = numarray.asarray(xdata)
		m_vector_y  = numarray.asarray(ydata)
		plt.setdata(m_vector_x,m_vector_y,fname,linetype)
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
		#self.m_canvas.show()

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
		self.m_canvas.show()

	def clearPlots(self,all=1):
		if self.m_myFigure == None: return 
		x = self.m_myFigure.get_axes()
		for a in x: self.m_myFigure.delaxes(a)
		for plt in self.m_plots:  del plt
		self.m_plots = []
		self.m_myFigure.clf()
		self.m_canvas.show()

	def setPlotTitle(self,title):
		self.setTitle(title)

	def setTitle(self,title):
		self.m_plotTitle = title
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_title(self.m_plotTitle)
			self.m_canvas.show()

	def setYlabel(self,ylabel):
		self.ylabel = ylabel

	def setXlabel(self,xlabel):
		self.xlabel = xlabel

	def setYtitle(self,title):
		self.ylabel = title
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_ylabel(title)
			self.m_canvas.show()

	def setXtitle(self,title):
		self.xlabel = title
		if self.m_firstAxes <> None: 
			self.m_firstAxes.set_xlabel(title)
			self.m_canvas.show()

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

	def toggleAllThree(self):
		self.showAllThree = not self.showAllThree
		self.redraw()
				
	def redraw(self,legend=True,location=-1):
		"""
		Get names of plots and plot individually.
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
		j = 0
		#print "MPLOTS = ", len(self.m_plots)
		for plt in self.m_plots: 
			cp_vector_x = plt.m_vector_x  # Why am I copying again?
			cp_vector_y = plt.m_vector_y
			#if plt.m_lined == False: continue
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
			if function <> None:
				function(cp_vector_x,cp_vector_y,label=plt.name,
					color=lineColor, 
					linestyle=lns, 
					linewidth=lineWidth, 
					marker=markerType, 
					markerfacecolor=markerColor, 
					markersize=mSize)
			labels.append(plt.name)

		for a in self.m_myFigure.get_axes(): a.grid(self.gridSetting)
		
		if len(self.m_plots) < 1: return
		plt = self.m_plots[0] 
		if self.m_plotTitle <> None:
			if len(self.m_plotTitle) > 0: 
				self.m_firstAxes.set_title(self.m_plotTitle)

		self.resetLegend()
		#print "Setting limits", xlim, ylim
		#self.m_firstAxes.set_xlim(xlim)
		#self.m_firstAxes.set_ylim(ylim)

		print "I am setting the Y label now : ", self.ylabel , " ..."
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
			
		ff.setTupleData(fname,xdata,ydata)

			

	#########################################################################################
	# These apply to the specific plot being shown. For now, I am defaulting ro the first
	# plot in the list of plots. 
	##########################################################################################
	def getYtitle(self):
		if self.m_plots <> None: 
			xstr = askstring("Y Label", "->")
			if xstr <> None:
				self.m_firstAxes.set_ylabel(xstr)
				self.m_canvas.show()


	def getXtitle(self):
		if self.m_plots <> None: 
			xstr = askstring("X Label", "->")
			if xstr <> None:
				self.m_firstAxes.set_xlabel(xstr)
				self.m_canvas.show()

	def getTitle(self):
		if self.m_plots <> None: 
			xstr = askstring("Title", "->")
			if xstr <> None:
				self.m_firstAxes.set_title(xstr)
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
			self.m_firstAxes.set_axis_bgcolor(scolor)
			self.m_canvas.show()



	# Replots using default line width of 1. 
	def defaultLine(self,pixels=1,lw=1):
		lines = self.m_firstAxes.get_lines()
		for line in lines:
			line.set_linewidth(lw)
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
		self.m_firstAxes.set_ylim([y0,y1])
		self.m_canvas.show()

	def setXAxisLimits(self):
		x0 = askfloat('Please enter lower limit for X axis',"X0")
		if x0 == None: return 
		x1 = askfloat('Please enter upper limit for X axis',"X1")
		if x1 == None: return 
		if x1 <= x0: 
			showwarning("Cannot set x1 lower than or equal to x0", "Error")
			return
		self.m_firstAxes.set_xlim([x0,x1])
		self.setTickLabels(yearSpan)
		self.m_canvas.show()
	########################################################################
	# 
	########################################################################	
	def zoomIn(self):
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
		self.m_canvas.show()

	########################################################################
	# How do I force the replot and redraw on the screen.
	########################################################################	
	def resetZoom(self):
		if (self.m_plots) < 1: return 
		if self.m_plotType == 'image': 
			x = self.m_myFigure.get_axes()
			print "Setting limits...", self.image_nx, self.image_ny
			for a in x: 	
				a.set_xlim([0,self.image_nx])
				a.set_ylim([0,self.image_ny])
			self.m_canvas.show()
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
		print "Resetting zoom ", x0,x1,y0,y1
		self.m_canvas.show()


# The next functions configure the axes
	def showAxis(self): 
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
		self.m_canvas.show()
	
	def swapAxes(self):
		for plt in self.m_plots: 
			plt.m_vector_y,plt.m_vector_x =	plt.m_vector_x,plt.m_vector_y
		self.redraw()

	def scatterPlot(self):
		self.m_plotType = 'scatter'
		self.redraw()

	def histogramY(self):
		self.m_plotType = 'hist'
		self.redraw()

	def plotDates(self):
		self.m_plotType = 'dates'
		self.redraw()

	def filled(self):
		self.m_plotType = 'fill'
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
	def showGrid(self):	
		self.m_firstAxes.grid(True)
		self.m_canvas.show()

	def hideGrid(self):
		self.m_firstAxes.grid(False)
		self.m_canvas.show()

	def showYgridLines(self,how=-11):
		xaxis = self.m_firstAxes.get_xaxis()
		xaxis.grid(True)
		self.m_canvas.show()

	def showXgridLines(self):
		yaxis = self.m_firstAxes.get_yaxis()
		yaxis.grid(True)
		self.m_canvas.show()

	def setGridColor(self,color):
		glines = self.m_firstAxes.get_xgridlines()
		for gline in glines: gline.set_color(color)
		glines = self.m_firstAxes.get_ygridlines()
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
		self.legendLocation = whence
		if whence == 11: legend._loc = (1.0,0.5)
		self.resetLegend()
		self.redraw()

	def testLegend(self,tup=(1.0,0.5)):
		legend = self.m_firstAxes.get_legend()
		legend._loc = tup
		self.redraw()

	def hideLegend(self):
		self.legendLocation = 0
		self.redraw()

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
		xstr = askstring("UNIX Printer Name (e.g. lplex125ps)", "Set Printer Name")
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
		
		if os.name == 'posix': 
			self.m_myaddmenu(self.m_menuBar, 'File', 'Set Printer ', self.setPrinterName)
			self.m_myaddmenu(self.m_menuBar, 'File', 'Print ', self.printImage)
			self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Save as image', self.saveasimage)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Save as ps', self.postscript)
		self.m_menuBar.addmenuitem('File', 'separator')
		#self.m_myaddmenu(self.m_menuBar, 'File', 'Default Lines', self.defaultLine)
		#self.m_myaddmenu(self.m_menuBar, 'File', 'Default Points', self.defaultPoints)
		#self.m_menuBar.addmenuitem('File', 'separator')
		self.m_myaddmenu(self.m_menuBar, 'File', 'Read Text', self.doReadFile)
		self.m_myaddmenu(self.m_menuBar, 'File', 'Show XY', self.dumpXY)

		#self.m_myaddmenu(self.m_menuBar, 'File', 'Quit',	   master.quit)

# Make the Axis menu				
		self.m_menuBar.addmenu('Axis', '')
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Zoom Reset',  self.resetZoom  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Line Only', self.nologScale )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'X Dates ', self.plotDates )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Scatter', self.scatterPlot)
		#Not working...self.m_myaddmenu(self.m_menuBar, 'Axis', 'Histogram Y',  self.histogramY  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Swap', self.swapAxes)
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Filled Line', self.filled )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Set X limits',  self.setXAxisLimits  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Set Y limits',  self.setYAxisLimits  )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'x logscale', self.xlogScale )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'y logscale', self.ylogScale )
		#Prone to disaster self.m_myaddmenu(self.m_menuBar, 'Axis', 'Log logscale', self.loglogScale )
		self.m_myaddmenu(self.m_menuBar, 'Axis', 'Debug Only',  self.showAxis  )
		
# Make the Background menu				
		self.m_menuBar.addmenu('Options', '')
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Comparative Display', self.toggleAllThree)
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set backgd color', self.chooseAxisBackground)
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set border color', self.chooseBackground)
		self.m_myaddmenu(self.m_menuBar, 'Options', 'Set ticks color', self.chooseTickFontColor)
		
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'descending', self.descending)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'x looseScale', self.xloose)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'y looseScale', self.yloose)
		####self.m_mychkmenu(self.m_menuBar, 'Axis', 'hide',	   self.showAxis  )

# Make the Grid menu
		self.m_menuBar.addmenu('Grid', '')
		#self.m_mychkmenu(self.m_menuBar, 'Grid', 'show', self.showGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show', self.showGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'hide', self.hideGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show Horz', self.showXgridLines )
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'show Vert', self.showYgridLines )
		#self.m_myaddmenu(self.m_menuBar, 'Grid', 'Minor', self.doMinorGrid)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Main Title', self.getTitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'X Title', self.getXtitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Y Title', self.getYtitle)
		self.m_myaddmenu(self.m_menuBar, 'Grid', 'Mouse Format Str', self.setMouseDecimalPlaces)
		#self.m_menuBar.addcascademenu('Grid', 'Color ', '')
		#self.m_myaddmenu(self.m_menuBar, 'Color ', 'red',   self.redGrid  )
		#self.m_myaddmenu(self.m_menuBar, 'Color ', 'blue',  self.blueGrid )
		#self.m_myaddmenu(self.m_menuBar, 'Color ', 'green', self.greenGrid)
		#self.m_myaddmenu(self.m_menuBar, 'Color ', 'black', self.blackGrid)
		#self.m_myaddmenu(self.m_menuBar, 'Color ', 'choose', self.chooseGrid)

		self.m_menuBar.addmenu('Legend', '')
		self.m_menuBar.addcascademenu('Legend', 'Type', '')
		self.legendLocations = { 'Upper Right' : 1, 'Upper Left' :2, 'Lower Left' : 3, 'Lower Right' : 4, 
				 'Center Left' : 6, 'Center Right': 7, 'Lower Center': 8, 'Upper Center': 9, 
				'Center': 10, 'Outside Rt': 11}
		a = lambda s=self,x=0: s.hisegend(x)
		self.m_myaddmenu(self.m_menuBar, 'Legend', 'Hide/Show', self.hideLegend)
		#The following option does not work: 'Right' : 5,

		s = self.legendLocations.keys()
		s.sort()
		for i in s:
			t = self.legendLocations[i]
			a = lambda s=self,x=t: s.showLegend(x)
			self.m_myaddmenu(self.m_menuBar, 'Type', i, a)


	####################################### HANDLERS 
	def mousePressHandler(self,event):
		"""
		Shows many different menus based on the location and
		button pressed. 
		"""
		#print dir(event)
		#print dir(event.guiEvent)
		#print event.button
		if event.button == 2 :
			self.dragging = 1 
			self.m_x0 = event.xdata
			self.m_y0 = event.ydata
			return 
		if event.button == 3:
			menu = Menu(self.m_master,tearoff=0)
			if event.inaxes: 
				a = lambda s=self,m='Chart': s.setDisplayAction(m)
				menu.add_command(label='Set Chart Color',command=a)
				a = lambda s=self,m='Options': s.setDisplayAction(m)
				menu.add_command(label='Options',command=a)
				#a = lambda s=self,e=event:s.showSeparateWindow(e)
				#menu.add_command(label='Show Separately',command=a)
				#a = lambda s=self,e=event:s.showDifferences(e)
				#menu.add_command(label='Show Differences',command=a)
				#a = lambda s=self,m='ZoomIn': s.setDisplayAction(m)
				#menu.add_command(label='Zoom In',command=a)
			else:
				a = lambda s=self,m='Title': s.setTitle(m)
				menu.add_command(label='Edit Title',command=a)
				a = lambda s=self,m='Border': s.setDisplayAction(m)
				menu.add_command(label='Set Border Color',command=a)
				a = lambda s=self,m='Test': s.testThis(m)
				menu.add_command(label='Clear',command=a)
			a = lambda s=self,m='Grid': s.setDisplayAction(m)
			menu.add_command(label='Toggle Grid',command=a)
			menu.add_command(label='Reset Zoom',command=self.resetZoom)
			menu.tk_popup(event.guiEvent.x_root,event.guiEvent.y_root)		
			#a = lambda s=self,m='ResetZoom': s.setDisplayAction(m)
			#menu.add_command(label='Reset Zoom',command=a)
			return

	def showOptions(self,fm=None):
		linenames = []
		if self.legendObj <> None: 
			txts = self.legendObj.get_texts()
			linenames = [ i.get_text() for i in txts]
		if fm <> None:
			self.chartOptsDlg = fm
		else:
			self.chartOptsDlg = Tk()
		self.chartOpts = chartOptions(self,self.chartOptsDlg,linenames)
		self.chartOpts.applyReadOptions(self.lineParameters)
		self.chartOpts.pack(side=TOP,fill=BOTH,expand=1)

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

	def setDisplayAction(self,displayAction):
		"""
		Handler to be called from within the popup menu on the charts dialog.
		"""
		if displayAction == 'Options': 	self.showOptions(); return
		if displayAction == 'Grid'   : 	
			self.gridSetting = not self.gridSetting
			for a in self.m_myFigure.get_axes(): a.grid(self.gridSetting)
			self.m_canvas.draw() 
			self.m_canvas.show()
		if displayAction == 'Border':	
			ret = askcolorstring('Set Border Color')		
			if ret == None: return 
			self.borderColor = ret
			self.m_myFigure.set_facecolor(self.borderColor)
			self.m_canvas.show()
		if displayAction == 'Chart': 	
			ret = askcolorstring('Set Background Color')		
			if ret == None: return 
			self.faceColor = ret
			self.m_firstAxes.set_axis_bgcolor(ret)
			self.m_canvas.show()

				
	def setMouseDecimalPlaces(self):
		xstr = askinteger("Set Format string", "Enter number of decimal places")
		if xstr <> None:
			self.mouseFormatStr = '%.' + str(xstr) + 'f %.' + str(xstr) + 'f'
			
		
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
						outstr= " %f, %f " % (event.xdata, event.ydata)
				else: 
					idt = str(event.xdata)
					outstr= " %f, %f " % (event.xdata, event.ydata)

			except:
				outstr= " %f, %f " , event.xdata, event.ydata
		else: 
			outstr = ""
		self.mouseText['text'] = outstr 
		
	def mouseReleaseHandler(self,event):
		if event.button == 2 :
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
					self.m_canvas.show()

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
		xlines = file.readlines()
		file.close()
		self.useCSVdata(filename,xlines,col1,col2)

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
		self.setTupleData(title,xdata,ydata)

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
		if len(line) < 1: continue
		if line[0] == '#': continue
		if not line[0] in string.digits: continue
		items = string.split(tline) 
		xdata.append(float(items[xcol]))
		ydata.append(float(items[ycol]))
		if y2col <> None:
			y2data.append(float(items[y2col]))
			
	root = Tk()				  # build Tk-environment
	ff = pSimpleXYPlotter(root)
	ff.setTupleData(sys.argv[1],xdata,ydata)
	if y2col <> None:
		ff.setTupleData("4"+sys.argv[1],xdata,y2data)
	root.mainloop()					# ...and wait for input
