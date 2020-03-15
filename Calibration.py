#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#  Calibration.py
#
#  Copyright 2018  Bill Williams
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
'''

import 	os
from   	collections import OrderedDict
import 	RPi.GPIO

from	tkinter import ttk
from 	tkinter.ttk import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

from 	Dialog			import *
from 	Mapping			import *
from	NotePage		import *
from	Utils			import *

class Calibration ( BasicNotepage ):
	Vref = 2.5
	
	def BuildPage ( self ):   
		#-----
		f1 = MyLabelFrame(self,'Analog to Digital Converter',0,0,span=2)
		Label(f1,text="Voltage Reference",anchor=W).grid(column=0,row=0,sticky='W',ipadx=3,ipady=3)
		self.VRefLabel = Label(f1,text="%0.3f V" % Calibration.Vref,anchor=E)
		self.VRefLabel.grid(column=1,row=0,sticky=E)

		f1 = MyLabelFrame(self,'Offset and Gain Calibration',1,0,span=2)
		b = ttk.Button(f1,text="Perform Offset & Gain Calibration",command=self.DoGainCalibration)#,ipadx=(0,2))
		b.grid(row=0,column=0,sticky='EW',padx=(5,5),pady=(10,0))   
		#Label(f1,text="Calibration process",anchor=W).grid(column=0,row=0,sticky='W',ipadx=3,ipady=3)

	def DoGainCalibration(self):
		# Call the thread and do an Offset/Gain Calibration
		pass
