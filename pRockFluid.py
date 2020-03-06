"""
This file handles the input/output for RockFluid objects.  The inputs can be in
XML files (preferred) or in POWERS text format.
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
import string

class pRockFluid(pObject):
	def __init__(self,ilo=None):
		pObject.__init__(self,ilo,'BEGIN_ROCK_AND_FLUID_PROPERTIES','END_ROCK_AND_FLUID_PROPERTIES')
		self.addKeyword('DEAD_CELL_POROSITY','6.17E-6',label='Dead Cell Porosity')
		self.addKeyword('INJECTED_GAS_DENSITY','1',label='Injected Gas Density')
		self.addKeyword('INJECTED_WATER_DENSITY','0.9998',label='Injected Water Density')
		self.addKeyword('MINIMUM_THICKNESS','0.000001',label='Minimum Thickness')
		self.addKeyword('PERMEABILITY_MIN','0.001',label='Minimum Permeability')
		self.addKeyword('POROSITY_MIN','0.06',label='Minimum Porosity')
		self.addKeyword('POROSITY_REFERENCE_PRESSURE','4330.0',label='Porosity Reference Pressure')
		self.addKeyword('ROCK_COMPRESSIBILITY','1.0',label='Rock Compressibility')

		self.addKeyword('FRACTURE_POROSITY_REFERENCE_PRESSURE','1.0',label='Fracture Porosity Reference Pressure')
		self.addKeyword('FRACTURE_ROCK_COMPRESSIBILITY','1.0',label='Fracture Rock Compressibility')
		self.addKeyword('FRACTURE_DEAD_CELL_POROSITY','6.17E-6',label='Fracture Dead Cell Porosity')
		self.addKeyword('FRACTURE_PERMEABILITY_MIN','0.001',label='Fracture Permeability Minimum')
		self.addKeyword('FRACTURE_POROSITY_MIN','0.06',label='Fracture Porosity Minimum')
		self.addKeyword('REPLACEMENT_FRAC_POROSITY','1.0',label='Replacement Fracture Porosity')
		self.addKeyword('THRESHOLD_FRAC_PERM','1.0',label='Threshold Fracture Permeability')
		# self.addKeyword('MODIFY_HIGH_PERM_FRAC_POROSITY','TRUE',('TRUE','FALSE'))

		self.aFractureKeywords = [ 'FRACTURE_POROSITY_REFERENCE_PRESSURE', 'FRACTURE_ROCK_COMPRESSIBILITY',
			'FRACTURE_DEAD_CELL_POROSITY', 'FRACTURE_PERMEABILITY_MIN', 'FRACTURE_POROSITY_MIN',
			'REPLACEMENT_FRAC_POROSITY', 'THRESHOLD_FRAC_PERM']
		self.aAllowedKeywords =  self.aKeywords.keys()

	#################################################################
	# Checks if the keywords inserted are indeed okay. Redundant.
	#################################################################
	def doConsistencyCheck(self):
		pass
	
	#################################################################
	# Parses pLineObjects
	#################################################################
	def parseLine(self,ilo):
		self.aLineContents.append(ilo)         # Add the line here for output back. 
		self.iLineObject = ilo                 # Retain the last line if you have to
		if ilo.mustProcess == 0: return   # Ignore the comments 
		items = ilo.getItems()
		if (len(items)==2):				# If key value line found. 
			keyword = string.upper(items[0])
			self.parseKeyword(keyword,items[1])
		else:
			ilo.markAsErred()
			self.addErrorMessage('Invalid Input', ilo)

	#################################################################
	# Only these keywords are allowed, any other keyword is flagged. 
	#################################################################
	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)

	#################################################################
	# Just so that I can change the name later.
	#################################################################
	def writeXMLfile(self,fd=sys.stdout,name='ROCKFLUID',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def readXMLfile(self,filename,xmldir='.'):
		ch = pRockFluidXMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)


##########################################################################
# The first pass attempts to recreate the aLineContents items in the file.
##########################################################################
class pRockFluidXMLhandler(ContentHandler):
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
		if name == 'PARAMETER':
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name == 'BLOCK_ROCK_FLUID':
			ilo = pLineObject('BLOCK_ROCK_FLUID',self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return
		if name == 'PARAMETER':
			key = attrs.get("NAME",'')
			val = attrs.get("VALUE",'')
			xstr = key + ' ' + val  + '\n'
			ilo = pLineObject(xstr,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return 
		if name in ['COMMENT']:
			self.thisLine = ''
			self.inBody = 1
			return
			
######################################################################################
# Test program to read in XML file from actual model file.
######################################################################################
import sys
if __name__ == '__main__':
	if len(sys.argv) < 1: 
		sys.exit(0)
	fname = sys.argv[1]
	ob = pRockFluid()
	ch = pRockFluidXMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	print ob.getEditableString()
	

	
