
from Tkinter import *
from tkMessageBox import showwarning
import Pmw


class doKeywordQuery:
	def __init__(self,parent=None):
		self.parent = parent
		self.dict   = {}
		self.dlg    = None
		self.fw = None
		self.cbKeywords = None
		self.parms = None
		self.keywd = None
		self.value = None

	def useDictionary(self,dict={}):
		self.dict = dict

	def askQuery(self):
		self.dlg = Pmw.Dialog(self.parent,buttons=('OK','Cancel'),defaultbutton='OK',
			title='Set Keyword',command=self.doCommand)
		self.fw = Frame(self.dlg.interior())
		self.fw.pack(side=TOP,expand=1,fill=BOTH)
		self.cbKeywords = Pmw.ComboBox(self.fw,label_text='Keyword',labelpos='W',listbox_width=24,dropdown=1,
			scrolledlist_items=self.dict.keys(), selectioncommand=self.choseEntry)
		self.cbKeywords.pack(side=TOP,fill=X,expand=0)
		self.efValue = Pmw.EntryField(self.fw,labelpos='w',label_text='Value',validate=None)
		self.efValue.pack(side=TOP,fill=X,expand=0)
		self.dlg.activate()


	def choseEntry(self,keywd):
		v = self.dict.get(keywd,'')
		self.efValue.setentry(v)

	def doCommand(self,parms):
		if parms <> 'OK':
			self.keywd = None
			self.value = None
		else: 
			self.keywd = self.cbKeywords.get()
			self.value = self.efValue.get()
		self.dict[self.keywd] = self.value
		self.dlg.deactivate()
		self.dlg = None

if __name__ == '__main__':
	def dome():
		eatme = {}
		eatme['hello'] = 'world'
		eatme['python'] = 'rocketh'
		pp = doKeywordQuery(root)
		pp.useDictionary(eatme)
		pp.askQuery()
		print pp.keywd, pp.value, pp.dict
	
	root = Tk()
	b = Button(root,text='pushme',command = dome)
	b.pack(side=TOP,fill=BOTH,expand=0,padx=10,pady=10)
	root.mainloop()
	
