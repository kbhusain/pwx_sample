#
#
# @author: Kamran Husain, Saudi Aramco, kamran.husain@aramco.com.sa
#
#####################################################
# Standard files 
#####################################################
import fileinput, sys
import xml.sax 
from xml.sax.handler import ContentHandler
from string import strip, find, split, replace, join
#####################################################
# Simulator specific files. 
# Each object is defined in its own file. Must reside
# in PATH or PYTHON_PATH or in frozen file as compiled
# modules. 
#
# Jun 22,2002 - Added pMigration 
# Dec 18,2002 - Added pCompositional 
#####################################################
from pObject import *
from pModel import *
from pRockFluid import *
from pComparator import *
from pEquilibration import *
from pFlowTable import *
from pSATTables import *
from pPVTTables import *
from pGridData  import *
from pModify	import *
from pRegion	import *
from pMigration import *
from pLGRitem   import *
from pSector   import *
from pCompositional import *
from time import *
import os
from string import split,find
from pPBFutils  import *

######################################################
# Constants for parsing blocks.
#####################################################

IN_NO_BLOCK = 0
IN_SIMULATOR_PARAMETERS = 1
IN_ROCK_FLUID_PROPERTIES = 2
IN_SIMULATOR_OPTIONS	= 3
IN_THE_EQUILIBRIUMPARAMETERS = 4
IN_FLOW_TABLE_OPTIONS	= 5
IN_SATTABLE_OPTIONS   = 6
IN_PVTTABLE_OPTIONS   = 7
IN_GRID_DATA		 = 8 
IN_MIGRATION_DATA	= 9
IN_LGR_DATA			= 10
IN_COMPARATOR			= 11
IN_SECTOR_EXTRACT         = 12
IN_COMPOSITION           = 13

#####################################################
# Rules to catch 
"""
	1. If in a BEGIN block, then you should not get another BEGIN block. DONE
	2. You should not get an END block if you don't have a BEGIN  DONE
	3. Start with an empty file. Must be done in the modelParser object.
"""
#####################################################


##########################################################################
# The first pass attempts to recreate the aLineContents items in the file.
##########################################################################
class pModelFileXMLhandler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name in ['REFERENCE','COMMENT']:
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		self.inBody = 0
		if name in ['REFERENCE','COMMENT']:
			attrname = attrs.get('name','')
			thisfile = attrs.get('file','')
			print "I will now attempt to read ", thisfile, ' into ', attrname
				#
				# 
				#
			blk = self.obj.m_internalBlocks[attrname]
			print 'Type of block', attrname, " is ", blk
			blk.readXMLfile(thisfile)  # Use the fullNme
			self.thisLine = ''
			self.inBody = 1
			return
			

#####################################################
# This is the specific parser for the model file.
#####################################################
class modelFileParser(cParserObject):
	def __init__(self):
		cParserObject.__init__(self)
		self.verbose = 0
		self.inBlock = 0
		self.blockStack = []


		self.blockType = IN_NO_BLOCK
		self.m_internalBlocks = {}  
		self.m_internalBlockNames = [ 'SIMULATOR', 'ROCKFLUID', 'EQUILIBRIUM',
			'FLOW', 'LGRPARMS', 'GRID', 'MIGRATION', 'COMPARATOR', 
			'SAT-GAS-OIL', 'SAT-OIL-WATER', 'PVT-OIL', 'PVT-GAS', 'PVT-WATER']
		self.lastSATTable   = None
		self.lastPVTTable   = None
		for wn in self.m_internalBlockNames: self.m_internalBlocks[wn] = None

		self.endOfBlock = 'NOTHING'
		self.iLineObject	= None;
		self.iLineNumber	= 0;
		self.blockDelimiter = {}
		self.comments = []
		self.sErrorStrings = [] 
		self.allDatesArray = { }   # Used to track information for time related information.
		self.allWellsArray = { }   # Master list of all the wells.
		self.allDatesPerWell = {}  # Well name index to list of dates where well is modified.

		self.recurrentFileObject = None
	
		self.mapOfTypes = {}
		self.mapOfTypes['BEGIN_SIMULATOR_PARAMETERS'] =  (pModel,'END_SIMULATOR_PARAMETERS')
		self.mapOfTypes['BEGIN_ROCK_AND_FLUID_PROPERTIES'] =  (pRockFluid,'END_ROCK_AND_FLUID_PROPERTIES')
		self.mapOfTypes['BEGIN_GRID_DATA'] =  (pGridData,'END_GRID_DATA')
		self.mapOfTypes['BEGIN_FLOW_TABLE_OPTIONS'] =  (pFlowTable,'END_FLOW_TABLE_OPTIONS')
		self.mapOfTypes['BEGIN_LGR_DATA'] =  (pLGRdata,'END_LGR_DATA')
		self.mapOfTypes['BEGIN_MIGRATION_LINE_OPTION'] = (pMigrationData,'END_MIGRATION_LINE_OPTION')
		self.mapOfTypes['BEGIN_EQUILIBRIUM_PARAMETERS'] = (pEquilibration,'END_EQUILIBRIUM_PARAMETERS')
		self.mapOfTypes['BEGIN_PVTTABLES_OIL'] = (pPVTTable,'END_PVTTABLES_OIL')
		self.mapOfTypes['BEGIN_PVTTABLES_GAS'] = (pPVTTable,'END_PVTTABLES_GAS')
		self.mapOfTypes['BEGIN_PVTTABLES_WATER'] = (pPVTTable,'END_PVTTABLES_WATER')
		self.mapOfTypes['BEGIN_SATTABLES_GAS_OIL'] = (pSATTable,'END_SATTABLES')
		self.mapOfTypes['BEGIN_SATTABLES_OIL_WATER'] = (pSATTable,'END_SATTABLES')
		self.mapOfTypes['BEGIN_COMPARATOR_PARAMETERS'] = (pComparator,'END_COMPARATOR_PARAMETERS')
		self.mapOfTypes['BEGIN_SECTOR_EXTRACT_OPTION'] = (pSectorExtract,'END_SECTOR_EXTRACT_OPTION')
		self.mapOfTypes['BEGIN_COMPOSITIONAL_PARAMETERS'] = (pCompositional,'END_COMPOSITIONAL_PARAMETERS')

		self.validBeginBlocks=self.mapOfTypes.keys()

	########################################################################
	def addErrorString(self,xstr,ilo=None):
		if ilo <> None: 
			estr = xstr + "\nFile %s, Line %d - [%s]\n" % (ilo.getFileName(), ilo.getLineNumber(), strip(ilo.getRawLine())) 
			self.sErrorStrings.append(estr)
		else:
			self.sErrorStrings.append(xstr+'\n')
	
	########################################################################
	def getListOfErrors(self):
		return self.sErrorStrings

	def getErrorMessages(self):
		return "".join(self.sErrorStrings)

	def parseLine(self,ilo):
		"""
		Each input line is processed through here.  This is in the main model file.
		I have to preserve the comments in the individual block
		"""
		self.iLineObject = ilo                     # Point to the line object in question 
		self.sline = ilo.getCookedLine()           # Get the line item
		if len(self.sline) < 1: 
			self.items = []
		else:
			self.items = split(self.sline)  # Single keywords are processed here.
		if (len(self.items) == 1):
			self.bname = self.items[0]  # Could this be a block name?
			self.bname = self.bname.upper() 
			#
			# Something to compensate for the silliness in input.
			#
			if (find(self.bname,'BEGIN_EQUILIBRATION_PARAMETERS',0) > -1):
				self.items[0] = replace(self.items[0],'BEGIN_EQUILIBRATION_PARAMETERS','BEGIN_EQUILIBRIUM_PARAMETERS')
				self.estr = "Changing BEGIN_EQUILIBRATION PARAMETERS to BEGIN_EQUILIBRIUM_PARAMETERS !"
				self.addErrorString(self.estr,ilo);
				self.bname = self.items[0]  # Could this be a block name?
			if (find(self.bname,'END_EQUILIBRATION_PARAMETERS',0) > -1):
				self.items[0] = replace(self.items[0],'END_EQUILIBRATION_PARAMETERS','END_EQUILIBRIUM_PARAMETERS')
				self.estr = "Changing END_EQUILIBRATION PARAMETERS to END_EQUILIBRIUM_PARAMETERS !"
				self.addErrorString(self.estr,ilo);
				self.bname = self.items[0]  # Could this be a block name?
			if self.bname in ['END_SATTABLES_GAS_OIL', 'END_SATTABLES_OIL_WATER']:
				self.items[0] = replace(self.items[0],self.bname,'END_SATTABLES')
				self.estr = "Changing %s to END_SATTABLES !\n" % (self.bname)
				self.addErrorString(self.estr,ilo);
				self.bname = 'END_SATTABLES'
			if (self.bname in self.validBeginBlocks):  
				self.checkBlockType() # This sets the end of the current upper level block
				return
			if (self.bname == self.endOfBlock):   
				self.inBlock = 0   # Valid termination
				self.comments = [] # Blow away the comments.
				self.blockType = IN_NO_BLOCK
				self.endOfBlock = 'NOTHING'
				if len(self.blockStack) > 0: 
					self.blockName,self.blockType,self.endOfBlock  = self.blockStack.pop()
					print "POPPING ", self.blockName, self.blockType, self.endOfBlock
				return
		##################################################################
		# Lines within specific blocks are parsed here. Pass the blank line.
		# Pass the line to its own handler. We can add block specific items 
		# there. Don't make this into a smaller function. I separated it 
		# deliberately. Kamran 
		##################################################################
		if (self.blockType == IN_SIMULATOR_PARAMETERS): 
			self.m_internalBlocks['SIMULATOR'].parseLine(ilo)
		if (self.blockType == IN_ROCK_FLUID_PROPERTIES): self.processRockFluidLines(ilo)
		if (self.blockType == IN_COMPARATOR): self.processComparatorLines(ilo)
		if (self.blockType == IN_SECTOR_EXTRACT): self.processSectorExtract(ilo)
		if (self.blockType == IN_COMPOSITION): self.processCompositional(ilo)
		if (self.blockType == IN_THE_EQUILIBRIUMPARAMETERS): self.processEquilibrationLines(ilo)
		if (self.blockType == IN_FLOW_TABLE_OPTIONS): self.processFlowTableLines(ilo)
		if (self.blockType == IN_SATTABLE_OPTIONS): self.lastSATTable.parseLine(ilo)
		if (self.blockType == IN_PVTTABLE_OPTIONS): self.lastPVTTable.parseLine(ilo)
		if (self.blockType == IN_GRID_DATA): self.m_internalBlocks['GRID'].parseLine(ilo)
		if (self.blockType == IN_MIGRATION_DATA): self.m_internalBlocks['MIGRATION'].parseLine(ilo)
		if (self.blockType == IN_LGR_DATA): self.processLGRLines(ilo)
		
		if (self.blockType == IN_NO_BLOCK) and (len(self.items) > 1) and ilo.mustProcess == 1:
			self.str = "Model Parser. Assignments defined outside block!" 
			self.addErrorString(self.str,ilo);
			
	########################################################################
	# This confirms that one block exists per item.
	# NOTE: the member self.bname has been set before this call.
	# NOTE: Do NOT do a compare == with bname since comments exist in line
	########################################################################
	def checkBlockType(self):
		if self.inBlock == 1:
			self.estr = "Already in a block, missing END statement [check if you need a %s here]\n" % self.endOfBlock
			self.addErrorString(self.estr,self.iLineObject);

		if (find(self.bname,'BEGIN_SIMULATOR_PARAMETERS',0) > -1):
			self.m_internalBlocks['SIMULATOR'] = self.processBlockType(self.bname,IN_SIMULATOR_PARAMETERS, 'SIMULATOR')
			return 
		if (find(self.bname,'BEGIN_LGR_DATA',0) > -1):
			self.m_internalBlocks['LGRPARMS'] = self.processBlockType(self.bname,IN_LGR_DATA,'LGRPARMS')
			return 
		if self.bname =='BEGIN_COMPARATOR_PARAMETERS':
			self.m_internalBlocks['COMPARATOR'] = self.processBlockType(self.bname,IN_COMPARATOR,'COMPARATOR')
			return
		if self.bname =='BEGIN_SECTOR_EXTRACT_OPTION':
			self.m_internalBlocks['SECTOR_EXTRACT'] = self.processBlockType(self.bname,IN_SECTOR_EXTRACT,'SECTOR_EXTRACT')
			return
		if self.bname =='BEGIN_COMPOSITIONAL_PARAMETERS':
			self.m_internalBlocks['COMPOSITION'] = self.processBlockType(self.bname,IN_COMPOSITION,'COMPOSITION')
			return
		if self.bname =='BEGIN_ROCK_AND_FLUID_PROPERTIES':
			self.m_internalBlocks['ROCKFLUID'] = self.processBlockType(self.bname,IN_ROCK_FLUID_PROPERTIES,'ROCKFLUID')
			return
		if self.bname == 'BEGIN_PVTTABLES_OIL': 
			self.m_internalBlocks['PVT-OIL'] = self.processBlockType(self.bname,IN_PVTTABLE_OPTIONS,'PVT-OIL',1)
			self.lastPVTTable   = self.m_internalBlocks['PVT-OIL'] 
			return
		if self.bname == 'BEGIN_PVTTABLES_GAS':
			self.m_internalBlocks['PVT-GAS'] = self.processBlockType(self.bname,IN_PVTTABLE_OPTIONS,'PVT-GAS',1)
			self.lastPVTTable   = self.m_internalBlocks['PVT-GAS'] 
			return
		if self.bname == 'BEGIN_PVTTABLES_WATER': 
			self.m_internalBlocks['PVT-WATER'] = self.processBlockType(self.bname,IN_PVTTABLE_OPTIONS,'PVT-WATER',1)
			self.lastPVTTable   = self.m_internalBlocks['PVT-WATER'] 
			return
		if self.bname == 'BEGIN_SATTABLES_GAS_OIL': 
			self.lastSATTable = self.processBlockType(self.bname,IN_SATTABLE_OPTIONS,'SAT-GAS-OIL',1)
			self.m_internalBlocks['SAT-GAS-OIL'] = self.lastSATTable
			return
		if self.bname == 'BEGIN_SATTABLES_OIL_WATER':
			self.lastSATTable = self.processBlockType(self.bname,IN_SATTABLE_OPTIONS,'SAT-OIL-WATER',1)
			self.m_internalBlocks['SAT-OIL-WATER'] = self.lastSATTable
			return
		if (find(self.bname,'BEGIN_FLOW_TABLE_OPTIONS',0) > -1):
			self.m_internalBlocks['FLOW'] = self.processBlockType(self.bname,IN_FLOW_TABLE_OPTIONS,'FLOW')
			return
		if (find(self.bname,'BEGIN_EQUILIBRIUM_PARAMETERS',0) > -1):
			self.m_internalBlocks['EQUILIBRIUM'] = \
				self.processBlockType(self.bname,IN_THE_EQUILIBRIUMPARAMETERS,'EQUILIBRIUM')
			return
		if (find(self.bname,'BEGIN_MIGRATION_LINE_OPTION',0) > -1):
			self.m_internalBlocks['MIGRATION'] = self.processBlockType(self.bname,IN_MIGRATION_DATA,'MIGRATION')
			return
		if (find(self.bname,'BEGIN_GRID_DATA',0) > -1):
			self.m_internalBlocks['GRID'] = self.processBlockType(self.bname,IN_GRID_DATA,'GRID')
			return

		self.inBlock = 0
		self.blockType = IN_NO_BLOCK
#
	########################################################################
	# Generate a block type based on map of start of block string
	########################################################################
	def processBlockType(self,name,bType,blockName,sendName=0):
		if self.inBlock == 1:
			self.estr = "Bad nesting. You're missing an END-ing statement [check if you need a %s here]\n" % self.endOfBlock
			self.addErrorString(self.estr,self.iLineObject);
			print "Pushing ... ", self.blockName,self.blockType, self.endOfBlock
			self.blockStack.append((self.blockName,self.blockType,self.endOfBlock))

		self.blockName = name				# Preserve the block name
		caller = self.mapOfTypes[name]		# Get beginning and end string 
		self.blockType = bType				# IN_XXX_DATA type of block
		self.endOfBlock = caller[1]			# Mark the end of string 
		block = self.m_internalBlocks[blockName]  # Check if this already has been caught.
		callee = caller[0] 				              # Otherwise, use the one in the map.
		if sendName == 0:
			block = callee(self.iLineObject);         # If you can use the default delimiter
		else:
			block = callee(name,self.iLineObject);    # Generally for SAT and PVT tables
			block.setDelimiters(name,self.endOfBlock) # If you have send a different delimiter
		block.addComments(self.comments);        # Attach accumulated comments.
		self.comments = []                       # Clear comments for next block
		self.inBlock = 1						 # Mark that you are in a block
		return block
	
	########################################################################
	# 
	########################################################################
	def createEmptyObject(self,filename=None):
		self.filename = filename
		self.iLineObject = pLineObject('')
		self.iLineNumber = self.iLineObject.getLineNumber()
		self.m_internalBlocks['SIMULATOR'] = pModel(self.iLineObject)
		self.m_internalBlocks['ROCKFLUID'] = pRockFluid(self.iLineObject)
		self.m_internalBlocks['COMPARATOR'] = pComparator(self.iLineObject)
		self.m_internalBlocks['SECTOR_EXTRACT'] = pSectorExtract(self.iLineObject)
		self.m_internalBlocks['EQUILIBRIUM'] = pEquilibration(self.iLineObject)
		self.m_internalBlocks['COMPOSITION'] = pCompositional(self.iLineObject)
		self.m_internalBlocks['FLOW'] = pFlowTable(self.iLineObject)
		self.m_internalBlocks['LGRPARMS'] = pLGRdata(self.iLineObject)
		self.m_internalBlocks['GRID']  = pGridData(self.iLineObject)
		self.m_internalBlocks['MIGRATION'] = pMigrationData(self.iLineObject);
		self.m_internalBlocks['SAT-GAS-OIL']  = pSATTable('BEGIN_SATTABLES_GAS_OIL',self.iLineObject)
		self.m_internalBlocks['SAT-OIL-WATER'] = pSATTable('BEGIN_SATTABLES_OIL_WATER',self.iLineObject)
		self.m_internalBlocks['PVT-OIL']  = pPVTTable('BEGIN_PVVTTABLES_OIL',self.iLineObject)		
		self.m_internalBlocks['PVT-GAS']  = pPVTTable('BEGIN_PVVTTABLES_GAS',self.iLineObject)		
		self.m_internalBlocks['PVT-WATER'] = pPVTTable('BEGIN_PVVTTABLES_WATER',self.iLineObject)		
   
	########################################################################
	# 
	########################################################################
	def processRockFluidLines(self,items):
		if (self.m_internalBlocks['ROCKFLUID'] == None):
			self.m_internalBlocks['ROCKFLUID'] = pRockFluid()
		self.m_internalBlocks['ROCKFLUID'].parseLine(items)

	########################################################################
	# 
	########################################################################
	def processComparatorLines(self,items):
		if (self.m_internalBlocks['COMPARATOR'] == None):
			self.m_internalBlocks['COMPARATOR'] = pComparator(None)
		self.m_internalBlocks['COMPARATOR'].parseLine(items)

	########################################################################
	# 
	########################################################################
	def processSectorExtract(self,items):
		if (self.m_internalBlocks['SECTOR_EXTRACT'] == None):
			self.m_internalBlocks['SECTOR_EXTRACT'] = pSectorExtract(None)
		self.m_internalBlocks['SECTOR_EXTRACT'].parseLine(items)

	########################################################################
	# 
	########################################################################
	def processCompositional(self,items):
		if (self.m_internalBlocks['COMPOSITION'] == None):
			self.m_internalBlocks['COMPOSITION'] = pCompositional(None)
		self.m_internalBlocks['COMPOSITION'].parseLine(items)

	########################################################################
	# 
	########################################################################
	def processLGRLines(self,items):
		if (self.m_internalBlocks['LGRPARMS'] == None): 
			self.m_internalBlocks['LGRPARMS'] = pLGRdata()
		self.m_internalBlocks['LGRPARMS'].parseLine(items)


	########################################################################
	# 
	########################################################################
	def processEquilibrationLines(self,items):
		if (self.m_internalBlocks['EQUILIBRIUM'] == None):
			self.m_internalBlocks['EQUILIBRIUM'] = pEquilibration()
		self.m_internalBlocks['EQUILIBRIUM'].parseLine( items )

	########################################################################
	# 
	########################################################################
	def processFlowTableLines(self,items):
		if (self.m_internalBlocks['FLOW'] == None):
			self.m_internalBlocks['FLOW'] = pFlowTable()
		self.m_internalBlocks['FLOW'].parseLine(items)

	########################################################################
	# Writes a simple preamble for the bare bones file
	########################################################################
	def printPreamble(self,fd):
		fd.write("# Model file created from modelParser.py\n"); 
		fd.write("# Author: Kamran Husain\n");
		fd.write("# --------------------- #\n");
		self.localtime = localtime() # placeholder from function.
		fd.write(strftime("#Date: %x on %X\n", self.localtime)); 



	########################################################################
	def writeModelFile(self,filename=None,useFd=None):
		"""
		Writes a bare bones model file that can be sent into POWERS
		TODO: Comments are NOT written out. I may add this later. 
		TODO: Also, blocks that were not in the file are not written out. Change to always write.
		"""
		if useFd == None:
			pathname = os.path.dirname(filename)
			basename = os.path.basename(filename) + ".txt"
			basename = basename.replace(".model",'')
			fd = open(filename,"w")                 # Write the information for the user.
		else:
			fd = useFd

		self.printPreamble(fd)                  # Our internal copyright
		self.makeItemsConsistent()              # Th 


		for name in ['SIMULATOR','ROCKFLUID','LGRPARMS','SECTOR_EXTRACT']: # COMPARATOR is not used
			if (self.m_internalBlocks[name] <> None):        
				self.m_internalBlocks[name].printStructure(fd,1)

		for name in ['EQUILIBRIUM','GRID','MIGRATION','FLOW']: 
			if (self.m_internalBlocks[name] <> None):        
				thisfilename = pathname + os.sep + name + '_' + basename 
				fd.write('INCLUDE_FILE "%s"\n' % thisfilename)
				fdo = open(thisfilename,'w')
				self.m_internalBlocks[name].printStructure(fdo,1)
				fdo.close()
	    #
		# These don't have printStructure functions
		#
		for item in ['SAT-GAS-OIL', 'SAT-OIL-WATER','PVT-OIL', 'PVT-GAS', 'PVT-WATER']:
			tbl = self.m_internalBlocks[item]
			if tbl == None: continue
			thisfilename = pathname + os.sep + item + "_" + basename 
			fd.write('INCLUDE_FILE "%s"\n' % thisfilename)
			tblStr = tbl.getEditableString(1)
			fdo = open(thisfilename,'w')
			fdo.write(tblStr)
			fdo.close()
		fd.close()

	########################################################################
	# Writes a simple preamble for the bare bones file
	########################################################################

	def readXMLFiles(self,modelname,xmldir):
		inputfilename = xmldir + os.sep + modelname + ".model.xml"
		print "I will now read ...", inputfilename 
		self.readOneXmlFile(inputfilename)

	def readOneXmlFile(self,inputfilename):
		self.createEmptyObject()                        # Always create an empty object
		self.sErrorStrings = []                         # 
		self.inputLines = []                            # Will be filled with raw input
		ch = pModelFileXMLhandler()                     #
		ch.setObj(self,inputfilename)
		self.sx = xml.sax.make_parser()
		self.sx.setContentHandler(ch)
		self.sx.parse(inputfilename)

	def writeXMLFiles(self,modelname,xmldir):
		"""
		modelname cannot have extensions, etc. I will add them myself.
		"""
		if xmldir == None: return
		if not os.path.isdir(xmldir):
			try:
				os.mkdir(xmldir)
			except: 
				print "Exception ..."
				return 

		# print self.m_internalBlocks.keys()
		# useThese = ['PVT-WATER', 'SAT-OIL-WATER', 'COMPARATOR', 'SIMULATOR', \
		# 'LGRPARMS', 'FLOW', 'SAT-GAS-OIL', 'GRID', 'MIGRATION', 'PVT-OIL',
		# 'PVT-GAS', 'ROCKFLUID', 'EQUILIBRIUM']
		# use These  'COMPARATOR' ??

		co = pObject()
		retstr = co.getXMLpreamble('MASTER',xmldir,'master.xsl')
		retstr += '<MODULES>\n'
		
		useThese = ['LGRPARMS','GRID', 'SECTOR_EXTRACT', 'PVT-WATER','PVT-GAS','PVT-OIL', 'SAT-GAS-OIL','SAT-OIL-WATER',\
			'SIMULATOR','ROCKFLUID','FLOW', 'MIGRATION', 'EQUILIBRIUM']

		useThese.sort()
		for nm in useThese: 
			fname = xmldir + os.sep + nm.lower() + '.xml'
			print "Creating ...", fname
			fd = open(fname,'w')
			blk = self.m_internalBlocks[nm]
			blk.writeXMLfile(fd,nm,xmldir)
			fd.close()
			retstr += '<REFERENCE name="%s" file="%s" />\n' % (nm,fname)
		retstr += '</MODULES>\n'
		retstr += co.getXMLpostamble('MASTER')

		if modelname[0] <> '/':
			mastername = xmldir + os.sep + modelname +'.model.xml'
		else:
			mname = os.path.basename(modelname)
			mastername = xmldir + os.sep + mname +'.xml'
		fd = open(mastername,'w')
		fd.write(retstr)
		fd.close()


	########################################################################
	# 
	########################################################################
	def makeItemsConsistent(self):
		"""
		This function is used to set the values in the main blocks just prior 
		to a write or right after a GUI update.
		"""

		# Check flow tables
	
		mblk = self.m_internalBlocks['SIMULATOR'] 
		if (self.m_internalBlocks['FLOW'] <> None):   
			blk = self.m_internalBlocks['FLOW']
			print "I have the following ...NUMBER_OF_FLUID_TABLES", blk.getNumberOfTables()
			mblk.setKeywordValue('NUMBER_OF_FLUID_TABLES', str(blk.getNumberOfTables()))
			

	def doMainConsistencyCheck(self):
		if self.verbose == 1: print "___________________________ LOOK _________________________"	


		self.checkModelTables()              #
		self.checkGridData()
		self.checkRockFluidTables()
		self.checkComparatorTables()
		self.checkEquilibriumTables()
		self.checkFlowTables()
		self.checkMigrationData()
		#self.checkLGRdata()

		##for tbl in self.blockSATTables.values():
			#if tbl <> None: tbl.doConsistencyCheck()
		#for tbl in self.blockPVTTables.values():
			#if tbl <> None: tbl.doConsistencyCheck()
		#if self.verbose == 1: print "___________________________ LOOK _________________________"	

	########################################################################
	# Called by objects doConsistencyCheck routine
	########################################################################
	def checkGridData(self):
		if (self.m_internalBlocks['GRID'] == None):
			xstr = "Unable to find Grid Data Structure! Using defaults\n"
			self.addErrorString(xstr,None);
			self.m_internalBlocks['GRID'] = pGridData(None);
		p = self.m_internalBlocks['SIMULATOR']
		self.m_internalBlocks['GRID'].setXYZ(p.iXnodes,p.iYnodes,p.iZnodes)
		self.m_internalBlocks['GRID'].doConsistencyCheck()


	########################################################################
	# Called by objects doConsistencyCheck routine
	########################################################################
	def checkLGRdata(self):
		if (self.m_internalBlocks['LGRPARMS'] == None): 
			self.m_internalBlocks['LGRPARMS']  = pLGRdata()
		self.m_internalBlocks['LGRPARMS'].doConsistencyCheck()
		if (self.m_internalBlocks['LGRPARMS'].getGridCount() <> self.m_internalBlocks['SIMULATOR'].iLgrRegionCount):
			xstr = "LGR Grids found (%d) do not match model Data (%d)!!\n" % (self.m_internalBlocks['LGRPARMS'].getGridCount(),self.m_internalBlocks['SIMULATOR'].iLgrRegionCount)
			self.addErrorString(xstr);

	########################################################################
	# Called by objects doConsistencyCheck routine
	########################################################################
	def checkMigrationData(self):
		if (self.m_internalBlocks['MIGRATION'] == None):
			self.m_internalBlocks['MIGRATION'] = pMigrationData();
		self.m_internalBlocks['MIGRATION'].doConsistencyCheck()
		if (self.m_internalBlocks['MIGRATION'].getLineCount() <> self.m_internalBlocks['SIMULATOR'].iMigrationLineCount):
			xstr = "Migration Lines found (%d) do not match model Data (%d)!!\n" % (self.m_internalBlocks['MIGRATION'].getLineCount() ,self.m_internalBlocks['SIMULATOR'].iMigrationLineCount)
			self.addErrorString(xstr);

	########################################################################
	# Called by objects doConsistencyCheck routine
	########################################################################
	def checkRockFluidTables(self):
		if (self.m_internalBlocks['ROCKFLUID'] == None):
			xstr = "Rock Fluid Structure not found! Using defaults\n"
			self.addErrorString(xstr);
			self.m_internalBlocks['ROCKFLUID'] = pRockFluid(None);
		self.m_internalBlocks['ROCKFLUID'].doConsistencyCheck()

	def checkComparatorTables(self):
		if (self.m_internalBlocks['COMPARATOR'] == None):
			#self.str = "Comparator Structure not found! Using defaults\n"
			#self.addErrorString(self.str);
			self.m_internalBlocks['COMPARATOR'] = pComparator(None);
		self.m_internalBlocks['COMPARATOR'].doConsistencyCheck()

	########################################################################
	# Called by objects doConsistencyCheck routine
	########################################################################
	def checkModelTables(self):
		if (self.m_internalBlocks['SIMULATOR'] == None):
			selfxstr = "Model Structure not found! Using defaults\n"
			self.addErrorString(selfxstr);
			self.m_internalBlocks['SIMULATOR'] = pModel(None);
		self.m_internalBlocks['SIMULATOR'].doConsistencyCheck()

	def checkFlowTables(self ): 
		""" Checks optional flow table """
		if (self.m_internalBlocks['FLOW'] <> None):
			self.m_internalBlocks['FLOW'].doConsistencyCheck()

	########################################################################
	#
	# This checks the equilibrium tables in the Equilibration object. 
	# Called by objects doConsistencyCheck routine
	#
	########################################################################
	def checkEquilibriumTables(self):
		block = self.m_internalBlocks['EQUILIBRIUM']
		if (block == None): 
			selfxstr = "Unable to find an Equilibration Block ...\n"
			self.addErrorString(selfxstr);
			return -1
		#if (block.iEqRegionCount <> block.getEquilibriumCount()):
		#	i = block.getEquilibriumCount();
		#	j = block.getLineNumber();
		#	cstr = "Error: Line %d: Regions declared (%d) dont match regions found (%d) \n" % (j,block.iEqRegionCount,i)
		#	self.addErrorString(cstr);
		#	return -1
#
		# self.i = self.blockEquilibration.getEquilibriumCount()
		# self.j = self.blockEquilibration.getBubblePointCount()
		# self.k = self.blockEquilibration.getLineNumber();
		#if (self.i <> self.j):
		#	self.str = ": Equilibriums declared (%d) at line %d dont match bubble point tables (%d) \n" % (self.i,self.k,self.j)
			
		#	self.addErrorString(self.str);
		#		return -1
		
		block.doConsistencyCheck()
		return 0

	########################################################################
	# Reads a model file from disk. 
	########################################################################
	def readModelFile(self,filename,verbose=0):
		if filename == None: return
		sext= filename[-3:].lower() 
		self.filename = filename

		self.sErrorStrings = []                         # 
		self.inputLines = []                            # Will be filled with raw input
	
		if sext == 'xml':
			basename  = os.path.basename(filename)      # without the extensions
			wmodelname,ext = os.path.splitext(basename)  # gives modelname
			modelname,ext = os.path.splitext(wmodelname)  # gives modelname
			dirname   = os.path.dirname(filename)       # without the extensions
			self.readXMLFiles(modelname,dirname)
			self.doMainConsistencyCheck()   # Automatically run a consistency check.
			return  1

		self.readDataFile(filename,keepCopyOfLine=1)			# Read but don't retain memory
		self.doMainConsistencyCheck()   # Automatically run a consistency check.
		return 1

	def clearMemory(self):
		self.createEmptyObject()                        # Always create an empty object

	#####################################################
	## Grid Block 
	#####################################################
	def collectSyntaxErrors(self):
		xstr = [ x for x in self.sErrorStrings ]

		# This now becomes a simple 'for' loop

		for bname in ['SIMULATOR','ROCKFLUID','MIGRATION']:
			if self.m_internalBlocks[bname] <> None: 
				for x in self.m_internalBlocks[bname].getErrorReport(): 
					xstr.append(x) 

		if self.m_internalBlocks['EQUILIBRIUM'] <> None: 
			block = self.m_internalBlocks['EQUILIBRIUM']
			for item in block.getErrorReport(): xstr.append(item)
			if block.getEquilibriumCount() > 0:
				for item in block.aEquilibriumTables:
					for x in item.getErrorReport(): xstr.append(x)
			if block.getBubblePointCount() > 0:
				for item in block.aBubblePointTables:
					for x in item.getErrorReport(): xstr.append(x)

		if self.m_internalBlocks['LGRPARMS']  <> None: 
			for item in self.m_internalBlocks['LGRPARMS'].tableArray:
				for x in item.getErrorReport(): xstr.append(x)
			for x in self.m_internalBlocks['LGRPARMS'].getErrorReport(): 
				xstr.append(x)
		#####################################################
		## Grid Block 
		#####################################################
		if self.m_internalBlocks['GRID'] <> None: 
			for x in self.m_internalBlocks['GRID'].getErrorReport(): xstr.append(x)
			for w in self.m_internalBlocks['GRID'].aModifyObjects:			
				for x in w.getErrorReport(): xstr.append(x)
			for w in self.m_internalBlocks['GRID'].aArrayObjects:
				for x in w.getErrorReport(): xstr.append(x)
			for w in self.m_internalBlocks['GRID'].aRegionObjects:
				for x in w.getErrorReport(): xstr.append(x)

		#if self.blockSATTables.values() <> None: 
			#for w in self.blockSATTables.values():
				#if w <> None: xstr = xstr + w.getErrorReport()
		#if self.blockPVTTables.values() <> None: 
			#for pvt in self.blockPVTTables.values():
				#if pvt <> None: xstr = xstr + pvt.getErrorReport()
		#return "".join(xstr)
		return xstr

	def createWellToDate(self,force=0):
		"""
		Upon return the self.allDatesPerWell is populated with lists of
		dates per well name.
		if force == 1, we do the work twice, so be careful with this call.
		"""
		if (force == 0): 
			self.allDatesPerWell = {}
		else:
			if (len(self.allDatesPerWell.keys()) > 0): return
			self.allDatesPerWell = {}


		dkeys = self.allDatesArray.keys()           # Get all the dates. 
		if len(dkeys) < 1: return                   # Don't process empty list.
		for dkey in dkeys:                          # for each date.
			dte = self.allDatesArray[dkey]          # 
			dname = dte.getDate()
			for well in dte.Wells.values():
				name = well.getWellName()
				if not self.allDatesPerWell.has_key(name): 
					self.allDatesPerWell[name] = []
				dateNames = self.allDatesPerWell[name]
				if not dname in dateNames:  self.allDatesPerWell[name].append(dname) 
		for w in self.allDatesPerWell.values(): w.sort()


########################################################################
# Sample test function.
########################################################################
def handleMain(filename,outfd=sys.stdout,doEcho=1,v=0,showxml=None,readXML=None):
	model = modelFileParser();
	model.verbose = v         # global 
	print filename
	if readXML <> None: 
		showxml = None

	thisdir = os.getcwd()
	os.chdir(os.path.dirname(filename))
	model.readModelFile(filename); 
	if (doEcho == 1):
		xstr = model.collectSyntaxErrors()
		outfd.write("".join(xstr))
		if (outfd <> sys.stdout):
			outfd.close()
	if (doEcho == 2):
		model.writeModelFile(None,useFd=fd) # This writes a comment-stripped file. 
		if (outfd <> sys.stdout):
			outfd.close()
	if showxml <> None: model.writeXMLFiles(filename,showxml) 
	os.chdir(thisdir)


def usage(name):
	print "Usage: %s modelFilename [opt]" % (sys.argv[0])
	print "%s -h  prints this help message " % (sys.argv[0])
	print "If no opt is specified, the output is sent to stdout\nThe opt must be one of the following formats:"
	print "opt:  -v is verbose mode "
	print "opt:  -f FILENAME writes a formatted output file FILENAME (for debugging)"
	print "opt:  -x dirName writes an XML formatted output file FILENAME (for future release)"
	#print "opt:  -e [1 | 2] is echo mode for my debugging only "


if __name__ == '__main__':
	#
	# Somehow catch the following options:
	# 
	filename = ''
	showXML  = None 
	readXML  = None 
	doEcho   = 1
	verbose  = 0
	outfd = sys.stdout
	allowedArgs = { '-f': 1, '-h':0 , '-v': 0 , '-x': 1 , '-r':0}
	
	if len(sys.argv) == 2:
		inputfilename = sys.argv[1]
		if (inputfilename == '-h'):
			usage(sys.argv[0])
		else:
			handleMain(inputfilename,outfd,doEcho,verbose,showXML)
		sys.exit(0)
	if (len(sys.argv) < 2):
		usage(sys.argv[0])
	else:
		args = sys.argv[1:]	# Remove the program name 
		xlen = len(args)	# Get the rest of the arguments.
		inputfilename  = args[0] # Get program name
		i = 1
		while i < xlen:
			si = args[i]
			if (si == '-h'):
				usage(sys.argv[0])
				sys.exit(0)
			if (si == '-v'):
				verbose = 1
				i = i + 1
				continue
			if (si.find('-r') > -1):
				readXML= 1
				i = i + 1
				continue
			if (si.find('-x') > -1):
				i = i + 1
				showXML=args[i]
				continue
			if (si.find('-e') > -1):
				i = i + 1
				doEcho = int(args[i])
				continue
			if (si.find('-f') > -1):
				i = i + 1
				si = args[i]
				outfd  = open(si,'w')
				doEcho = 2
				continue
			i = i + 1
		handleMain(inputfilename,outfd,doEcho,verbose,showXML,readXML)
