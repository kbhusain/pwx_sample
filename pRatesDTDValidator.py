
from xml.parsers.xmlproc.xmlapp import ErrorHandler

class RatesDTDErrorHandler(ErrorHandler):
	def warning(self,msg):
		print "Warning: ", msg
		self.errors = 0

	def error(self,msg):
		print "Error: ", msg
		self.errors = 1

	def fatal(self,msg):
		print "Fatal: ", msg
		self.errors = 1

