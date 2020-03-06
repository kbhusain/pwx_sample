

from Tkinter import *
import os
import sys
import string, types, Tkinter
#============================================================================
# ArrayVar
#----------------------------------------------------------------------------
class ArrayVar(Tkinter.Variable):
	_default = ''

	def __init__(self, master = None):
		Tkinter.Variable.__init__(self, master)

	def get(self, index = None):
		if not index:
			res = {}
			for i in self.names():
				res[i] = self._tk.globalgetvar(self._name, i)
			try: del res['None']
			except KeyError: pass
			return res
		else:
			return self._tk.globalgetvar(self._name, index)

	def names(self):
		return string.split(self._tk.call('array', 'names', self._name))

	def set(self, index, value = ''):
		if value == None:
			value = ''
		return self._tk.globalsetvar(self._name, index, value)


	#def __del__(self):
	#	del self._arrays[self._name]
	#	self._tk.eval("array unset %s" % self._name)

	def __str__(self):
		return self._name

	def __repr__(self):
		return '<%s @ 0x%08X>' % (self.__class__.__name__, id(self))

	def _coords(self, coords=[]):
		if type(coords) is not list:
			ValueError("Bad item coordinates %s: must be <row>,<col>" % str(coords))
		return int(coords[0]), int(coords[1])

	def __getitem__(self, coords):
		row, col = self._coords(coords)
		return self._tk.eval("return $%s(%d,%d)" % (self._name, row, col))

	def __setitem__(self, coords, value):
		row, col = self._coords(coords)
		self._tk.eval("set %s(%d,%d) {%s}" % (self._name, row, col, value))
		
#----------------------------------------------------------------------------

