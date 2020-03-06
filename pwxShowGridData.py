
import wx
import wx.grid
import numarray


class MyGridDataFrame(wx.Frame):
	def __init__(self,title="Data",rows=10,cols=2):
		self.rowLabels = []
		self.colLabels = []
		wx.Frame.__init__(self,None,title=title,size=(100,400))
		self.grid = wx.grid.Grid(self)

	def setData(self,rows,cols,data,rowlbls,collbls):
		"""
		data is an array of numarray vectors per column
		"""
		self.grid.CreateGrid(rows,cols)
		for col in range(cols):
			self.grid.SetColLabelValue(col,collbls[col])
			colvector = data[col]
			for row in range(rows):
				self.grid.SetCellValue(row,col,'%s'% colvector[row])

if __name__ == '__main__':
	pp = wx.PySimpleApp() 
	ff = MyGridDataFrame(title='Kamran')
	aa = numarray.arange(10)
	ab = numarray.arange(10)
	ac = numarray.arange(10)
	dd = (aa,ab,ac)
	ff.setData(10,3,dd,None,['c1','c2','c3'])
	ff.Show()
	pp.MainLoop()
	
