# -*- coding: iso-8859-15 -*-
'''
AboutDialog.py - a data logging application written in Python/tkinter
  
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
from	platform	import *
from 	tkinter 	import *
from 	tkinter 	import ttk
import	numpy
import  matplotlib

from	Dialog	import *
from	Utils	import *
from	Mapping	import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

NoRequire = False
try:
	from pkg_resources import require
except ImportError:
	print ( "Cannot import 'require' from 'pkg_resources'" )
	NoRequire = True

from NotePage import BasicNotepage

#
# General About Dialog.
#
class AboutDialog ( Dialog ):
	def BuildDialog ( self ):
		#self.MainFrame.columnconfigure(0,weight=1)
		#self.MainFrame.rowconfigure(1,weight=1)

		image = PIL.Image.open('Assets/micro symbol.png')
		#image = image.resize((50,106), Image.ANTIALIAS)
		photo = ImageTk.PhotoImage(image)
		img = Label(self.MainFrame,image=photo)
		img.image = photo
		img.grid(row=0,column=0,sticky='W')

		l4 = Label(self.MainFrame,text='microLogger ver 0.1  ',
			font=('Helvetica',20,'bold italic'), \
			foreground='blue') #,anchor='center')
		l4.grid(row=0,column=1,sticky='W') #'EW')

		n = Notebook(self.MainFrame,padding=(5,5,5,5))
		n.grid(row=1,column=0,columnspan=2,sticky='NSEW')
		n.columnconfigure(0,weight=1)
		n.rowconfigure(0,weight=1)

		AboutPage = About(n)
		LicensePage = License(n)
		CreditsPage = Credits(n)

		n.add(AboutPage,text='About',underline=0)
		n.add(LicensePage,text='License',underline=0)
		n.add(CreditsPage,text='Credits',underline=0)

# Handle microDAQ About
class About ( BasicNotepage ):
	RPIBoardNumber = 1
	ADCBoardID = 0x0F
	
	def BuildPage ( self ):
		Label(self,text='microLogger Application',
			anchor='center',font=('Helvetica',14),foreground='blue') \
			.grid(row=0,column=0,)

		Label(self,text='Copyright (C) 2020',
			anchor='center',font=('Helvetica',12)).grid(row=1,column=0,)
		Label(self,text='Bill Williams (github.com/Billwilliams1952/)',
			anchor='center',font=('Helvetica',12)).grid(row=2,column=0,)

		Separator(self,orient='horizontal').grid(row=3,column=0,
			columnspan=2,sticky='NSEW',pady=10)

		# Only on PI for PiCamera!
		txt = linux_distribution()
		if txt[0]:
			os = 'Linux OS: %s %s' % ( txt[0].title(), txt[1] )
		else:
			os = 'Unknown Linux OS'
		Label(self,text=os).grid(row=5,column=0,sticky='NSEW')

		l = Label(self,text='Python version: %s' % python_version())
		l.grid(row=6,column=0,sticky='NSEW')

		if NoRequire:
			PILVer = "Pillow (PIL) library version unknown"
		else:
			PILVer = "Pillow (PIL) library version %s" % require('Pillow')[0].version

		Label(self,text="tkinter library version: " + str(tkinter.TclVersion)).grid(row=7,column=0,sticky='NSEW')
		Label(self,text="numpy library version: " + str(numpy.version.version)).grid(row=8,column=0,sticky='NSEW')
		Label(self,text="matplotlib library version: " + str(matplotlib.__version__)).grid(row=9,column=0,sticky='NSEW')
		Label(self,text="wiringPI library version: " + "Built using version 2.5.2 for RPI4 support").grid(row=10,column=0,sticky='NSEW')
		Label(self,text=PILVer).grid(row=12,column=0,sticky='NSEW')
		s = processor()
		if s:
			txt = 'Processor type: %s (%s)' % (processor(), machine())
		else:
			txt = 'Processor type: %s' % machine()
		Label(self,text=txt).grid(row=14,column=0,sticky='NSEW')
		Label(self,text='Platform: %s' % platform()).grid(row=15, \
				column=0,sticky='NSEW')
				
		Label(self,text='RPI Board Number type (for GPIO): %d' % About.RPIBoardNumber).grid(row=16, \
				column=0,sticky='NSEW')
		Label(self,text='ADC Board ID: 0x%X' % About.ADCBoardID).grid(row=17, \
				column=0,sticky='NSEW')

# Handle GPL License
class License ( BasicNotepage ):
	def BuildPage ( self ):
		self.rowconfigure(0,weight=1)
		self.sb = Scrollbar(self,orient='vertical')
		self.sb.grid(row=0,column=1,sticky='NS')
		self.text = Text(self,width=50,wrap='word', #height=15,
			yscrollcommand=self.sb.set)
		self.text.grid(row=0,column=0)#,sticky='NEWS')
		self.text.bind("<Key>",lambda e : "break")	# ignore all keypress
		# Note: return "break" from event handler to ignore
		self.sb.config(command=self.text.yview)
		data = ""
		try:
			with open('Assets/gpl-3.0.txt') as f: self.text.insert(END,f.read())
		except IOError:
			self.text.insert(END,"\n\n\n\t\tError reading file 'Assets/gpl-3.0.txt'")

# Handle Credits
class Credits ( BasicNotepage ):
	def BuildPage ( self ):
		self.rowconfigure(0,weight=1)
		f = MyLabelFrame(self,'Thanks To',0,0)
		string = \
		"Many thanks to Gorden at http://wiringpi.com/ for his excellent\n" \
		"library for controlling the RPI GPIO pins via C++ in the shared library!\n\n" \
		"Tooltip implementation courtesy of:\n" \
		"    code.activestate.com/recipes/576688-tooltip-for-tkinter/\n\n" \
		"Various free icons courtesy of:\n" \
		"    iconfinder.com/icons/ and icons8.com/icon/\n" \
		""
		Label(f,text=string,style='DataLabel.TLabel').grid(row=0,column=0,sticky='NSEW')
