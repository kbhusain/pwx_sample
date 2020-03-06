"""
##################################################################################################
This is a DEBUG utility only.
This file reads in an XML file from pPerfFileToXML.py and displays it as a tree.
##################################################################################################
"""
import os
import sys
import string
from Tkinter import *
import Pmw
from  Tree import *
from pPerfsXMLHandler import *


###################################################################
# The workhorse. Can this be class-ed into a box?
###################################################################
def get_contents(node):
	myname = node.full_id()   # get the list of parent ids, and self.
	fullname = string.join(myname,'/')
	print fullname
	outstr = ''
	if fullname == 'perfs':
		for child in myHandler.theTree:
			if child.tag == 'WELLS':
				thisID = child.ndx
				t.add_node(name=thisID,id=thisID, flag=1)
	else:
		node = myHandler.akeys[myname[-1]]
		if node.tag == 'WELLS':
			for pe in node.perfs:
				t.add_node(name=pe.tag,id=pe.ndx, flag=1)
		if node.tag == 'PERF':
			node = myHandler.akeys[myname[-1]]
			print myname, node
			for k in node.attributes.keys():
				thisID = node.attributes[k]
				lbl = k + ":" + thisID
				outstr = outstr + lbl + '\n'
				t.add_node(name=lbl,id=thisID, flag=0)
	editBox.settext(outstr)
		
def buttonPress(b):
	print "Hey -> ", b

if __name__ == '__main__':
	root=Tk()
	root.title("Perforations viewer")
	
	fd = open(sys.argv[1],'r')
	myHandler = PerfsHandler()   # The holder.
	sxp = make_parser()    # 
	sxp.setContentHandler(myHandler)
	sxp.parse(fd)

	t=Tree(master=root, root_id='perfs', root_label='Perforations',
		get_contents_callback=get_contents, width=300)
	t.grid(row=0, column=0, sticky='nsew') 

	root.grid_rowconfigure(0, weight=1)
	root.grid_columnconfigure(0, weight=1)
	sb=Scrollbar(root)
	sb.grid(row=0, column=1, sticky='ns')
	t.configure(yscrollcommand=sb.set)
	sb.configure(command=t.yview)
	sb=Scrollbar(root, orient=HORIZONTAL)
	sb.grid(row=1, column=0, sticky='ew')
	t.configure(xscrollcommand=sb.set)
	sb.configure(command=t.xview) 
	t.focus_set()

   
	btnBox = Pmw.ButtonBox(root)
	btnBox.grid(row=2, column=0, columnspan=3)
	btnBox.add('Quit',   command=root.quit)
	btnBox.add('Add',    command= lambda b = 'add': buttonPress(b)) 
	btnBox.add('Del',    command= lambda b = 'del': buttonPress(b)) 
	
	editBox  = Pmw.ScrolledText(root,labelpos=N,label_text='Contents',usehullsize=1,
			hull_height=400,hull_width=300,text_wrap=None)
	editBox.grid(row=0,rowspan=2,column=2,sticky='nsew')
	
	# expand out the root 
	t.root.expand() 
	root.mainloop()
