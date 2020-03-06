
from Tkinter import *
import Pmw
import os,sys, errno,fcntl,string 

externalExtractionString = "bash /red/ssd/appl/khusain/parallelExtract.ksh %s /red/simdata/EXT400/%s"
tuser = os.getenv('USER')
fname = '/red/restart/lincx/ABSF2005/AD_53/AD_53.smspec'
tcmd = externalExtractionString % (fname,tuser)
print tcmd


def readappend(fh,_):
	try: mstr = fh.read()
	except IOError, (errnum,mstr):
		if errnum != errno.EAGAIN: raise
	if mstr == '': sys.exit(0)
	global slb_list
	slb_list.insert("end",mstr[:-1])

def make_nonblocking(fh):
	if hasattr(fh,'fileno'): fh = fh.fileno()
	fcntl.fcntl(fh,fcntl.F_SETFL,os.O_NDELAY | fcntl.fcntl(fh,fcntl.F_GETFL))

r = Tk() 
slb = Pmw.ScrolledListBox(r,items=[],labelpos=N,label_text=tcmd)
slb.pack(side=TOP,fill='both',expand=1)
slb_list = slb.component('listbox')

pih = os.popen(tcmd)
#pih = sys.stdin
make_nonblocking(pih)
tkinter.createfilehandler(pih,tkinter.READABLE,readappend)

r.mainloop()

