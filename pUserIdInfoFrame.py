
from Tkinter import *
import os
import Pmw

from tkMessageBox import showwarning, askyesno
#from tkSimpleDialog import askstring
#from tkFileDialog import *

def returnDefinedUserDirectory():
	ret = 		{ "abbasrt" : "/home/pet_2/eorrta",\
					"agilma" : "/home/pet_2/eormaa",\
					"ahmeaa0j" : "/home/ecc_12/eaoaaa",\
					"ahmesj0b" : "/home/pet_6/ahmesj0b",\
					"alburara" : "/home/pet_5/alburara",\
					"alwanka" : "/home/ecc_13/eaokaa",\
					"aruriad" : "/home/pet_2/eorada",\
					"awamaa0b" : "/home/pet_2/eoraaa",\
					"awamiba" : "/home/pet_2/eorbaa",\
					"awamifh" : "/home/pet_2/eorfha",\
					"awbethuh" : "/home/pet_2/awbethuh",\
					"banagamr" : "/home/pet_2/eormrb",\
					"bukhamny" : "/home/pet_3/bukhamny",\
					"chiffoyx" : "/home/pet_2/chiffoyx",\
					"corredjh" : "/home/pet_6/corredjh",\
					"dialdiha" : "/home/pet_2/dialdiha",\
					"edillofl" : "/home/pet_2/eorfle",\
					"elrafiea" : "/home/pet_3/elrafiea",\
					"fazaaam" : "/home/pet_2/eoramf",\
					"garnisa" : "/home/pet_1/eorsag",\
					"ghamma0t" : "/home/pet_2/eormag",\
					"halomopm" : "/home/exp_8/halomopm",\
					"hamaam0a" : "/home/pet_5/hamaam0a",\
					"hamamhh" : "/home/pet_5/hamamhh",\
					"hasaah0c" : "/home/pet_2/eorahh",\
					"hotysa" : "/home/pet_6/hotysa",\
					"huangkx" : "/home/pet_3/eorkxh",\
					"humaaa0n" : "/home/pet_2/esbaah",\
					"hussax0g" : "/home/pet_2/eoraxh",\
					"jameina" : "/home/pet_1/jameina",\
					"jilanisz" : "/home/pet_5/jilanisz",\
					"khanim" : "/home/pet_2/eorimk",\
					"khawha0a" : "/home/ecc_18/eaohak",\
					"krishnam" : "/home/pet_2/eoramk",\
					"kumarat" : "/home/ecc_17/kumarat",\
					"laukk" : "/home/ecc_18/eaokkl",\
					"lemoinme" : "/home/pet_2/eormel",\
					"lincx" : "/home/pet_2/eorcxl",\
					"liujs" : "/home/pet_2/eorjsl",\
					"lucianer" : "/home/pet_2/eorerl",\
					"marquebo" : "/home/pet_2/eorbom",\
					"marzah0e" : "/home/pet_2/eorahm",\
					"mohama0d" : "/home/pet_2/eormma",\
					"muslumak" : "/home/pet_2/eocakm",\
					"pavlasej" : "/home/pet_2/eorejp",\
					"qahtaa19" : "/home/ecc_17/eaoaag",\
					"qahtas1w" : "/home/pet_2/qahtas1w",\
					"shammm0q" : "/home/pet_2/eormas",\
					"shenawsh" : "/home/pet_3/shenawsh",\
					"shubhm0b" : "/home/pet_3/shubhm0b",\
					"siual" : "/home/ecc_16/eaoals",\
					"sultanaj" : "/home/pet_6/sultanaj",\
					"thuwaijs" : "/home/pet_3/eorjst",\
					"towailhs" : "/home/pet_2/towailhs",\
					"ubahm" : "/home/pet_2/ubahm",\
					"vohrair" : "/home/pet_2/eorirv",\
					"whitejp" : "/home/pet_2/eorjpw",\
					"yuenbb" : "/home/pet_2/eorbby",\
					"abdmohra" : "/home/ecc_17/eaoraa",\
					"ahmeaa0j" : "/home/ecc_12/eaoaaa",\
					"awajima" : "/home/ecc_12/eaomaa",\
					"baddouma" : "/home/ecc_17/eaomab",\
					"badrma" : "/home/ecc_17/eaomxb",\
					"burikamm" : "/home/ecc_16/eaommb",\
					"dossmn0f" : "/home/ecc_1/dossmn0f",\
					"gehaidya" : "/home/ecc_12/gehaidya",\
					"habibawa" : "/home/ecc_18/eaowah",\
					"hajrmk0h" : "/home/ecc_17/hajrmk0h",\
					"harbbm0b" : "/home/ecc_16/eaobmh",\
					"hayderem" : "/home/ecc_11/eaoemh",\
					"hugotaag" : "/home/ecc_17/hugotaag",\
					"husainkb" : "/home/ecc_17/eaqkbh",\
					"ibrama0y" : "/home/ecc_17/ibrama0y",\
					"khannu" : "/home/ecc_17/eaonuk",\
					"khawha0a" : "/home/ecc_18/eaohak",\
					"labatlx" : "/home/ecc_8/labatlx",\
					"lamyvc" : "/home/ecc_13/lamyvc",\
					"laukk" : "/home/ecc_18/eaokkl",\
					"madanihs" : "/home/ecc_6/madanihs",\
					"mohammzh" : "/home/ecc_8/mohammzh",\
					"msikaba" : "/home/ecc_14/msikaba",\
					"nahdiua" : "/home/ecc_12/eapuan",\
					"nuaimms" : "/home/ecc_17/nuaimms",\
					"powers" : "/home/ecc_17/powers",\
					"qannsm0a" : "/home/ecc_13/qannsm0a",\
					"saidaa0j" : "/home/ecc_12/saidaa0j",\
					"shehma0s" : "/home/ecc_17/shehma0s",\
					"siual" : "/home/ecc_16/eaoals",\
					"smarts" : "/home/ecc_12/smarts",\
					"sunbelsm" : "/home/ecc_1/sunbelsm",\
					"tibanaa" : "/home/ecc_12/tibanaa",\
					"vobadm" : "/home/ecc_15/baddouma",\
					"zamilks" : "/home/ecc_17/zamilks"}

	return ret;
	


class pUserIdFrame(Frame):
	"""
	This is used to create the frame for hte `
	"""
	def __init__(self,parent,modelObject,mainFrame):
		Frame.__init__(self,parent)
		self.parent=parent
		self.modelObject = modelObject
		self.mainFrame   = mainFrame
	
		self.usersdir = {}
		try:
			xlines = open('/red/ssd/appl/khusain/userInfo.txt','r').readlines()
			for xln in xlines: 
				username, homedir = xln.split(':')
				self.usersdir[username.strip()] = homedir.strip()
		except:
			self.usersdir = returnDefinedUserDirectory()

		self.userids = self.usersdir.keys()
		self.userids.sort()
		self.chosen = StringVar()

		ulen = len(self.userids)
		uid  = 0
		row  = 0
		col  = 0
		while uid < ulen:
			txt = "%-10s" % self.userids[uid]
			btn = Radiobutton(self,text=txt,value=txt,variable=self.chosen,width=10,relief='raised')
			btn.grid(row=row,column=col,sticky=W)
			col += 1
			if col > 8: col = 0; row += 1
			uid += 1
		row += 1;
		a = lambda s=self,m=None: s.openAnyway(m)
		self.buttonOk = Button(self,text=" OK ",command=a,fg='white',bg='blue')
		self.buttonOk.grid(row=row,column=2)

		unamehome = os.getenv('USER')
		a = lambda s=self,m='HOME': s.openAnyway(m)
		self.buttonOk = Button(self,text=unamehome,command=a,fg='white',bg='blue')
		self.buttonOk.grid(row=row,column=3)
		self.buttonOk = Button(self,text="Browse User Directory",command=self.chosenCommand,fg='white',bg='blue')
		self.buttonOk.grid(row=row,column=4,columnspan=2)

	def setModelObject(self,modelObject):
		self.modelObject = modelObject


	def openAnyway(self,where=None):
		if where == None: 
			username = self.chosen.get()
			username = username.strip()
			userdir =  self.usersdir.get(username,None)
		else:
			username = os.getenv('USER')
			userdir =  os.getenv(where)
			
		#userdir =  '/home/pet_2/' + username.strip()  + '/powersdata'
		
		if userdir == None: 
			showwarning("Error","The user has has no home data directory in \n" + username)
			return
		
		userdir =  self.usersdir.get(username,None) + '/powersdata'
		try:
			ms = os.chdir(userdir)
		except:
			showwarning("Error","The user has has no powers gui data directory in \n" + username)
			return
		
		filename = userdir + os.sep + 'projects.xml' 
		try:
			ms = os.stat(filename)
		except:
			showwarning("Error","The user has has no projects.xml \nfile in their gui data directory in \n" + userdir)
			return

		self.modelObject.forceopenProjectXMLfile(eraseList=1,initDir=userdir)
		self.mainFrame.nb.selectpage('Office')
		self.modelObject.setToFirstProject()

	def chosenCommand(self):
		username = self.chosen.get()
		username = username.strip()
		#userdir =  '/home/pet_2/' + username.strip()  + '/powersdata'
		userdir =  self.usersdir.get(username,None)
		if userdir == None: 
			showwarning("Error","The user has has no home data directory in \n" + userdir)
			return
		userdir =  self.usersdir.get(username,None) + '/powersdata'
		try:
			ms = os.chdir(userdir)
		except:
			showwarning("Error","The user has has no powers gui data in \n" + userdir)
			return
		re = self.modelObject.openProjectXMLfile(eraseList=1,initDir=userdir)
		if re == 1: 
			self.mainFrame.nb.selectpage('Office')
			self.modelObject.setToFirstProject()

