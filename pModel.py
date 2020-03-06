"""
This handles SIMULATOR_PARAMETERS items for the model file. 
The inputs can be in XML files (preferred) or in POWERS text format.
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
import string

class pModel(pObject):
	def __init__(self,ilo=None):
		pObject.__init__(self,ilo)
		pObject.setDelimiters(self,'BEGIN_SIMULATOR_PARAMETERS','END_SIMULATOR_PARAMETERS')

		self.bWriteToDisk = 1					# This is a required object.
		self.dDateStart = '1970/1/1'

		#
		# Variables are added only when required later in the program or the GUI.
		#
		self.iXnodes = 1
		self.iYnodes = 1
		self.iZnodes = 1
		self.iPhases = 0
		self.iCompletionCount = 0
		self.iWellCount =0
		self.iFluidTableCount  =0
		self.iEqRegionCount = 0
		self.iMigrationLineCount = 0
		self.iRockTableCount = 0
		self.iGridLevelCount = 0
		self.iLgrRegionCount = 0
		self.iMaxWells	   = 100
		self.iMaxGroupParm  = 0
		self.iGroupCount	 = 0
		self.iWellParmCount  = 0
		self.iMaxGroupCond   = 0
		self.iActionsPerGp   = 0
		self.iMaxRulesPerGp  = 0
		self.iMaxWellCond	= 0
		self.sNumberOfComponents = 3
		self.sTitleString = ''
		self.sModelType = 'BLACK_OIL'

		self.compositionalNames = ['NUMBER_OF_COMPONENTS' ]

		# For new compressibility block.
		#	'WATER_COMPRESSIBILITY', 'WATER_REFERENCE_PRESSURE',
		#	'WATER_REFERENCE_MOLAR_DENSITY', 'RESERVOIR_TEMPERATURE', 'INITIAL_COMPOSITION_CONSTANT']
		#	self.addKeyword('WATER_COMPRESSIBILITY','0.0')
		#	self.addKeyword('WATER_REFERENCE_PRESSURE','0.0')
		#	self.addKeyword('WATER_REFERENCE_MOLAR_DENSITY','0.0')
		#	self.addKeyword('RESERVOIR_TEMPERATURE','0.0')
		#	self.addKeyword('INITIAL_COMPOSITION_CONSTANT','0.0')

		self.sValidationTypeStrings = ('NONE','ERROR_CHECK','WELL_CHECK','INIT_CHECK')
		self.sValidation  = ''

		self.sModelTypeStrings = ('BLACK_OIL', 'COMPOSITIONAL', 'EXTENDED_BLACK_OIL')

		#self.sModelTypeStrings = ('BLACK_OIL', 'COMPOSITIONAL', )
	
		# Numeric entries		
		self.addKeyword('GRID_ROTATION_ANGLE','0')


		self.addKeyword('RESERVOIR_TYPE','NON_FRACTURE', ('NON_FRACTURE','FRACTURE'),label='Reservoir Type') 
		self.addKeyword('FRACTURE_PERMEABILITY_VALUE_X','BLOCK_CENTER',('BLOCK_CENTER', 'BLOCK_FACE') ,label='Fracture Permeability in X')
		self.addKeyword('FRACTURE_PERMEABILITY_VALUE_Y','BLOCK_CENTER',('BLOCK_CENTER', 'BLOCK_FACE') ,label='Fracture Permeability in X')
		self.addKeyword('FRACTURE_PERMEABILITY_VALUE_Z','BLOCK_CENTER',('BLOCK_CENTER', 'BLOCK_FACE') ,label='Fracture Permeability in Z')
		self.addKeyword('WELLS_COMPLETED_IN_FRACTURE','FALSE',('TRUE', 'FALSE'),label='Wells Completed in fracture')

		self.addKeyword('NUMBER_OF_FLUID_TABLES','0',label='Number of fluid tables')
		self.addKeyword('NUMBER_OF_EQUILIBRIUM_REGIONS','0',label='Number of equilibrium regions')
		self.addKeyword('NUMBER_OF_MIGRATION_LINES','0',label='Number of migration lines')
		self.addKeyword('NUMBER_OF_ROCK_TABLES',		'0',label='Number of rock tables')
		self.addKeyword('NUMBER_OF_COMPONENTS', '0',label='Number of components')
		self.addKeyword('NUMBER_OF_GRID_LEVELS','1', ('1','2'),label='Number of grid levels')
		self.addKeyword('NUMBER_OF_LGR_REGIONS','0',label='Number of LGR regions')
		self.addKeyword('PHASES','3',('1','2','3'),label='Number of Phases')
		self.addKeyword('X_ORIGIN_UTM','0',label='X Origin in UTM')
		self.addKeyword('Y_ORIGIN_UTM','0',label='Y Origin in UTM')
		self.addKeyword('XNODES','0',label='Number of X nodes')
		self.addKeyword('YNODES','0',label='Number of Y nodes')
		self.addKeyword('ZNODES','0',label='Number of Z nodes')
		self.addKeyword('MAX_WELLS_LGR','2',label='Max. Wells Per LGR')

		# String entries have to be declared first
		for a in ['TITLE', 'WELL_PERFS', 'WELL_RATES', 'RECURRENT_DATA', 'RESTART_INPUT', 'RESTART_OUTPUT', 'BOUNDARY_FLUX',
			'RESTART_OUTPUT', 'MAPS_OUTPUT',  'BINARY_DATA_DIRECTORY', 'SURFACE_NETWORK']:
			self.sQuotedKeywords.append(a)
		self.addKeyword('TITLE',label='Title String')
		self.addKeyword('WELL_PERFS',label='Input Perforations file')
		self.addKeyword('WELL_RATES',label='Input Rates file')
		self.addKeyword('RECURRENT_DATA',label='Recurrent data file')
		self.addKeyword('RESTART_INPUT',label='Location of RESTART INPUT file')
		self.addKeyword('RESTART_OUTPUT',label='Location of RESTART OUTPUT file')
		self.addKeyword('BINARY_DATA_DIRECTORY',label='Location of BINARY DATA files')
		self.addKeyword('BOUNDARY_FLUX',label='Boundary flux, if any')
		self.addKeyword('SURFACE_NETWORK',label='Surface network, if any'); 
		self.addKeyword('MAPS_OUTPUT',label='MAPS output location'); 

		# Optional boxes. 
		self.addKeyword('CAPILLARY_PRESSURE_OPTION','PC_FUNCTION',('PC_FUNCTION','LEVERETT_J_FUNCTION'),label='Capillary Pressure')
		self.addKeyword('DRAW_SYSTEM_ORIENTATION','RIGHT_HAND',('RIGHT_HAND','LEFT_HAND'),label='Drawing Orientation')
		self.addKeyword('GRID_SYSTEM_ORIENTATION','RIGHT_HAND',('RIGHT_HAND','LEFT_HAND'),label='Grid Orientation')
		self.addKeyword('INPUT_DATA_SYSTEM','LEFT_HAND',('RIGHT_HAND','LEFT_HAND'),label='Input Data Orientation')
		self.addKeyword('INITIALIZATION_OPTION','GRAVITY_CAPILLARY_EQUILIBRIUM',
			('GRAVITY_CAPILLARY_EQUILIBRIUM','NON_EQUILIBRIUM'),label='Initialization Option')
		self.addKeyword('LINEAR_SOLUTION_OPTION','REDUCED_SYSTEM_SERIES',('REDUCED_SYSTEM_SERIES','NONE'),
			label='Linear Solution Option') 	# page 6-22
		self.addKeyword('LINEARIZATION_OPTION','IMPLICIT',('IMPLICIT','IMPES'),
			label='Linearization Option')
		self.addKeyword('PERMEABILITY_VALUE_X','BLOCK_CENTER',('BLOCK_CENTER','BLOCK_FACE'),
			label='Permeability X')
		self.addKeyword('PERMEABILITY_VALUE_Y','BLOCK_CENTER',('BLOCK_CENTER','BLOCK_FACE'),
			label='Permeability Y')
		self.addKeyword('PERMEABILITY_VALUE_Z','BLOCK_CENTER',('BLOCK_CENTER','BLOCK_FACE'),
			label='Permeability Z')
		self.addKeyword('PERMEABILITY_VALUE','BLOCK_CENTER',('BLOCK_CENTER','BLOCK_FACE'), label='Total Permeability')
		self.addKeyword('PRE_CONDITIONER_OPTION','REDUCED_SYSTEM_SERIES',('REDUCED_SYSTEM_SERIES','NONE'),
			label='Pre conditioner Option')	# page 6-22
		self.addKeyword('PRESSURE_DEPENDENCE_OPTION','MARS',('MARS','ECLIPSE'),label='Pressure Dependance')
		self.addKeyword('PRESSURE_INTERPOLATION_OPTION','LINEAR', ('LINEAR','ANALYTIC'),label='Pressure Interpolation')
		self.addKeyword('SATURATION_INTERPOLATION_OPTION','LINEAR', ('LINEAR','ANALYTIC'),label='Saturation Interpolation')
		self.addKeyword('TRANSMISSIBILITY_OPTION','MARS',('MARS','ECLIPSE'),label='Transmissibility')
		self.addKeyword('GRID_INPUT','LOCAL',('UTM','LOCAL'),label='Grid Input Axes')
		self.addKeyword('GRID_OUTPUT','LOCAL',('UTM','LOCAL'),label='Grid Output Axes')
		self.addKeyword('WELL_FORMULATION','EXPLICIT_WELL',('EXPLICIT_WELL','IMPLICIT_BHP','IMPLICIT_MOB','IMPLICIT_BHP_MOB'),
			label='Well Formulation')
		self.addKeyword('ACCEPT_DEPTH_VIOLATION','TRUE',('TRUE','FALSE'),label='Accept Depth Violation') 			# page 6-34
		self.addKeyword('ASCII_WELL_OUTPUT','TRUE',('TRUE','FALSE'),label='ASCII Well Output') 			# page 6-24
		self.addKeyword('WELL_OUTPUT','TRUE',('TRUE','FALSE'),label='Other Well Output') 			# page 6-24
		self.addKeyword('ASCII_MIG_LINE_OUTPUT','FALSE',('TRUE','FALSE'),label='Migration Line Output') 			# page 6-24
		self.addKeyword('COMPLETION_DATA','FALSE',('TRUE','FALSE'),label='Completion Data Output') 			# page 6-36 - Override 
		self.addKeyword('DETAILED_SIMVIEW_DATA','TRUE',('TRUE','FALSE'),label='SIMVIEW Data Output')		# page 6-22
		self.addKeyword('MARS_OUTPUT','TRUE',('TRUE','FALSE'),label='MARS Data Output') 			# page 6-23
		self.addKeyword('MAPS_COORDINATE_SYSTEM','RIGHT_HAND',('RIGHT_HAND','LEFT_HAND'),label='MAPS Coordinates') 			# page 6-36
		self.addKeyword('MATBAL_OUTPUT','TRUE',('TRUE','FALSE'),label='Material Balance Output') 			# page 6-23
		self.addKeyword('MATRIX_SCALE_OPTION','TRUE',('TRUE','FALSE'),label='Matrix Scale Output')
		self.addKeyword('OUTPUT_CUM_RATES','TRUE',('TRUE','FALSE'),label='Cummulative Rates Output') 			# page 6-22
		self.addKeyword('SHOW_INACTIVE_CELLS','TRUE',('TRUE','FALSE'),label='Show Inactive Cells') 			# page 6-24
		self.addKeyword('WELLS_COMPLETED_IN_FRACTURE','FALSE',('TRUE','FALSE'),label='Show Fracture Completed Wells') 			# page 6-36
		self.addKeyword('NONLINEAR_UPDATE','EXACT_SATURATION',('EXACT_SATURATION','EXACT_MASS_BALANCE'), 
			label='Nonlinear Update')				# page 6-22
		self.addKeyword('MODEL_TYPE',   'BLACK_OIL', self.sModelTypeStrings,label='Model Type') 
		self.addKeyword('VALIDATION','None',self.sValidationTypeStrings, label='Validation Type')
		
		# Create the keys for display...
		self.aAllowedKeywords = self.aKeywords.keys()

	#################################################################
	# These functions are required for the user interface
	#################################################################
	def getCompositionalNames(self):
		return self.compositionalNames

	def printStructure(self,fd,showHeader=0):
		items = self.getContentsAsList(showHeader)
		i = 0
		for ln in items: 
			f = ln.find('VALIDATION')
			if f == 0: 
				xitems = ln.split()
				if len(xitems) == 2:
					value = xitems[1]
					if value == 'NONE': 
						del items[i]
			i = i + 1
		if len(items) > 0: fd.write("".join(items))

	#################################################################
	# This function is required for parsing errors in the text.
	#################################################################
	def doConsistencyCheck(self):
		return
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0: continue 
			items = ilo.getItems()
			if (len(items) <> 2):                           # Only very few assgts are allowed here.
				if items[0] in ['TITLE','Title', 'INITIAL_COMPOSITION_CONSTANT']: continue
				ilo.markAsErred()
				self.addErrorMessage('Invalid Input ', ilo)
				continue
			keyword = items[0]
			if x in self.aKeywords.items():		# True if keyword is okay.
				k,v = x
				if keyword in self.aOptions.keys(): 
					opts = self.aOptions[keyword]       # Must ignore case
					olower = map(string.upper,opts) 	# both in option 
					vlower = v.upper()				    # and entered value
					if (not vlower in olower): self.addWarningMessage('Bad Option for %s' % keyword, ilo)
				else:   # Unknown keyword.
					if not keyword in self.sQuotedKeywords: 
						self.addWarningMessage('1. Unrecognized keyword in input: [%s,%s]\n' % (keyword,thisline))

	#################################################################
	# Part of the consistency check is to see if sane values are 
	# assigned to the numeric values.
	# These tests could include: 
	# (a) sane integer values
	# (b) numeric values within reason for floating point number 
	# (c) ascii strings instead of numbers
	# Missing values should be caught. 
	#################################################################
	def parseLine(self,incoming):
		""" 
		Parses each line individually. Requires the base class parseLine function 
		The main start of block and end of block parameters not kept.
		"""
		self.addContentLine(incoming)
		if incoming.mustProcess == 0: return  
		self.iLineObject = incoming
		items = self.iLineObject.getItems()
		keyword = string.upper(items[0])
		if len(items) < 2: 
			if not keyword in self.sQuotedKeywords: 
				self.addErrorMessage('2. Unrecognized keyword SIMULATOR_BLOCK:', self.iLineObject)
			return
		self.parseKeyword(keyword,items[1:])
			 

	#################################################################
	# The value could be a list.  
	#################################################################
	def parseKeyword(self,keyword,ivalue):
		keyword = keyword.upper()
		if not keyword in self.aAllowedKeywords:  # Check if it is allowed. 
			self.addWarningMessage('3. Unrecognized keyword ', self.iLineObject)  # Otherwise add as error.
			return; 

		###################################################################################
		# First check if value is a list. If this a list, join them together.
		###################################################################################
		if ivalue == '': value = '0' 
		if type(ivalue) is str: 
			value = ivalue
		else: 
			value = ivalue[0]
		if not keyword in self.sQuotedKeywords: value = value.upper()  # Leave included file names alone.

		self.setKeywordValue(keyword,value)
		if (keyword == 'MODEL_TYPE'):
			if not value in self.sModelTypeStrings and value <> '': 
				self.addErrorMessage('4. Unrecognized MODEL_TYPE in SIMULATOR_BLOCK:', self.iLineObject)
			else:
				self.sModelType = value
			return

		if (keyword == 'TITLE'): # VERY SPECIAL HANDLING HERE .. 
			if type(ivalue) is str: 
				self.sTitleString = value
			else:
				self.sTitleString = join(ivalue,' ')
			self.sTitleString = self.sTitleString.replace('&',' ')
			self.sTitleString = self.sTitleString.replace('<',' ')
			self.sTitleString = self.sTitleString.replace('>',' ')
			#self.sTitleString = self.sTitleString.replace('---',' ')
			self.sTitleString = self.sTitleString.replace('-','')
			self.setKeywordValue(keyword,self.sTitleString)
			return

		########################################################################################
		# Check if the options work.
		########################################################################################
		if keyword in self.aOptions.keys(): 
			if not value in self.aOptions[keyword]:       # Must ignore case
				if not keyword in self.sQuotedKeywords: 
					self.addErrorMessage('5. Unrecognized keyword in input [250]', self.iLineObject)
			return 

		if (keyword == 'XNODES'): 
			self.iXnodes = int(value)
			return 
		if (keyword == 'YNODES'): 
			self.iYnodes = int(value)
			return 
		if (keyword == 'ZNODES'): 
			self.iZnodes = int(value)
			return 
		if (keyword == 'VALIDATION'):
			if not value in self.sValidationTypeStrings and value <> '': 
				self.addWarningMessage('Bad VALIDATION value in SIMULATION_BLOCK',self.iLineObject)
			else:
				self.sValidation = value
			return;
		if (keyword == 'NUMBER_OF_COMPONENTS'): 
			self.sNumberOfComponents = int(value)
			return;
		if (keyword == 'MAX_NUMBER_OF_COMPLETIONS'):
			self.iCompletionCount = int(value)
			return;
		if (keyword == 'MAX_NUMBER_OF_WELLS'):
			self.iWellCount = int(value)
			return;
		if (keyword == 'NUMBER_OF_FLUID_TABLES'):
			self.iFluidTableCount  = int(value)
			return;
		if (keyword == 'NUMBER_OF_EQUILIBRIUM_REGIONS'):
			self.iEqRegionCount = int(value)
			return;
		if (keyword == 'NUMBER_OF_MIGRATION_LINES'):
			self.iMigrationLineCount = int(value)
			return;
		if (keyword == 'NUMBER_OF_ROCK_TABLES'): 
			self.iRockTableCount = int(value);       #This should have an exception if no number found
			return
		if (keyword == 'NUMBER_OF_GRID_LEVELS'):
			self.iGridLevelCount = int(value)
			return;
		if (keyword == 'NUMBER_OF_LGR_REGIONS'):
			self.iLgrRegionCount = int(value)
			return;
		if (keyword == 'MAX_WELLS_LGR'):
			self.iMaxWells	   = int(value)
			return;
		if (keyword == 'MAX_GROUP_PARAMETERS'):
			self.iMaxGroupParm  = int(value)
			return;
		if (keyword == 'MAX_NUMBER_OF_GROUPS'):
			self.iGroupCount	 = int(value)
			return;
		if (keyword == 'MAX_WELL_PARAMETERS'):
			self.iWellParmCount  = int(value)
			return;
		if (keyword == 'WM_MAX_GROUP_CONDITIONS'):
			self.iMaxGroupCond   = int(value)
			return;
		if (keyword == 'WM_MAX_ACTIONS_PER_GROUP'):
			self.iActionsPerGp   = int(value)
			return;
		if (keyword == 'WM_MAX_RULES_PER_GROUP'):
			self.iMaxRulesPerGp  = int(value)
			return
		if (keyword == 'WM_MAX_WELL_CONDITIONS'):
			self.iMaxWellCond	= int(value)
			return

	##################################################################################
	#
	##################################################################################
	def writeXMLfile(self,fd=sys.stdout,name='BLOCK_SIMULATION',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def readXMLfile(self,filename,xmldir='.'):
		ch = pModelXMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)

####################################################################################################
# The handler for the xml input ... Please don't try to make this into one object.
####################################################################################################
class pModelXMLhandler(ContentHandler):
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
		if name == 'SIMULATOR':
			ilo = pLineObject('BEGIN_SIMULATOR_PARAMETERS',self.filename,self.lineNumber)
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
	ob = pModel()
	ch = pModelXMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	print ob.getEditableString()
	

