#!/work0/kamran/python2.2.2/python

import socket
import time 
import string
import os

port = 8098
host = 'lnx5e090'

def sendMessage(aname='PBF',mtype='INIT',parm='None'):
	username=os.getenv('LOGNAME')
	if username == None: username=os.getenv('USERNAME')
	if username == None: username=os.getenv('USER')
	if username == None: username='NOBODY'
	
	try: 
		s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		ig = time.localtime(time.time()) 
		g = map(str,ig)
		args = (mtype,parm,aname,g[0],g[1],g[2],g[3],g[4],g[5],username)
		xstr = string.join(args,',')

		s.sendto(xstr,(host,port))
	except: 
		pass

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.bind(("",port))
	while 1: 
		data,addr = s.recvfrom(512)
		fd = open('./pbfLog.txt','a')
		xstr = data + ',' + addr[0] + '\n'
		fd.write(xstr)
		fd.close()
		print xstr,
		if data == 'QUIT':
			break
