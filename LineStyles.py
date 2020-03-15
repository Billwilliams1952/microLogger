'''
Linestyles.py - a data logging application written in Python/tkinter
  
Copyright 2020  <billwilliams2718@gmail.com>

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation, either version 3 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful,but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import 	os
import 	datetime
from	tkinter import *
from	tkinter.colorchooser import askcolor
import	tkinter.filedialog as FileDialog
import	tkinter.messagebox
from 	tkinter import ttk
import	tkinter.font
import	matplotlib
from	matplotlib import lines

from 	Dialog	    import *
from 	Mapping	    import *
from	NotePage	import *
from	Utils		import *
from	Tooltip	    import *

import 	PIL
from 	PIL import Image

class LineStylesDialog ( Dialog ):
	CurrentLine = None              # What PlotLine we are talking about
	CurrentLineIndex = 0

	def BuildDialog ( self ):
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(0,weight=1)

		n = Notebook(self.MainFrame,padding=(5,5,5,5)) #,width=60,height=200)
		n.grid(row=0,column=0,sticky='NEWS')

		self.LinesPage = Lines(n,cancel=self.CancelButton,data=self)
		self.OtherPage = Other(n,cancel=self.CancelButton)

		n.add(self.LinesPage,text='Lines',underline=0)
		n.add(self.OtherPage,text='Other',underline=0)
		
	def OkPressed ( self ):
		if not self.LinesPage.SaveChanges(): return False
		#self.OtherPage.SaveChanges()
		return True
 
class Lines ( BasicNotepage ):
	# Change back to BuildPage
	def OtherBuildPage ( self ):
		# Setup default folder to save pictures and videos
		f = MyLabelFrame(self,'Change Plot Line parameters...',0,0)
		
		# Set Visibility of the line.....
		
		Label(f,text="Line Name:").grid(row=0,column=0,pady=(5,5),sticky=W)
		print(LineStylesDialog.CurrentLine.get_label())
		
		Label(f,text="Line Color:").grid(row=1,column=0,pady=(0,5),sticky=W)
		# Color - string - #XXXXXX - RGB format
		print(LineStylesDialog.CurrentLine.get_color())
		
		Label(f,text="Line Style:").grid(row=2,column=0,pady=(0,5),sticky=W)
		# Linestyle       '-' , '--',   '-.'  ,   ':' ,  ''
		#                solid, dash, dash-dot, dotted, none
		self.LineStyle = Combobox(f,state='readonly',width=15)
		self.LineStyle.bind('<<ComboboxSelected>>',self.Changed)
		self.LineStyle.grid(row=2,column=1,sticky='W',padx=5)
		self.LineStyle['values'] = list(lines.lineStyles.values())
		self.LineStyles = ['-','--','-.',':','']
		idx = self.LineStyles.index(LineStylesDialog.CurrentLine.get_linestyle())
		self.LineStyle.current(idx)
		#ToolTip(self.AcquireRate,121)
		self.markers = ( [[ func, m ] for m, func in matplotlib.lines.Line2D.markers.items() ])
		
		print(list(lines.lineStyles.values()))
		
		Label(f,text="Line Width:").grid(row=3,column=0,pady=(0,5),sticky=W)
		print(LineStylesDialog.CurrentLine.get_linewidth())
		   
		'''
		linestyle = '-' = solid '--' = dashed ':' = dotted '-.' = dashdot
		markers = {'.': 'point', ',': 'pixel', 'o': 'circle', 
		   'v': 'triangle_down', '^': 'triangle_up', 
		   '<': 'triangle_left', '>': 'triangle_right', 
		   '1': 'tri_down', '2': 'tri_up', '3': 'tri_left', 
		   '4': 'tri_right', '8': 'octagon', 's': 'square', 
		   'p': 'pentagon', '*': 'star', 'h': 'hexagon1', 
		   'H': 'hexagon2', '+': 'plus', 'x': 'x', 
		   'D': 'diamond', 'd': 'thin_diamond', 
		   '|': 'vline', '_': 'hline', 'P': 'plus_filled', 
		   'X': 'x_filled', 0: 'tickleft', 1: 'tickright', 
		   2: 'tickup', 3: 'tickdown', 4: 'caretleft', 
		   5: 'caretright', 6: 'caretup', 7: 'caretdown', 
		   8: 'caretleftbase', 9: 'caretrightbase', 
		   10: 'caretupbase', 11: 'caretdownbase', 
		   'None': 'nothing', None: 'nothing', ' ': 'nothing', '': 'nothing'}
		'''
		Label(f,text="Marker Style:").grid(row=4,column=0,pady=(0,5),sticky=W)
		self.MarkerStyle = Combobox(f,state='readonly',width=15)
		self.MarkerStyle.bind('<<ComboboxSelected>>',self.Changed)
		self.MarkerStyle.grid(row=4,column=1,sticky='W',padx=5)
		#ToolTip(self.AcquireRate,121)
		self.markers = ( [[ func, m ] for m, func in matplotlib.lines.Line2D.markers.items() ])
		#print (self.markers)
		# Get CurrentLine's marker type and set combo to it

		self.MarkerStyle['values'] = [ key[0] for key in self.markers ]
		#self.MarkerStyle.current(self.MarkerStyle['values'].index(str(LineStylesDialog.MarkerStyle)))	
		
		# filled_markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
		# Only for these can you choose a fill color.....
		
		'''
		everyNone or int or (int, int) or slice or List[int] or float or (float, float)
		Which markers to plot.

		every= None, every point will be plotted.
		every= N, every N-th marker will be plotted starting with marker 0.
		every= (start, N), every N-th marker, starting at point start, will be plotted.
		every= slice(start, end, N), every N-th marker, starting at point start, 
				up to but not including point end, will be plotted.
		every= [i, j, m, n], only markers at points i, j, m, and n will be plotted.
		every= 0.1, (i.e. a float) then markers will be spaced at approximately 
				equal distances along the line; the distance along the line 
				between markers is determined by multiplying the display-coordinate 
				distance of the axes bounding-box diagonal by the value of every.
		every= (0.5, 0.1) (i.e. a length-2 tuple of float), the same functionality 
				as every=0.1 is exhibited but the first marker will be 0.5 
				multiplied by the display-coordinate-diagonal-distance along the line.
		'''

	def Changed(self,val):
		idx = self.MarkerStyle.current()
		LineStylesDialog.CurrentLine.set_marker(self.markers[idx][1])
		LineStylesDialog.CurrentLine.set_markersize(10.0)
		LineStylesDialog.CurrentLine.set_linestyle(list(lines.lineStyles.keys())[self.LineStyle.current()])

	def SaveChanges(self):
		# Update CurrentLine to the values...
		return True

class Other ( BasicNotepage ):
	pass
