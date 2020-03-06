"""
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


##################################################################################################
# The grammar for handling the keywords in the RECURRENT FILES
##################################################################################################
period = Str(".")
letter = Range('AZaz') | Any("_") | Any("-") | Any('&') | period | Any('?')
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
space = Any(" ;\t\n,")
##################################################################################################
# 
##################################################################################################
class cRecurrentFile(cParserObject):	
	def __init__(self, useTheseDates = None):
		cParserObject.__init__(self)
		self.filename = None
		self.fd = None
		self.resword = Str("group","injector","producer")
		self.keywords = {}
		##################################### LEX ######################################
		self.lexicon = Lexicon([ (name, 'ident'),
			(number, 'number'),
			(math,  TEXT), 
			(eob,  TEXT), 
			(self.resword, 'Kamran'),
			(closebrace, TEXT),
			(openbrace, TEXT),
			(closelist, TEXT),
			(openlist, TEXT),
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

		self.lastWell = None
		self.lastDate = None
		self.state = self.ST_IDLE
		self.previousState = self.state
		self.lastToken = '' 


		self.userDates  = {}                      # Always do this.
		self.allDates   = {}                      #
		if useTheseDates <> None:
			self.allDates   = useTheseDates
			self.userDates  = useTheseDates
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
		self.keywordHolder.addKeyword('MATBAL_OUTPUT','FREQ 1 MONTH')
		self.keywordHolder.addKeyword('MATRIX_SCALE_OPTION','TRUE',('TRUE','FALSE'))
		self.keywordHolder.addKeyword('MAX_MGRID_ITERATIONS','0.1')        	    #  
		self.keywordHolder.addKeyword('MIN_PORE_VOL_TIMESTEP','700.0')     	#
		self.keywordHolder.addKeyword('NON_LINEAR_MAXIMUM_ITERATIONS','6')        	    #  
		self.keywordHolder.addKeyword('NON_LINEAR_MINIMUM_ITERATIONS','5')        	    #  
		self.keywordHolder.addKeyword('NON_LINEAR_TOLERANCE','.0001')        	    #  
		self.keywordHolder.addKeyword('NUM_OF_ORTHOGONAL_DIRECTIONS','10')        	    #  
		self.keywordHolder.addKeyword('OIL_RESIDUAL_RELTOL','1.E-2')        	    #  
		self.keywordHolder.addKeyword('PRE_CONDITIONER_OPTION','RED_BLACK_Z_LINE') 
		self.keywordHolder.addKeyword('START_OF_SIMULATION_DATE','None')
		self.keywordHolder.addKeyword('RESTART_OUTPUT','FREQ   1 MONTH')
		self.keywordHolder.addKeyword('WELL_OUTPUT', 'FREQ 1 MONTH')
		self.keywordHolder.addKeyword('WATER_RESIDUAL_RELTOL','1.E-2')
		self.aAllowedKeywords = self.keywordHolder.aKeywords.keys()

		self.multipleValueList = {}
		self.multipleValueList['MAPS_OUTPUT'] = 3
		self.multipleValueList['MATBAL_OUTPUT'] = 3
		self.multipleValueList['RESTART_OUTPUT'] = 3
		self.multipleValueList['START_OF_PREDICTION'] = 0

	##################################################################################################
	def handleONEWELL(self,token):
		if token == '/':  						 # Don't terminate the lastWell here 
			self.state = self.ST_IN_WELLS;       # since it may have perforation
			return
		equalTo = self.scanner.read()
		rhs     = self.scanner.read()
		if equalTo[1] == '=':  
			self.lastWell.addKeyword(string.upper(token),rhs[1])

	##################################################################################################
	def handlePERFS(self,token):
		if token == '/': self.state = self.ST_IN_WELLS; return
		equalTo = self.scanner.read()
		rhs     = self.scanner.read()
		if equalTo[1] == '=':  self.lastPerforation.addKeyword(token,rhs[1])

	##################################################################################################
	def handleWELLS(self,token):
		if token == 'ENDWELLS': self.state = self.ST_IN_DATE
		if token == '&PERF':    
			self.lastWell = self.lastDate.Wells[self.lastWell.getWellName()]  # Explicitly get the well by name
			id = self.lastWell.getNextPerfId()                                # Use the last well
			self.lastPerforation = cPerfObject(0,str(id))            # Create an object
			self.lastWell.perforations.append(self.lastPerforation)  # Add to last well.
			self.state = self.ST_PERFS         # You are now in the perforation item
		if token == '&WELL':    
			self.lastWell = cWellObject()      # Create a new well object.
			self.state = self.ST_ONEWELL       # It cannot be added till you add the name for the well.
			named   = self.scanner.read()      # Read &Name
			equalTo = self.scanner.read()      # Read = sign
			rhs     = self.scanner.read()      # Read Name of well
			name = string.upper(named[1])
			if name <> 'NAME': 
				print "Error! -> You have defined a well without a Name in ", self.lastDate.getDate()
				return;
			self.lastWell.addKeyword('NAME',rhs[1])       # Explicitly force the name
			self.lastDate.addWell(rhs[1], self.lastWell)  # Explicitly add the object to dates
										
	##################################################################################################
	def handlePSEUDO(self,token):
		if token == 'ENDPSEUDO': self.state = self.previousState
		# Ignore all keywords in this

	##################################################################################################
	def handleGROUPRULES(self,token):
		# This is where I have to process these rules and actions. 
		if token == 'END_GROUPRULES': self.state = self.previousState

	##################################################################################################
	def handleGROUP(self,token):
		if token == '}': 
			self.state = self.ST_IN_CONNECTIONS
			return
		group = self.lastDate.Groups[self.groupName]
		self.lastDate.Groups[token] = []
		group.append(token)

	##################################################################################################
	def handlePRODUCER(self,token):
		if token == '}': 
			self.state = self.ST_IN_CONNECTIONS
			return
		group = self.lastDate.Producers[self.producerName]
		group.append(token)

	##################################################################################################
	def handleINJECTOR(self,token):
		if token == '}': 
			self.state = self.ST_IN_CONNECTIONS
			return
		group = self.lastDate.Injectors[self.injectorName]
		group.append(token)

	##################################################################################################
	def handleCONNECTIONS(self,token):
		if token == 'END_CONNECTIONS': self.state = self.ST_IN_DATE
		if self.allInGroup == 1: 
			check = 0
			if token in [ 'group', 'producer', 'injector' ] : check = 1
		else:
			check = 0 
			if token == 'group': check = 1
		if check == 1:
			self.state = self.ST_IN_GROUP
			value = self.scanner.read()
			name = value[1]
			self.groupName  = name
			if not self.lastDate.Groups.has_key(name): 
				if not name in self.lastDate.Groups.keys(): self.lastDate.GroupRoot.append(name)
				self.lastDate.Groups[name] = []
			value = self.scanner.read()   # Read past the curly brace.
			if value[1] == 'PSEUDO': value = self.scanner.read()   # Read past the curly brace.
			return
		if token == 'injector': 
			self.state = self.ST_IN_INJECTOR
			value = self.scanner.read()
			name = value[1]
			self.injectorName  = name
			if not self.lastDate.Injectors.has_key(name): 
				if not name in self.lastDate.Injectors.keys(): self.lastDate.InjectorRoot.append(name)
				self.lastDate.Injectors[name] = []
			value = self.scanner.read()   # Read past the curly brace.
			if value[1] == 'PSEUDO': value = self.scanner.read()   # Read past the curly brace.
			return
		if token == 'producer': 
			self.state = self.ST_IN_PRODUCER
			value = self.scanner.read()
			name = value[1]
			self.producerName  = name
			if not self.lastDate.Producers.has_key(name): 
				if not name in self.lastDate.Producers.keys(): self.lastDate.ProducerRoot.append(name)
				self.lastDate.Producers[name] = []
			value = self.scanner.read()   # Read past the curly brace.
			if value[1] == 'PSEUDO': value = self.scanner.read()   # Read past the curly brace.
			return

	##################################################################################################
	def handleIdleState(self,token):
		if token == 'DATE': 
			self.createDateObject(token)
			return
		self.handleToken(self.keywordHolder,token)                 # get token into master

	##################################################################################################
	def createDateObject(self,token):
		value = self.scanner.read()               # Read the actual token here
		self.state = self.ST_IN_DATE              # Set the state
		self.processDateLine(('DATE',value[1]))   # self.lastDate is set or created here.
		
	##################################################################################################
	def handleDATE(self,token):
		if token == 'DATE': 
			self.createDateObject(token)
			return
		if token == 'PSEUDO': self.state = self.ST_IN_PSEUDO; return
		if token == 'CONNECTIONS': self.state = self.ST_IN_CONNECTIONS; return
		if token == 'WELLS': self.state = self.ST_IN_WELLS; return
		if token == 'GROUPRULES': self.state = self.ST_IN_GROUPRULES; return
		self.handleToken(self.lastDate,token)

	##################################################################################################
	def handleToken(self,where,token):                                    # If date object has keywords
		if token in self.aAllowedKeywords:
			if token in self.multipleValueList.keys():
				r = self.multipleValueList[token]
				if r == 0: 
					where.setKeywordValue(token,' ')
					return
				xstr = []
				for k in range(r):
					value = self.scanner.read() 
					xstr.append(value[1])
				where.setKeywordValue(token,string.join(xstr,' '))
			else:
				value = self.scanner.read() 
				where.setKeywordValue(token,value[1])
			return
			
	##################################################################################################
	def readFile(self, filename):
		self.filename = filename
		try:
			self.fd = open(filename,'r')
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
			token = tokens[1]	
			if self.state == self.ST_IDLE: 
				self.handleIdleState(token)
				continue
			if self.state == self.ST_IN_DATE:
				self.previousState= self.state          # 
				self.handleDATE(token)
				continue
			if self.state == self.ST_IN_PSEUDO:  self.handlePSEUDO(token); continue
			if self.state == self.ST_IN_GROUPRULES:  self.handleGROUPRULES(token); continue
			if self.state == self.ST_IN_CONNECTIONS:  self.handleCONNECTIONS(token); continue
			if self.state == self.ST_IN_WELLS:  self.handleWELLS(token); continue
			if self.state == self.ST_ONEWELL:  self.handleONEWELL(token); continue
			if self.state == self.ST_PERFS:  self.handlePERFS(token); continue
			if self.allInGroup == 1:
				if self.state in [  self.ST_IN_GROUP, self.ST_IN_PRODUCER, self.ST_IN_GROUP ]:
						  self.handleGROUP(token); continue
			else: 
				if self.state == self.ST_IN_GROUP:  self.handleGROUP(token); continue
				if self.state == self.ST_IN_PRODUCER:  self.handlePRODUCER(token); continue
				if self.state == self.ST_IN_INJECTOR:  self.handleINJECTOR(token); continue


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
	def printConnections(self):
		#
		# Sort the keys 
		#
		skeys = self.allDates.keys()
		skeys.sort()
		for sk in skeys:
			dte = self.allDates[sk]
			print "Date:", dte.getDate()
			if len(dte.Groups.keys()) > 0: 
				#print "Group Count = ", len(dte.Groups.keys())
				#print "Producer Count = ", len(dte.Producers.keys())
				#print "Injector Count = ", len(dte.Injectors.keys())
				depth = 0
				for name in dte.GroupRoot:
					print name
					self.PrintGroupTree(dte,name,depth)
				depth = 0
				for name in dte.ProducerRoot:
					print "Producer:", name
					self.PrintProducerTree(dte,name,depth)
				depth = 0
				for name in dte.InjectorRoot:
					print "Injector:", name
					self.PrintInjectorTree(dte,name,depth)

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
					print "\t", w.getWellName(), " has " , len(w.perforations), " perforations"
					for k in w.aKeywords.keys():
						print "\t\t", k, w.aKeywords[k]

	def printDiagnostics(self):
		k =  self.allDates.keys();
		k.sort()
		print  k
		
if __name__ == '__main__':
	qq = cRecurrentFile(None)
	qq.readFile(sys.argv[1])
	qq.printDates()
	#qq.printConnections()

