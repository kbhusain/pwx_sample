#! /usr/env/python

from Tkinter import *
import Pmw
import sys, string
import os
import WizardShell

#############################################################################
# The installation information can be kept here.
#############################################################################



class Installer(WizardShell.WizardShell):
	wizname = 'Install Widgets'
	panes   = 4

	def createButtons(self):
		self.buttonAdd('Cancel',			command=self.quit, state=1) 
		self.nextB = self.buttonAdd('Next', command=self.next, state=1)
		self.prevB = self.buttonAdd('Prev', command=self.prev, state=0)
			   
	def createTitle(self, idx, title):
		label = self.createcomponent('l%d' % idx, (), None,
								Label,(self.pInterior(idx),),
								text=title,
								font=('courier', 18, 'bold', 'italic'))
		label.pack()
		return label
	
	def createExplanation(self, idx):
		text = self.createcomponent('t%d' % idx, (), None,
									Text,(self.pInterior(idx),),
									bd=0, wrap=WORD, height=6)
		fd = open('install%d.txt' % (idx+1))
		text.insert(END, fd.read())
		fd.close()
		text.pack(pady=15)
			
	def createPanelOne(self):
		self.createTitle(0, 'Welcome!')
		self.createExplanation(0)

	def createPanelTwo(self):
		self.createTitle(1, 'Select Destination\nDirectory')
		self.createExplanation(1)

		#
		# Create your elaborate frame here
		# 
		frame = Frame(self.pInterior(1), bd=2, relief=GROOVE) 
		bframe = Frame(frame, bd=2, relief=GROOVE) 
		bframe.pack(side=TOP,expand=1)
		self.entry = Label(bframe, text=os.getenv("HOME") , font=('Courier', 10))
		self.entry.pack(side=LEFT, padx=10)
		self.btn   = Button(bframe, text='Browse...')
		self.btn.pack(side=LEFT, ipadx=5, padx=5, pady=5)
		bframe = Frame(frame, bd=2, relief=GROOVE)
		bframe.pack(side=TOP,expand=1)
		self.modelName = Pmw.EntryField(bframe, labelpos=W, label_text='MODEL NAME')
		self.modelName.pack(side=BOTTOM, padx=10)
		frame.pack()
			
	def createPanelThree(self):
		self.createTitle(2, 'Select Components')
		self.createExplanation(2)
		frame = Frame(self.pInterior(2), bd=0)
		idx = 0
		for label, lval in [('BLOCK_SIZE',''),('NX','10'),
							('NY','10'),
							('NZ','10')]:
			lbl = Label(frame, text=label).grid(row=idx, column=0, sticky=W)
			t0 = Pmw.EntryField(frame, labelpos=W, label_text='',value=lval).grid(row=idx,column=1)
			#ck  = Checkbutton(frame).grid(row=idx, column=0)
			#siz = Label(frame, text=).grid(row=idx, column=5)
			idx = idx + 1
		frame.pack()
			
	def createPanelFour(self):
		self.createTitle(3, 'Finish Installation')
		self.createExplanation(3)

	def createInterface(self):
		WizardShell.WizardShell.createInterface(self)
		self.createButtons()
		self.createPanelOne()
		self.createPanelTwo()
		self.createPanelThree()
		self.createPanelFour()
		
	def done(self):
		print 'This is where the work starts!'

if __name__ == '__main__':
	install = Installer()
	install.run()
