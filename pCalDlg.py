
from Tkinter import *
import Pmw
import time
import calendar

class makeMyCalendar:
	def __init__(self,root,obj=None,y=2006,m=10,d=1):
		self.master = root
		self.caldlg = Pmw.Dialog(self.master,title ='kamran',buttons=('ok','cancel'),command=self.dodone)
		self.calfrm = Frame(self.caldlg.interior())
		self.calfrm.pack()
		self.objCallback = obj
		self.caltitle = StringVar()
		self.daystring = StringVar()
		self.m = m
		self.d = d
		self.y = y
		self.ok = 0
		self.caltitle.set('%d-%4d' % (self.m,self.y))
		self.calLabel = Label(self.calfrm, textvariable=self.caltitle)
		self.calLabel.grid(row=0,column=3,columnspan=3)
		self.calLeft = Button(self.calfrm,text='<',command=self.prevmonth)
		self.calLeft.grid(row=0,column=1)
		self.calRight = Button(self.calfrm,text='>',command=self.nextmonth)
		self.calRight.grid(row=0,column=6)
		self.daystring.set('%2d' % (self.d))
		self.showDay = Label(self.calfrm, textvariable=self.daystring)
		self.showDay.grid(row=0,column=2)
		col_cnt = 0
		for nm in calendar.day_name: 
			lbl = Label(self.calfrm,text=nm[:2])
			lbl.grid(row=1,column=col_cnt)
			col_cnt += 1
		self.buttons = []
		self.resetCalendar()

	def resetCalendar(self):
		for b in self.buttons: b.destroy()
		self.buttons = []
		self.caltitle.set('%d-%4d' % (self.m,self.y))
		mc = calendar.monthcalendar(self.y,self.m)
		btn_cnt = 0
		rlen = len(self.buttons)
		for i in range(len(mc)):
			for j in range(7):
				num = mc[i][j]
				if num == 0: 
					state='disabled'
					n = ''
					border = 0
				else: 
					state='active'
					n = `num`
					border = 2
				a = lambda s=self,n=num,b=btn_cnt: s.doday(n,b)
				btn = Button(self.calfrm,text=n,width=2,state=state,command=a)
				btn.grid(row=i+2,column=j)
				btn['state'] = state 
				btn['text'] = n 
				btn['border'] = border 
				btn_cnt += 1
				self.buttons.append(btn)
		
	
	def nextmonth(self):
		self.m += 1 
		if self.m >= 12: 
			self.m = 1
			self.y += 1
		self.resetCalendar()

	def prevmonth(self):
		self.m -= 1 
		if self.m <= 0: 
			self.m = 12
			self.y -= 1
		#print self.m, self.y
		self.resetCalendar()

	def doday(self,n,bn):
		self.d = int(n)
		self.daystring.set('%2d' % (self.d))
		for b in self.buttons: b['bg'] = 'gray'
		btn = self.buttons[bn]
		btn['bg'] = 'red'

	def dodone(self,parm):
		self.ok = 0
		if parm == 'ok' and self.objCallback <> None: 
			self.ok = 1
			self.objCallback.handleCalendar()
		self.caldlg.destroy()

if __name__ == '__main__':
	root = Tk()
	fm = makeMyCalendar(root)
	root.mainloop()




