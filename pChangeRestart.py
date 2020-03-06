"""
Substitutes the /red/restart/$USER if BINARY_DATA_DIRECTORY is not writeable.
If the BINARY_DATA_DIRECTORY is not found, create one for the user. 
"""
import sys, os, re

def verifyCopyModelFile(inputfile, filename):
	xlines = open(inputfile).readlines()
	modified = 0
	bindirfound = 0 
	j = 0 
	for xln in xlines:
		if not re.match("^\w*#",xln):
			f = xln.find('BINARY_DATA_DIRECTORY')
			if f >= 0:
				print xln
				bindirfound = 1
				items = xln.split()
				delete = 1
				odir = items[1]
				odir = odir.replace("'",'')
				foobar = odir + os.sep + 'foobar.txt'
				try:
					fd = open(foobar,'w')
				except:
					items[1] = "'/red/restart/" + os.getenv('USER')  +"'"
					delete = 0
					xlines[j] = " ".join(items) + "\n"
					print "I have to modify BINARY_DATA_DIRECTORY"
				if delete: os.remove(foobar)
				break
		j = j + 1  # Count the line numbers 
	if bindirfound == 0: 
		j = 0 
		for xln in xlines:
			if re.match('^\w*BEGIN_SIMULATOR_PARAMETERS',xln):
				xlines.insert(j+1,"BINARY_DATA_DIRECTORY '/red/restart/%s\n'" % os.getenv('USER'))
				modified = 1
				break
			j = j + 1
	
	fd = open(filename,'w') # Open the file for writing
	for xln in xlines: fd.write(xln)
	fd.close()
		#except:
	print " I write to .. " , filename
			
if __name__ == '__main__':
	if len(sys.argv) < 2: sys.exit(0)
	verifyCopyModelFile(sys.argv[1],sys.argv[2])





			

