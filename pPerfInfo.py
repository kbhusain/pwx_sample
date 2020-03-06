#!/work0/kamran/Python-2.2.2/python


from Tkinter import *
import Pmw
from string import find

##################################################################################
# This is a class to define the user interface for a Perf information object 
# in a rates file.
##################################################################################

class framePerfInfoParms(Frame):
    def __init__(self,master,useitem=None):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=X)
        self.PerfItem = useitem                           # Track the 
        self.names = ['Name','Type','Well_Radius','CD',
                'Productivity_Index',
                'I','J','K','Rf','K_BOTTOM','K_TOP','GRID_NAME']
        xrow = 0
        self.widgets = []
        for name in self.names:
            widget = Pmw.EntryField(self,labelpos=W,label_text=name, validate=None,value='')
            widget.grid(row=xrow,col=0)
            self.val = widget.component('entry')
            self.val['width']=12
            xrow = xrow + 1
            self.widgets.append(widget);
        Pmw.alignlabels(self.widgets)
        if (useitem <> None): 
            self.mapObjToGui(useitem)

    def mapObjToGui(self,thisitem):
        if (thisitem == None): # No parameters.
            return;
        self.PerfItem = thisitem
        self.usedKeywords = self.PerfItem.getKeywords()
        for self.widget in self.widgets:
            wtxt = self.widget.component('label')                   # Get the keyword from label 
            atext = wtxt['text']
            self.val  = self.PerfItem.getKeywordValue(atext) # get value from object for label
            if (find(self.val,'Error') <> -1):
                self.val = ''
            self.widget.setentry(self.val)

    # Only maps specific keywords and if item was checked for it.
    def mapGuiToObj(self,thisitem):
        if (thisitem == None): # No parameters.
            return;
        thisitem.clearKeywords()
        for self.widget in self.widgets:
            lbl = self.widget.component('label')
            txt = lbl['text'] 
            val = self.widget.component('entry').get()
            if len(val)>0:
                thisitem.addKeyword(txt,val)
       
    def clearFields(self):
        for w in self.widgets:
            w.setentry('')
            
        