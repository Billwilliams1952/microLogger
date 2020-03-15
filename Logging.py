#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Logging.py - a data logging application written in Python/tkinter
  
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
import  tkinter as tk
from	tkinter import ttk
from 	tkinter.ttk import *

import 	PIL
from 	PIL import Image, ImageTk, ExifTags

from 	Dialog			import *
from 	Mapping			import *
from	NotePage		import *
from	Utils			import *

class Logging ( BasicNotepage ):
    def BuildPage ( self ):
        pass 
