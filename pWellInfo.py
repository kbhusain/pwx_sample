
from Tkinter import *
import Pmw
from string import find,upper
from pObject import cWellAllowedKeywords, cPerfAllowedKeywords

sAllowedWellParms = map(upper,cWellAllowedKeywords)
sAllowedPerfParms = map(upper,cPerfAllowedKeywords)
sPlottableWellParms = ['WELL_DEPTH_DATUM','MAX_DDP','MAX_BHP','MIN_BHP','BHP','WELL_PI','QO','QW','QG']
sPlottableWellParms.sort()

##################################################################################
# This is a class to define the user interface for a well information object 
# in a rates file.
##################################################################################

class frameWellPerfInfoParms(Frame):
    def __init__(self,master,wtype,useitem=None):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=X)
        self.wellItem = useitem                           # Track the 
        if (wtype == 0):
            self.names = sAllowedWellParms
        else:
            self.names = sAllowedPerfParms
        self.specialKeywords  = ['Name','Type','CD'] 
        xrow = 0
        self.widgets = []
        for name in self.names:
            widget = Pmw.EntryField(self,labelpos=W,label_text=name, validate=None,value='')
            widget.grid(row=xrow,column=0)
            self.val = widget.component('entry')
            self.val['width']=12
            xrow = xrow + 1
            self.widgets.append(widget);
        Pmw.alignlabels(self.widgets)
        if (useitem <> None): 
            self.mapObjToGui(useitem)


    ######################################################################
    # 
    ######################################################################
    def removeQuotes(self,incoming):
        xstr = incoming.replace("'",'')
        xstr = xstr.replace('"','')
        return xstr

    ######################################################################
    # 
    ######################################################################
    def mapObjToGui(self,thisitem):
        if (thisitem == None): # No parameters.
            return;
        self.wellItem = thisitem
        self.usedKeywords = self.wellItem.getKeywords()
        for self.widget in self.widgets:
            wtxt = self.widget.component('label')                   # Get the keyword from label 
            atext = wtxt['text']
            val  = self.wellItem.getKeywordValue(atext) # get value from object for label
            if atext in self.specialKeywords:
                val = self.removeQuotes(val)
            self.widget.setentry(val)

    # Only maps specific keywords and if item was checked for it.
    def mapGuiToObj(self,thisitem):
        if (thisitem == None): # No parameters.
            return;
        thisitem.clearKeywords()
        for self.widget in self.widgets:
            lbl = self.widget.component('label')
            txt = lbl['text'] 
            val = self.widget.component('entry').get()
            if txt in self.specialKeywords:
                val = "'" + val + "'"           # Add quote
            if len(val)>0:
                thisitem.addKeyword(txt,val)
       
    def clearFields(self):
        for w in self.widgets:
            w.setentry('')

###############################################################################
# This object is used to display information about a cWellInfo
###############################################################################

