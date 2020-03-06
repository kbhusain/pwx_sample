
import sys
from string import split, find, strip
from pychart import *
theme.get_options()
theme.scale_factor = 2
theme.use_color = True 
theme.reinitialize()
##################################################################################



def doPlot(filename, prefix, dolast=1):
	lines = open(filename).readlines()
	pcount = 0
	state  = 0
	data   = [] 
	labels = []
	lunits = []
	minV = 0
	maxV = 0

	for ln in lines: 
		sline = strip(ln)
		if len(sline) < 1: 
			continue
		if sline[0] == '#': continue
		items = split(sline)
		if state == 0 and items[0] == 'TABLE':
			state = 1
			data   = [] 
			labels = []
			lunits = []
			minV = 0
			maxV = 0
			continue
		if state == 1 and items[0] == 'ENDTABLE': 
			xstr = prefix + str(pcount) + ".eps"
			xlabel = xstr + ": Table" + "%d" % (int(pcount) + 1)
			# Create plot here. 
			can = canvas.init(xstr)
			if minV < maxV: 
				interval = (maxV - minV) / 8  
				print minV, maxV, interval
				xaxis = axis.X(label=xlabel,format="/a-90/hR%6.2f", tic_interval=interval)
			else:
				xaxis = axis.X(label=xlabel,format="/a-90/hR%6.2f")
			yaxis = axis.Y(label=labels[0])
			#ar = area.T(x_axis=xaxis, y_axis=yaxis,y_range=(0,5000),x_range=(0,5000))
			ar = area.T(x_axis=xaxis, y_axis=yaxis, loc=(-100,0))
			cols = len(lunits) - dolast -1
			print cols, " columns ....", labels
			for k in range(cols): 
				tstr = labels[k+1] + '-' + lunits[k+1]
				tstr = tstr.replace('/','//')
				tick1 = tick_mark.Plus(size=5)
				if k == 1: tick1 = tick_mark.Circle(size=3)
				if k == 2: tick1 = tick_mark.Triangle(size=3)
				if k == 3: tick1 = tick_mark.Diamond(size=5)
				if k == 4: tick1 = tick_mark.Square(size=3)
				plot = line_plot.T(label=tstr, data=data, ycol=0,xcol=k+1,tick_mark=tick1)
				#plot = line_plot.T(data=data, xcol=0,ycol=k+1)
				ar.add_plot(plot)
			print xstr
			ar.draw(can)
			state = 0
			pcount = pcount + 1
			continue
		if len(items) < 2: continue
		if items[0] in ['STANDARD_DENSITY_GAS','STANDARD_DENSITY_OIL', 'BUBBLE_POINT_PRESSURE'] : 
			continue
		if state == 1: 
			if items[0] == 'GRAPH_UNITS' : lunits = items[1:]; continue
			if items[0] == 'GRAPH_LABELS': 
				labels = items[1:]; 
				continue
			fitems = map(float,items)

			xfitems = fitems[1:]
			if dolast == 1: xfitems = xfitems[1:-1]
			for v in xfitems:
				if v < minV: minV = v
				if v > maxV: maxV = v

			data.append(tuple(fitems))
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "%d Usage: %s filename prefix [dolast]\n prefix is required for output filenames\ndolast implies all columns" % (len(sys.argv), sys.argv[0])
		sys.exit(0)
	dolast=0	
	if len(sys.argv) > 3: 
		if sys.argv[3] == 'dolast': dolast=1
	doPlot(sys.argv[1],sys.argv[2],dolast)

