"""
#
# The handler to create trees from the XML 
#
"""
from xml.sax import make_parser, ContentHandler

import sys

class cDateNode:
	def __init__(self,dt=''):
		self.tag = "DATE"
		self.ndx = dt

class cWellsNode:
	def __init__(self,dt=''):
		self.tag = "WELLS"
		self.ndx = dt
		self.perfs = []

class cPerfNode:
	def __init__(self,id=''):
		self.tag = "PERF"
		self.ndx = id
		self.attributes = {}

	def setAttr(self,attr,value):
		self.attributes[attr] = value

	def getAttr(self,attr):
		if self.attributes.has_key(attr): 
			return self.attributes[attr]
		return None

class PerfsHandler(ContentHandler):
	def __init__(self):
		self.nid = 0
		self.theTree = [] 
		self.akeys = {}
		self.lastDate = ''
		self.lastWell = ''
		self.lastPerf = ''
		self.ST_IN_IDLE = 0
		self.ST_IN_PERF = 2
		self.state = self.ST_IN_PERF
		self.contents = '' 
		self.getContents = 1
		self.allowedAttr = ["WNAME","I","J","K","K_TOP","K_BOTTOM","GRID_NAME", \
			"Rf","Skin","CD","LPI","WNDF"]

	# Start of element. 
	def startElement(self,name,attrs):
		if name == "DATE": 
			ids = attrs.get('NID')
			self.lastDate = cDateNode(ids)
			self.akeys[ids] = self.lastDate 
			self.theTree.append(self.lastDate)
			return
		if name == "WELLS": 
			ids =	attrs.get('NID')
			self.lastWell = cWellsNode(ids)
			self.akeys[ids] = self.lastWell 
			self.theTree.append(self.lastWell)
			return
		if name == "PERF": 
			ids = attrs.get('NID')
			self.lastPerf = cPerfNode(ids)
			self.akeys[ids] = self.lastPerf
			self.state = self.ST_IN_PERF
			self.contents = ''
			self.lastWell.perfs.append(self.lastPerf)
			return 
		if self.state == self.ST_IN_PERF and name in self.allowedAttr:
			self.contents = ''
			self.getContents = 1
			return
			
	def characters(self,ch):
		if self.ST_IN_PERF and self.getContents: self.contents += ch

	def endElement(self,name):
		if name == "PERF": self.state = self.ST_IN_IDLE
		if self.state == self.ST_IN_PERF and name in self.allowedAttr:
			self.lastPerf.setAttr(name,self.contents)
			self.contents = ''
			self.getContents = 0


	def printIt(self,xn=1):
		ik = 0
		for bb in self.theTree:
			if bb.tag == 'WELLS':
				print bb.ndx
				for pe in bb.perfs:
					print pe.ndx
					for k in pe.attributes.keys():
						print k,pe.attributes[k]
				ik += 1
			if ik > xn:  break;

if __name__ == '__main__':
	chx = PerfsHandler()
	sxp = make_parser()
	sxp.setContentHandler(chx)
	sxp.parse(sys.stdin)
	chx.printIt(10)
