
"""
This is for setting your parameters for each line. 
TODO:
	reset the style to not include the close 
"""

import os, sys
import numarray
import matplotlib
from matplotlib.numerix import arange, sin, pi
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

class pwxChartParms(wx.Frame):
	def __init__(self, *args, **kwds):

		self.linestyles = {"solid":"-","dashed" : "--" , "dash-dot": "-." , "dotted" : ':' } # , "points": '.', "pixels" :',' }
		self.markerstyles = { 
			"None" : ' ', "Circles" : 'o', 
			"Up-Triangle" : '^' , "Dn-Triangle" : 'v' , "Lt-Triangle" : '<' , "Rt-Triangle" : '>', 
			"Square" : 's' , "Plus" : '+' , "Cross" : 'x' ,
			"Diamond" : 'D' , 
			"Thin-Diamond" : 'd', "Up-Tripod" : "2" , "Dn-Tripod" :"1",
			"Lt-Tripod" : "3", "Rt-Tripod" : "4" , "Hexagon-1" : "H" , "Hexagon-2" : "h" ,
			"Pentagon" : 'p', "Vertical" : '|' , "Horizontal" : '_'  } 
		self.markerstyleskeys = self.markerstyles.keys()
		self.markerstyleskeys.sort()
		# begin wxGlade: pwxChartParms.__init__
		kwds["style"] = wx.DEFAULT_FRAME_STYLE
		#kwds["style"] = wx.RESIZE_BORDER
		wx.Frame.__init__(self, *args, **kwds)
		self.sizer_4_staticbox = wx.StaticBox(self, -1, "Line Parameters")
		self.sizer_5_staticbox = wx.StaticBox(self, -1, "")
		self.sizer_6_staticbox = wx.StaticBox(self, -1, "")
		self.sizer_3_staticbox = wx.StaticBox(self, -1, "Trace name")
		self.label_1 = wx.StaticText(self, -1, "Line label", style=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE)
		self.text_ctrl_trace = wx.TextCtrl(self, -1, "")
		self.button_trace_color = wx.Button(self, -1, "Color of trace")
		self.spin_ctrl_1 = wx.SpinCtrl(self, -1, "1", min=0, max=10)
		self.combo_box_line_type = wx.ComboBox(self, -1, "solid", choices= self.linestyles.keys(),style=wx.CB_DROPDOWN)
		self.button_marker_color = wx.Button(self, -1, "Color of marker")
		self.spin_ctrl_marker = wx.SpinCtrl(self, -1, "1", min=0, max=10)
		self.combo_box_marker_type = wx.ComboBox(self, -1, "None", choices=self.markerstyleskeys, style=wx.CB_DROPDOWN)
		self.m_myFigure = Figure(figsize=(1,1),dpi=100)   # Set the appropriately
		self.m_canvas = FigureCanvas(self,-1,self.m_myFigure)
		self.button_3 = wx.Button(self, -1, "Redraw")
		self.button_4 = wx.Button(self, -1, "Reset")
		self.button_5 = wx.Button(self, -1, "Apply")

		self.__set_properties()
		self.__do_layout()
		# end wxGlade

		#
		# I have to set the bindings here. 
		#
		self.Bind(wx.EVT_BUTTON, self.drawSampleTrace, self.button_3)
		self.Bind(wx.EVT_BUTTON, self.resetLine, self.button_4)
		self.Bind(wx.EVT_BUTTON, self.applyParms, self.button_5)
		self.Bind(wx.EVT_CLOSE, self.handleDeadPlot)

		self.Bind(wx.EVT_BUTTON, self.setTraceColor, self.button_trace_color)
		self.Bind(wx.EVT_BUTTON, self.setMarkerColor, self.button_marker_color)
		self.Bind(wx.EVT_COMBOBOX, self.setTraceStyle, self.combo_box_line_type)
		self.Bind(wx.EVT_COMBOBOX, self.setMarkerStyle, self.combo_box_marker_type)

		self.Bind(wx.EVT_SPINCTRL, self.setLineWidth, self.spin_ctrl_1)
		self.Bind(wx.EVT_SPINCTRL, self.setMarkerWidth, self.spin_ctrl_marker)

	def __set_properties(self):
		# begin wxGlade: pwxChartParms.__set_properties
		self.SetTitle("Set Line Parameters")
		self.combo_box_line_type.SetSelection(-1)
		self.combo_box_marker_type.SetSelection(-1)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: pwxChartParms.__do_layout
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_2 = wx.BoxSizer(wx.VERTICAL)
		sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
		sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
		sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
		sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
		sizer_3.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 1)
		# sizer_3.Add(self.text_ctrl_trace, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
		sizer_4.Add(self.button_trace_color, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_4.Add(self.spin_ctrl_1, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_4.Add(self.combo_box_line_type, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_2.Add(sizer_4, 0, wx.EXPAND, 0)
		sizer_5.Add(self.button_marker_color, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_5.Add(self.spin_ctrl_marker, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_5.Add(self.combo_box_marker_type, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_2.Add(sizer_5, 0, wx.EXPAND, 0)
		#sizer_2.Add(self.text_ctrl_1, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		#self.sizer = wx.BoxSizer(wx.VERTICAL)
		sizer_2.Add(self.m_canvas, 1, wx.LEFT| wx.TOP | wx.GROW)
		sizer_6.Add(self.button_3, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_6.Add(self.button_4, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_6.Add(self.button_5, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
		sizer_2.Add(sizer_6, 0, wx.EXPAND, 0)
		sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
		self.SetAutoLayout(True)
		self.SetSizer(sizer_1)
		sizer_1.Fit(self)
		sizer_1.SetSizeHints(self)
		self.Layout()
		# end wxGlade

		self.m_firstAxes = None 
		self.x = arange(10) * 1.0
		self.y = arange(10) * 1.0 
		self.label = ''
		self.lineColor = 'b'
		self.lineStyle = '-'
		self.lineWidth  = 1
		self.markerType  = ''
		self.markerColor = 'r'
		self.markerSize = 0
		self.master = None
		self.linenumber = 0

	def handleDeadPlot(self,event):
		if self.master == None: return 
		self.master.handleDeadLineParms(self.master)

	def applyParms(self,event):
		if self.master == None: return 
		self.master.setLineParameters(self.master, self.linenumber, [self.label, self.lineStyle, self.lineColor , self.lineWidth  , self.markerType  , self.markerColor , self.markerSize] )
	
	def setMaster(self,who,ln):
		self.master = who
		self.linenumber = ln

	def getParameters(self): 
		return ( [self.label, self.lineColor, self.lineStyle , self.lineWidth  , self.markerType  , self.markerColor ,
		self.markerSize] )

	def setParameters(self,parms):
		"""
		lbl, style.color.width of line type.color.size of marker.
		"""
		self.label,  self.lineStyle , self.lineColor , self.lineWidth , self.markerType , \
		self.markerColor , self.markerSize  = parms
		self.drawSampleTrace()

	def resetLine(self,event=None):
		self.lineStyle = '-'
		self.lineColor = 'b'
		self.lineWidth  = 1
		self.markerType  = ''
		self.markerColor = 'r'
		self.markerSize = 0
		self.drawSampleTrace()

	def setLineWidth(self,event):
		self.lineWidth = int(event.GetEventObject().GetValue())
		self.drawSampleTrace()

	def setMarkerWidth(self,event):
		self.markerSize = int(event.GetEventObject().GetValue())
		self.drawSampleTrace()
	
	def setTraceStyle(self,event):
		x =  event.GetEventObject().GetValue()
		self.lineStyle = self.linestyles.get(x,'-')
		self.drawSampleTrace()

	def setMarkerStyle(self,event):
		x=  event.GetEventObject().GetValue()
		self.markerType = self.markerstyles.get(x,'')
		self.drawSampleTrace()

	def setTraceColor(self,event):
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			data = dlg.GetColourData()
			self.button_trace_color.SetBackgroundColour(data.GetColour())
			xlist = data.GetColour()
			self.lineColor = "#%02X%02X%02X" % (xlist.Red(),xlist.Green(),xlist.Blue())
		dlg.Destroy()
		self.drawSampleTrace()
			
	def setMarkerColor(self,event):
		dlg = wx.ColourDialog(None)
		if dlg.ShowModal() == wx.ID_OK:
			data = dlg.GetColourData()
			self.button_marker_color.SetBackgroundColour(data.GetColour())
			xlist = data.GetColour()
			self.markerColor = "#%02X%02X%02X" % (xlist.Red(),xlist.Green(),xlist.Blue())
		dlg.Destroy()
		self.drawSampleTrace()

	def drawSampleTrace(self,event=None):
		#print self.lineColor 
		#print "Line style = " , self.lineStyle 
		#print self.lineWidth 
		#print "Marker Type = ", self.markerType 
		#print self.markerColor 
		#print self.markerSize
		
		#self.text_ctrl_trace.SetValue(
		self.m_myFigure.clf()
		r1 = [0.1, 0.1, 0.8, 0.8]
		self.m_firstAxes = self.m_myFigure.add_axes(r1, label='firstAxes')
		self.m_firstAxes.plot(self.x,self.y, 
					color=self.lineColor, 
					linestyle=self.lineStyle, 
					linewidth=self.lineWidth, 
					marker=self.markerType, 
					markerfacecolor=self.markerColor, 
					markersize=self.markerSize)
		self.m_canvas.Refresh()

# end of class pwxChartParms


if __name__ == "__main__":
	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()
	frame_1 = pwxChartParms(None, -1, "")
	app.SetTopWindow(frame_1)
	frame_1.Show()
	app.MainLoop()
