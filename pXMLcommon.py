"""

Common routines for handling XML related input/output for the
following modules: 

pPVTTables.py
pSATTables.py

Routines starting with g_ are meant to be global with the first
parameter that of the incoming object.

"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import string 
import os

####################################################################################
#
####################################################################################
class pPST_tableHandler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name in  ['GRAPH_LABELS_LINE','GRAPH_UNITS_LINE','LINE']:
			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name in ['COMMENT']:
			self.thisLine = ''
			self.inBody = 1
			return
		if name in  ['GRAPH_LABELS_LINE','GRAPH_UNITS_LINE','LINE']:
			self.thisLine = ''
			self.inBody = 1
			return

####################################################################################################
# The handler for the xml input ... Please don't try to make this into one object.
####################################################################################################
class pPST_XMLhandler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name == 'COMMENT':
			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			self.thisLine = ''
			self.inBody = 0
			return 
		if name == 'TABLES': 
			self.thisLine = ''
			self.inBody = 0
			#
			# Now reconstruct the tables in the tablesArray array with the files 
			# in the tableReferences array.
			#
			self.thisLine = ''
			self.inBody = 0
			return 
		if name == 'PARAMETER':
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name in ['COMMENT']:
			self.thisLine = ''
			self.inBody = 1
			return
		if name == 'TABLEREF':
			fname = attrs.get('file','')
			self.obj.tableReferences.append(fname)

			ilo = pLineObject('TABLE',self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			ch = pPST_tableHandler()
			ch.setObj(self.obj,fname)
			qx = make_parser()
			qx.setContentHandler(ch)
			qx.parse(fname)

			ilo = pLineObject('ENDTABLE',self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return
		if name == 'TABLES':
			self.obj.tablesArray = []
			self.obj.tableReferences = []
			return
		if name == 'PARAMETER':
			key = attrs.get("NAME",'')
			val = attrs.get("VALUE",'')
			xstr = key + ' ' + val  + '\n'
			if len(val) == 0: return 
			ilo = pLineObject(xstr,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return 

