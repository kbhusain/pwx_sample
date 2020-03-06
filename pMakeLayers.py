#!/work0/kamran/Python-2.2.2/python

################################################################################
# pMakeLayers.py
# This is a sample program to create a 3D array.
################################################################################

from Tkinter import *        # The Tk package
import Pmw                   # The Python MegaWidget package
import math                  # import the sin-function
import sys
from string import split
from Numeric import *

################################################################################
#
################################################################################
class gPlaneFrame(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.g = Pmw.Blt.Graph(master)                     # make a new graph area
        self.vector_x = Pmw.Blt.Vector()   
        self.vector_y = Pmw.Blt.Vector()   
        self.vector_z = Pmw.Blt.Vector()   
        self.g.pack(expand=1, fill='both')
        self.g.line_create('TestMe',                 # and create the graph
              xdata=self.vector_x,           # with x data,
              ydata=self.vector_y,           # and  y data
              color='red',              # and a color
              dashes=0,                 # and no dashed line
              linewidth=0,              # and 2 pixels wide
              symbol='square')           # ...and no disks
        self.g.configure(title='Layer view')          # enter a title

    def grid_toggle(self):
        self.g.grid_toggle()

    def setAxes(self,maxx,maxy):
        self.g.xaxis_configure(min=0,max=maxx)
        self.g.yaxis_configure(min=0,max=maxy)

    def assignVectors(self,v_x,v_y):
        self.vector_x = v_x
        self.vector_y = v_y
        self.g.element_configure("TestMe",xdata=self.vector_x,ydata=self.vector_y)
        
################################################################################
#
################################################################################
class gButtonFrame(Frame):
    def __init__(self,master,gui,thegrid):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.buttons = Pmw.ButtonBox(master, labelpos='n', label_text='Options')
        self.gui = gui
        self.grid = thegrid
        self.buttons.pack(fill='both', expand=1, padx=10, pady=10)
        self.buttons.add('Grid',       command=self.gui.grid_toggle)
        self.buttons.add('Symbols',    command=self.showPlane)
        #self.buttons.add('Smooth',     command=smooth)     
        #self.buttons.add('Animate',    command=animate)
        self.buttons.add('Quit',       command=master.quit)
        self.k = 0

    def showPlane(self):
        #################################################################
        # Get the plane vectors for the current value of k
        # assign them to the gui
        #################################################################
        v_x, v_y = self.grid.getPlaneVectors(self.k)
        self.gui.setAxes(self.grid.nx,self.grid.ny)
        self.gui.assignVectors(v_x,v_y)

################################################################################
# This reads an input file and creates a 3D array of 0s with specific points 
# specified with value at x,y,z with a value of V
################################################################################
class internalGrid:
    def __init__(self,filename):
        self.nx = 100
        self.ny = 100
        self.nz = 10
        self.points  = []
        try:
            self.fd = open(filename,'r')         # Open the file to read. 
            inputline= self.fd.readline()        # Get the dimensions 
            if not inputline:
                print "Cannot read dimensions" 
                sys.exit(0)
            (self.nx,self.ny,self.nz) = map(int,split(inputline))    # Get the dimensions into tuple 
            while 1:
                inputline= self.fd.readline()
                if not inputline:      break
                self.processLine(inputline)
            self.fd.close()
        except IOError:
            print "Cannot open file", filename 
        print self.points
        a = (self.nx,self.ny,self.nz)
        self.marray = zeros(a)
        self.populate3D()

    def processLine(self,inputLine):
        items  =  split(inputLine)
        if (len(items) < 1): return
        if (items[0] == '#'): return
        x = int(items[0])
        y = int(items[1])
        z = int(items[2])
        v = int(items[3])
        if (x >= 0) and (x < self.nx) and (y >= 0) and (y < self.ny) and (z >= 0) and (z < self.nz):
            self.points.append((x,y,z,v))
        else:
            print "Rejecting this line as out of bounds:",inputLine

    def populate3D(self):
        for (x,y,z,v) in self.points:
            self.marray[x][y][z] = v
            # At this point you can populate the array's coordinate around the point....

    def getPlaneVectors(self,z):
        v_x = Pmw.Blt.Vector()
        v_y = Pmw.Blt.Vector()
        for x in range(self.nx):
            for y in range(self.ny):
                v = self.marray[x][y][z]
                if (v <> 0):
                    v_x.append(x)
                    v_y.append(y)
        return v_x,v_y

################################################################################
# Generate the data into an array.
################################################################################

if __name__ == '__main__':
    master = Tk()                # build Tk-environment
    filename = sys.argv[1] 
    grid = internalGrid(filename)
    #    applyGrid(filename,gFrame)
    f1 = Frame(master)
    f1.pack(expand=YES,fill=BOTH,side=TOP)
    f2 = Frame(master)
    f2.pack(expand=YES,fill=BOTH,side=TOP)
    gFrame = gPlaneFrame(f1)     # Create the plane frame
    bFrame = gButtonFrame(f2,gFrame,grid)

    master.mainloop()            # ...and wait for input

