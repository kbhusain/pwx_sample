#!/work0/kamran/vtkbins/bin/vtkpython
#!/peasd/ssd/husainkb/eaqkbh/vtkbins/bin/vtkpython

##############################################################
#
##############################################################

import math				  # import the sin-function
import string
from os import path
from struct import *
from string import strip , find, rfind, join
from array import array
from tkColorChooser import *


##############################################################
#
##############################################################
class pMathUtils:
	def __init__(self):
		self.m_minv = 0
		self.m_maxv = 0
		self.m_minHit = 0
		self.m_maxHit = 0

	def performHistogram(self,datapts,binCount,accummulate=0):
		""" Returns a tuple of the number of bins. If accumulate
		is set to 1, then it returns a normalized accumulation."""
		bins = array('f')
		for i in range(binCount): bins.append(0); 
		self.m_minv = datapts[0]
		self.m_maxv = datapts[0]
		for v in datapts:
			if v < self.m_minv: self.m_minv = v
			if v > self.m_maxv: self.m_maxv = v
		vrange = self.m_maxv - self.m_minv
		if vrange == 0: return []   # No range == no histogram
		for v in datapts:
   	   		ti = int(((v - self.m_minv) * binCount)/(vrange))
	   		if (ti < 0): ti = 0 
	   		if (ti >= binCount): ti = binCount - 1  
			bins[ti] = bins[ti] + 1
		
		######################################################
		### We have to show the minimum and maximum values ###
		######################################################
		self.m_minHit = bins[0]
		self.m_maxHit = bins[0]
		for v in bins:
			if v < self.m_minHit: self.m_minHit = v
			if v > self.m_maxHit: self.m_maxHit = v
		if accummulate:
			sum = 0
			vlen = len(bins)
			max = len(datapts)
			for i in range(vlen):
				sum = sum + bins[i]
				bins[i] = sum / max
		return tuple(bins)




class regression:
	def __init__(self): 
		self.b = 0
		self.a = 0

	def getSlope(self):
		return self.b

	def getIntercept(self):
		return self.a

	def doRegression(self,datax,datay):
		sumx = 0 
		sumy =  0
		sumxx = 0
		sumyy = 0
		sumxy = 0
		for i in range(len(datax)):
			x, y = data[i]
			sumx = sumx + x
			sumy = sumy + y
			sumxx = sumxx + (x * x)
			sumyy = sumyy + (y * y)
			sumxy = sumxy + (y * x)
		if (n > 0):
			Sxx = sumxx - (sumx * sumx)/n
			yy  = sumyy - (sumy * sumy)/n
			Sxy = sumxy - (sumx * sumy)/n
			self.b = Sxy/Sxx                    # Slope 
			self.a = (sumy - self.b * sumx)/n   # Intercept
			return (self.b,self.a)






#####################################################################
def oldtryOptions(m):
	trytocreate = 0
	readable = 0
	try:
		fd = open('optionDB','r')
		readable = 1	
	except:
		readable = 0
	if readable:
		fd.close()
		m.option_readfile('optionDB')
		return
	try:
		fd = open('optionDB','w')
	except:
		return
	fd.write('*font:	Courier 9\n')
	fd.close()
	m.option_readfile('optionDB')


def tryOptions(root):
	try:
		root.option_readfile("/red/ssd/appl/khusain/optionDB")
	except:
		print "Using defaults"
		root.option_add("*font",'Times 10')
		root.option_add("*background",'gray')
		root.option_add("*foreground",'black')
		root.option_add("*Label*foreground",'#1F5977')
		root.option_add("*Label*background",'gray')
		root.option_add("*Frame*background",'gray')
		root.option_add("*Button*background",'#0D18BA')
		#root.option_add("*Button*foreground",'black')
		root.option_add("*Button.borderwidth",'2')

	try:
		tt = os.getenv('HOME') + "/powersdata/optionDB"
		root.option_readfile(tt)
		print "Using user optionDB" ,tt
	except:
		pass





def confirmXSLfile(filename):
	try:
		fd = open(filename,'r')
		readable = 1	
	except:
		readable = 0
	if readable:
		fd.close()
		return
	try:
		fd = open(filename,'w')
	except:
		return
	xstr = """
	<?xml version="1.0"?>\n
	<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n

	<xsl:template match="/">\n
			<H1>Plots</H1>\n
			<xsl:apply-templates select="ALLPLOTS/PLOT"/>\n
    <HR/><B>Equation File:<xsl:value-of select="ALLPLOTS/EQUATIONFILENAME"/></B><HR/>\n
	</xsl:template>\n
	

	<xsl:template match="PLOT">\n
	<TABLE BORDER="1">\n
	<TR><TD>Plot Name</TD><TD><xsl:value-of select="NAME"/></TD></TR>\n
	<TR><TD>FileName</TD><TD><xsl:value-of select="FILENAME"/></TD></TR>\n
	<TR><TD>X Axis</TD><TD><xsl:value-of select="XNAME"/></TD></TR>\n
	<TR><TD>Y Axis</TD><TD><xsl:value-of select="YNAME"/></TD></TR>\n
	<TR><TD>Symbol</TD><TD><xsl:value-of select="SYMBOL"/></TD></TR>\n
	<TR><TD>Color</TD><TD><xsl:value-of select="COLOR"/></TD></TR>\n
	<TR><TD>Action</TD><TD><xsl:value-of select="ACTION"/></TD></TR>\n
	<TR><TD>Step Value</TD><TD><xsl:value-of select="STEPVALUE"/></TD></TR>\n
	<TR><TD>Pixel Width</TD><TD><xsl:value-of select="PIXELWIDTH"/></TD></TR>\n
	<TR><TD>Line Width</TD><TD><xsl:value-of select="LINEWIDTH"/></TD></TR>\n
	<TR><TD>Use Subvolume</TD><TD><xsl:value-of select="USESUBVOLUME"/></TD></TR>\n
	<TR><TD>X0</TD><TD><xsl:value-of select="X0"/></TD></TR>\n
	<TR><TD>Y0</TD><TD><xsl:value-of select="X1"/></TD></TR>\n
	<TR><TD>Y0</TD><TD><xsl:value-of select="Y0"/></TD></TR>\n
	<TR><TD>Y1</TD><TD><xsl:value-of select="Y1"/></TD></TR>\n
	<TR><TD>Z0</TD><TD><xsl:value-of select="Z0"/></TD></TR>\n
	<TR><TD>Z1</TD><TD><xsl:value-of select="Z1"/></TD></TR>\n
	</TABLE>\n
	</xsl:template>\n
	</xsl:stylesheet>\n
	"""
	fd.write(xstr)
	fd.close()





def ccw(p1x,p1y,p2x,p2y,p3x,p3y):
	dx1 = p2x - p1x; dy1 = p2y - p1y
	dx2 = p3x - p2x; dy2 = p3y - p2y
	if (dy1*dx2 < dy2*dx1): return 1
	return 0

def intersect(l1p1x,l1p1y,l1p2x,l1p2y,l2p1x,l2p1y,l2p2x,l2p2y):
	a = (ccw(l1p1x,l1p1y,l1p2x,l1p2y,l2p1x,l2p1y) <> ccw(l1p1x,l1p1y,l1p2x,l1p2y,l2p2x,l2p2y))
	b = (ccw(l2p1x,l2p1y,l2p2x,l2p2y,l1p1x,l1p1y) <> ccw(l2p1x,l2p1y,l2p2x,l2p2y,l1p2x,l1p2y))
	if a and b: return 0
	return 1 


def inside(px,py, polygon):
	"""
	polygon is an array of (x,y) tuples 
	"""
	ltp1x=0; ltp1y=0; ltp2x=px; ltp2y=py
	count = 0
	for i in range(len(polygon)-1):
		x1,y1=polygon[i]	
		x2,y2=polygon[i+1]	
		if intersect(ltp1x,ltp1y,ltp2x,ltp2y,x1,y1,x2,y2): count = count + 1
	return (count % 2)    # Returns 1 if inside, 0 if outside


def findInArray(data,v):
	xlen = len(data)
	if v < data[0]: return -1 
	for k in range(xlen):
		if v < data[k]: return k
	return xlen



def askcolorstring(titlestr='Chooseit'):
	ret = askcolor(title=titlestr)
	color = ret[0]
	if color == None: return None
	scolor = '#%02X%02X%02X' % (int(color[0]), int(color[1]), int(color[2]))
	return scolor
		

if __name__ == '__main__':
	a = []
	for i in range(10):
		a.append(float(i)/10)
	v = 4.01
	k = findInArray(a,v)
	print k


