
import sys
from Tkinter import *
import Pmw
from tkMessageBox import showwarning, askyesno
from tkSimpleDialog import *

class calibrationObject:
	def __init__(self):
		self.calibString = """#!/bin/sh
#PBS -l nodes=14,walltime=180:00:00
#PBS -N utcalib
#PBS -o cal.out
#PBS -e cal.err
#PBS -V
#PBS -S /bin/csh
#PBS -V 
##PBS -M  ! email address
#PBS -me     
#PBS -q parallel@plcc

EX='STR_EX'
cd /red/ssd/usr/awajima/eaomaa/Powers/Calibration
MODEL=STR_MODEL
well_test="STR_well_test"
#WHP, QLIQ, QOIL,BHP
Design_Variable="STR_Design_Variable"
max_no_runs=STR_max_no_runs
calib_tol=STR_calib_tol
Well_percentage=STR_Well_percentage
well_flow_table="STR_well_flow_table"
flow_table_file="STR_flow_table_file"

run_no=STR_run_no
Decision_Variable=STR_Decision_Variable
PI_USED="STR_PI_USED"
Max_Mult=STR_Max_Mult

no_match=1

recurrent=`grep RECURRENT_DATA data/$MODEL.model | grep -v "#" | grep -v "!" | grep -v "/ " | awk '{print $2}'`
recurrent=`echo $recurrent | sed -e "s/'//g"`
perf_file=`grep WELL_PERFS data/$MODEL.model | grep -v "#" | grep -v "!" | grep -v "/ " | awk '{print $2}'`
perf_file=`echo $perf_file | sed -e "s/'//g"`

if [ ! -d calib_output ]
 then
 mkdir calib_output
fi

if [ ! -d stout_calib ]
 then
 mkdir stout_calib
fi
#cat $well_test | awk '{print $1"  "$2"  "$5"  "$9"  "$10"  "$11"  "$14}' > welltest$$

cat $PBS_NODEFILE
while [ $run_no -le $max_no_runs ] && [ $no_match -gt 0 ] ; do
   if [ -f calib_output/$MODEL.new_PI ] && [ $run_no -eq 2 ] ;
    then
    if [ $Decision_Variable = "PI" ] ; then
     echo "INCLUDE_FILE  'calib_output/$MODEL.new_PI'" >> $recurrent
    fi
    if [ $Decision_Variable = "RF" ] ; then
     echo "INCLUDE_FILE  'calib_output/$MODEL.perf_Mod'" >> $recurrent
    fi
   fi
 mpirun.ch_gm -np 14 -machinefile $PBS_NODEFILE $EX/powers2004r2.5b data/${MODEL}.model > stout_calib/${MODEL}.out_$run_no
   echo "'POWERS'" > $MODEL.input_$run_no
   echo $MODEL >> $MODEL.input_$run_no
   echo "'$well_test'" >> $MODEL.input_$run_no
   echo "'$well_flow_table'" >> $MODEL.input_$run_no
   echo "'$flow_table_file'" >> $MODEL.input_$run_no
   echo "'$Decision_Variable'" >> $MODEL.input_$run_no
   echo "'$Design_Variable'" >> $MODEL.input_$run_no
   echo "$run_no  $run_no" >> $MODEL.input_$run_no
   echo "$calib_tol" >> $MODEL.input_$run_no
   echo "$PI_USED" >> $MODEL.input_$run_no
   echo "$Well_percentage" >> $MODEL.input_$run_no
   echo "$Max_Mult" >> $MODEL.input_$run_no
 ./CALIBRATION.EXE $MODEL.input_$run_no
 no_match=`wc -l calib_output/${MODEL}_badwells$run_no | awk '{print $1}'`
 run_no=`expr $run_no + 1`
done
"""

	def writeOutput(self,where=None):
		if where == None:
			sys.stdout.write(self.calibString)


class makeCalibrationWindow(Frame):
	def __init__(self,parent,useThis):
		Frame.__init__(self,parent)
		self.parent = parent
		self.object = useThis
		self.pack(expand=YES,fill=X)
		self.parms = {}
		self.parms['EX']    ='/data1/appl/test/bin'
		self.parms['MODEL'] ='calib'
		self.parms['well_test'] = "welltest_27Jun2004"
		self.parms['Design_Variable'] = "WHP"
		self.parms['max_no_runs'] = '20'
		self.parms['calib_tol'] = '10'
		self.parms['Well_percentage'] = '10'
		self.parms['well_flow_table'] = 'data/calib.recurrent'
		self.parms['flow_table_file'] = "utmnflowtables_newfmt"
		self.parms['run_no'] = "1"
		self.parms['Decision_Variable'] = "PI"
		self.parms['PI_USED'] = "TEST"
		self.parms['Max_Mult'] = "TEST"

		self.widgets = []
		xrow = 0
		for name in self.parms.keys():
			w = Pmw.EntryField(self,labelpos=W,label_text=name, validate=None) 
			w.pack(side=TOP,fill=X,expand=1)
			xrow=xrow+1
			w.setentry(self.parms[name])
			self.widgets.append(w)
		Pmw.alignlabels(self.widgets,sticky='e')

		self.buttonForm = Frame(self)
		self.buttonForm.pack(side=TOP,fill=X,expand=1)
		self.buttonBox = Pmw.ButtonBox(self.buttonForm,labelpos='n',label_text='Actions',orient='horizontal',padx=0)
		self.buttonBox.pack(side=LEFT,expand=1,fill=Y)
		self.buttonBox.add('Run',command = lambda s=self :  s.runCommand());
		self.buttonBox.add('Quit',command = lambda s=self :  sys.exit());

	def runCommand(self):
		for w in self.widgets:
			ent = w.component('label')
			name = ent['text'] 
			val  = w.get()
			strname = 'STR_'+name
			self.object.calibString = self.object.calibString.replace(strname,val)
		self.object.writeOutput()

if __name__ == '__main__':
	root = Tk()
	root.geometry("%dx%d+0+0" %(800,450))
	q = calibrationObject()
	calib = makeCalibrationWindow(root,q)
	root.mainloop()

