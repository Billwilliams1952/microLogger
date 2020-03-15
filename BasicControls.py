#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
BasicControls.py - a data logging application written in Python/tkinter
  
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

import	tkinter as tk
from	tkinter import ttk, DISABLED
from 	tkinter.ttk import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

from	Globals				import *
from 	Dialog				import *
from 	Mapping				import *
from	NotePage			import *
from	Utils				import *
from	Calibration			import *
from	LineStyles			import *

class BasicControls ( BasicNotepage ):
	#
	SampleRate = 20.0
	Gain = 1
	# This shows the assignment of the channels
	# 0xFF (255) = not used.  TODO: 0xC0 = Disabled - need to implement
	# 
	# This MUST be written to the INI file
	ADCInputList = [1,255,255,255,255,255,255,255]
	# List of Channel Names
	# This MUST be written to the INI file
	ADCNames = ['CHANNEL 1', 'CHANNEL 2','CHANNEL 3','CHANNEL 4',
				'CHANNEL 5','CHANNEL 6','CHANNEL 7','CHANNEL 8']
	'''
		These next three don't really have to be written to the INI file
		since they can be built based on ADCInputList and ADCNames
	'''
	# ADCInputs is the list of MUX inputs sent to the Thread
	# Build by: BasicControls.ADCInputs = [x for x in BasicControls.ADCInputList if x < 255]
	ADCInputs = []
	# List of MUX Channel names written to the log file
	# Build by: BasicControls.ADCInputNames = [x for i, x in enumerate(BasicControls.ADCNames) if BasicControls.ADCInputList[i] < 255]
	ADCInputNames = []
	# Finally, the plots that are active can be obtained by:
	# plots = [i for i, val in enumerate(BasicControls.ADCInputList) if val < 255]
	CurrentPlots = []
	
	def BuildPage ( self ):
		#-----
		f1 = MyLabelFrame(self,'Acquisition',0,0,span=2)
		Label(f1,text="Aquisition rate in samples per second:").grid(column=0,row=0,sticky='W',ipady=3)
		self.AcquireRate = Combobox(f1,state='readonly',width=5)
		self.AcquireRate.bind('<<ComboboxSelected>>',self.AcquireRateChanged)
		self.AcquireRate.grid(row=0,column=1,sticky='W',padx=5)
		#ToolTip(self.AcquireRate,121)
		self.AcquireRate['values'] = [1.0,2.0,5.0,10.0,20.0,25.0,50.0] # TODO: Update for faster later ,100.0,200.0]
		self.AcquireRate.current(self.AcquireRate['values'].index(BasicControls.SampleRate))
		
		Label(f1,text="ADC Gain (Default is 1):").grid(column=0,row=1,sticky='W',ipady=3)
		self.GainAmt = Combobox(f1,state='readonly',width=5)
		self.GainAmt.bind('<<ComboboxSelected>>',self.GainAmtChanged)
		self.GainAmt.grid(row=1,column=1,sticky='W',padx=5)
		#ToolTip(self.AcquireRate,121)
		self.GainAmt['values'] = [1,2,4,8,16,32,64,128]
		self.GainAmt.current(self.GainAmt['values'].index(str(BasicControls.Gain)))	
		self.GainChanged = True
		f2 = Frame(f1)
		f2.grid(row=2,column=0,columnspan=2,sticky=NSEW)
		self.GainText = ttk.Label(f2,text="",style='DataLabel.TLabel')
		self.GainText.grid(column=0,row=0,sticky='W',ipady=3,ipadx=20)
		self.UpdateFullScale()
		#----

		#-------------------	Build ADC Multiplexer Inputs
		self.MuxFrame = MyLabelFrame(self,'Select Input Channels and Channel Names...',2,0,span=4)
		self.MuxFrame.columnconfigure(3,weight=1)
		
		image = PIL.Image.open('Assets/Prefs.png')
		self.AdjustImage = GetPhotoImage(image)
		
		Label(self.MuxFrame,text="From").grid(column=0,row=1,ipadx=3,ipady=3)
		Label(self.MuxFrame,text="To").grid(column=2,row=1,ipadx=3,ipady=3)	
		Label(self.MuxFrame,text="Name (CSV file and Plot)").grid(column=3,row=1,columnspan=3,ipadx=3,ipady=3)
					
		# Use Dropdown lists - fill each one with IN 0 thru IN 7 and GND
		# Have eight of them....  
		self.Muxes = []
		self.NameEntry = []
		self.NameVars = []
		self.Options = []
		self.Mux1Dict = [ 0xF0, 0x00, 0x10, 0x20, 0x30,
						  0x40, 0x50, 0x60, 0x70, 0x80 ] # ADDED GND to first +IN
		self.Mux2Dict = [ 0x00, 0x01, 0x02, 0x03,
						  0x04, 0x05, 0x06, 0x07, 0x08 ]
		# FIX ME HERE -- Add Ground to Mux1Names to allow GND to IN X (invert voltage reading)
		self.Mux1Names = ['NONE', 'IN 0','IN 1','IN 2', 'IN 3', 'IN 4', 'IN 5', 'IN 6', 'IN 7', 'GND']
		self.Mux2Names = ['IN 0','IN 1','IN 2', 'IN 3', 'IN 4', 'IN 5', 'IN 6', 'IN 7', 'GND']

		#---------------- Build MUX and Channel Names ------------------
		# e.g: ADCInputList = [0x67,255,255,0x58,255,255,0x45,255]
		RowOffset = 2		# In case we add more rows above later
		for i, Input in enumerate(BasicControls.ADCInputList):
			c = ttk.Combobox(self.MuxFrame,state='readonly',width=6)
			c.bind('<<ComboboxSelected>>',self.InputChanged)
			c.grid(row=i+RowOffset,column=0,sticky='W',padx=5)
			c['values'] = self.Mux1Names
			self.FindMux(self.Mux1Dict,Input & 0xF0,c)
			self.Muxes.append(c)
			#ToolTip(c,121)			# Tooltip Mux1
			
			Label(self.MuxFrame,text="to",anchor=E).grid(column=1,row=i+RowOffset,sticky='E',ipadx=3,ipady=3)
			
			c = ttk.Combobox(self.MuxFrame,state='readonly',width=6)
			c.bind('<<ComboboxSelected>>',self.InputChanged)
			c.grid(row=i+RowOffset,column=2,sticky='W',padx=5)
			c['values'] = self.Mux2Names
			self.FindMux(self.Mux2Dict,Input & 0x0F,c)
			self.Muxes.append(c)
			#ToolTip(c,121)			# Tooltip Mux2
			
			var1 = MyStringVar(BasicControls.ADCNames[i])
			vcmd = (self.register(self.MuxNameChanged),'%P')
			e = ttk.Entry(self.MuxFrame,textvariable=var1,validate="key",validatecommand=vcmd)
			e.grid(row=i+RowOffset,column=3,sticky='NSEW',padx=5,pady=2)
			self.NameVars.append(var1)
			self.NameEntry.append(e)
			#ToolTip(c,121)			# Tooltip Channel name
			
			b = ttk.Button(self.MuxFrame,image=self.AdjustImage)
			b.grid(row=i+RowOffset,column=4,sticky='NSEW',pady=2)
			b["command"] = lambda e=i:self.PlotOptionsClicked(e)
			self.Options.append(b)
			#ToolTip(c,121)			# Linestyle button
			
		f = Frame(self.MuxFrame)
		f.grid(row=11,column=0,columnspan=4,sticky=NSEW);
		self.Confirm = ttk.Button(f,text="Confirm Changes",command=self.ConfirmMuxChanges)
		self.Confirm.grid(row=0,column=0,sticky='EW',pady=(15,0),padx=(5,5))
		self.ErrorMux = ttk.Label(f,anchor=W,wraplength=300,style='RedMessage.TLabel')
		self.ErrorMux.grid(column=1,row=0,columnspan=3,sticky='W',pady=(8,0),padx=(5,0))

		self.InputChanged(None)
		
		self.BuildPlotData()

	def PlotOptionsClicked(self,index):
		# index is the 0 based index into microLogger.PlotLines array
		# Get the line and pass it to the Dialog to handle changing its'
		# appearance
		LineStylesDialog.CurrentLine = Globals.PlotLines[index]
		LineStylesDialog.CurrentLineIndex = index
		LineStylesDialog(self,title='Set Plot Linestyle',
			minwidth=400,minheight=550,okonly=True)

	def BuildPlotData(self):
		BasicControls.CurrentPlots = [i for i, val in enumerate(BasicControls.ADCInputList) if val < 255]
		BasicControls.ADCInputs = [x for x in BasicControls.ADCInputList if x < 255]
		BasicControls.ADCInputNames = [x for i, x in enumerate(BasicControls.ADCNames) if BasicControls.ADCInputList[i] < 255]

	# c.current([i for i, val in enumerate(MuxDict) if val == muxVal][0]) 
	def FindMux(self,MuxDict,muxVal,c):
		for i, val in enumerate(MuxDict):
			if val == muxVal:
				c.current(i)
				return
		c.current(0)	# No match - set to first entry
		
	def InputChanged(self,val):
		self.Confirm['state'] = "!disabled"
		k = 0
		for i, c in enumerate(self.Muxes):
			if i % 2 == 0:
				Off = c.current() == 0
				self.Muxes[i+1]["state"] = "disabled" if Off else "readonly"
				self.NameEntry[k]["state"] = "disabled" if Off else "normal"
				self.Options[k]["state"] = "disabled" if Off else "!disabled"
				k = k + 1
		
	def ConfirmMuxChanges(self):
		self.ErrorMux['text'] = ""
		Error = True
		for i, c in enumerate(self.Muxes):
			if i % 2 == 0 and not c.current() == 0:
				Error = False
				break
		if Error:
			self.ErrorMux['text'] = "ERROR:\nAt least one Mux input must be selected";
			return

		# Check the same by shifting MUX1 val >> 4 and comparing to MUX 2
		for i, c in enumerate(self.Muxes):
			if i % 2 == 0 and c.current() > 0:
				if c.current() - 1 == self.Muxes[i+1].current():
					self.ErrorMux['text'] = "ERROR:\nMux1 input MUST NOT equal Mux2 input";
					return
		
		# Rebuild ADCInputList... MUST WRITE TO INI
		BasicControls.ADCInputList = []
		for i, mux in enumerate(self.Muxes):
			if i % 2 == 0:
				if mux.current() == 0:
					BasicControls.ADCInputList.append(255)
				else:
					val = self.Mux1Dict[mux.current()] | self.Mux2Dict[self.Muxes[i+1].current()]
					BasicControls.ADCInputList.append(val)
		
		# Rebuild ADCNames ... MUST WRITE TO INI
		BasicControls.ADCNames = []
		for name in self.NameVars:
			BasicControls.ADCNames.append(name.get())
		
		self.BuildPlotData()
		
		self.ReadDataThread.SetMuxInputs(BasicControls.ADCInputs)
		
		self.MuxInputsChanged = True 
		self.Confirm['state'] = "disabled"
		
	def MuxNameChanged(self,val):
		self.Confirm['state'] = "!disabled"
		
	def HaveMuxInputsChanged(self):
		changed = self.MuxInputsChanged
		self.MuxInputsChanged = False
		return changed
		
	def DisableMuxChanges(self,Disable):
		for child in self.MuxFrame.winfo_children():
			name = child.winfo_class()
			if name in ['Label', "TEntry"]:
				child['state'] = "disabled" if Disable else "normal"
			elif name == "TCombobox":
				child['state'] = "disabled" if Disable else "readonly"
			else: pass
		if not Disable:
			self.InputChanged(None)
		self.Confirm['state'] = "disabled"
		
	def AcquireRateChanged(self,val):
		BasicControls.SampleRate = float(self.AcquireRate.get())
		self.ReadDataThread.SetSampleRate(BasicControls.SampleRate)

	def UpdateFullScale(self):
		BasicControls.Gain = int(self.GainAmt.get())
		s = "Full scale voltage is +/- %0.4f Volts (IN A minus IN B)\n" \
		"Where IN A can be IN 0 thru IN 7 or GND and IN B can be any\n" \
		"other input EXCEPT what is selected for IN A\n\n" \
		"Note that the range of values on ANY input is ~0.0V to ~+5.0V"
		Max = str.format(s % (2.0 * float(Calibration.Vref) / float(BasicControls.Gain)))
		self.GainText['text'] = Max

	def GainAmtChanged(self,val):
		self.UpdateFullScale()
		self.ReadDataThread.SetGain(BasicControls.Gain)
		self.GainChanged = True
		
	def HasGainChanged ( self ):
		changed = self.GainChanged
		self.GainChanged = False
		return changed
	
	def NameChanged(self):
		self.after(50,self.AcceptNameChange())
		return True
		
	def AcceptNameChange(self):
		pass
		
	def DataThread ( self, thread , queue):
		self.ReadDataThread = thread
		self.queue = queue
		self.ReadDataThread.SetMuxInputs(BasicControls.ADCInputs)



