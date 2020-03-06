from Tkinter import *
import Pmw
from tkSimpleDialog import askstring 

"""
# Description: A megawidget to manage items in a list of options. 
# Author: Kamran Husain

Displays a list of items. There are three buttons on the bottom. 
Two are shown, the third can be made visible by function call.

[Multiple selections are done with the control or shift key pressed 
while clicking in the list.]

As a programmer, you will most likely use only two functions: 
	setSelectionList(inp) - sets the list to the items in inp
	getSelectedList() - returns what the user selected. 

Don't use the other internal features without reading the code. ;-)
	
"""
class pModifiableList(Pmw.MegaWidget):
	def __init__(self,parent=None,**kw):
		optiondefs = (
			('fill', 'red', None),
			('defaultString', 'None', None),
			('useThis', ['a','b','c','d'], None),
			) 

		self.deleteCommand = None
		self.selectCommand = None
		self.editCommand   = None

		self.defineoptions(kw,optiondefs)
		Pmw.MegaWidget.__init__(self,parent)
		interior = self.interior()

		self.itemListC = self.createcomponent('items', (), None, 
			Frame, (interior,), borderwidth=0)
		a = lambda s=self : s.callSelectionCommand()
		self.scrolledList  = Pmw.ScrolledListBox(self.itemListC, items=[], labelpos=None, 
				selectioncommand=a, listbox_selectmode=EXTENDED)
		self.fromList  = self.scrolledList.component('listbox')
		self.scrolledList.pack(side=TOP,fill=BOTH,expand=1)
		self.itemListC.pack(side=TOP,fill=BOTH,expand=1)

		self.scrolledList.setlist(self['useThis'])

		self.btnsForm = self.createcomponent('btnsForm', (), None, 
			Frame, (interior,), borderwidth=0)

		
		a = lambda s = self: s.addItemToList()
		self.btnAddItem   = Button(self.btnsForm,text='ADD',command=a)
		a = lambda s = self: s.delItemFromList()
		self.btnDelItem   = Button(self.btnsForm,text='DEL',command=a)
		a = lambda s = self: s.editItemInList()
		self.btnEditItem     = Button(self.btnsForm,text='EDIT',command=a)
		self.btnAddItem.pack(side=LEFT,fill=X,pady=5)
		self.btnDelItem.pack(side=LEFT,fill=X,pady=5)
		self.btnEditItem.pack(side=LEFT,fill=X,pady=5)
		self.btnEditItem.pack_forget()
		self.btnsForm.pack(side=TOP,fill=X,expand=1)

	def setSelectionCommand(self,a): 
		self.selectCommand = a 

	def callSelectionCommand(self):
		if self.selectCommand <> None: 
			self.selectCommand()

	def setWidth(self,v=40):	
		self.fromList['width']=v

	def clearList(self):
		self.fromList.delete(0,END)

	def showDefaultButton(self,show=1):
		if show==1: 
			self.btnEditItem.pack()
		else:
			self.btnEditItem.pack_forget()

	def addDefaultString(self):
		"""
		The default string is entered as item 0 on the left side. 
		"""
		if len(self['defaultString']) > 1:		
			self.usesList.insert(0,self['defaultString'])

	def editItemInList(self,xstr):
		if self.editCommand <> None: self.editCommand(self.parameter)

	def doAddItem(self,xstr):
		xlist = self.fromList.curselection()      # Get entire selection
		k = 0
		if len(xlist) > 0: k = xlist[0]
		self.fromList.insert(k,xstr)

	def doRemoveItem(self):
		"""
		Removes any selected items from the right side list...
		"""
		xlist = self.fromList.curselection()      # Get entire selection
		for k in xlist: 
			if self.deleteCommand <> None: self.deleteCommand(k)
			self.fromList.delete(k)   # Already selected list.

	def setList(self,doThis,erasePrevious=1):
		"""
		Sets the list on the left side to select items from
		If erasePrevious is set to 0, the right list is left untouched.
		"""
		self['useThis'] = doThis
		self.scrolledList.setlist(self['useThis'])
		#self.fromList.delete(0,END)
		#for i in doThis: self.fromList.insert(END,i)
		
	def delItemFromList(self):
		self.doRemoveItem()

	def addItemToList(self):
		x = askstring("New", "Enter:")
		self.doAddItem(x)


if __name__ == '__main__':
	root=Tk()
	root.title("Eatme")
	Pmw.initialise()
	c =[ 'kamran', 'was', 'here', 'and', 'left','and','now','for','something','completely','different']
	g1 = pModifiableList(root,useThis=c)
	g1.pack(side=TOP,fill=BOTH)

	root.mainloop()
