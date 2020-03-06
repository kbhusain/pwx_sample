"""

I have deprecated this entire function because of the problems with included files.
The Plex parser does not handle inclusions well. I could read the entire set of files
into one stream, but I won't handle multiple inclusions well.


###################################################################################
#
# TODO:
#  Add in support for GROUPRULES 
#  Add in support for RIGS 
#  Add in support for case-insensitive keywords
#
###################################################################################
"""
import string 
from Plex import *
import sys
from pObject import *
import copy

#####################################################################################
# Start of class description
#####################################################################################
class cRecurrentFlattener(cParserObject):
	def __init__(self):
		cParserObject.__init__(self)

	################################################################
	def flattenRecurrentFile(self,filename,outfilename):
		self.readIncludedFiles(filename)
		fd = open(outfilename,'w')
		for oln in self.inputLines: 
			if oln.mustProcess == 0: continue
			fd.write(oln.getRawLine())
		fd.close()

##################################################################################################
# The grammar for handling the keywords in the RECURRENT FILES
##################################################################################################
period = Str(".")
letter = Range('AZaz') | Any("_") | Any("-") | Any('&') | period | Any('?') | Any('*')
digit  = Range('09')
name1   = letter+Rep(letter | digit )
name2  = Rep1(digit)+Any('_')+Rep1(digit)
name   = name1 | name2
integer = Rep1(digit)
float1 = Rep(digit)+period+Rep1(digit)
float2 = Rep1(digit)+period+Rep(digit)
number = integer | float1 | float2
math = Any('=<>')
eob  = Any('/')
quote = Any("'") | Any('"')
greater = Any(">")
openbrace = Any('{') 
closebrace = Any('}')
openlist = Any('(')
closelist = Any(')')
comment_begin = Any('#') | Any('!') | Any('/')
comment_char  = AnyBut('\n')
comment_end = Eol
semicolon = Any(';')
space = Any(" ;\t\n,")
##################################################################################################
# 
##################################################################################################
class cRecurrentFile(cParserObject):	
	def __init__(self, useTheseDates={}, useTheseWellNames={}):
		cParserObject.__init__(self)
		self.applyInitialTree(useTheseDates,useTheseWellNames)
		self.filename = None
		self.fd = None
		self.resword = Str("group","injector","producer")
		self.keywords = {}
		self.collectionType  = ''
		self.collectionName   = '' 
		self.collectionOption = '' 
		self.lastPseudoItem = None
		self.lastRigItem = None

		##################################### LEX ######################################
		self.lexicon = Lexicon([ (name, 'ident'),
			(number, 'number'),
			(math,  TEXT), 
			(eob,  TEXT), 
			(name,  TEXT), 
			(self.resword, 'Kamran'),
			(closebrace, TEXT),
			(openbrace, TEXT),
			(closelist, TEXT),
			(openlist, TEXT),
			(semicolon, TEXT),
			(space | quote , IGNORE),
			(comment_begin, Begin('comment')), 
			State('comment', [
				(comment_char, IGNORE), 
				(comment_end, Begin(''))
				]) ])

		self.ST_IDLE  = 0
		self.ST_IN_DATE = 1
		self.ST_IN_PSEUDO = 2
		self.ST_IN_WELLS = 3
		self.ST_IN_CONNECTIONS = 4
		self.ST_IN_GROUPRULES = 5
		self.ST_ONEWELL = 6
		self.ST_PERFS = 7
		self.ST_IN_GROUP = 8
		self.ST_IN_PRODUCER = 9
		self.ST_IN_INJECTOR =10 
		self.ST_PSEUDO_ITEM =11 
		self.ST_RIG_ITEM =12 
		self.ST_IN_RIGS=13 

		self.lastWell = None
		self.lastDate = None
		self.state = self.ST_IDLE
		self.previousState = self.state
		self.lastToken = '' 

		self.groupRuleState = 0
		self.lastGroupRule = None
		self.groupRuleStack = []



		#
		# The keywordHolder object is used to store the keywords which are at a global level
		#
		self.keywordHolder = pObject()
		self.keywordHolder.addKeyword('DT_MIN','0.0001')
		self.keywordHolder.addKeyword('DT_MAX','1.0 91.0')              	# 
		self.keywordHolder.addKeyword('DT_INIT','0.00001')               	# 
		self.keywordHolder.addKeyword('END_OF_SIMULATION_DATE','None')    	# 
		self.keywordHolder.addKeyword('FRACTURE_MAX_DS_ITER','0.3')    	# 
		self.keywordHolder.addKeyword('GAS_RESIDUAL_RELTOL','0.01')    	# 
		self.keywordHolder.addKeyword('HYDROCARBON_RESIDUAL_RELTOL','0.01')    	# 
		self.keywordHolder.addKeyword('LINEAR_MAXIMUM_ITERATIONS','120') 	# 
		self.keywordHolder.addKeyword('LINEAR_SOLUTION_OPTION','ORTHOMIN',('ORTHOMIN','REDUCED_SYSTEM_SERIES')) 	# 
		self.keywordHolder.addKeyword('LINEAR_TOLERANCE','0.05') 	# 
		self.keywordHolder.addKeyword('MAX_DBPP_ITER','100')     			#
		self.keywordHolder.addKeyword('MAX_DBPP_TOL','100')     			#
		self.keywordHolder.addKeyword('MAX_DP_TIMESTEP','2000.0')        	# 
		self.keywordHolder.addKeyword('MAX_DP_ITER','100')        	    #  
		self.keywordHolder.addKeyword('MAX_DP_TOL','0.50')        	    #  
		self.keywordHolder.addKeyword('MAX_DS_ITER','0.15')        	    #  
		self.keywordHolder.addKeyword('MAX_DS_TOL','0.005')       	    #  
		self.keywordHolder.addKeyword('MAX_DS_TIMESTEP','0.1')        	    #  
		self.keywordHolder.addKeyword('MAX_DT_INCREASE_FACTOR','5.0')    	# 
		self.keywordHolder.addKeyword('MAX_TIMESTEP','2000')     			#
		self.keywordHolder.addKeyword('MAX_TIMESTEP_REPEAT','2000')      	# 
		self.keywordHolder.addKeyword('MAX_MGRID_ITERATIONS','3')      	# 
		self.keywordHolder.addKeyword('MGRID_RESIDUAL_RELTOL','0.5')      	# 
		self.keywordHolder.addKeyword('MGRID_SYNC_GAS_FLAG',('TRUE','FALSE'))      	# 
		self.keywordHolder.addKeyword('MATBAL_OUTPUT','FREQ 1 MONTH')
		self.keywordHolder.addKeyword('MATRIX_SCALE_OPTION','TRUE',('TRUE','FALSE'))
		self.keywordHolder.addKeyword('MAX_MGRID_ITERATIONS','0.1')        	    #  
		self.keywordHolder.addKeyword('MIN_PORE_VOL_TIMESTEP','700.0')     	#
		self.keywordHolder.addKeyword('MOST_RECENT_TS_CUTS','3')     	#
		self.keywordHolder.addKeyword('NON_LINEAR_MAXIMUM_ITERATIONS','6')        	    #  
		self.keywordHolder.addKeyword('NON_LINEAR_MINIMUM_ITERATIONS','5')        	    #  
		self.keywordHolder.addKeyword('NON_LINEAR_TOLERANCE','.0001')        	    #  
		self.keywordHolder.addKeyword('NUM_OF_ORTHOGONAL_DIRECTIONS','10')        	    #  
		self.keywordHolder.addKeyword('NUMBER_OF_ORTHOGONAL_DIRECTIONS','10')        	    #  
		self.keywordHolder.addKeyword('NUMBER_OF_SERIES_TERMS','2')        	    #  
		self.keywordHolder.addKeyword('OIL_RESIDUAL_RELTOL','0.01')        	    #  
		self.keywordHolder.addKeyword('PRESSURE_ITERATION_TOLERANCE','0.5')        	    #  
		self.keywordHolder.addKeyword('PRE_CONDITIONER_OPTION','REDUCED_SYSTEM_SERIES') 
		self.keywordHolder.addKeyword('SATURATION_CONSTRAINT_TOL','0.001')
		self.keywordHolder.addKeyword('SATURATION_ITERATION_TOL','0.01')
		self.keywordHolder.addKeyword('START_OF_SIMULATION_DATE','None')
		self.keywordHolder.addKeyword('START_OF_PREDICTION','None')
		self.keywordHolder.addKeyword('STOP_SIMULATION','None')
		self.keywordHolder.addKeyword('RESTART_OUTPUT','FREQ   1 MONTH')
		self.keywordHolder.addKeyword('WELL_OUTPUT', 'FREQ 1 MONTH')
		self.keywordHolder.addKeyword('WATER_RESIDUAL_RELTOL','0.01')
		self.aAllowedKeywords = self.keywordHolder.aKeywords.keys()

		self.multipleValueList = {}
		self.multipleValueList['ASCII_WELL_OUTPUT'] = 3
		self.multipleValueList['MATBAL_OUTPUT'] = 3
		self.multipleValueList['MAPS_OUTPUT'] = 3
		self.multipleValueList['MIG_LINE_OUTPUT'] = 3
		self.multipleValueList['WELL_OUTPUT'] = 3
		self.multipleValueList['RESTART_OUTPUT'] = 3
		self.multipleValueList['START_OF_PREDICTION'] = 0
		self.multipleValueList['BOUNDARY_FLUX_OUTPUT'] = 3

		self.collections = {'GROUP': self.ST_IN_GROUP, 'PRODUCER' : self.ST_IN_PRODUCER, 'INJECTOR': self.ST_IN_INJECTOR}

	##################################################################################################
	def handleONEWELL(self,token):
		if token == '/':  						 # Don't terminate the lastWell here 
			self.state = self.ST_IN_WELLS;       # since it may have perforation
			return
		if token == 'DATE': self.createDateObject(token);  return  # for all date at the start
		equalTo = self.scanner.read()
		rhs     = self.scanner.read()
		if equalTo[1] == '=':  
			token = token.upper()
			if token in cWellAllowedKeywords:
				self.lastWell.addKeyword(token,rhs[1])
			else:
				self.addErrorMessage(token,rhs[1])
				

	##################################################################################################
	def handlePERFS(self,token):
		if token == '/': 
			self.lastPerforation.setPerfName()
			self.lastWell.addPerforation(self.lastPerforation)  # Add to last well.
			self.state = self.previousState; return
		equalTo = self.scanner.read()  # if <> '=', cause grief
		rhs     = self.scanner.read()
		if equalTo[1] == '=':  self.lastPerforation.addKeyword(token.upper(),rhs[1])

	##################################################################################################
	def handleWELLS(self,token):
		if token == 'DATE': 
			if token == 'DATE': self.createDateObject(token);  return  # for all date at the start
			#self.handleToken(self.keywordHolder,token)                 # get token into master
			return
		if token == 'ENDWELLS': 
			self.state = self.ST_IN_DATE
			self.lastDate.mergeExistingWells(self.allWellNames.keys())   # July 26, 2005 - Reset running well names list
			return
		if token == '&PERF':    
			name = self.lastWell.getWellName() 
			self.lastWell = self.lastDate.Wells[name]
			self.lastPerforation = cPerfObject(None)
			self.previousState = self.state    #
			self.state = self.ST_PERFS         # You are now in the perforation item
			return
		if token in ['&WELL', '&PSEUDO']:    
			self.state = self.ST_ONEWELL       # It cannot be added till you add the name for the well.
			named   = self.scanner.read()      # Read &Name
			equalTo = self.scanner.read()      # Read = sign
			rhs     = self.scanner.read()      # Read Name of well
			name = string.upper(named[1])
			if name <> 'NAME': 
				print "Error! -> You have defined a well without a Name in ", self.lastDate.getDate()
				return;
			name = string.upper(rhs[1])
			
			######################################################################################
			#
			# Has this well been defined previously?
			#
			# At this point the date may have a well defined from Rates parser. Use it.
			# The addWell function will copy any existing Perforations and/or keywords at
			# this date.
			# The global list of allWellNames is already set per well in the
			######################################################################################
			self.lastWellName = name
			if self.lastDate.Wells.has_key(name):   # Well already exists.
				self.lastWell = self.lastDate.addWell(name,useThisWell=self.lastDate.Wells[name])
			else:
				self.lastWell = self.lastDate.addWell(name) # Create a new one.
				self.allWellNames[name] = self.lastWell                            # Add to global running count
			######################################################################################
			if token == '&PSEUDO': 
				#print "token = ", token, " " , name
				self.lastWell.isPseudo = 1     # Sep 13, 2005
										
	##################################################################################################
	def handlePSEUDOITEM(self,token):
		if token == '/': self.state  = self.previousState; return
		if token == '&PSEUDO': 
			value = self.scanner.read() 		  # Get the name 
			value = self.scanner.read() 		  # Get the =
			value = self.scanner.read() 		  # Get the actual name
			name = value[1]                       # and save it 
			name = name.replace("'",'')
			self.lastPseudoItem = self.lastDate.addPseudo(name)
			self.state = self.ST_PSEUDO_ITEM
			value = self.scanner.read() 		  # Get the next item 
			if value[1] == '/':
				self.state  = self.previousState
				return
			value = self.scanner.produce(value) 		  # Get the actual name
			return
		value = self.scanner.read() 		  # Get the =
		value = self.scanner.read() 		  # Get the value of the token..
		if self.lastPseudoItem <> None:
			self.lastPseudoItem.setKeywordValue(token,value[1])

	##################################################################################################
	def handlePSEUDO(self,token):
		"""
		I am now in the main PSEUDO state, if I get another one, use it as an object.
		"""
		if token == '&PSEUDO': 
			self.handlePSEUDOITEM(token); 
			self.previousState = self.ST_IN_PSEUDO
			return
		if token == 'ENDPSEUDO': self.state = self.ST_IN_DATE

	##################################################################################################
	def handleRIGS(self,token):
		"""
		I am now in the main RIGS state, if I get another one, use it as an object.
		"""
		if token == 'RIGS': 
			self.handleRIGITEM(token); 
			self.previousState = self.ST_IN_RIGS
			return
		if token == 'ENDRIGS': self.state = self.ST_IN_DATE

	#################################################################################################
	#
	#################################################################################################
	def handleRIGITEM(self,token):
		"""
		Handles tokens for RIGS and RIG blocks. 
		Any unknown keywords in the RIG block are ignored. I have to add 
		some means of showing these off to the user. Spelling matters but
		case does not since all input tokens are set to uppercase values. 
		"""
		if token == 'DATE': self.createDateObject(token);  return  # for all date at the start
		if token == 'RIGS': return
		if token == '/': self.state  = self.previousState; return
		if token == '&RIG': 
			self.lastRigItem = self.lastDate.addRig()
			self.state = self.ST_RIG_ITEM
			value = self.scanner.read() 		  # Get the next item 
			if value[1] == '/':
				self.state  = self.previousState
				return
			value = self.scanner.produce(value)   # Get the actual name
			return
		value = self.scanner.read() 		  # Get the =
		value = self.scanner.read() 		  # Get the value of the token..
		# ###################################################
		# TODO:
		# Actually, I only allow certain keywords for rigs. 
		# The unrecognized keywords are ignored.
		# ###################################################
		if self.lastRigItem <> None: 
			token = token.upper()
			if token in cRigAllowedKeywords: 
				self.lastRigItem.setKeywordValue(token,value[1])
			else:
				self.addErrorMessage(token,value[1])

	#################################################################################################
	# The group rules state machine. 
	# state   Actions 
	# 0 Idle
	# 1 waiting for name for new group rule item (usually a group name)
	# 2 waiting for actiontoken 
	#################################################################################################
	def handleGROUPRULES(self,token):
		"""
		This is where I have to process these rules and actions.  I just track em.
		0 Idle
		1 waiting for name for new group rule item (usually a group name)
		2 waiting for actiontoken 
		"""
		#print "Line 325:", token
		if token in ['END_GROUPRULES','ENDGROUPRULES']: 
			self.groupRuleState = 0
			self.state = self.ST_IN_DATE
			return 
		if token == 'GROUPRULES': 
			self.groupRuleState = 1
			return 
		if self.groupRuleState == 1:
			self.lastGroupRule = self.lastDate.addGroupRule(); 
			self.lastGroupRule.setID(token)                     # New group rule name
			self.groupRuleState = 2
			self.groupRuleStack = [] 
			return 
		if self.groupRuleState == 2:
			if token in ['{',';']: 
				self.groupRuleStack.append(token)
				self.groupRuleStack.append('\n')
				p = " ".join(self.groupRuleStack)
				self.lastGroupRule.addLineItem(p)
				self.groupRuleStack = [] 
				return
			if token == '}': 
				self.groupRuleState = 1
				self.groupRuleStack.append('\n')
				self.groupRuleStack.append(token)
				p = " ".join(self.groupRuleStack)
				self.lastGroupRule.addLineItem(p)
				self.groupRuleStack = [] 
				return 
			self.groupRuleStack.append(token)
			return 
		if token == 'END_GROUPRULES': self.state = self.previousState


	def handleGIP(self,token):
		"""
		This is the part of the state machine that handles tokens for GROUP, PRODUCERS, INJECTORS blocks.
		"""
		if token == '{': return 
		if token == '}': 
			self.state = self.ST_IN_CONNECTIONS    # Actually previousState.
			return
		if len(token) > 8: self.addErrorMessage('\nToken %s is longer than 8 characters\n' % token)
		self.lastDate.addToCollection(self.collectionType,self.collectionName,token)



	##################################################################################################
	def handleCONNECTIONS(self,token):
		if token in ['END_CONNECTIONS','ENDCONNECTIONS']: 
			self.state = self.ST_IN_DATE
			return
		ltoken = token.upper()                    # First check if you have a token.
		if ltoken in self.collections.keys():     # Only allow these ... see above
			self.state = self.collections[ltoken] # Get the next state
			value = self.scanner.read() 		  # Get the name of the GROUP,INJECTOR,..
			name = value[1]                       # and save it 
			self.collectionType  = ltoken         # The type to use
			self.collectionName  = name           # The name of the collection
			self.lastDate.addCollection(ltoken,name) # If needed, else use existing
			value = self.scanner.read()             # Read past the curly brace.
			self.collectionOption  = ''             # Reset any options
			if value[1] in ['PSEUDO','ADD', 'DEL']: # If Option is valid
				self.collectionOption  = value[1]   # Save it 
				value = self.scanner.read()   	  # Read past the curly brace.

	##################################################################################################
	def handleIdleState(self,token):
		if token == 'DATE': self.createDateObject(token);  return  # for all date at the start
		self.handleToken(self.keywordHolder,token)                 # get token into master

	##################################################################################################
	def createDateObject(self,token):
		value = self.scanner.read()               # Read the actual token here
		self.state = self.ST_IN_DATE              # Set the state
		self.processDateLine(('DATE',value[1]),source=sourceRECURRENT) # self.lastDate!! 
		#print "DATE:cRecurrentParser:line 386: ", token, self.lastDate.sIdString
		self.lastDate.mergeExistingWells(self.allWellNames.keys())   # July 26, 2005 - Reset running well names list
		#print "Creating ", value[1]
		
	##################################################################################################
	def handleDATE(self,token):
		if token == 'DATE': self.createDateObject(token); return                 # Next date
		if token == 'PSEUDO': self.state = self.ST_IN_PSEUDO; return             # this block
		if token == '&PSEUDO':    # Just in case the user forgets to enter in main state.
			self.previousState = self.state;
			self.state = self.ST_PSEUDO_ITEM; 
			self.handlePSEUDOITEM(token)
			return             # this block
		if token == 'CONNECTIONS': self.state = self.ST_IN_CONNECTIONS; return
		if token == 'WELLS': 
			self.state = self.ST_IN_WELLS; 
			return
		if token == 'GROUPRULES': 
			self.state = self.ST_IN_GROUPRULES; 
			self.handleGROUPRULES(token)
			return
		if token == 'RIGS': 
			self.previousState = self.state;
			self.state = self.ST_RIG_ITEM; 
			self.handleRIGS(token)
			return             # this block
		#print "handling", token
		self.handleToken(self.lastDate,token)                    # On a per date basis.

	##################################################################################################
	def handleToken(self,where,token):                               # If date object has keywords
		if not token in self.aAllowedKeywords: 
			return
		if token in ['BINARY_ARRAY_OUTPUT','TEXT_ARRAY_OUTPUT']: 
			value = self.scanner.read()           # Read the filename 
			xstr = value[1].replave("""'""", '')  #
			where.setKeywordValue(token,xstr)     # 

			value = self.scanner.read()           # Read the filename 
			if value[1] <> '{':
				self.scanner.produce(value)   # Push it back for future
				return
				
			value = self.scanner.read()           # Read the new name 
			while value[1] <> '}':
				equal = self.scanner.read()            # Read the equal sign
				if equal[1] == '}':
					xstr = token + " assign " + value[1] + "=" + value2[1]
					return 
				value2 = self.scanner.read()           # Read the old name
				xstr = token + " assign " + value[1] + "=" + value2[1]
				where.addContentLine(xstr)
				value = self.scanner.read()           # Read the filename 
			return

		if token in self.multipleValueList.keys():
			value = self.scanner.read()               # Read the actual token here
			if value[1] == 'FREQ':
				xstr = 'FREQ '
				value = self.scanner.read() 
				xstr = xstr + value[1] + ' '
				value = self.scanner.read() 
				xstr = xstr + value[1] + ' '
				where.setKeywordValue(token,xstr)
				return	
			f = value[1].find("""'""")                    # Is this a file 
			if f == 0:
				where.setKeywordValue(token,xstr)
				return
			where.setKeywordValue(token,' ')
			self.scanner.produce(value)   # Push it back for future
			return
		else:
			value = self.scanner.read() 
			where.setKeywordValue(token,value[1])
			
	##################################################################################################
	def readFile(self, filename):
		qf = cRecurrentFlattener()
		flatfile = os.getenv('HOME') + os.sep + 'flattened.txt'    # HOME will change to PPARSER?
		qf.flattenRecurrentFile(filename,flatfile)
		self.filename = flatfile
		try:
			self.fd = open(flatfile,'r')
		except:
			return
		self.scanner = Scanner(self.lexicon, self.fd)
		self.state = 0
		self.group = None
		self.lastDate = "Start"
		if self.userDates == None: 
			self.allDates = {}
		else:
			self.allDates = self.userDates
		self.currentObject = self
		self.allInGroup = 1

		while 1: 
			tokens = self.scanner.read(); 
			if tokens[0] == None: break
			token = tokens[1].upper()
			if self.state == self.ST_IDLE: 
				self.handleIdleState(token)
				continue
			if self.state == self.ST_IN_DATE:
				self.previousState= self.state          # 
				self.handleDATE(token)
				continue
			if self.state == self.ST_PSEUDO_ITEM:  self.handlePSEUDOITEM(token); continue
			if self.state == self.ST_IN_RIGS:  self.handleRIGS(token); continue
			if self.state == self.ST_RIG_ITEM:  self.handleRIGITEM(token); continue
			if self.state == self.ST_IN_PSEUDO:  self.handlePSEUDO(token); continue
			if self.state == self.ST_IN_GROUPRULES:  self.handleGROUPRULES(token); continue
			if self.state == self.ST_IN_WELLS:  self.handleWELLS(token); continue
			if self.state == self.ST_ONEWELL:  self.handleONEWELL(token); continue
			if self.state == self.ST_PERFS:  self.handlePERFS(token); continue

			if self.state == self.ST_IN_CONNECTIONS:  self.handleCONNECTIONS(token); continue
			if self.state == self.ST_IN_GROUP:     self.handleGIP(token); continue
			if self.state == self.ST_IN_PRODUCER:  self.handleGIP(token); continue
			if self.state == self.ST_IN_INJECTOR:  self.handleGIP(token); continue


	##################################################################################################
	def PrintGroupTree(self,dte,name,depth):
		if not dte.Groups.has_key(name): return
		depth = depth + 1
		children = dte.Groups[name]
		for child in children:
			print "---" * depth, child
			self.PrintGroupTree(dte,child,depth)

	##################################################################################################
	def PrintProducerTree(self,dte,name,depth):
		if not dte.Producers.has_key(name): return
		depth = depth + 1
		children = dte.Producers[name]
		for child in children:
			print "---" * depth, child
			self.PrintProducerTree(dte,child,depth)

	##################################################################################################
	def PrintInjectorTree(self,dte,name,depth):
		if not dte.Injectors.has_key(name): return
		depth = depth + 1
		children = dte.Injectors[name]
		for child in children:
			print "---" * depth, child
			self.PrintInjectorTree(dte,child,depth)

	##################################################################################################
	def printDates(self):
		s = self.keywordHolder.aKeywords.keys()
		s.sort()
		#for k in s: print k," = ", self.keywordHolder.aKeywords[k]
		skeys = self.allDates.keys()
		skeys.sort()
		for sk in skeys:
			dte = self.allDates[sk]
			print "DATE:", dte.getDate()
			#for k in dte.aKeywords.keys(): print "\t\t", k, dte.aKeywords[k]
			for k in dte.Wells.keys():
				w = dte.Wells[k]
				nm = w.getWellName(); 
				if nm in ['BRRI0310','BRRI0106']:
					print "\t", w.getWellName(), " has " , len(w.perforations.keys()), " perforations"
					for k in w.aKeywords.keys():
						print "\t\t", k, w.aKeywords[k]

	##################################################################################################
	def printXMLoutput(self,fd=sys.stdout):
		#
		# Sort the keys 
		#
		v = pObject()
		retstr = pObject.getXMLpreamble(v,"RECURRENT", xslsheet='/peasd/ssd/husainkb/template/recurrent.xsl')

		skeys = self.allDates.keys()
		skeys.sort()
		for sk in skeys:
			dte = self.allDates[sk]
			dte.setParentage()
			retstr += '<DATE value="%s">\n' %  dte.getDate()
			retstr += dte.getXMLcontent()

			for ck in dte.pseudoItems.keys():
				pseudo = dte.pseudoItems[ck]
				retstr += '<PSEUDO name="%s">\n' % (ck)    # Start GROUP node
				retstr += pseudo.getXMLcontent()
				retstr += '</PSEUDO>\n'

			for ck in dte.Wells.keys():
				w = dte.Wells[ck]
				nm = w.getWellName(); 
				retstr += '<WELL name="%s">\n' % (nm)    # Start GROUP node
				retstr += w.getXMLcontent()
				retstr += '</WELL>\n'

			#
			# First get the groups in this date.
			#
			grpNames   = dte.getCollectionNames('GROUP')
			injNames   = dte.getCollectionNames('INJECTOR')
			proNames   = dte.getCollectionNames('PRODUCER')
			groups = dte.collections['GROUP']
			for ck in groups.keys():
				pname = dte.parentage.get(ck,'')
				retstr += '<GROUP name="%s" parent="%s">\n' % (ck,pname)    # Start GROUP node
				items = groups[ck]
				for k in items:                        # For each item in the list of sub
					if k in grpNames:           # If item is a group, mark it such.
						retstr += '<item type="GROUP" name="%s"/>\n' % (k)
					elif k in injNames:           # If item is a group, mark it such.
						retstr += '<item type="INJECTOR" name="%s"/>\n' % (k)
					elif k in proNames:           # If item is a group, mark it such.
						retstr += '<item type="PRODUCER" name="%s"/>\n' % (k)
				retstr += '</GROUP>\n'


			for subName in dte.collections.keys():
				if subName == 'GROUP': continue         # Since you have done that above.
				inj = dte.collections[subName]          # Get the list of injectors
				for ck in inj.keys():
					pname = dte.parentage.get(ck,'')
					retstr += '<%s name="%s" parent="%s">\n' % (subName,ck,pname)    # Start GROUP node
					items = inj[ck]
					for k in items:             # For each item in the list of sub
						pname = dte.parentage.get(k,'')
						retstr += '<WELL parent="%s" name="%s"/>\n' % (pname,k)
					retstr += '</%s>\n' % subName


			retstr += "</DATE>\n" 
		retstr += pObject.getXMLpostamble(v,"RECURRENT")
		fd.write(retstr);


	def printDiagnostics(self):
		k =  self.allDates.keys();
		k.sort()
		print  k


if __name__ == '__main__':
	qq = cRecurrentFile(None)
	qq.readFile(sys.argv[1])
	#qq.printDates()
	qq.printDiagnostics()
	#qq.printXMLoutput()

