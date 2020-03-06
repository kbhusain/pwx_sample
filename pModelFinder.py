


import os.path 
import sys

def visit(arg,dirname,files):
	for name in files: 
		f = name.rfind('.model')
		if f > 0: 
			fullname = dirname + os.sep + name
			xlines = open(fullname,'r').readlines()
			arg.append( "<MODEL>\n")
			arg.append( "<FULLPATH>%s</FULLPATH>\n" % fullname)
			arg.append( "<BASENAME>%s</BASENAME>\n" % os.path.basename(fullname))
			arg.append( "<COMMENTS>Comments go here </COMMENTS>\n")
			for ln in xlines:	
				for inc in ['INCLUDE_FILE','BINARY_FILE','TEXT_FILE']:
					f = ln.find(inc)
					if f > 0: arg.append("<%s>%s</%s>\n" % (inc,fullname,inc))
			arg.append( "</MODEL>\n")

retlist = []
retlist.append('<?xml version="1.0"?>\n')
retlist.append("<CATALOG>\n")
retlist.append("<ALLMODELS>\n")
os.path.walk(sys.argv[1],visit,retlist)
retlist.append("</ALLMODELS>\n")
retlist.append("</CATALOG>\n")
print "".join(retlist)
