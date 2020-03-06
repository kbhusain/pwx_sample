"""
This handles the main PVTTable object. 

On importing the data, the included files are read into one string. The tables
are then written as independant XML files with references in the TABLEREF records.


Some of the PVT and SAT table handling routines are common and are therefore 
placed in the pObject file.

"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
import string 
import os
import sys

class pPVTTable(pObject):
	def __init__(self,id='',iLineNumber=None):
		pObject.__init__(self,iLineNumber)
		self.sIdString = id
		self.bInOptions   = 0
		self.typeOfTable = 'PVT'
		self.bInTable = 0
		self.tablesArray = []
		self.tableReferences  = []
		self.lastTable    = []

		self.aAllowedKeywords = [] 
		self.addKeyword('TABLE_INTERPOLATION_OPTION','Linear')
		self.addKeyword('TABLE')
		self.addKeyword('GRAPH_LABELS')
		self.addKeyword('GRAPH_UNITS')
		self.addKeyword('ENDTABLE')
		self.addKeyword('BUBBLE_POINT_PRESSURE')

		if (id == 'BEGIN_PVTTABLES_OIL'):
			self.specificParameters = ['FVFO_LENGTH_PER_TABLE', 'CMPO_LENGTH_PER_TABLE', 'VISO_LENGTH_PER_TABLE',
				'CMPVISO_LENGTH_PER_TABLE', 'RSO_LENGTH_PER_TABLE']
			self.addKeyword('STANDARD_DENSITY_OIL')
		elif (id == 'BEGIN_PVTTABLES_WATER'):
			self.specificParameters = [ 'FVFW_LENGTH_PER_TABLE', 'CMPW_LENGTH_PER_TABLE', 'VISW_LENGTH_PER_TABLE',
				'CMPVISW_LENGTH_PER_TABLE', 'RSW_LENGTH_PER_TABLE']
			self.addKeyword('STANDARD_DENSITY_WATER')
		else:
			self.specificParameters = [ 'FVFG_LENGTH_PER_TABLE', 'CMPG_LENGTH_PER_TABLE', 'VISG_LENGTH_PER_TABLE',
				'CMPVISG_LENGTH_PER_TABLE','RSG_LENGTH_PER_TABLE']
			self.addKeyword('STANDARD_DENSITY_GAS')
		for k in self.specificParameters: self.addKeyword(k,'2000')
		self.aAllowedKeywords = self.aKeywords.keys()

		# All tables will be included in here in the entirety...
		#self.aAllowedKeywords.append('INCLUDE_FILE')


		self.aAllowedKeywords.append('TABLE_INTERPOLATION_OPTION')
		# These keys are NOT used even in verbose move. Don't add to usedkeys.
		self.aAllowedKeywords.append('BINARY_FILE')
		self.aAllowedKeywords.append('PVTTABLES_OPTIONS')
		self.aAllowedKeywords.append('ENDPVTTABLES_OPTIONS')

	
	def removeTable(self,ndx):
		try:
			del self.tablesArray[ndx]
		except:
			return -1
		return 0		


	def resetTables(self):
		self.tablesArray = []
		self.lastTable    = []
		
	def parseLine(self,ilo):
		if self.bInTable == 1:
			if ilo.mustProcess == 0: return 
			items = ilo.getItems()
			if len(items) < 1:  return
			word = items[0]
			if word[0] in floatingDigits:  # If it is raw data, keep it in table. 
				self.lastTable.append(ilo) # Keep the raw string, don't interpret.
				return

		self.addContentLine(ilo)
		if ilo.mustProcess == 0: return
		items = ilo.getItems()
		keyword = items[0]
		if (keyword == 'ENDPVTTABLES_OPTIONS'):
			self.bInOptions = 0;
			return
		if (keyword  == 'PVTTABLES_OPTIONS'):
			self.bInOptions = 1;
			return
		if (keyword == 'ENDTABLE'):
			self.bInTable = 0
			self.tablesArray.append(self.lastTable)
			self.lastTable = []
			return
		if (keyword == 'TABLE'):
			self.lastTable = []
			self.bInTable = 1
			return
		if keyword in ['GRAPH_LABELS', 'GRAPH_UNITS', 'BUBBLE_POINT_PRESSURE' ,'STANDARD_DENSITY_OIL', 
				'STANDARD_DENSITY_WATER', 'STANDARD_DENSITY_GAS' ]: 
			self.lastTable.append(ilo); return
		if (len(items) == 2):
			self.addKeyword(keyword,items[1]);
		else:
			xstr = '[%s] Bad line ignored\n' % (self.sIdString)
			self.addErrorMessage(xstr,ilo)

	def doConsistencyCheck(self):
		self.clearErrors() 
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0: continue
			items = ilo.getItems()
			if len(items) < 1: continue
			word = items[0]
			if word[0] in floatingDigits: continue
			if (not word in self.aAllowedKeywords):
				self.str = 'PVTTABLE %s Bad keyword [%s]\n' % (self.sIdString,word)
				self.addErrorMessage(self.str)

	def writeXMLfile(self,fd=sys.stdout,name='BLOCK_PVT_TABLES',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 
		
	def getXMLpreamble(self,nm,xmldir):
		retlist = []
		for item in self.getIteratedXMLpreamble(nm,xmldir,xslsheet='tables.xsl'): retlist.append(item)
		return "".join(retlist)

	def getXMLcontent(self,nm,xmldir):
		return "".join(self.getXmlTableContent(nm,xmldir,'PVTTABLE')) # override

	def readXMLfile(self,filename,xmldir='.'):
		return self.readXmlTableFile(filename,xmldir)

	def getEditableString(self,showHeader=0):
		return self.getTableAsEditableString(showHeader)


		

######################################################################################
# Test program to read in XML file from actual model file.
######################################################################################

if __name__ == '__main__':
	if len(sys.argv) < 1: 
		sys.exit(0)
	fname = sys.argv[1]
	ob = pPVTTable()
	ch = pPST_XMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	#print ob.getEditableString()
	print "No. of table = ", len(ob.tablesArray)

	for tbl in ob.tablesArray:
		print tbl
		
	

