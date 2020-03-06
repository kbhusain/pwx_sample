


import os, sys

from xml.parsers.xmlproc import xmlval 
from pRatesDTDValidator import RatesDTDErrorHandler

xv = xmlval.XMLValidator()
ve = RatesDTDErrorHandler(xv.app.locator)
xv.set_error_handler(ve)
xv.parse_resource(sys.argv[1])

