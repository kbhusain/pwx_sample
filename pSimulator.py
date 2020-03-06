#
# This is special since it only deals with specific options. 
# These options affect how you deal with data so they are 
# created for you even if unspecified in the input.
#
from pObject import *
from string import *

class pSimulator(pObject):
    def __init__(self,iLineNumber=0):
        pObject.__init__(self,iLineNumber)
        pObject.setDelimiters(self,'BEGIN_SIMULATOR_OPTIONS','END_SIMULATOR_OPTIONS')
        self.aKeywords['CAPILLARY_PRESSURE_OPTION'] = 'LEVERETT_J_FUNCTION'
        self.aKeywords['INITIALIZATION_OPTION'] = 'NON_EQUILIBRIUM'
        self.aKeywords['LINEARIZATION_OPTION'] = 'IMPLICIT'
        self.aKeywords['PERMEABILITY_VALUE_X'] = 'BLOCK_CENTER'
        self.aKeywords['PERMEABILITY_VALUE_Y'] = 'BLOCK_CENTER'
        self.aKeywords['PERMEABILITY_VALUE_Z'] = 'BLOCK_CENTER'
        self.aKeywords['PRESSSURE_INTERPOLATION_OPTION'] = 'LINEAR'
        self.aKeywords['SATURATION_INTERPOLATION_OPTION'] = 'LINEAR'
        self.aKeywords['WELL_FORMULATION'] = 'EXPLICIT_WELL'
        self.aOptions = {}
        self.aOptions['CAPILLARY_PRESSURE_OPTION'] = ('PC_FUNCTION','LEVERETT_J_FUNCTION')
        self.aOptions['INITIALIZATION_OPTION'] = ('GRAVITY_CAPILLARY_EQUILIBRIUM','NON_EQUILIBRIUM')
        self.aOptions['LINEARIZATION_OPTION'] = ('IMPLICIT','IMPES')
        self.aOptions['PERMEABILITY_VALUE_X'] = ('BLOCK_CENTER','BLOCK_FACE')
        self.aOptions['PERMEABILITY_VALUE_Y'] = ('BLOCK_CENTER','BLOCK_FACE')
        self.aOptions['PERMEABILITY_VALUE_Z'] = ('BLOCK_CENTER','BLOCK_FACE')
        self.aOptions['PRESSSURE_INTERPOLATION_OPTION'] = ('LINEAR','ANALYTIC')
        self.aOptions['SATURATION_INTERPOLATION_OPTION'] = ('LINEAR','ANALYTIC')
        self.aOptions['WELL_FORMULATION'] = ('EXPLICIT_WELL','IMPLICIT_BHP','IMPLICIT_MOB','IMPLICIT_BHP_MOB')

    def doConsistencyCheck(self):
        self.clearErrors() 
        self.lines = self.getNonCommentLines()
        for iLine in self.lines:
            items = split(iLine)
            if (len(items) == 2):
                keyword = items[0]
                if keyword in self.aKeywords.keys():
                    k = self.aKeywords[keyword]
                    opt = self.aOptions[keyword]
                    if (not k in opt):
                        self.addErrorMessage('Unrecognized option for keyword in input: [%s,%s]\n' % (keyword,k))
						ostr = "".join(opt) 
                        self.addWarningMessage("Allowed options for %s = ( %s )\n" % (keyword, ostr))
                else:
                    self.addWarningMessage('Unrecognized keyword in Simulator: [%s,%s]\n' % (keyword,iLine))
            else:
				if not items[0] in ['TITLE','Title']: 
                	self.addWarningMessage('Questionable input: [%s]\n' % (iLine))

    def parseLine(self,incoming):
        if (pObject.parseLine(self,incoming) > 0):          # Add the line here for output back. 
            self.items = split(incoming)    # check if you have keywords
            if (len(self.items) == 2):
                self.parseKeyword(self.items[0],self.items[1])


    def parseKeyword(self,keyword,value):
        if (self.aKeywords.has_key(keyword)):
            self.aKeywords[keyword] = value;
        else:
            self.str = "Error! Simulator Block  * Unrecognized keyword= %s attempt to assign %s\n" % (keyword,value);
            self.addWarningMessage(self.str)
