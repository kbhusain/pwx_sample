"""
#
# This object for  migration line option items.
#
Author: Kamran Husain  PEASD/SSD

"""
from pObject import *
from string import *

###############################################################################
# The holder for all other migration line items. 
###############################################################################
class pMigrationLine(pObject):
	def __init__(self,name,ilo=None):
		self.id = name
		self.sIdString = 'MIGRATION_LINE_NAME %s' % name
		pObject.__init__(self,ilo)
		self.dataItems = []

	def addWindow(self,items):
		self.dataItems.append(items)	# Keep the tuple. 
		
	def setName(self,name):
		self.id = name
		self.sIdString = 'MIGRATION_LINE_NAME %s' % name

	def getString(self):
		xstr = ''
		for item in self.dataItems: 
			xstr = xstr + join(item,' ') + "\n"
		return xstr
		
	def getXMLcontent(self,nm,xmldir='.'):
		retlist = []
		retlist.append('<MIGRATION_LINE_NAME name="%s" />\n' % self.id)
		for line in self.dataItems:
			retlist.append('<WINDOW>%s</WINDOW>\n' % "".join(line,' '))
		return "".join(retlist)
		
	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs. 
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append(self.sIdString + '\n')
		#allkeys = self.aKeywords.keys()
		#allkeys.sort()
		#for k in allkeys:
			#v = self.aKeywords[k]
			#items.append("%s %s\n" % (k,v))
		for x in self.dataItems: 
			items.append('WINDOW ' + " ".join(x) + '\n')	
		if showHeader == 1: items.append('/\n')
		return items

###############################################################################
# The holder for all other migration line items. 
###############################################################################
class pMigrationData(pObject):
	def __init__(self,ilo=None):
		self.id = id
		self.sIdString = ''
		pObject.__init__(self,ilo,'BEGIN_MIGRATION_LINE_OPTION','END_MIGRATION_LINE_OPTION')
		self.pLineItems = []	  # The number of substructures
		self.clearErrors()		  # Initialization. 
		self.inMigrationLine = 0
		
	def parseLine(self,ilo):
		keywords = ilo.getItems() 
		if len(keywords) < 2: 
			self.addContentLine(ilo)
			return 
		keyword =  keywords[0]   
		if keyword == 'MIGRATION_LINE_NAME':
			if len(keywords) <> 2:
				self.addWarningMessage('Migration Line Name: Unspecified name for line' , ilo)
				return
			name = keywords[1]
			self.addContentLine(ilo)
			self.pLine = pMigrationLine(name,ilo)
			self.pLineItems.append(self.pLine)
			self.inMigrationLine = 1
			self.pLine.setName(name)
			return			
		if keyword == 'WINDOW':
			if len(keywords)  == 9 and keywords[8] == '/':
				self.pLine.addWindow(keywords[:-1])
				self.pLine.addContentLine(ilo)
			elif len(keywords)  <> 8:
				self.addWarningMessage('Migration Item: Bad Input Line: ',ilo)
			else:
				self.pLine.addContentLine(ilo)
				self.pLine.addWindow(keywords)

	def getLineCount(self):
		return len(self.pLineItems)
	
	def doConsistencyCheck(self):
		pass
		#self.clearErrors();
		#For each line, .. parse it to see if have the right keywords..??


	######################################################################
	# I have to merge the "WINDOW" statements with those in aLineContents.
	######################################################################
	def mergeIntoLineContents(self):
		Litems =  []
		for iLine in self.aLineContents:
			if (iLine.find('MIGRATION_LINE_NAME') > -1) or (iLine.find('WINDOW') > -1): 
				continue
			Litems.append(iLine)
		
		self.aLineContents = Litems
		###################################################################
		# Now add the data after the first block. We cannot keep the order
		# of the comments.
		###################################################################
		for thisLine in self.pLineItems:
			self.aLineContents.append(thisLine.sIdString)
			for dataItem in thisLine.dataItems:
				xstr = join(dataItem,' ') 
				self.aLineContents.append(xstr)
			self.aLineContents.append('\n')

	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs. 
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append(self.sStartOfBlock + '\n')
		allkeys = self.aKeywords.keys()
		allkeys.sort()
		for k in allkeys:
			v = self.aKeywords[k]
			items.append("%s %s\n" % (k,v))
		for ilo in self.aLineContents:            # fd
			if ilo.isComment == 1: items.append(ilo.getRawLine())

		for tbl in self.pLineItems:
			lineItems = tbl.getContentsAsList()
			for x in lineItems: items.append(x)
		if showHeader == 1: items.append(self.sEndOfBlock + '\n')
		return items

	def getXMLcontent(self,name='MIGRATION',xmldir='.'):
		retlist = []
		for ilo in self.aLineContents:
			if ilo.mustProcess == 0:
				retlist.append("<COMMENT>%s</COMMENT>\n" % ilo.getRawLine())
			if (ilo.hasErrors == 1):
				retlist.append("<ERROR>%s</ERROR>\n" % ilo.getRawLine())
		for item in self.getIteratedXMLKeywords():	retlist.append(item)
		retlist.append("<TABLES>\n<COUNT>%d</COUNT>" % len(self.pLineItems))
		k = 1 
		for tbl in self.pLineItems:
			fname = xmldir + os.sep + name + '-table-%d.xml' % k
			print "Creating ", fname
			retlist.append('<TABLEREF file="%s" />\n' % fname)
			fdout = open(fname,'w')
			tbl.writeXMLfile(fdout,'MIGRATION_LINE',xmldir)
			fdout.close()
			k = k + 1
		retlist.append('</TABLES>\n')
		return "".join(retlist)

		##===================================================================
		#retstr = ''
		#for ilo in self.aLineContents:
			#if ilo.mustProcess == 0:
				#retstr +="<COMMENT>" + ilo.getRawLine() + "</COMMENT>\n"
			#else:	
				#items = ilo.getItems()
				#if (ilo.hasErrors == 1):
					#retstr +="<ERROR>" + ilo.getRawLine() + "</ERROR>"
		#retstr += self.getXMLkeywords()
		#retstr +="<TABLES>\n<COUNT>%d</COUNT>" % len(self.pLineItems)
		#k = 1 
		#for tbl in self.pLineItems:
			#fname = xmldir + os.sep + name + '-table-%d.xml' % k
			#print "Creating ", fname
			#retstr +='<TABLEREF file="%s" />\n' % fname
			#fdout = open(fname,'w')
			#tbl.writeXMLfile(fdout,'MIGRATION_LINE',xmldir)
			#fdout.close()
			#k = k + 1
		#retstr +='</TABLES>'
		#return retstr
		##===================================================================

	def readXMLfile(self,filename,xmldir='.'):
		ch = pMig_XMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)


	def getEditableString(self,showHeader=0):
		return self.getTableAsEditableString(showHeader)

####################################################################################
#
####################################################################################
class pMigTable_Handler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name in ['COMMENT', 'WINDOW']:
			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)                    # The line is kept in raw form
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name in ['COMMENT','WINDOW']:
			self.thisLine = ''
			self.inBody = 1
			return
		if name == 'MIGRATION_LINE_NAME':
			xstr = 'MIGRATION_LINE_NAME ' + attrs.get("name",'UNKNOWN')
			ilo =  pLineObject(xstr,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)                    # The line is kept in raw form
			return

####################################################################################################
# The handler for the xml input ... Please don't try to make this into one object.
####################################################################################################
class pMig_XMLhandler(ContentHandler):
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

	def startElement(self, name, attrs):
		"""
		Capture incoming comments.
		"""
		if name in ['COMMENT']:
			self.thisLine = ''
			self.inBody = 1
			return
		if name == 'TABLEREF':
			fname = attrs.get('file','')
			ch = pMigTable_Handler()
			ch.setObj(self.obj,fname)
			qx = make_parser()
			qx.setContentHandler(ch)
			qx.parse(fname)
			return


if __name__ == '__main__':
	if len(sys.argv) < 1: sys.exit(0)
	fname = sys.argv[1]
	ob = pMigrationData()
	ch = pMig_XMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	print "Number of tables = ", ob.getLineCount()
	for mi in ob.pLineItems: 
		#print "Id  = ", mi.id
		print "sIdString = ", mi.sIdString
		

	


