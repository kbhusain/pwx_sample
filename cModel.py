
#
# Create a frame and put all the MODEL_SIZE_PARAMETERS in it.
#
from Tkinter import *
import Pmw

#######################################################
#
#######################################################
class frameModelSizeParms(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=BOTH)
        self.f1 = Frame(self)
        self.f2 = Frame(self)
        self.f1.pack(expand=YES,side=LEFT)
        self.f2.pack(expand=YES,side=RIGHT)
        self.rvDates  = Pmw.EntryField(self.f1,labelpos=W,label_text="YYYY/mm/dd", validate={'validator':'date','min':'1970/1/1','max':'2010/12/31','minstrict':0,'format':'ymd'},value='1970/01/01')
        self.rvXnodes = Pmw.EntryField(self.f1,labelpos=W,label_text="XNODES", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvYnodes = Pmw.EntryField(self.f1,labelpos=W,label_text="YNODES", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvZnodes = Pmw.EntryField(self.f1,labelpos=W,label_text="ZNODES", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvPhases = Pmw.EntryField(self.f1,labelpos=W,label_text="Phases", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvCompletions =Pmw.EntryField(self.f1,labelpos=W,label_text="Completions", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvWells  = Pmw.EntryField(self.f1,labelpos=W,label_text="Wells", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvFTables  = Pmw.EntryField(self.f1,labelpos=W,label_text="Fluid Tables", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvEqRgns  = Pmw.EntryField(self.f1,labelpos=W,label_text="Equib Regions", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvMigLns  = Pmw.EntryField(self.f1,labelpos=W,label_text="Migration Lns", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        widgets1 = (self.rvDates,self.rvXnodes,self.rvYnodes,self.rvZnodes,self.rvPhases,
                    self.rvCompletions,self.rvWells,self.rvFTables,
                    self.rvEqRgns,self.rvMigLns)
        for widget in widgets1:
            widget.pack(fill=X,expand=YES,padx=10,pady=5)
            
        self.rvRockTbl  = Pmw.EntryField(self.f2,labelpos=W,label_text="Rock Tables", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=10)
        self.rvGridLvl  = Pmw.EntryField(self.f2,labelpos=W,label_text="Grid Levels", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=1)
        self.rvLgrRgns  = Pmw.EntryField(self.f2,labelpos=W,label_text="LGR Regions", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=1)
        self.rvMaxLgr   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max LGR Wells", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=1)
        self.rvGpParms   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Group Parms", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=1)
        self.rvGpCount   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Group Count", validate={'validator':'numeric','min':1,'max':1000,'minstrict':0},value=1)
        self.rvWellParms   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Well Parms", validate={'validator':'numeric','min':0,'max':1000,'minstrict':0},value=0)
        self.rvGpCond    = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Group Cond", validate={'validator':'numeric','min':0,'max':1000,'minstrict':0},value=0)
        self.rvActions   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Actions/Gp", validate={'validator':'numeric','min':0,'max':1000,'minstrict':0},value=0)
        self.rvRules   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Rules", validate={'validator':'numeric','min':0,'max':1000,'minstrict':0},value=0)
        self.rvWellCond   = Pmw.EntryField(self.f2,labelpos=W,label_text="Max Well Cond.", validate={'validator':'numeric','min':0,'max':1000,'minstrict':0},value=0)
        
        widgets2 = (self.rvRockTbl,self.rvGridLvl,self.rvLgrRgns,self.rvMaxLgr,
                    self.rvGpParms,self.rvGpCount,self.rvWellParms,self.rvGpCond,
                    self.rvActions,self.rvRules,self.rvWellCond)
        for widget in widgets2:
            widget.pack(fill=X,expand=YES,padx=10,pady=5)
        Pmw.alignlabels(widgets1)
        Pmw.alignlabels(widgets2)


def makeButton(root,text,side,fill,cmd=None):
    w = Button(root,text=text,bg='gray64',fg='green',borderwidth=4,relief='raised',command=cmd)
    w.pack(side=side,expand=YES,fill=fill)
    return w


##########################################################################################
# Create a frame and put all the SIMULATOR information in it.
##########################################################################################
class frameSimulatorParms(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=X)
        self.capOptions = ('PC_FUNCTION','LEVERETT_J_FUNCTION')
        self.initOptions = ('GRAVITY_CAPILLARY_EQUILIBRIUM','NON_EQUILIBRIUM')
        self.lineOptions = ('IMPLICIT','IMPES')
        self.permOptions = ('BLOCK_CENTER','BLOCK_FACE')
        self.pressOptions = ('LINEAR','ANALYTIC')
        self.wellOptions = ('EXPLICIT_WELL','IMPLICIT_BHP','IMPLICIT_MOB','IMPLICIT_BHP_MOB')
        self.gcbCapOptions  = self.makeComboBox("CAPILLARY_PRESSURE_OPTION",self.capOptions);
        self.gcbInitOptions  = self.makeComboBox("INITIALIZATION_OPTION", self.initOptions);
        self.gcbLineOptions  = self.makeComboBox("LINERIZATION_OPTION", self.lineOptions);
        self.gcbPermXOptions  = self.makeComboBox("PERMEABILITY_VALUE_X", self.permOptions);
        self.gcbPermYOptions  =self.makeComboBox("PERMEABILITY_VALUE_Y",self.permOptions);
        self.gcbPermZOptions  = self.makeComboBox("PERMEABILITY_VALUE_Z",self.permOptions);
        self.gcbPressOptions = self.makeComboBox("PRESSURE_INTERPOLATION_OPTION",self.pressOptions);
        self.gcbSattOptions  = self.makeComboBox('SATURATION_INTERPOLATION_OPTION',self.pressOptions);
        self.gcbWellOptions  = self.makeComboBox("WELL_FORMULATION", self.wellOptions);
        self.widgets2 = (self.gcbCapOptions,self.gcbInitOptions,self.gcbLineOptions,
                self.gcbPermXOptions,self.gcbPermYOptions,self.gcbPermZOptions,
                self.gcbPressOptions,self.gcbSattOptions,self.gcbWellOptions )
        for self.widget in self.widgets2:
            self.widget.pack(fill=NONE,expand=YES,padx=10,pady=5)
        for self.widget in self.widgets2:
            self.widget.selectitem(0)
          
        Pmw.alignlabels(self.widgets2)

    def makeComboBox(self,txt,opts):
        self.i = Pmw.ComboBox(self,labelpos=W,
                        label_text=txt, listheight=60,
                        listbox_width=24,scrolledlist_items=opts);
        return self.i
    
       # self.aKeywords['CAPILLARY_PRESSURE_OPTION'] = 'LEVERETT_J_FUNCTION'
       # self.aKeywords['INITIALIZATION_OPTION'] = 'NON_EQUILIBRIUM'
       # self.aKeywords['LINEARIZATION_OPTION'] = 'IMPLICIT'
       # self.aKeywords['PERMEABILITY_VALUE_X'] = 'BLOCK_CENTER'
       # self.aKeywords['PERMEABILITY_VALUE_Y'] = 'BLOCK_CENTER'
       # self.aKeywords['PERMEABILITY_VALUE_Z'] = 'BLOCK_CENTER'
       # self.aKeywords['PRESSSURE_INTERPOLATION_OPTION'] = 'NON_EQUILIBRIUM'
       # self.aKeywords['SATURATION_INTERPOLATION_OPTION'] = 'LINEAR_ANALYTIC'


##########################################################################################
# Create a frame and put all the ROCK and FLUID information in it.
##########################################################################################
class frameRockFluidParms(Frame):
    def __init__(self,master):
        Frame.__init__(self,master)
        self.pack(expand=YES,fill=X)
        self.rvDeadCell     = Pmw.EntryField(self,labelpos=W,label_text="DEAD_CELL_POROSITY", validate={'validator':'real','minstrict':0},value=10)
        self.rvInjectedGas  = Pmw.EntryField(self,labelpos=W,label_text="INJECTED_GAS_DENSITY", validate={'validator':'real','minstrict':0},value=10)
        self.rvInjectedWtr  = Pmw.EntryField(self,labelpos=W,label_text="INJECTED_WATER_DENSITY", validate={'validator':'real','minstrict':0},value=10)
        self.rvMinThickness = Pmw.EntryField(self,labelpos=W,label_text="MINIMUM_THICKNESS", validate={'validator':'real','minstrict':0},value=10)
        self.rvPermCutoff   = Pmw.EntryField(self,labelpos=W,label_text="PERMEABILITY_CUTOFF", validate={'validator':'real','minstrict':0},value=10)
        self.rvPorosCutoff  = Pmw.EntryField(self,labelpos=W,label_text="POROSITY_CUTOFF", validate={'validator':'real','minstrict':0},value=10)
        self.rvPorosRefer   = Pmw.EntryField(self,labelpos=W,label_text="POROSITY_REFERENCE", validate={'validator':'real','minstrict':0},value=10)
        self.rvRockCompress = Pmw.EntryField(self,labelpos=W,label_text="ROCK_COMPRESSIBILITY", validate={'validator':'real','minstrict':0},value=10)
        self.widgets = (self.rvDeadCell,self.rvInjectedGas ,self.rvInjectedWtr ,
            self.rvMinThickness,self.rvPermCutoff ,self.rvPorosCutoff ,self.rvPorosRefer ,self.rvRockCompress)
        for self.widget in self.widgets:
            self.widget.pack(fill=NONE,expand=YES,padx=10,pady=5)
    
    def mapObjToGui(self,rockparms):
        if (rockparms == None): # No parameters.
            return;
        self.rvDeadCell.setentry(str(rockparms.fDeadCellPorosity))
        self.rvInjectedGas.setentry(str(rockparms.fInjectedGasDensity ))
        self.rvInjectedWtr.setentry(str(rockparms.fInjectedWaterDensity))
        self.rvMinThickness.setentry(str(rockparms.fMinimumThickness ))
        self.rvPermCutoff.setentry(str(rockparms.fPermeabilityCutoff))
        self.rvPorosCutoff.setentry(str(rockparms.fPorosityCutoff))
        self.rvPorosRefer.setentry( str(rockparms.fPorosityReferencePressure))
        self.rvRockCompress.setentry(str(rockparms.fRockCompressability))


class dframeSimulatorParms(Frame):
    def __init__(self,master):
        Frame.__init__(self,bg='gray50')
        self.pack(side=LEFT,expand=NO,fill=BOTH)
        a =lambda s=self, l=self.flist: s.quit();
        self.btn1= makeButton(self,'Quit',LEFT,BOTH,a)
#        a =lambda s=self, l=self.flist: s.askFileName(l);
        self.btn1= makeButton(self,'Add',LEFT,BOTH,a)
#        a =lambda s=self, l=self.flist: s.clearText(l);
        self.btn2 = makeButton(self,'Clr',LEFT,BOTH,a)
#        a =lambda s=self, l=self.flist: s.clearSelection(l);
        self.btn2 = makeButton(self,'Del',LEFT,BOTH,a)
#        a =lambda s=self, l=self.flist: s.changeDirectory();
        self.btn4 = makeButton(self,'Cwd',LEFT,BOTH,a)
#        self.btn3= Button(self,text='View',bg='blue',fg='yellow',borderwidth=4,relief='raised',
#                     command=lambda s=self, l=self.flist: s.listText(l))
#        self.btn3.pack(side=LEFT,expand=YES,fill=BOTH)


class App:
    def __init__(self,master):
        fm = Frame(master) # the graph must exist on the master.
        sm = (fm)
        fm.pack()
         
if __name__ == '__main__':
    root =Tk()
    root.option_add('*font',('arial',10,'bold'))
    root.title("LogPro application")
    display= App(root)
    root.mainloop()
