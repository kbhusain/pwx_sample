"""
##################################################################################################
This is the first step in transforming a PERF file into an XML document. 
You can then use a DTD to validate the document and an XSL program to reformat it.
##################################################################################################
"""
from string import *
from Plex import *
import pLexicon
import sys

##################################################################################################
# The class definition for the main program begins here
##################################################################################################
class pPerfToXML:
	def __init__(self):
		self.tags = [] 
		self.ST_IDLE = 0
		self.ST_IN_DATE    = 1
		self.ST_IN_WELL    = 2
		self.ST_IN_PERF    = 3
		self.lastWell = ""

	def writePreamble(self,fdout):
		fdout.write('<?xml version="1.0" standalone="yes"?>\n')
		fdout.write('<!DOCTYPE perfs SYSTEM "Perfs.DTD">\n')
		fdout.write('<perfs>\n')
		#fdout.write('<author> Kamran Husain, Saudi Aramco,  PEASD-SSD, 9663 874 7898 </author>\n')

	def writePostamble(self,fdout):
		fdout.write('</perfs>')

	def convertFile(self,scanner,fdout):
		self.state = 0
		self.group = None
		self.lastdate = ""
		self.nodeCounter = 0
		self.writePreamble(fdout)	
		while 1: 
			token = scanner.read()           # Check for input end
			if token[0] == None: break;
			elif token[1] == 'DATE': 		# Check end condition
				token = scanner.read()      # Read next token
				self.lastdate = token[1]    # for the actual value
				fdout.write('<DATE NID="%s"/>\n' % token[1])   # with no wells
			elif token[1] == 'ENDWELLS': 	 		 # Check end condition
				fdout.write('</WELLS>\n');
			elif token[1] == 'WELLS': 	 		 # Check start condition
				fdout.write('<WELLS NID="W_%s">' % self.lastdate);
			elif token[1] == '&WELL':        # got another well
				value = scanner.read()     # Read 'Name' keyword
				value = scanner.read()     # Read next token for well name 
				self.lastWell = value[1]
				continue
			elif token[1] == '&PERF':        # got another well
				self.state = self.ST_IN_PERF
				self.nodeCounter += 1; 
				self.nodeID = 'P_' + str(self.nodeCounter)
				fdout.write('\n<PERF NID="%s"><WNAME>%s</WNAME>\n' % (self.nodeID,self.lastWell))   # End this well
				continue
			#elif self.state == self.ST_IN_WELL:
				#if token[0] == 'eob':
					# fdout.write('</WELL>\n')   # End this well
					#self.state = self.ST_IN_DATE
				#continue
			if self.state == self.ST_IN_PERF:
				if token[0] == 'eob':          # Otherwise read the value
					fdout.write('</PERF>\n')   # End this well
					self.state = self.ST_IN_WELL
					continue
				if token[0] == 'ident':        # Otherwise read the value
					value = scanner.read()     # Read next token
					fdout.write("<"+token[1]+">"+value[1]+"</"+token[1]+'>')
					continue
		self.writePostamble(fdout)	
					
if __name__ == '__main__':
	f = open(sys.argv[1],'r')
	scanner = Scanner(pLexicon.ratesLexicon, f, sys.argv[1])
	xx = pPerfToXML()
	xx.convertFile(scanner,sys.stdout)
