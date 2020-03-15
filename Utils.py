'''
Utils.py - a data logging application written in Python/tkinter
  
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

from 	tkinter import *
from 	tkinter.colorchooser import askcolor
import 	tkinter.filedialog
import 	tkinter.messagebox
from 	tkinter import ttk
import	tkinter.font
from	tkinter.font	import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

#from 	Dialog	import *
from	Tooltip	import *

#
# General utility functions
#
def UnderConstruction ( window ):
	Label(window,text='UNDER CONSTRUCTION',font=('Arial',14,('bold')),
		anchor='center').grid(row=0,column=0,sticky='EW')

def OnOff ( val ): return 'On' if val else 'Off'

def EvenOdd ( val ): return 'even' if val else 'odd'

# Add BooleanVar in here
def MyRadio ( f, txt, varValue, varName, cmd=None, row=0, col=0, stick='W',
				  span=1, pad=(5,5,5,5), tip='No Tip number provided'):
#def MyRadio ( f, txt, varValue, varName = None, cmd=None, row=0, col=0, stick='W',
#				  span=1, pad=(5,5,5,5), tip='No Tip number provided'):
	# if varName is None:
	#		# Determine type of var from varValue and create one
	#		if type(varValue) is int:
	# 			varName = MyIntVar(varValue)
	#		elif type(varValue) is boolean:
	# 			varName = MyBooleanVar(varValue)
	#		elif type(varValue) is str:
	# 			varName = MyStringVar(varValue)
	if cmd is None:
		r = ttk.Radiobutton(f,text=txt,value=varValue,variable=varName,
			 padding=pad)
	else:
		r = ttk.Radiobutton(f,text=txt,value=varValue,variable=varName,
			command=lambda:cmd(varValue),padding=pad)
	r.grid(row=row,column=col,sticky=stick, columnspan=span)
	ToolTip(r,msg=tip)
	return r # , varName		# return RadioButton and BooleanVar

def MyComboBox ( parent, values, current, callback, width=5, row=0, col=0,
					  sticky='EW', state='disabled', tip='No Tip number provided' ):
	combo = ttk.Combobox(parent,state=state,width=width)
	combo.grid(row=row,column=col,sticky=sticky)
	combo.bind('<<ComboboxSelected>>',callback)
	combo['values'] = values
	combo.current(current)
	ToolTip(combo,tip)
	return combo

def MyLabelFrame ( f, txt, row, col, stick='NEWS', py=5, span=1, pad=(5,5,5,5)):
	l = ttk.LabelFrame(f,text=txt,padding=pad)
	l.grid(row=row,column=col,sticky=stick,columnspan=span,pady=py)
	return l

def MyBooleanVar ( setTo ):
	b = BooleanVar()
	b.set(setTo)
	return b

def MyIntVar ( setTo ):
	b = IntVar()
	b.set(setTo)
	return b

def MyStringVar ( setTo ):
	s = StringVar()
	s.set(setTo)
	return s

# image = PIL.Image.open('Assets/stop.png')
# self.StopImage = ImageTk.PhotoImage(image.resize((22,22),Image.ANTIALIAS))

def GetPhotoImage ( filename ):
	if isinstance(filename,str):
		return ImageTk.PhotoImage(PIL.Image.open(filename))
	else:
		return ImageTk.PhotoImage(filename)
