
#
# This reads in a file ... I have to plot it somehow.
#
from plot import *
from pObject import *
from string import *

class pTableReader(pObject):
    def __init__(self,iLineNumber=0):
        pObject.__init__(self,iLineNumber)
        self.plots = None
        self.graph = []                 # current lcv
        self.allgraphs = []             # all graphs. 
        self.showLines = {}             # names of curves
        self.colors    = ['blue','red','green','magenta','gray','brown']
        self.aAllowedKeywords=['STANDARD_DENSITY_WATER','STANDARD_DENSITY_OIL','STANDARD_DENSITY_GAS',
                'STANDARD_DENSITY_WATER','BUBBLE_POINT_PRESSURE']
    
    def parseLine(self,incoming):
        if (pObject.parseLine(self,incoming,0) < 1): # If comment return. 
            return;
        sline = split(strip(incoming))
        if (len(sline) < 1):
            return;
        keyword = sline[0]
        if keyword in self.aAllowedKeywords:
            return;
        if (keyword == 'TABLE'):
            self.graph = []                     # a new graph. 
            self.allgraphs.append(self.graph)   # add it. 
            return
        if (keyword == 'ENDTABLE'):
            return
        if (keyword == 'GRAPH_UNITS'):
            return
        if (keyword == 'GRAPH_LABELS'):
            self.numLines  = len(sline) - 2
            for i in sline[2:]:
                self.showLines[i] = 1           # The curvename are all shown
            self.titleItems = sline[1:]
            for i in range(self.numLines):
                self.line = []
                self.graph.append(self.line)     # no. of lines for this graph.
            return
        for i in range(self.numLines):
            self.line = self.graph[i]            # get the array for each column. 
            self.line.append((float(sline[0]),float(sline[i+1])))

    # Read the table input file and parse each line.
    def parseFile(self,filename):
        try:
            self.fd = open(filename,'r')
            while 1:
                self.inputline = self.fd.readline()
                if not self.inputline:
                    break
                self.parseLine(self.inputline)
            self.fd.close()

            return 1
        except IOError:
            return 0

    def plotFile(self):
        self.root = Toplevel()
        color     = 0
        #
        pFrame = Frame(self.root)
        xstr = 'Horizontal' + self.titleItems[0] 
        pLabel = Label(pFrame,text=xstr,relief=SUNKEN)
        pLabel.pack(side=LEFT,fill=BOTH,expand=YES)
        for i in range(self.numLines):
            xstr = self.titleItems[i+1]
            self.cmd =lambda s=self, t=xstr: s.toggleLine(t);
            pButton = Button(pFrame,text=xstr,fg=self.colors[color],command=self.cmd)
            pButton.pack(side=LEFT,fill=BOTH,expand=NO)
            color = color + 1
            if (color >= len(self.colors)):
                color = 0
        pFrame.pack(side=TOP,fill=BOTH,expand=NO)
        self.plots = []
        self.drawItems()


    def drawItems(self):
        color = 0
        for plot in self.plots:
            plot.destroy()
        self.plots = []
        for graph in self.allgraphs:   # for all graphs
            objects = []               # collect the data for lines. 
            i = 1         # 0 is horizontal
            color = 0
            for line in graph:         # for each line in this graph.
                name = self.titleItems[i]     # get the name of the curve
                if (self.showLines[name]):      # for this curve.
                    pLine  = GraphLine(line, color=self.colors[color], smooth=0)
                    objects.append(pLine)
                color = color + 1
                if (color >= len(self.colors)):
                    color = 0
                i = i + 1
            if len(objects) > 1:
                graphObject = GraphObjects(objects)   # All the lines in this plot.
                plot  = GraphBase(self.root, 400, 100, relief=SUNKEN, border=2)
                plot.pack(side=TOP, fill=BOTH, expand=YES)
                plot.draw(graphObject, 'automatic', 'automatic')
                self.plots.append(plot);
        
    def toggleLine(self,name):
        if (self.showLines[name]):
            self.showLines[name] = 0
        else:
            self.showLines[name] = 1
        self.drawItems()
