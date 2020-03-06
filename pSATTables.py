"""
This object is a collection of an array of SAT table objects.

Author: Kamran Husain  PEASD/SSD

"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
import string 
import os

#################################################################################
# The SAT Tables options.
#################################################################################
class pSATTable(pObject):
	def __init__(self,id='',ilo=None):
		pObject.__init__(self,ilo,id,'END_SATTABLES') # This is the beginning of each block.
		self.sIdString = id
		self.bInOptions   = 0
		self.aAllowedKeywords = []
		self.bInTable = 0
		self.typeOfTable = 'SAT'
		self.tablesArray = []
		self.lastTable    = []
		if (id == 'BEGIN_SATTABLES_GAS_OIL'):
			self.specificParameters = ['KRG_LENGTH_PER_TABLE', 'KROG_LENGTH_PER_TABLE', 'PCOG_LENGTH_PER_TABLE']
		else:
			self.specificParameters = ['KRW_LENGTH_PER_TABLE', 'KROW_LENGTH_PER_TABLE', 'PCOW_LENGTH_PER_TABLE']
		for k in self.specificParameters: 
			self.addKeyword(k,'2000')
		self.addKeyword('TABLE_INTERPOLATION_OPTION','Linear')
		self.addKeyword('LEVERETT_J_PARAMETER', 0.0)
		self.addKeyword('J_TO_PC_MAX_FACTOR', 1.0)
		self.addKeyword('J_TO_PC_MIN_FACTOR', 1.0)
		self.addKeyword('DRAINAGE_FOR_INIT',0)
		self.addKeyword('RELPERM_ENDPT_ADJ_THRESHOLD_SW',0)
		self.addKeyword('TABLE')
		self.addKeyword('GRAPH_LABELS')
		self.addKeyword('GRAPH_UNITS')
		self.addKeyword('ENDTABLE')
		self.addKeyword('BUBBLE_POINT_PRESSURE')
		self.aAllowedKeywords = self.aKeywords.keys()
		#self.aAllowedKeywords.append('INCLUDE_FILE')
		
		# Dont add these keys to the used keys.
		self.aAllowedKeywords.append('BINARY_FILE')
		self.aAllowedKeywords.append('SATTABLES_OPTIONS')
		self.aAllowedKeywords.append('ENDSATTABLES_OPTIONS')

	def resetTables(self):
		self.tablesArray = []
		self.lastTable    = []

	def parseLine(self,ilo):
		"""
		This function reads in a pLineObject. If I am in a table, the 
		line is appended into the table in question otherwise it is 
		processed internally
		"""
		if self.bInTable == 1:
			if ilo.mustProcess == 0: return
			items = ilo.getItems()
			word = string.strip(items[0])
			if word[0] in floatingDigits: 
				self.lastTable.append(ilo)
				return
			# Otherwise drop down.
		self.addContentLine(ilo)
		if ilo.mustProcess == 0: return
		items = ilo.getItems()
		keyword = items[0]
		if (keyword == 'ENDSATTABLES_OPTIONS'):
			self.bInOptions = 0;
			return
		if (keyword == 'SATTABLES_OPTIONS'):
			self.bInOptions = 1;
			return
		if (keyword == 'ENDTABLE'):
			self.bInTable = 0
			self.tablesArray.append(self.lastTable)  # Do this FIRST 
			self.lastTable = []                       # THEN do this
			return
		if (keyword  == 'TABLE'):
			self.lastTable = []
			self.bInTable = 1
			return
		if keyword in ['GRAPH_LABELS', 'GRAPH_UNITS' ]: 
			self.lastTable.append(ilo)
			return
		if (keyword in self.aAllowedKeywords):
			self.addKeyword(keyword,items[1])

#####################################################################################
# Overridden functions here.
#####################################################################################
	def doConsistencyCheck(self):
		self.clearErrors() 
		for ilo in self.aLineContents:
			if items.mustProcess == 0: continue
			items = ilo.getItems()
			if len(items) < 1: continue
			word = items[0]
			if word[0] in floatingDigits: continue
			if (not word in self.aAllowedKeywords):
				errstr = 'SATTABLE %s Bad keyword [%s]' % (self.sIdString,word)
				self.addErrorMessage(errstr,ilo)

	def writeXMLfile(self,fd=sys.stdout,name='BLOCK_SAT_TABLES',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def getXMLpreamble(self,nm,xmldir):
		retlist = []
		for item in self.getIteratedXMLpreamble(nm,xmldir,xslsheet='tables.xsl'): retlist.append(item)
		return "".join(retlist)

	def getXMLcontent(self,nm,xmldir):
		return "".join(self.getXmlTableContent(nm,xmldir,'SATTABLE')) # override

	def readXMLfile(self,filename,xmldir='.'):
		return self.readXmlTableFile(filename,xmldir)

	def getEditableString(self,showHeader=0):
		return self.getTableAsEditableString(showHeader)

if __name__ == '__main__':
	if len(sys.argv) < 1: 
		sys.exit(0)
	fname = sys.argv[1]
	ob = pSATTable()
	ch = pPST_XMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	print ob.getEditableString()
	

