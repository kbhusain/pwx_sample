"""
 This is the base class for all the objects in the system.
 
 June 21, 2002 - Added verbose flag . 
 Sep  08, 2003 - Added several objects
 	cPerfObject
	cWellObject
	cPseudoObject
	cDateObject

 Mar 19, 2005 - Added cParserObject.

 May 14, 2005 - Added pLineObject for tracking incoming lines.
 
Author: Kamran Husain  PEASD/SSD
"""
import sys, os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import escape
import copy
from string import strip,find,split,join,replace,lower,digits
from time import *
from pPBFutils  import *

sourceRATES     = 0
sourcePERFS     = 1
sourceRECURRENT = 2
monthnames=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

def deriveWorkpaths(filename):
	workpath = os.path.dirname(filename)                 # Get the working path.
	projectpath = workpath 	                             # set it as the original path.
	f = workpath.rfind('/data')                          # Remove the trailing /data
	if f >= 0 : projectpath = workpath[:f]               # from the project path 
	return workpath,projectpath

def deriveIncludePath(incoming,workpath,projectpath): 
	verbose = 0
	if verbose == 1: 
		print "Work Path = ", workpath
		print "Proj Path = ", projectpath
	incpath = replace(incoming,'"','') 
	incpath = replace(incpath,"""'""",'') 
	incpathWork = incpath
	incpathProj = incpath
	done = 0
	if incpath[0] <> '/':                    # absolute path.
		incpathProj = projectpath + os.sep + incpath
		incpathWork = workpath + os.sep +  incpath
		if verbose == 1: 
			print "Work file ", incpathWork 
			print "Proj file", incpathProj 
	ableToOpen = 0
	try: 
		incpath = incpathProj
		fdi = open(incpath,'r')
		ableToOpen = 1
	except: 
		incpath = None
		ableToOpen = 0
	if ableToOpen == 0:
		try: 
			incpath = incpathWork
			fdi = open(incpath,'r')
			ableToOpen = 1
			fdi.close()
		except: 
			ableToOpen = 0
			incpath = None
	if verbose == 1:  "---> Returning "  , incpath, " from ", incoming
	return incpath			


#####################################################################################
# !!!PLATFORM SPECIFIC INITIALIZATION HERE!!!!
# The object must remember from a global value
#####################################################################################

floatingDigits = digits + '.' 
globalxmltemplatedir = '/peasd/ssd/husainkb/template'
def setPlatformSpecificPaths():
	try:
		globalxmltemplatedir = os.getenv('PEXL')
	except:
		if os.name == 'nt':
			globalxmltemplatedir = 'D:\powers\templates'
		else:
			globalxmltemplatedir = '/peasd/ssd/husainkb/template'

	
#####################################################################################
class pLineObject:
	"""
	The core object for the incoming lines.  Keeps a copy of the incoming line.
	Also keeps an id for the file being read. This can prove to be very costly, 
	so I used an integer.
	"""
	def __init__(self,incoming=None,filename='',linenumber=0):
		self.setLine(incoming,filename,linenumber)
	
	def setLine(self,incoming,filename='',linenumber=0,keepcopy=1):
		self.fileId       = 0                   # The id of the file being included
		self.sFileName    = filename            # The id of the file being included
		self.iLineNumber  = linenumber          # The linenumber in the file being included
		if keepcopy == 1:
			self.rawItem      = copy.copy(incoming)      # ALWAYS KEEP A COPY - not a reference. 
		else:
			self.rawItem      = incoming
		self.isTerminator = 0                   # Not a terminator by default
		self.hasErrors    = 0 					# Set by external reader 
		self.isComment    = 0                   # Not a comment by default
		self.mustProcess  = 0                   # No need to process unless you have to
		self.cookedItem   = ''
		self.splitcookedItems = []
		if self.rawItem == None: return 
		if len(self.rawItem) < 1: return 
		self.cookedItem = strip(self.rawItem)   #  Remove trailing and leading spaces
		f = find(self.cookedItem,'!')           #  Find the comment starter if any
		if f >= 0: 
			self.isComment  = 1                             # It has a comment part
			self.cookedItem = self.cookedItem[0:f]          # Remove from comment out
			self.cookedItem = strip(self.cookedItem)        # Remove trailing again
		f = find(self.cookedItem,'#')           #  Find the comment starter if any
		if f >= 0: 
			self.isComment  = 1                             # It has a comment part
			self.cookedItem = self.cookedItem[0:f]          # Remove from comment out
			self.cookedItem = strip(self.cookedItem)        # Remove trailing again
		f = find(self.cookedItem,'/')                       # Find FORTRAN comment starter
		if f == 0:                                          # Remove from comment out ONLY if first char.
			self.cookedItem = self.cookedItem[0:f+1]        # Blank line may not be returned
			self.terminator = 1                             # Only for doubly used characters 
			self.isComment  = 0                             # Special case, it's not a comment
			self.cookedItem = strip(self.cookedItem)        # Remove trailing and leading
		if len(self.cookedItem) > 0: 
			self.mustProcess = 1   # Must have at least one char to process
			self.splitcookedItems = split(self.cookedItem)
	
	def getRawLine(self):
		return self.rawItem

	def getCookedLine(self):
		return self.cookedItem

	def getLineNumber(self):
		return self.iLineNumber

	def getFileName(self):
		return self.sFileName

	def getItems(self):
		return self.splitcookedItems

	def markAsErred(self):	
		self.hasErrors = 1
		
	def markAsClean(self):	
		self.hasErrors = 0
	
	def __repr__(self):
		return self.cookedItem


#####################################################################################
# Used for Perforations and well objects 
#####################################################################################
class pTrimObject: 
	def __init__(self, iLineObject=None,startOfBlock='',endOfBlock=''):
		self.sIdString = 'GenericObjectBlock'
		self.aKeywords  = {}
		self.aOptions   = {}
		self.aLabels     = {}     # indexed by label
		self.aKeyToLabel = {}     # indexed by key
		self.bVerbose	= 0		  #  if set to 1, even unused values will be printed.
		self.iLineObject = iLineObject
		self.sQuotedKeywords   = ['INCLUDE_FILE','BINARY_FILE'] 
		if self.iLineObject <> None: 
			self.iLineNumber  = self.iLineObject.getLineNumber()  # when created,
		else: 
			self.iLineNumber  = 0
		self.xmltemplatedir = globalxmltemplatedir;
		self.sStartOfBlock = startOfBlock
		self.sEndOfBlock   = endOfBlock

	#####################################################################################
	def setID(self,id):
		self.sIdString = id 
	
	#####################################################################################
	def clearKeywords(self):
		self.aKeywords = {}

	#####################################################################################
	def getLineNumber(self):
		return self.iLineNumber

	#####################################################################################
	def setDelimiters(self,sStart,sEnd):
		self.sStartOfBlock = sStart
		self.sEndOfBlock   = sEnd

	#####################################################################################
	def setVerbosity(self,i):
		self.bVerbose = i

	def getRecommendedWidth(self,name):
		if name in self.sQuotedKeywords: return 60
		return 20
 
	def getXMLcontent(self,name='IGNORED',pathname='.'):
		return "</NONE>"

	########################################################
	# Remove the quote FIRST, then add to INCLUDE or BINARY 
	# lists. The quotes will be added on retrieval.
	########################################################
	def addKeyword(self,keyword,value=None,options=[],label=None):
		"""
			Remove the quote FIRST, then add to INCLUDE or BINARY 
			lists. Input quotes are the callers responsibility.

			The value is the default value.  If NONE it is returned
			as a blank string.

			options if not empty force the list of answers. 
		"""
		if keyword in self.sQuotedKeywords:
			if value <> None: 
				value = value.replace("""'""",'')  # remove single quotes
				value = value.replace('"','')      # remove double quotes
		if keyword == 'INCLUDE_FILE':
			if not value in self.sIncludeFilenames:	 # Don't allow duplicates. 
				self.sIncludeFilenames.append(value)
		if keyword == 'BINARY_FILE':					# Don't allow duplicates. 
			if not value in self.sBinaryFilenames:
				self.sBinaryFilenames.append(value)
		self.aKeywords[keyword] = value  # Add the line here for output back. 
		if len(options) > 1: 
			self.aOptions[keyword] = options
		if label <> None: 
			self.aLabels[label] = keyword 
			self.aKeyToLabel[keyword] = label

	def getKeywordLabel(self,key):
		v = self.aKeyToLabel.get(key,None)
		if v == None: return key
		return v

	def setKeywordValue(self,key,value):
		"""
		Allows the user to set the values and us to massage the values.
		I ck if the 'key' passed is a label, then if not a label, i use
		it literally as a key.
		"""
		v = self.aLabels.get(key,None)      
		if v <> None:  key = v
		if key in self.sQuotedKeywords:
			if value <> None: 
				value = value.replace("""'""",'')  # remove single quotes
				value = value.replace('"','')      # remove double quotes
		self.aKeywords[key] = value

	########################################################
	# Special case for handling INCLUDE_FILE and BINARY_FILE
	########################################################
	def getKeywordValue(self,key):
		"""
		I don't return quotes to the interface. The output has to handle it.
		"""
		kv = self.aLabels.get(key,None)
		if kv <> None: 
			value = self.aKeywords[kv];
			if value == None: return '' 
			if key == 'INCLUDE_FILE': value = self.getNextIncludeFile() 
			if key == 'BINARY_FILE':  value = self.getNextBinaryFile() 
			return value
		elif (self.aKeywords.has_key(key)):
			value = self.aKeywords[key];
			if value == None: return '' 
			if key == 'INCLUDE_FILE': value = self.getNextIncludeFile() 
			if key == 'BINARY_FILE':  value = self.getNextBinaryFile() 
			return value
		else:
			return ''

	########################################################
	#
	########################################################
	def getKeywords(self):
		return  self.aKeywords.keys()


#####################################################################################
# This is used in the case of normal block
#####################################################################################
class pObject(pTrimObject):
	def __init__(self,iLineObject=None,startOfBlock='',endOfBlock=''):
		pTrimObject.__init__(self,iLineObject,startOfBlock,endOfBlock)
		self.bFlushToDisk = 0
		self.aLineContents = []
		self.aErrorMessages = []
		self.aComments = []
		self.aWarningMessages = []

		self.sIncludeFilenames = []
		self.xmlIncludes = {}     # for included XML, XSL files
		self.indexIncludeFile = 0
		self.lastIncludedFile = ''
		self.sBinaryFilenames = []

		self.indexBinaryFile  = 0
		self.treeNode = None
		self.lastLineNumber = self.iLineNumber 

	#####################################################################################
	def clearContents(self):
		"""
		Removes any lines that have data in them ... Very cautiously used function
		You should override this in your defined object. 
		"""
		for i in self.aLineContents:
			if ilo.mustProcess == 0: continue   # Ignore the comments 
			items = ilo.getItems()
			keyword = items[0]      
			if (keyword in self.aAllowedKeywords):
				self.aLineContents.remove(ilo)
				continue

	#####################################################################################
	def addContentLine(self,incoming):
		self.aLineContents.append(incoming) # Add the line here for output back. 

	#####################################################################################
	def addErrorMessage(self,outstr,ilo=None):
		errstr = "Error:" + outstr  
		if ilo <> None:
			errstr += '\nFile %s, Line %d' % (ilo.getFileName(), ilo.getLineNumber()) +  ' ' +  ilo.getRawLine()
		self.aErrorMessages.append(errstr) # Add the line here for output back. 

	#####################################################################################
	def addWarningMessage(self,incoming,ilo=None):
		errstr = "Warning:" + incoming  
		if ilo <> None:
			errstr += 'File %s, Line %d' % (ilo.getFileName(), ilo.getLineNumber()) +  ' ' +  ilo.getRawLine()
		self.aWarningMessages.append(errstr) # Add the line here for output back. 

	#####################################################################################
	def getErrorCount(self):
		return len(self.aErrorMessages)

	#####################################################################################
	def getWarningCount(self):
		return len(self.aWarningMessages)


	#####################################################################################
	def addComments(self,incoming):
		for i in incoming: self.aComments.append(i)

	#####################################################################################
	def setFlushToDisk(self,i):
		self.bFlushToDisk = i

	#####################################################################################
	def clearErrors(self):
		self.aWarningMessages = []
		self.aErrorMessages   = []

	#####################################################################################
	def parseLine(self,incoming,addIt=1):
		"""
		This is used to track all input lines in between an object.
	    The incoming has changed from a string to a pLineObject
		"""
		if (addIt == 1):       self.aLineContents.append(incoming) # Add the line here for output back. 
		if (incoming  == ''):	 # This is a comment line. ignore.
			return -1; 
		#print 'pObject:Incoming = ',incoming[0:15]
		if (incoming[0] == '#'):	 # This is a comment line. ignore.
			return -1; 
		elif incoming[0] == '@INCLUDE_BEGIN':
			self.lastIncludedFile = incoming[1] 
			return -1
		elif incoming[0] == '@INCLUDE_END':
			self.lastIncludedFile = ''
			return -1
		return 1;  # Okay it looks like something the derived class can use.

	def getNonCommentLines(self):
		"""
		Return only those lines that have non commented lines back to the 
		parser for the user interface or the syntax checker.
		"""
		self.ret = []
		for ln in self.aLineContents:
			  if (len(ln) < 1):   continue
			  if (ln[0] == '#'):  continue
			  self.ret.append(self.i)
		return self.ret

	def getCommentLines(self):
		rret = []
		for ln in self.aLineContents:
			  if (len(ln) < 1): continue
			  if (ln[0] == '#'): self.ret.append(ln)
		return rret

	def getOneLiner(self):
		xkeys = self.aKeywords.keys()
		xkeys.sort();
		xlist = []
		for x in xkeys: xlist.append(' x=%s' % self.aKeywords[x])
		return "".join(xlist)

	def readXmlTableFile(self,filename,xmldir='.'):
		"""
		The object must be a pPVTTable or pSATTable.  
		The file must exist, since I have no exception handlers for this.
		"""
		fname = xmldir + os.sep + filename
		ch = pPST_XMLhandler()
		ch.setObj(self,fname)
		sx = make_parser()
		sx.setContentHandler(ch)
		sx.parse(filename)
		return 0
	
	def getTableAsEditableString(self,showHeader=0):
		"""
		This returns a string representation of the obj in POWERS format. This 
		is useful when editing in the GUI text windows.
		"""
		xstr = ''
		if showHeader == 1: xstr +=  '\n%s\n' % (self.sStartOfBlock); 
		#for ilo in self.aLineContents: xstr += ilo.getRawLine() 
		k = 1 
		for tbl in self.tablesArray:
			xstr += '\nTABLE %d\n' % k
			xstr += '# From within tbl itself - \n'
			for tt in tbl: xstr += tt.getRawLine()
			xstr += '\nENDTABLE %d\n' % k
			k = k + 1
		if showHeader == 1: xstr +=  "\n%s\n" % self.sEndOfBlock; 
		return xstr
	
	def getXmlTableContent(self,name='UNKNOWN',xmldir='.',ttype='UNKNOWN'):
		"""
		Returns the representation of SAT and PVT tables as one XML object
		without the first header line. You can plunk this into a stream.
		References to table data are included as TABLEREF nodes. The tables
		in TABLEREF are also created.
		"""
		retlist = []

		# Deal with this shortly.
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLKeywords():	retlist.append(item)
		
		retlist.append("<TABLES>\n<COUNT>%d</COUNT>\n" % len(self.tablesArray))
		k = 1 

		for tbl in self.tablesArray:
			fname = xmldir + os.sep + name + '-table-%d.xml' % k
			print "Creating ", fname
			retlist.append( '<TABLEREF file="%s" number="%d" />\n' % (fname,k))
			sublist = []
			for item in self.getIteratedXMLpreamble(ttype,xmldir): sublist.append(item)
			sublist.append('<ID number="%d" />' % k)
			for ilo in tbl: 
				ln = ilo.getRawLine()
				f = ln.find('GRAPH_LABELS')
				if f >= 0: 
					sublist.append('<GRAPH_LABELS_LINE>%s</GRAPH_LABELS_LINE>\n<GRAPH_LABELS>\n' % ln)
					items = ilo.getItems()
					for lbl in items[1:]: sublist.append('<LABEL>%s</LABEL>\n'% lbl)
					sublist.append('</GRAPH_LABELS>\n')
					continue
				f = ln.find('GRAPH_UNITS')
				if f >= 0: 
					sublist.append('<GRAPH_UNITS_LINE>%s</GRAPH_UNITS_LINE>\n<GRAPH_UNITS>' % ln)
					items = ilo.getItems()
					for lbl in items[1:]: sublist.append('<UNITS>%s</UNITS>\n'% lbl)
					sublist.append('</GRAPH_UNITS>\n')
					continue
				items = ilo.getItems()
				if len(items) == 2:
					sublist.append('<PARAMETER NAME="%s" VALUE="%s" />' % (items[0],items[1]))
					continue	
				sublist.append('<LINE>\n%s</LINE>\n' % ilo.getRawLine())
			for item in self.getIteratedXMLpostamble(ttype): sublist.append(item)
			self.xmlIncludes[fname] = sublist  
			k = k + 1	
		retlist.append("</TABLES>\n")
		return retlist


#--------------------------------------------------------------------------------
	def OLD_getXMLTableContent(self,name='UNKNOWN',xmldir='.',ttype='UNKNOWN'):
		retstr = self.getXMLpreamble(name,xmldir,xslsheet=self.xmltemplatedir + os.sep + 'tables.xsl')
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0:
				retstr +="<COMMENT>" + ilo.getRawLine() + "</COMMENT>\n"
			if ilo.hasErrors == 1: retstr +="<ERROR>" + ilo.getRawLine() + "</ERROR>"
		retstr += self.getXMLkeywords()
			# #######################################################################
			# Now publish the names of all the tables in this block as their own file
			# #######################################################################
		retstr +="<TABLES>\n<COUNT>%d</COUNT>\n" % len(self.tablesArray)
		k = 1 
		for tbl in self.tablesArray:
			fname = xmldir + os.sep + name + '-table-%d.xml' % k
			print "Creating ", fname
			retstr +='<TABLEREF file="%s" number="%d" />\n' % (fname,k)
			substr = self.getXMLpreamble(ttype,xmldir)
			substr += '<ID number="%d" />' % k
			for ilo in tbl: 
				ln = ilo.getRawLine()
				f = ln.find('GRAPH_LABELS')
				if f >= 0: 
					substr += '<GRAPH_LABELS_LINE>\n'
					substr += ln
					substr += '</GRAPH_LABELS_LINE>\n'
					substr += '<GRAPH_LABELS>\n'
					for lbl in items[1:]: substr += '<LABEL>%s</LABEL>\n'% lbl
					substr += '</GRAPH_LABELS>\n'
					continue
				f = ln.find('GRAPH_UNITS')
				if f >= 0: 
					substr += '<GRAPH_UNITS_LINE>\n'
					substr += ln
					substr += '</GRAPH_UNITS_LINE>\n'
					items = ilo.getItems()
					substr +=  '<GRAPH_UNITS>\n'
					for lbl in items[1:]: substr += '<UNITS>%s</UNITS>\n'% lbl
					substr += '</GRAPH_UNITS>\n'
					continue
				items = ilo.getItems()
				if len(items) == 2:
					substr +=  '<PARAMETER NAME="%s" VALUE="%s" />' % (items[0],items[1])
					continue	
				substr += '<LINE>\n'
				substr += ilo.getRawLine()
				substr += '</LINE>\n'
			substr += self.getXMLpostamble(ttype)
			self.xmlIncludes[fname] = substr  
			k = k + 1	
		retstr += "</TABLES>\n"
		return retstr

	########################################################
	#
	########################################################
	def initKeywordIndices(self):
		self.indexIncludeFile = 0
		self.indexBinaryFile  = 0

	########################################################
	#
	########################################################
	def getNextIncludeFile(self):		
		xlen = len(self.sIncludeFilenames)
		if (xlen < 1) or (self.indexIncludeFile > xlen): return ''
		retstr = self.sIncludeFilenames[self.indexIncludeFile]
		self.indexIncludeFile = self.indexIncludeFile + 1
		return retstr;

	########################################################
	#
	########################################################
	def getNextBinaryFile(self):		
		""" Gets the next binary file name in the list of names 
		if you are at the end of the list, it returns an empty string"""
		xlen = len(self.sBinaryFilenames)
		if (xlen < 1) or (self.indexBinaryFile >= xlen): return ''
		retstr = self.sBinaryFilenames[self.indexBinaryFile]
		self.indexBinaryFile = self.indexBinaryFile + 1
		return retstr
	########################################################
	#
	########################################################
	def getOptionsList(self,key):
		return self.aOptions.get(key,('No Options',))

	############################################################# 
	#
	############################################################# 
	def getSummaryReport(self,item=None):
		if (item == None): item = self
		if len(item.sStartOfBlock) <> 0:
			xstr = '%d Errors, %d Warnings between %s and %s\n' % (item.getErrorCount(),item.getWarningCount(),item.sStartOfBlock,item.sEndOfBlock)
		else:
			xstr = '%d Errors, %d Warnings in this block: %s\n' % (item.getErrorCount(),item.getWarningCount(),item.sIdString)
		return xstr
	
	#################################################################
	#
	#################################################################
	def getErrorReport(self,item=None):
		"""
		Returns a list of error strings if there were no errors. 
		If there are errors, an 
		error string is returned.
		"""
		if (item == None): item = self
		if (item.getErrorCount() == 0) and (item.getWarningCount() == 0): return []

		ret = []
		ret.append(item.getSummaryReport())
		if (item.getErrorCount() > 0):
			for x in item.aErrorMessages:  
				ret.append(x) 
		if (item.getWarningCount() > 0):
			for x in item.aWarningMessages:  
				ret.append(x) 
		return ret


	def getStringErrorReport(self,item=None):
		"""
		Deprecated.
		"""
		if (item == None): item = self
		if (item.getErrorCount() == 0) and (item.getWarningCount() == 0): return []
		### Okay, return the errors.
		sAccumulatedStrings = self.getSummaryReport()
		createdLine = "Nearest created object [%s] at line %d \n" % (self.sIdString, self.iLineNumber)
		sAccumulatedStrings = sAccumulatedStrings  + createdLine
		if (item.getErrorCount() > 0):
			sAccumulatedStrings = sAccumulatedStrings + join(item.aErrorMessages); 
		if (item.getWarningCount() > 0):
			sAccumulatedStrings = sAccumulatedStrings + join(item.aWarningMessages); 
		return sAccumulatedStrings

	#################################################################
	# Writes the included XML and XSL files if any
	#################################################################
	def writeXMLfile(self,fd=sys.stdout,nm='object',xmldir='.'):
		self.writeXMLstring(fd,nm,xmldir)          # No need to concatenate
		for fkey in self.xmlIncludes.keys():       # You MUST do this.
			fdout = open(fkey,'w')                 # Open the included file.
			fdout.write("".join(self.xmlIncludes[fkey]))  # Write the joined strings.
			fdout.close()                          # close.

	#################################################################
	#
	#################################################################
	def writeXMLstring(self,fd,nm,xmldir):
		fd.write(self.getXMLpreamble(nm,xmldir)) # 
		fd.write(self.getXMLcontent(nm,xmldir))  # expects a string
		fd.write(self.getXMLpostamble(nm))

	#################################################################
	# The style sheet specification has to be changed to a more 
	# specific one based on the root type.
	#################################################################
	def getXMLpreamble(self,rootName,xmldir='.',xslsheet=None): 
		if xslsheet == None: 
			usexslsheet = self.xmltemplatedir + os.sep + 'demo.xsl'
		else:
			usexslsheet = self.xmltemplatedir + os.sep + xslsheet
		retlist = []
		retlist.append('<?xml version="1.0"?>\n')
		retlist.append('<?xml-stylesheet type="text/xsl" href="%s"?>\n' % usexslsheet)
		retlist.append("<%s>\n" % rootName)
		retlist.append("<BLOCKNAME>%s</BLOCKNAME>\n" % rootName)
		retlist.append("<Info>\n<Author>GUI written by Kamran Husain</Author>\n")
		retlist.append('<Location DIR="%s"  />\n'  % xmldir )
		retlist.append("<Contact>PEASD/SSD 03-874-7898</Contact>\n" )
		retlist.append("<Email>kamran.husain@aramco.com</Email>\n" )
		self.localtime = localtime() # placeholder from function.
		retlist.append(strftime("<CreationDate>%x</CreationDate>\n<CreationTime>%X</CreationTime>\n</Info>\n", self.localtime))
		retstr = "".join(retlist)
		return retstr

	def getIteratedXMLpreamble(self,rootName,xmldir='.',xslsheet=None): 
		if xslsheet == 'tables.xsl': xslsheet = self.xmltemplatedir + os.sep + 'tables.xsl'
		if xslsheet == None: xslsheet = self.xmltemplatedir + os.sep + 'demo.xsl'
		yield '<?xml version="1.0"?>\n'
		yield '<?xml-stylesheet type="text/xsl" href="%s"?>\n' % xslsheet
		yield "<%s>\n" % rootName
		yield "<BLOCKNAME>%s</BLOCKNAME>\n" % rootName
		yield "<Info>\n<Author>GUI written by Kamran Husain</Author>\n"
		yield '<Location DIR="%s"  />\n'  % xmldir 
		yield "<Contact>PEASD/SSD 03-874-7898</Contact>\n" 
		yield "<Email>kamran.husain@aramco.com</Email>\n" 
		self.localtime = localtime() # placeholder from function.
		yield strftime("<CreationDate>%x</CreationDate>\n<CreationTime>%X</CreationTime>\n</Info>\n", self.localtime)
		
	#################################################################
	def getIteratedXMLpostamble(self,rootName):
		yield '<copyright> Saudi Aramco 2005 </copyright>'
		yield '</%s>\n' % rootName 

	def getXMLpostamble(self,rootName):
		return '</%s>\n' % rootName 

	#################################################################
	# Only these keywords are allowed, any other keyword is flagged. 
	# Don't the repeat the root words
	#################################################################
	def getXMLcontent(self,name='IGNORED',pathname='.'):
		retlist = []
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLKeywords():	retlist.append(item)
		return "".join(retlist)

	#################################################################
	def getIteratedXMLlineItems(self):
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0: continue
			yield "<LINE>%s</LINE>\n" % ilo.getRawLine()

	def getIteratedXMLnumericLines(self,count=None):
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0: continue
			items = ilo.getItems()
			if len(items) == counted or counted == None: 
				xstr = items[0]
				if xstr.isdigit():
					yield "<LINE>%s</LINE>\n" % ilo.getRawLine()
	
	def getIteratedXMLComments (self):
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0:
				yield "<COMMENT>%s</COMMENT>" % ilo.getRawLine() 
			if ilo.hasErrors == 1:
				yield "<ERROR>%s</ERROR>" % ilo.getRawLine() 

	#################################################################
	def getIteratedXMLKeywords(self):
		keys = self.aKeywords.keys()
		keys.sort()
		for key in keys:
			if self.aKeywords[key] <> None: 
				yield '<PARAMETER NAME="%s" VALUE="%s" />\n' % (key,str(self.aKeywords[key]))
			else:
				yield '<PARAMETER NAME="%s" VALUE="" />\n' % (key)
		

	#################################################################
	def getXMLkeywords(self):
		retlist = []
		keys = self.aKeywords.keys()
		keys.sort()
		for key in keys:
			if self.aKeywords[key] <> None: 
				retlist.append('<PARAMETER NAME="%s" VALUE="%s" />\n' % (key,str(self.aKeywords[key])))
			else:
				retlist.append('<PARAMETER NAME="%s" VALUE="" />\n' % (key))
		return "".join(retlist)

	def readXMLfile(self,filename,handler,xmldir='.'):
		"""
		The filename can be absolute in which case xmldir is ignored 
		otherwise the filename is appened to os.sep + xmldir 

		The handler must be a derived class of the XMLContentHandler
		"""
		if filename[0] <> '/':                           #if not absolute path
			fname = xmldir + os.sep + filename
		else:
			fname = filename
		handler.setObj(self,fname)
		sx = make_parser()
		sx.setContentHandler(handler)
		sx.parse(filename)

	def printStructure(self,fd,showHeader=0):
		items = self.getContentsAsList(showHeader)
		if len(items) > 0: fd.write("".join(items))

	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs. 
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append('%s\n' % (self.sStartOfBlock))
		if includeLineContents==0:
			allkeys = self.aKeywords.keys()
			allkeys.sort()
			for k in allkeys:
				v = self.aKeywords[k]
				items.append("%s %s\n" % (k,v))
		else:
			for ilo in self.aLineContents:        # Okay, the guys wants it all
				if ilo.isComment == 1: continue
				items.append(ilo.getRawLine())
		for ilo in self.aLineContents:            # fd
			if ilo.isComment == 1: items.append(ilo.getRawLine())
		if showHeader == 1: items.append("%s\n" % self.sEndOfBlock)
		return items


	def getEditableList(self,showHeader=0):
		xstr = []
		if showHeader == 1: xstr.append('%s\n' % self.sStartOfBlock)
		for ilo in self.aLineContents: xstr.append(ilo.getRawLine())
		if showHeader == 1: xstr.append("%s\n" % self.sEndOfBlock)
		return xstr


	# #######################################################################
	def getEditableString(self,showHeader=0):
		xstr = ''
		if showHeader == 1: xstr +=  '%s\n' % (self.sStartOfBlock); 
		for ilo in self.aLineContents: xstr += ilo.getRawLine() 
		if showHeader == 1: xstr +=  "%s\n" % self.sEndOfBlock; 
		return xstr


#####################################################################################
class cDateObject(pTrimObject):
	"""
	Encapsulates the DATE object used in Rates, Perfs and quite possibly the Recurrent file
	"""
	def __init__(self,ilo=None):
		pTrimObject.__init__(self,ilo)
		self.sIdString = '' 
		self.Wells = {}		       # Indexed by a name; no duplicates allowed. 
		self.pseudoItems = {}      # Indexed by names.
		self.groupRules  = []      # All keywords in a group. 
		self.allRigs = []
		self.collections = {'GROUP': {}, 'PRODUCER' : {}, 'INJECTOR': {}}
		self.existingWells =[]
		self.parentage = {}
		self.month = 1
		self.year  = 1942
		self.day = 1
		self.bModified = 0              # If modified, write to recurrent.
		self.mSource   = None           # From rates, perfs or recurrent.

	def getSource(self):
		"""
		sourceRATES     = 0
		sourcePERFS     = 1
		sourceRECURRENT = 2
		"""
		if self.mSource == sourceRATES: return 'RATES'
		if self.mSource == sourcePERFS: return 'PERFS'
		if self.mSource == sourceRECURRENT: return 'RECURRENT'
		return ""

	def mergeExistingWells(self,newlist):
		for nm in newlist:
			if not nm in self.existingWells: self.existingWells.append(nm)

	def getWellCount(self):
		s = "No. of wells= %d" % len(self.Wells)
		return s

	def setDate(self,x):
		self.sIdString = x		

	def getDate(self):
		return self.sIdString

	def getOneLiner(self):
		return 'DATE %s-%02d-%4d' % (monthnames[self.month-1],int(self.day),int(self.year))

	def addWell(self,name,ilo=None,useThisWell=None):
		if not self.Wells.has_key(name) :
			self.Wells[name] = cWellObject(ilo)  # Create one if not there
		if useThisWell <> None: 
			well = self.Wells[name]              # Don't copy yourself.
			if well <> useThisWell:
				tpkeys = useThisWell.perforations.keys()
				for tk in tpkeys:
					perf = useThisWell.perforations[tk]
					well.addPerforation(copy.copy(perf))
				for k in useThisWell.aKeywords.keys(): 
					well.setKeywordValue(k,useThisWell.aKeywords[k])
		x = self.Wells[name]           # Use the old or new one
		x.sIdString = name             # assign it to placeholder
		x.aKeywords['NAME'] = name     # A function call is slower
		return x

	def getCollectionNames(self,whence):
		"""
		whence can be 'GROUP','INJECTOR','PRODUCER'
		"""
		gip = self.collections[whence]
		return gip.keys()

	def addCollection(self,whence,name):
		"""
		whence can be 'GROUP','INJECTOR','PRODUCER'
		The collection is added here.
		"""
		gip = self.collections[whence]    # Returns a dictionary.
		if not gip.has_key(name): gip[name] = [] 

	def delCollection(self,whence,name):
		"""
		whence can be 'GROUP','INJECTOR','PRODUCER'
		The collection is removed from the main dictionary.
		"""
		gip = self.collections[whence]    # Returns a dictionary.
		if gip.has_key(name): 
			gip[name] = [] 
			del gip[name]


	def delItemFromCollection(self,whence,collectionName,item):
		gip = self.collections[whence]
		thisCollection = gip[collectionName] 
		try:
			thisCollection.remove(item)
		except:
			pass


	def replaceTextInCollections(self,oldText,newText):
		count = 0

		#
		# Pass 1
		#
		for whence in self.collections.keys():  # For all types collections 
			gip = self.collections[whence]
			print "Checking .. ", whence
			gipKeys = gip.keys()
			for collectionName in gipKeys:
				if collectionName == oldText:
					print "Replace collection name ", oldText, " with ", newText
					gip[newText] = gip[collectionName]  # Preserve this pointer
					gip[collectionName]  = None         # Explicity force to Null
					del gip[collectionName]             # Then delete this reference
					count = count + 1
		#
		# Pass 2
		#
		for whence in self.collections.keys():  # For all types collections 
			gip = self.collections[whence]
			print "Checking .. ", whence
			gipKeys = gip.keys()
			for collectionName in gipKeys:
				thisCollection = gip[collectionName] 
				print "Checking inside ", collectionName
				useThis = []
				for item in thisCollection: 
					if item == oldText: 
						useThis.append(newText)
						print "Replace item ", item, " with ", newText
						count = count + 1
					else: 
						useThis.append(item)
				gip[collectionName] = useThis
		return count

	def addToCollection(self,whence,collectionName, item):
		"""
		whence can be 'GROUP','INJECTOR','PRODUCER'
		The collection named by collectionName is added to here.
		item is a string .. I have to have .
		"""
		gip = self.collections[whence]
		thisCollection = gip[collectionName] 
		thisCollection.append(item)


	def getNamedCollection(self,whence,collectionName): 
		"""
		Returns a POINTER to the list ...
		whence can be 'GROUP','INJECTOR','PRODUCER'
		The collection named by collectionName is returned here 
		"""
		gip = self.collections[whence]
		return gip.get(collectionName,None) 

	def getCollection(self,name):
		if name in ['GROUP','INJECTOR','PRODUCER']:
			return self.collections[name].keys()
		else:
			return []

	def setParentage(self):
		groups   = self.collections['GROUP']
		injector = self.collections['INJECTOR']
		producer = self.collections['PRODUCER']
		self.parentage = {}
		for grpName in groups.keys():    # For each group
			grpItems = groups[grpName]   # Get the names in each 
			for nm in grpItems: self.parentage[nm] = grpName
		for inj in injector.keys():    # For each group
			injItems = injector[inj]   # Get the names in each 
			for nm in injItems: self.parentage[nm] = inj
		for pro in producer.keys():    # For each group
			proItems = producer[pro]   # Get the names in each 
			for nm in proItems: self.parentage[nm] = pro

	def addGroupRule(self):
		item = pGroupRuleObject()
		self.groupRules.append(item)
		return item

	def addPseudo(self,name):
		if not self.pseudoItems.has_key(name):
			ilo = pLineObject(name)
			self.pseudoItems[name] = cPseudoObject(ilo)
		return self.pseudoItems[name]

	def addRig(self,name=''):
		xstr = "RIG %d" % (len(self.allRigs) + 1)
		ilo = pLineObject(name)
		f = cRigObject(ilo)
		self.allRigs.append(f)
		return f

	def getPseudoItem(self,name):
		return self.pseudoItems.get(name,None)


class pGroupRuleObject(pTrimObject):
	def __init__(self,ilo=None,id='Unknown'):
		pTrimObject.__init__(self,ilo)
		self.sIdString = id
		self.aLineItems = [] 

	
	def addLineItem(self,s):
		"""
		The s must be a tuple.
		"""
		self.aLineItems.append(s)

	def getEditableString(self,showHeader=1):
		xstr = []
		xstr.append(self.sIdString+" ")
		for i in self.aLineItems:
			xstr.append(i)
		return "".join(xstr)

		
#####################################################################################
# LOOK AT THE DEFINITIONS BELOW
#####################################################################################
cPerfAllowedKeywords = ['WELL_RADIUS','CD','K_TOP','K_BOTTOM','WNDF','LPI','SKIN','SHUT_IN',
                    'PRODUCTIVITY_INDEX',  'I','J','K','RF','GRID_NAME']
cPerfAllowedKeywords.sort()

def cPerfMakeId(dict):
	id = ''
	for i in ['I','J','K','K_TOP','K_BOTTOM']:
		id += '%s=%s ' % (i,dict.get(i,'0'))
	return id.strip()


#####################################################################################
class cPerfObject(pTrimObject):
	"""
	This object tracks the keywords for a perforation object in a rates file. 
	"""
	def __init__(self,ilo=None,id='Unknown'):
		pTrimObject.__init__(self,ilo)
		self.sIdString = id
		self.aKeywords['I'] = '0'
		self.aKeywords['J'] = '0'
		self.aKeywords['K'] = '0'
		self.aKeywords['K_BOTTOM'] = '0'
		self.aKeywords['K_TOP'] = '0'
		self.sIdString = "I=0 J=0 K=0 K_TOP=0 K_BOTTOM=0"

	def setPerfName(self):
		self.sIdString = ''
		for i in ['I','J','K','K_TOP','K_BOTTOM']:
			self.sIdString += '%s=%s ' % (i,self.getKeywordValue(i))
		self.sIdString.strip()

	def getPerfName(self):
		return self.sIdString

	def getOneLiner(self):
		xstr = ''
		for k in self.aKeywords.keys():
			v = self.aKeywords[k]
			if k in ['CD','GRID_NAME']: 
				xstr += " %s='%s'," %(k,v)
			else:
				xstr += " %s=%s," %(k,v)

		if len(xstr) > 2:
			if xstr[-1] == ',': return xstr[:-1]
		return xstr

#####################################################################################
# LOOK AT THE DEFINITIONS BELOW
#####################################################################################
cRigAllowedKeywords = ['WORKOVER_COUNT', 'DRILL_AS_NEEDED', 'DRILL_COUNT', 
	'FLOWWELL_INTERVAL', 'WORKOVER_INTERVAL', 'DRILLING_INTERVAL', 
	'SHUTIN_WELLRATE_REDUCTION', 'SHUTIN_WELL_TEST_FREQUENCY']
cRigAllowedKeywords.sort()

#####################################################################################
class cRigObject(pTrimObject):
	def __init__(self,iLineNumber=None,id='Unknown'):
		pTrimObject.__init__(self,iLineNumber)
		self.sIdString = id

	def setRigName(self,name):
		self.aKeywords['NAME'] = name
   
	def getRigName(self):
		return self.aKeywords['NAME'];

	def getEditableString(self,showHeader=1):
		xstr = []
		if showHeader == 1: xstr.append('&RIG\n')
		for k in self.aKeywords.keys():
			xstr.append('%s = %s\n' % (k,self.aKeywords[k]))
		if showHeader == 1: xstr.append('/\n')
		return "".join(xstr)


#####################################################################################
class cPseudoObject(pTrimObject):
	def __init__(self,iLineNumber=None,id='Unknown'):
		pTrimObject.__init__(self,iLineNumber)
		self.sIdString = id

	def setPseudoName(self,name):
		self.aKeywords['NAME'] = name
   
	def getPseudoName(self):
		return self.aKeywords['NAME'];

	def getEditableString(self,showHeader=1):
		xstr = []
		if showHeader == 1: xstr.append('&PSEUDO\n')
		for k in self.aKeywords.keys():
			xstr.append('%s = %s\n' % (k,self.aKeywords[k]))
		if showHeader == 1: xstr.append('/\n')
		return "".join(xstr)


cWellAllowedKeywords = [ 'MAX_QO','MAX_QW', 'MAX_QL', 'MAX_QG', 'MIN_Q0','MIN_QW', 'MIN_QL', 'MIN_QG', 'FLUID',
	'MIN_BHP','MAX_BHP','MAX_DDP','MIN_WHP','MAX_BUP','FLOW_TABLE','WELL_PRIORITY','WELL_PI','INJ_COMP',
	'MINBHP','MAXBHP','BHP','WELL_DEPTH_DATUM','QO','QG','QW','TYPE','NAME' ]
cWellAllowedKeywords.sort()
#####################################################################################
class cWellObject(pTrimObject):
	"""
	This object tracks the keywords for a well object in a perf or rates file. 
	I have to overwrite the function to print it out based on perf or rates output. 
	"""
	def __init__(self,ilo=None):
		pTrimObject.__init__(self,ilo)
		self.perforations = {}                    # An array of objects
		self.sourceString = 'Unknown'
		self.isPseudo = 0

	def clearPerforations(self):
		self.perforations = {}                    # Reset for user interface

	def setSourceName(self,xstr):
		self.sourceString = xstr

	def getSourceName(self):
		return self.sourceString

	def setWellName(self,name):
		if len(name) > 8: name = name[:8]
		self.aKeywords['NAME'] = name
  
	def addPerforation(self,perfObj):
		id = perfObj.getPerfName()
		self.perforations[id] = perfObj

	def addAnotherPerforation(self):
		skeys = self.perforations.keys()
		skeys.sort()

		tp = cPerfObject(None,None) # Create a new perforation.
		kp = self.perforations.keys()  # Get the perforations. 
		if len(kp) < 0: 
			tp.setPerfName()
		else:
			kp.sort()                               # Sort the names 
			lp = self.perforations[kp[-1]] # Get the last name
			for k in lp.aKeywords.keys():
				print lp.getKeywordValue(k), k
				tp.setKeywordValue(k,lp.getKeywordValue(k))
			v = int(tp.getKeywordValue('K'))+1
			tp.setKeywordValue('K',str(v))
			tp.setPerfName()
		#
		# Finally, add the last perforation ...
		#
		print "Perforation Added:", tp.getPerfName()
		id = tp.getPerfName()
		self.perforations[id] = tp
	

	def getWellName(self):
		return self.aKeywords['NAME'];

	def printWellLine(self,fd=None):
		"""
		Given a file descriptor, this will write out a WELL's information.
		Returns an array of the wells strings AND Perforations for the well.
		"""
		retstr = []
		xs = '\n\t&WELL Name = "%s" ' % self.aKeywords['NAME'] 
		retstr.append(xs)
		if self.aKeywords.has_key('Type'):
			xs = ' Type ="%s" \n' % self.aKeywords['Type']
			retstr.append(xs)
		retstr.append('\n\t\t')
		for i in self.aKeywords.keys():
			if i not in ['NAME','Type']: 
				xs = ' %s=%s\n' % (i , self.aKeywords[i])
				retstr.append(xs)
		# Now terminate the well and return any Perforations. 
		retstr.append('\n\t/\n')
		for perf in self.perforations.values():            # For incoming well object.
			retstr.append('\n\t\t&PERF')
			retstr.append(perf.getOneLiner())
			retstr.append('\t/')
		if fd <> None: fd.write("".join(retstr))
		return retstr
	
	def mergeData(self, wobj):
		"""
		Merges the data in the wobj object with that in the current object.
		Perforation objects are not duplicated, however, two perforation objects may 
		contain the same data within since Perforations don't have unique names. 
		"""
		for key in wobj.aKeywords.keys():	
			self.setKeywordValue(key,wobj.getKeywordValue(key))
		mykeys = self.perforations.keys()
		for perf in wobj.perforations.values():            # For incoming well object.
			thisID = perf.getPerfName()           # Get this incoming perforation.
			if not thisID in mykeys:  	 # If not there, add it. 
				self.addPerforation(perf)
			else: 
				mperf = self.perforations[thisID]
				for xkey in perf.aKeywords.keys():	
					mperf.setKeywordValue(key,perf.getKeywordValue(xkey))


#####################################################################################
class cParserObject:
	def __init__(self):
		self.inputLines = []
		self.verbose = 0
		self.monthsOfYear=monthnames
		self.sIncludedFilenames = []
		self.lineNumber = 0
		self.userDates  = {}
		self.allDates   =  self.userDates
		self.userWellNames = {}
		self.allWellNames    = self.userWellNames
		self.aErrorMessages   = []
		self.filename = ''

	def applyInitialTree(self,useTheseDates,useTheseWellNames):
		#print "My date names =", len(useTheseDates.keys())
		#print "My well names =", len(useTheseWellNames.keys())
		self.userDates  = useTheseDates
		self.allDates   = useTheseDates
		self.userWellNames   = useTheseWellNames
		self.allWellNames    = useTheseWellNames

	def removeQuotes(self,incoming):
		if incoming == None: return incoming 
		xstr = incoming.replace("'",'')
		xstr = xstr.replace('"','')
		return xstr

	def processDateLine(self,incomingItems,source=0):
		""" 
		Create a date object and parse the rest of the input line.  
		This expects a ['DATE', 'MMM-DD-YYYY']


		"""
		if len(incomingItems) == 4:
			month = incomingItems[1]
			month = month.upper()                       # Convert to upper case ...
			day   = int(incomingItems[2])
			year  = int(incomingItems[3])
			sdate = "".join(incomingItems[1:4])
		else: 
			sdate = incomingItems[1]                    # Convert it to 
			month = sdate[0:3]    
			month = month.upper()                       # Convert to upper case ...
			day   = int(sdate[4:6])
			year  = sdate[7:11]
		#else:
			#print "BAD DATE:", incomingItems
			#sdate = "Bad Date"
			#month = 'Jan'
			#day   = 1
			#year  = 2005 
			#if not self.allDates.has_key(sdate):
			#	self.allDates[sdate] = cDateObject()
			#self.lastDate =  self.allDates[sdate]
			#self.lastDate.setDate(sdate)
			#return
		if not month in self.monthsOfYear:
			self.errStr = self.errStr + "Error Line %d Bad month [%s] " % (self.lineNumber, month)
		if day < 1 or day > 31: 
			self.errStr = self.errStr + "Error Line %d Bad day [%s] " % (self.lineNumber, day)
		if month == 'FEB' and (day > 29):
			self.errStr = self.errStr + "Error Line %d Bad day [%s] " % (self.lineNumber, day)
			# So, I don't catch leap years etc. Big deal. 
		if year < 1900:
			self.errStr = self.errStr + "Error Line %d Bad year [%s] " % (self.lineNumber, year)
		sdate = "%04d-%02d-%02d" % (int(year),self.monthsOfYear.index(month)+1,int(day))

		if not self.allDates.has_key(sdate):
			self.allDates[sdate] = cDateObject()
		self.lastDate =  self.allDates[sdate]
		self.lastDate.year = year
		self.lastDate.month = self.monthsOfYear.index(month)+1
		self.lastDate.day   = day 
		self.lastDate.setDate(sdate)
		self.lastDate.mSource = source
		return sdate


	def writeDataFile(self,filename):
		fd = open(filename,'w')
		dkeys = dte.allDates.keys();
		dkeys.sort()
		for dk in dkeys():
			dte = self.allDates[dk]
			fd.write(dte.getOneLiner()+'\n')
			wkeys = dte.Wells.keys()
			if len(wkeys) > 0: 
				for wk in wkeys: 
					well = self.Wells[wk]              # Don't copy yourself.
					well.printWellString(fd)
			fd.write('\n')
		fd.close()
		
		
	def readDataFile(self,filename,keepCopyOfLine=0,notifyFunction=None):
		"""
		Reads in a data file and keeps all it's lines in memory. 

		workpath --->  PROJECT_DIRECTORY/data   with no os.sep at end
		projectpath --->  PROJECT_DIRECTORY with no os.sep at end
		incpath  --->


		"""
		self.clearMemory()
		self.lineNumber = 0
		workpath, projectpath = deriveWorkpaths(filename)
		if self.verbose == 1: 
			print "readDataFile: Work Path = ", workpath
			print "readDataFile: Proj Path ", projectpath 
		incpath = ''
		try:
			fd = open(filename,'r')
		except IOError:
			self.errStr =  "IOError READ FILE: Cannot open file", filename 
			return None
		lineNumber = 0
		self.verbose=1


		xln = pLineObject('','',lineNumber)
		self.sIncludedFilenames = []
		stackFiles = []
		self.inputLines = []

		self.filename = filename   # Save first file name
		thisfilename = filename    # Initialize loop count
		self.verbose = 0
		tmA = time()

		print "Starting ...", filename

		# We also have to know the total size of the file when we open it for the first time.
		fss = os.fstat(fd.fileno())
		filesize = fss[6]

		try:	
			while 1:
				ln = fd.readline()
				if not ln: 
					fd.close()
					if len(stackFiles) < 1: break           # Any more files?
					thisfilename,location,lineNumber = stackFiles.pop()                   # Go back to last file
					#print "Restoring ...", thisfilename, location, lineNumber
					fd = open(thisfilename,'r') 			# Restore the pathname
					fd.seek(location)                       # Restore the location
					self.lineNumber = lineNumber            # Restore the line number
					continue                                # Go to top of loop
				if len(ln) < 1: 
					self.lineNumber += 1        # Count them
					continue                    # Ignore blank lines
				items = split(ln)               # Break it apart
				if len(items) < 1:  
					continue                    # Ignore blank lines
				f = find(items[0],'INCLUDE_FILE')           # Are we including a file here?
				if f == 0:                      # Okay, inclusion found.
					incpath = strip(items[1])   # derive the filename 
					done = 0                    # Is this an absolute filename? If so, use it verbatim.
					incpath  = deriveIncludePath(incpath,workpath,projectpath)
					if incpath <> None:
						stackFiles.append((thisfilename,fd.tell(),self.lineNumber))
						self.lineNumber = 1
						self.sIncludedFilenames.append(incpath)   # Keep a list of the name
						fd.close()
						thisfilename = incpath
						fd = open(thisfilename,'r')
						fss = os.fstat(fd.fileno())
						filesize = fss[6]
				else:  # File 
					if keepCopyOfLine == 1:
						xln = pLineObject(ln,thisfilename,self.lineNumber)
						self.inputLines.append(xln)
					else:
						xln.setLine(ln,keepcopy=0)              
					#if xln.mustProcess <> 0:  self.parseLine(xln)
					self.parseLine(xln)
				self.lineNumber += 1
				if self.lineNumber % 50000 == 0: 
					if notifyFunction <> None: 
						#fss = os.fstat(fd.fileno())
						#print "Location = ", fd.tell(), " size = ", fss[6], "\n", fss
						#apply(notifyFunction,(fd.tell(),fss[6])) 
						apply(notifyFunction,(self.lineNumber,100000)) 
					print "Time :", time() - tmA, " 100000 lines", self.lineNumber,ln,
		except IOError:
			self.errStr =  "FILE ERROR: Cannot open file", filename , " or ", incpath
			return -1
		print "Time :", time() - tmA, " 100000 lines", self.lineNumber,ln,
		if notifyFunction <> None: apply(notifyFunction,(0,100))


	def readOneIncludeFile(self,incpath):
		try:
			lines = open(incpath,'r').readlines()
		except: 
			print "INCLUDE FILE ERROR: Cannot read file",  incpath
			lines = []
		return lines

	def readIncludedFiles(self,filename,keepPathName=1):
		"""
		This is a required function 


		I have to read in all the contents of all the included files in the INCLUDE_FILE directives. 
		The incoming lines are tagged in the self.inputLines array as pLineObjects.
		If keepPathName == 1, then each line will contain a pathname of where it came from.
		"""
		workpath, projectpath = deriveWorkpaths(filename)
		if self.verbose == 1: 
			print "readIncludedFiles: Work Path = ", workpath
			print "readIncludedFiles: Proj Path = ", projectpath 
		incpath = ''

		try:
			fd = open(filename,'r')
		except IOError:
			self.errStr =  "IOError READ FILE: Cannot open file", filename 
			return None
		self.inputLines = []
		lineNumber = 0
		self.verbose = 0
		fileid = 0
		self.sIncludedFilenames = [filename]   #  Include yourself 


		try:	
			while 1:
				ln = fd.readline()
				if not ln: 
					fd.close()
					break
				if len(ln) > 1: 
					items = split(ln)
					if len(items) < 1:  continue;
					f = find(items[0],'INCLUDE_FILE')
					if f == 0:                                   # Okay, inclusion found.
						incpath = strip(items[1])				 # derive the filename 
						# Is this an absolute filename? If so, use it verbatim.
						done = 0
						incpath = deriveIncludePath(incpath,workpath,projectpath)
						if incpath == None: return
						print "Reading ...", incpath
						lines = self.readOneIncludeFile(incpath)
						if len(lines) < 1: continue 
						self.sIncludedFilenames.append(incpath)
						fileid = self.sIncludedFilenames.index(incpath)
						k = 0
						iln = "#@INCLUDE_BEGIN " + incpath + "\n"
						if keepPathName == 1:
							xln = pLineObject(iln,incpath,k)
						else:
							xln = pLineObject(iln,'',k)
						self.inputLines.append(xln)
						for iln in lines: 
							k = k + 1
							if keepPathName == 1:
								xln = pLineObject(iln,incpath,k)
							else:
								xln = pLineObject(iln,'',k)
							self.inputLines.append(xln)
						iln = "#@INCLUDE_END " + incpath  + "\n"
						xln = pLineObject(iln,incpath,k)
						self.inputLines.append(xln)
					else:
						if keepPathName == 1:
							xln = pLineObject(ln,self.sIncludedFilenames[0],lineNumber)
						else:
							xln = pLineObject(ln,'',lineNumber)
						self.inputLines.append(xln)
						lineNumber += 1
						
		except IOError:
			self.errStr =  "FILE ERROR: Cannot open file", filename , " or ", incpath
			return -1

		self.verbose=0
		return len(self.inputLines)


	#####################################################################################
	def addErrorMessage(self,outstr,parm=None):
		errstr = "File %s (or in inclusions): Error -- %s\n" % (self.filename, outstr)
		if parm <> None: errstr += parm
		self.aErrorMessages.append(errstr) # Add the line here for output back. 

	#####################################################################################
	def getErrorCount(self):
		return len(self.aErrorMessages)

	#####################################################################################
	def clearErrors(self):
		self.aErrorMessages   = []

	def getListOfErrors(self):
		return self.aErrorMessages

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
			self.obj.parseLine(ilo)
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name in ['COMMENT']:
			self.lineNumber += 1
			self.thisLine = ''
			self.inBody = 1
			return
		if name in  ['GRAPH_LABELS_LINE','GRAPH_UNITS_LINE','LINE']:
			self.lineNumber += 1
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
			########################################################################
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

