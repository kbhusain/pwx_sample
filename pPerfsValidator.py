


import os, sys

from xml.parsers.xmlproc import xmlval 
from pPerfsDTDValidator import PerfsDTDErrorHandler

xv = xmlval.XMLValidator()
ve = PerfsDTDErrorHandler(xv.app.locator)
xv.set_error_handler(ve)
xv.parse_resource(sys.argv[1])

