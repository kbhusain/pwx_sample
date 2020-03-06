
##################################################################################################
# This is a Rate file parser. 
##################################################################################################
from string import *
from Plex import *
import pLexicon
import sys


##################################################################################################
# The class definition for the main program begins here
##################################################################################################
class pRateToXML:
	def __init__(self):
		self.tags = [] 
		self.ST_IDLE = 0
		self.ST_WAIT_FOR_DATE = 1
		self.ST_IN_DATE    = 2
		self.ST_IN_WELL    = 3
		self.ST_IN_KEYWORD = 4

	def writePreamble(self,fdout):
		fdout.write('<?xml version="1.0" standalone="yes"?>\n')
		fdout.write('<!DOCTYPE rates SYSTEM "Rates.DTD">\n')
		fdout.write('<rates>\n')
		#fdout.write('<author> Kamran Husain </author>\n')

	def writePostamble(self,fdout):
		fdout.write('</rates>')

	def convertFile(self,scanner,fdout):
		self.state = 0
		self.group = None
		self.lastdate = ""
		self.writePreamble(fdout)	
		while 1: 
			token = scanner.read()           # Check for input end
			if token[0] == None: break;
			elif token[1] == 'DATE': 	 		  # Check end condition
				token = scanner.read()        # Read next token
				self.lastdate = token[1]      # for the actual value
				fdout.write('<DATE value="%s"/>\n' % token[1])   # start of date
			elif token[1] == 'ENDWELLS': 	 		 # Check end condition
				fdout.write('</WELLS>\n');
			elif token[1] == 'WELLS': 	 		 # Check start condition
				fdout.write('<WELLS date="%s">' % self.lastdate);
			elif token[1] == '&WELL':        # got another well
				value = scanner.read()     # Read 'Name' keyword
				value = scanner.read()     # Read next token for well name 
				fdout.write("<WELL>\n<NAME>"+value[1]+"</NAME>\n")
				self.state = self.ST_IN_WELL
				continue
			if self.state == self.ST_IN_WELL:
				if token[0] == 'eob':          # Otherwise read the value
					fdout.write('</WELL>\n')   # End this well
					self.state = self.ST_IN_DATE
					continue
				if token[0] == 'ident':        # Otherwise read the value
					value = scanner.read()     # Read next token
					if token[1] in ['Fluid','Type']:
						fdout.write("<"+token[1]+' value="'+value[1]+'"/>')
					else:
						fdout.write("<"+token[1]+">"+value[1]+"</"+token[1]+'>')
					continue
		self.writePostamble(fdout)	
					
if __name__ == '__main__':
	f = open(sys.argv[1],'r')
	scanner = Scanner(pLexicon.ratesLexicon, f, sys.argv[1])
	xx = pRateToXML()
	xx.convertFile(scanner,sys.stdout)
