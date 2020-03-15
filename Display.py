#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Display.py - a data logging application written in Python/tkinter
  
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
from   	collections import OrderedDict
import 	RPi.GPIO

import  tkinter as tk
from	tkinter import ttk
from 	tkinter.ttk import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

from 	Dialog			import *
from 	Mapping			import *
from	NotePage		import *
from	Utils			import *

'''
    Handle all plotting options
    Start / Stop plot
    Add/Remove Mux channels
    Change Vertical Scale - Set Min, Set Max
    Change plot line style, colors and thickness
    Plot as points, as lines, etc
    
'''
class Cursor(object):
	def __init__(self, ax):
		self.ax = ax
		self.lx = ax.axhline(color='k')  # the horiz line
		self.ly = ax.axvline(color='k')  # the vert line

		# text location in axes coords
		self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

	def mouse_move(self, event):
		if not event.inaxes:
			return

		x, y = event.xdata, event.ydata
		# update the line positions
		self.lx.set_ydata(y)
		self.ly.set_xdata(x)

		self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
		self.ax.figure.canvas.draw()

"""
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
"""
class SnaptoCursor(object):
	def __init__(self, ax, x, y):
		self.ax = ax
		self.lx = ax.axhline(color='k')  # the horiz line
		self.ly = ax.axvline(color='k')  # the vert line
		self.x = x
		self.y = y
		# text location in axes coords
		self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

	def mouse_move(self, event):
		if not event.inaxes:
			return

		x, y = event.xdata, event.ydata
		indx = min(np.searchsorted(self.x, x), len(self.x) - 1)
		x = self.x[indx]
		y = self.y[indx]
		# update the line positions
		self.lx.set_ydata(y)
		self.ly.set_xdata(x)

		self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
		print('x=%1.2f, y=%1.2f' % (x, y))
		self.ax.figure.canvas.draw()
        
'''
    Handle all plot display updates
'''
class Display ( BasicNotepage ):
	DisplayUpdateRate = 5
	SavePlotLength = 120.0
	PlotTitle = "microLogger Plot"
	PlotTitleFontSize = 18
	XAxisText = "Plot-time in seconds from Start"
	XAxisFontSize = 12
	YAxisText = "Volts"
	YAxisFontSize = 12
	PlotFactor = 1.0
	XAxisTimePeriod = 30.0

	# Add checkbutton: Use Default YAxis Values
	UseYAxisDefaults = True
	# If False, then use these values...
	YAxisMin = -5.0
	YAxisMax =  5.0
	ShowXAxisGrids = True
	ShowYAxisGrids = True

	'''
		# Adjust legend information...

		self.legend = self.figure.legend()
		for text in self.legend.get_texts():
			text.set_fontsize('large')
	'''
    
	def BuildPage ( self ):  
		#-----
		f1 = MyLabelFrame(self,'Display Update Rate and Plot Retention',0,0,span=2)
		Label(f1,text="Display Update Rate:",anchor=W).grid(column=0,row=0,sticky='W')
		self.UpdateRate = Combobox(f1,state='readonly',width=5)
		self.UpdateRate.bind('<<ComboboxSelected>>',self.UpdateRateChanged)
		self.UpdateRate.grid(row=0,column=1,sticky='EW',padx=(0,5))
		#ToolTip(self.AcquireRate,121)
		self.UpdateRate['values'] = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]
		self.UpdateRate.current(self.UpdateRate['values'].index(Display.DisplayUpdateRate))
		Label(f1,text="updates per second",anchor=W).grid(column=2,row=0,sticky='W')
		s = "NOTE: The actual display update rate will be affected by the number" \
			" of plot lines, the amount of data being plotted, and the screen size."
		l = ttk.Label(f1,text=s,anchor=W,wraplength=400,style='DataLabel.TLabel')
		l.grid(column=0,row=1,columnspan=3,sticky='EW',padx=5,pady=(5,5)) 
		
		Label(f1,text="Length of Plot Data:",anchor=W).grid(column=0,row=2,sticky='W')
		self.SavePlotLength = Combobox(f1,state='readonly',width=5)
		self.SavePlotLength.bind('<<ComboboxSelected>>',self.SavePlotLengthChanged)
		self.SavePlotLength.grid(row=2,column=1,sticky='EW',padx=(0,5))
		#ToolTip(self.AcquireRate,121)
		self.SavePlotLength['values'] = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0]
		self.SavePlotLength.current(self.SavePlotLength['values'].index(Display.SavePlotLength))
		Label(f1,text="seconds",anchor=W).grid(column=2,row=2,sticky='W')
		s = "This value determines the number of seconds of plot data that is saved " \
			"and available for plotting. Note that a larger number consumes more memory " \
			"and may slow down the plot updates."
		l = ttk.Label(f1,text=s,anchor=W,wraplength=400,style='DataLabel.TLabel')
		l.grid(column=0,row=3,columnspan=3,sticky='EW',padx=5,pady=(5,5)) 
		
		#-----
		f1 = MyLabelFrame(self,'Plot Text',1,0,span=2)
		f1.columnconfigure(1,weight=1) # Let text entry fields expand to fill width
		
		image = PIL.Image.open('Assets/Prefs.png')
		self.AdjustImage = GetPhotoImage(image)
		
		Label(f1,text="Plot Title:",anchor=E).grid(column=0,row=0,sticky='E')
		self.var1 = MyStringVar(Display.PlotTitle)
		vcmd = (self.register(self.PlotTitleChanged),'%P')
		e = ttk.Entry(f1,textvariable=self.var1,validate="key",validatecommand=vcmd)
		e.grid(row=0,column=1,sticky='NSEW',padx=5,pady=2)
		b = ttk.Button(f1,image=self.AdjustImage)
		b.grid(row=0,column=2,sticky='NSEW',pady=2)

		Label(f1,text="X-Axis Text:",anchor=E).grid(column=0,row=1,sticky='E')
		self.var2 = MyStringVar(Display.XAxisText)
		vcmd1 = (self.register(self.XAxisTextChanged),'%P')
		e1 = ttk.Entry(f1,textvariable=self.var2,validate="key",validatecommand=vcmd1)
		e1.grid(row=1,column=1,sticky='NSEW',padx=5,pady=2)
		b = ttk.Button(f1,image=self.AdjustImage)
		b.grid(row=1,column=2,sticky='NSEW',pady=2)
		
		Label(f1,text="Y-Axis Text:",anchor=E).grid(column=0,row=2,sticky='E')
		self.var3 = MyStringVar(Display.YAxisText)
		vcmd2 = (self.register(self.YAxisTextChanged),'%P')
		e2 = ttk.Entry(f1,textvariable=self.var3,validate="key",validatecommand=vcmd2)
		e2.grid(row=2,column=1,sticky='NSEW',padx=5,pady=2)
		b = ttk.Button(f1,image=self.AdjustImage)
		b.grid(row=2,column=2,sticky='NSEW',pady=2)
		
		#-----
		f1 = MyLabelFrame(self,'Plot Options',3,0,span=2)
		f1.columnconfigure(2,weight=1) # Let text entry fields expand to fill width
		Label(f1,text="Plot X Axis time:",anchor=W).grid(column=0,row=0,sticky='W',pady=2,padx=(0,15))
		self.XAxisTimePeriod = Combobox(f1,state='readonly',width=7)
		self.XAxisTimePeriod.bind('<<ComboboxSelected>>',self.XAxisTimePeriodChanged)
		self.XAxisTimePeriod.grid(row=0,column=1,sticky='EW',padx=(0,5))
		#ToolTip(self.AcquireRate,121)
		self.XAxisTimePeriod['values'] = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0 ]
		self.XAxisTimePeriod.current(self.XAxisTimePeriod['values'].index(Display.XAxisTimePeriod)) 
		Label(f1,text="seconds",anchor=W).grid(column=2,row=0,sticky='NSEW',pady=2)   
		
		# Label(f1,text="Plot Factor:",anchor=E).grid(column=0,row=1,sticky='W',pady=2)
		# self.PlotFactorVar = MyStringVar(Display.PlotFactor)
		# self.PlotFactorEntry = ttk.Entry(f1,textvariable=self.PlotFactorVar,validate="all",
			# validatecommand=self.PlotFactorVarChanged)
		# self.PlotFactorEntry.grid(row=1,column=1,sticky='W',pady=2)

		#-----
		f2 = Frame(f1)
		f2.grid(row=2,column=0,columnspan=3,sticky=NSEW)
		
		self.VGridsVar = MyBooleanVar(Display.ShowYAxisGrids)
		self.VGrids= ttk.Checkbutton(f2,text="Show Vertical gridlines",variable=self.VGridsVar,
			command=self.GridsChecked)
		self.VGrids.grid(row=0,column=0,sticky='W')

		self.HGridsVar = MyBooleanVar(Display.ShowXAxisGrids)
		self.HGrids= ttk.Checkbutton(f2,text="Show Horizontal gridlines",variable=self.HGridsVar,
			command=self.GridsChecked)
		self.HGrids.grid(row=1,column=0,sticky='W')      

	def NameChanged(self):
		#self.after(50,self.AcceptNameChange())
		return True
	def PlotTitleChanged(self, Val):
		Display.PlotTitle = Val 
		try:    # May be called before these are valid
			#font={'fontname':'Arial','fontsize': 32, 'fontweight': 'medium'}
			self.Axes.set_title(Display.PlotTitle,fontsize=Display.PlotTitleFontSize)      
			self.Canvas.draw()
		except: pass
		return True
	def XAxisTextChanged(self,val):
		Display.XAxisText = val
		try:
			self.Axes.set_xlabel(Display.XAxisText,fontsize=Display.XAxisFontSize)        
			self.Canvas.draw()
		except: pass
		return True
	def YAxisTextChanged(self,val):
		Display.YAxisText = val
		try:
			self.Axes.set_ylabel(Display.YAxisText,fontsize=Display.YAxisFontSize)        
			self.Canvas.draw()
		except: pass
		return True

	def XAxisTimePeriodChanged(self,val):
		Display.XAxisTimePeriod = float(self.XAxisTimePeriod.get())
		print("XAxis: %d sec"%int(Display.XAxisTimePeriod))
		self.Canvas.draw()
		
	def PlotFactorVarChanged(self):
		return True
		
	def GridsChecked(self):
		# which : {'major', 'minor', 'both'}, optional
		self.Axes.grid(b=False)
		if self.VGridsVar.get() and self.HGridsVar.get():
			self.Axes.grid(axis='both', which='both', color='0.65', linestyle='--')
		elif self.VGridsVar.get():
			self.Axes.grid(axis='y', which='both', color='0.65', linestyle='--')
		elif self.HGridsVar.get():
			self.Axes.grid(axis='x', which='both', color='0.65', linestyle='--')
		self.Canvas.draw()

	def SetPlotInfo(self,figure, canvas, axes):
		self.Figure = figure
		self.Canvas = canvas
		self.Axes = axes
		
	def UpdateRateChanged(self,val):
		Display.DisplayUpdateRate = float(self.UpdateRate.get())
		print("Display Update Rate = %0.1f Hz" % float(Display.DisplayUpdateRate))

	def SavePlotLengthChanged(self,val):
		Display.SavePlotLength = float(self.SavePlotLength.get())
		print("Save Plot Length = %0.1f sec" % float(Display.SavePlotLength))
