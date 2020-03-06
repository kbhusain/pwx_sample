

from Tkinter import *
import Pmw
from tkMessageBox import showwarning , showerror
from tkSimpleDialog import askstring
from tkFileDialog import *
import string
from pObject import *

from cModelParser import *
from pModel import *
from pCompositional  import *

##########################################################################################
# Create a frame and put all the Compositional items in it
##########################################################################################
class frameCompositionalParms(Frame):
	def __init__(self,master):
		Frame.__init__(self,master,relief='raised',bd=3)
		self.pack(expand=YES)

		self.widgets = []
		self.compositionalParms = pCompositional();
		names = self.compositionalParms.getKeywords(); 
		xrow = 0
		names.sort()
		for n in names:
			lname = self.compositionalParms.getKeywordLabel(n)
			f1 = Frame(self)
			f1.pack(side=TOP,fill=X,expand=0)
			w = Pmw.EntryField(f1,labelpos=W,label_text=lname, validate={'validator':'real','minstrict':0},value=10)
			self.widgets.append(w)
			w.pack(side='left',fill=X,expand=0)
			val = w.component('entry')
			val['width']=10
			xrow = xrow + 1
		Pmw.alignlabels(self.widgets)
		#
		# Now create a text entry for the binary coefficients 
		#
		self.mpFrame= Pmw.NoteBook(self)
		self.mpFrame.pack(side=TOP,expand=1,fill=BOTH)
		self.fBinary = self.mpFrame.add('Binary Coefficient')
		self.fInit  = self.mpFrame.add('Initial Component')
		self.fComp  = self.mpFrame.add('Component')
		self.fSeparator = self.mpFrame.add('Separator')
		self.fGradient  = self.mpFrame.add('Gradient')


		self.binaryCoeffText = Pmw.ScrolledText(self.fBinary,borderframe=1,labelpos=N,label_text ='Binary Coeff', text_wrap='none',
			usehullsize=1, hull_width=500, hull_height=200)
		self.binaryCoeffText.pack(side=RIGHT,fill=Y,expand=YES)

		self.initialCompText = Pmw.ScrolledText(self.fInit,borderframe=1,labelpos=N,label_text ='Initial Comp Value', text_wrap='none',
			usehullsize=1, hull_width=500, hull_height=200)
		self.initialCompText.pack(side=RIGHT,fill=Y,expand=YES)

		self.componentPropText = Pmw.ScrolledText(self.fComp,borderframe=1,labelpos=N,label_text ='Component Properties', text_wrap='none',
			usehullsize=1, hull_width=500, hull_height=200)
		self.componentPropText.pack(side=RIGHT,fill=Y,expand=YES)

		self.gradientText = Pmw.ScrolledText(self.fGradient,borderframe=1,labelpos=N,label_text ='Gradient Properties', text_wrap='none',
			usehullsize=1, hull_width=500, hull_height=200)
		self.gradientText.pack(side=RIGHT,fill=Y,expand=YES)

		self.separatorText = Pmw.ScrolledText(self.fSeparator,borderframe=1,labelpos=N,label_text ='Separator Text', text_wrap='none',
			usehullsize=1, hull_width=500, hull_height=200)
		self.separatorText.pack(side=RIGHT,fill=Y,expand=YES)

		f1 = Frame(self)
		f1.pack(side=TOP,fill=X,expand=0)
		self.enabledWidget = Button(f1,text ="Save Changes",command=self.saveme)
		self.enabledWidget.pack(side=LEFT,expand=0)

	#######################################################################
	# This maps my rock fluid parameters to the user interface objects. 
	####################################################################### 
	def mapObjToGui(self,myparms):
		if (myparms == None): # No parameters.
			return;
		self.compositionalParms = myparms
		for w in self.widgets:
			txt = w.component('label')			        # Get the keyword from label 
			val  = myparms.getKeywordValue(txt['text']) # get value from object for label
			w.setentry(val)
		self.binaryCoeffText.settext("".join(myparms.stringedArray['BINARY_COEFFICIENTS']))
		self.initialCompText.settext("".join(myparms.stringedArray['INITIAL_COMPOSITION']))
		self.componentPropText.settext("".join(myparms.stringedArray['COMPONENT_PROPERTIES']))
		self.gradientText.settext(myparms.gradient.getEditableString(showHeader=1))
		self.separatorText.settext(myparms.separator.getEditableString(showHeader=1))

	def saveme(self):
		for w in self.widgets:
			txt = w.component('label')
			val = w.component('entry').get()
			self.compositionalParms.parseKeyword(txt['text'],val)
		xstr = self.binaryCoeffText.get()
		self.compositionalParms.stringedArray['BINARY_COEFFICIENTS'] =  xstr.split('\n')
		xstr = self.initialCompText.get() 
		self.compositionalParms.stringedArray['INITIAL_COMPOSITION'] =  xstr.split('\n')
		xstr = self.componentPropText.get() 
		self.compositionalParms.stringedArray['COMPONENT_PROPERTIES'] =  xstr.split('\n')

		myparms = self.compositionalParms 
		for txtb,obj  in [(self.separatorText,myparms.separator), (self.gradientText,myparms.gradient)]: 
			xstr = txtb.get() 
			sln = xstr.split('\n')
			ilo = pLineObject()
			for x in xstr: 
				ilo.setLine(x)
				obj.parseLine(ilo)
		
	#######################################################################
	# This maps my user interface objects to the rock fluid parameters ...
	####################################################################### 
	def mapGuiToObj(self,myparms):
		"""
		Copy the items from the gui to the myparms object.
		"""
		if (myparms == None): return;
		self.compositionalParms = myparms
		self.saveme()


if __name__ == '__main__':
	r = Tk()
	f = frameCompositionalParms(r)
	r.mainloop()
