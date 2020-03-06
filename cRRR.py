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


#####################################################################################
# Start of class description
#####################################################################################
class cRecurrentFlattener(cParserObject):
	def __init__(self):
		cParserObject.__init__(self)

	################################################################
	def flattenRecurrentFile(self,filename,outfilename):
		self.verbose = 1
		self.readIncludedFiles(filename)
		#fd = open(outfilename,'w')
		#for oln in self.inputLines: 
			#if oln.mustProcess == 0: continue
			#fd.write(oln.getRawLine())
		#fd.close()

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
		self.collectionType  = ''
		self.collectionName   = '' 
		self.collectionOption = '' 


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

		self.collections = {'GROUP': self.ST_IN_GROUP, 'PRODUCER' : self.ST_IN_PRODUCER, 'INJECTOR': self.ST_IN_INJECTOR}

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
		"""
		# This is where I have to process these rules and actions. 
		"""
		if token == 'END_GROUPRULES': self.state = self.previousState

	def handleGIP(self,token):
		"""
		This is the part of the state machine that handles tokens for GROUP, PRODUCERS, INJECTORS blocks.
		"""
		if token == '{': return 
		if token == '}': 
			self.state = self.ST_IN_CONNECTIONS    # Actually previousState.
			return

		#
		# Based on the collectionOption, perform your action here.
		#
		self.lastDate.addToCollection(self.collectionType,self.collectionName,token)

	##################################################################################################
	def handleCONNECTIONS(self,token):
		if token == 'END_CONNECTIONS': self.state = self.ST_IN_DATE
		ltoken = token.upper()                    # First check if you have a token.
		if ltoken in self.collections.keys():     # Only allow these ... see above
			self.state = self.collections[ltoken] # Get the next state
			value = self.scanner.read() 		  # Get the name of the collection
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
		self.processDateLine(('DATE',value[1]))   # self.lastDate = is set or created here.
		
	##################################################################################################
	def handleDATE(self,token):
		if token == 'DATE': self.createDateObject(token); return                 # Next date
		if token == 'PSEUDO': self.state = self.ST_IN_PSEUDO; return             # this block
		if token == 'CONNECTIONS': self.state = self.ST_IN_CONNECTIONS; return
		if token == 'WELLS': self.state = self.ST_IN_WELLS; return
		if token == 'GROUPRULES': self.state = self.ST_IN_GROUPRULES; return
		self.handleToken(self.lastDate,token)

	##################################################################################################
	def handleToken(self,where,token):                               # If date object has keywords
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
		qf = cRecurrentFlattener()
		flatfile = os.getenv('HOME') + os.sep + 'flattened.txt'    # HOME will change to PPARSER?
		qf.flattenRecurrentFile(filename,flatfile)
		return
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
	def printConnections(self,fd=sys.stdout):
		#
		# Sort the keys 
		#
		v = pObject()
		retstr = pObject.getXMLpreamble(v,"RECURRENT", xslsheet='/peasd/ssd/husainkb/template/recurrent.xsl')

		skeys = self.allDates.keys()
		skeys.sort()
		for sk in skeys:
			dte = self.allDates[sk]
			retstr += '<DATE value="%s">\n' %  dte.getDate()
			retstr += dte.getXMLcontent()
			for collectionType in dte.collections.keys():
				retstr += '<COLLECTION type="%s" >\n' % collectionType
				collection = dte.collections[collectionType]
				for ck in collection.keys():
					retstr += '<%s name="%s">\n' % (collectionType,ck)
					items = collection[ck]
					items.sort()
					for item in items: 
						retstr += '<item type="%s" name="%s"/>\n' % (collectionType,item)
					retstr += '</%s>\n' % collectionType
				retstr += '</COLLECTION>\n'
			retstr += "</DATE>\n" 

		retstr += pObject.getXMLpostamble(v,"RECURRENT")
		fd.write(retstr);

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
	#qq.printDates()
	qq.printConnections()

