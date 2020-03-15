'''
PreferencesDialog.py - a data logging application written in Python/tkinter
  
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
import 	webbrowser		

from 	Dialog		import *
from 	Mapping		import *
from	NotePage	import *
from	Utils		import *
from	Tooltip		import *

import 	PIL
from 	PIL import Image	#, ImageTk

#
# All microLogger preferences are handled here
#
class PreferencesDialog ( Dialog ):
	RCParams = None
	DefaultFilesDir = "/home/pi/Documents/"
	DefaultScreenShotDir = "/home/pi/Documents/"
	DefaultScreenshotName = "microLogger"
	DefaultFilename = "microLogger"
	DefaultTimestampFormat = "%Y-%m-%d-%H:%M:%S"	# Need to format for ConfigFile
	ScreenshotTimestamp = True
	LoggingTimestamp = True
	AutoCreateNewLogFile = True		# If False, user prompted for new filename
	
	DefaultTheme = 'clam'
	
	# Hardware related
	MaxInputsOnADC = 8
	
	def BuildDialog ( self ):
		self.MainFrame.columnconfigure(0,weight=1)
		self.MainFrame.rowconfigure(0,weight=1)
		
		n = Notebook(self.MainFrame,padding=(5,5,5,5)) #,width=60,height=200)
		n.grid(row=0,column=0,sticky='NEWS')

		self.GeneralPage = General(n,cancel=self.CancelButton,data=self)
		self.InterfacePage = Interface(n,cancel=self.CancelButton)
		self.OtherPage = Other(n,cancel=self.CancelButton)

		n.add(self.GeneralPage,text='General',underline=0)
		n.add(self.InterfacePage,text='Interface',underline=0)
		n.add(self.OtherPage,text='Other',underline=0)

	def OkPressed ( self ):
		if not self.GeneralPage.SaveChanges(): return False
		#self.InterfacePage.SaveChanges()
		#self.OtherPage.SaveChanges()
		return True

	def CancelPressed ( self ):
		if tkMessageBox.askyesno("microLogger Preferences","Exit without saving changes?"):
			return True

# Handle General preferences
class General ( BasicNotepage ):
	def BuildPage ( self ):
		# Setup default folder to save pictures and videos
		f = MyLabelFrame(self,'Set default directories for...',0,0)

		self.iconFiles = PIL.Image.open('Assets/files.png')
		self.iconFiles = ImageTk.PhotoImage(self.iconFiles.resize((22,22),Image.ANTIALIAS))
		
		self.iconCamera = PIL.Image.open('Assets/camera-icon.png')
		self.iconCamera = ImageTk.PhotoImage(self.iconCamera.resize((22,22),Image.ANTIALIAS))

		b = ttk.Button(f,text="Logging files",image=self.iconFiles,compound='left',
			command=self.SelectFilesDirectory,width=12)
		b.grid(row=2,column=0,sticky='W',pady=(5,5))
		ToolTip(b,6004)
		self.FilesDirLabel = Label(f,foreground='#0000FF',
			text=PreferencesDialog.DefaultFilesDir,anchor=W)
		self.FilesDirLabel.grid(row=3,column=0,sticky='EW',padx=10, pady=(0,10));
		ToolTip(self.FilesDirLabel,6005)
		
		b = ttk.Button(f,text="Screenshots",image=self.iconCamera,compound='left',
			command=self.SelectScreenshotDirectory,width=12)
		b.grid(row=4,column=0,sticky='W',pady=(0,5))
		ToolTip(b,6002)
		self.ScreenshotDirLabel = Label(f,foreground='#0000FF',
			text=PreferencesDialog.DefaultScreenShotDir,anchor=W)
		self.ScreenshotDirLabel.grid(row=5,column=0,sticky='EW',padx=10);
		ToolTip(self.FilesDirLabel,6003)
		
		f = MyLabelFrame(self,'Default Filenames and Timestamps...',1,0)
		f1 = Frame(f)
		f1.grid(row=0,column=0,columnspan=2,sticky=NSEW)
		Label(f1,text='Logging Filename:').grid(row=0,column=0,sticky='W')
		self.DefaultFilename = MyStringVar(PreferencesDialog.DefaultFilename)
		e = ttk.Entry(f1,width=25,textvariable=self.DefaultFilename)
		e.grid(row=0,column=1,sticky='W')
		ToolTip(e,6060)
		
		Label(f1,text='Screenshot Filename:').grid(row=1,column=0,sticky='W',pady=(5,0))
		self.DefaultPlotFilename = MyStringVar(PreferencesDialog.DefaultScreenshotName)
		e = ttk.Entry(f1,width=25,textvariable=self.DefaultPlotFilename)
		e.grid(row=1,column=1,sticky='W',pady=(5,0))
		ToolTip(e,6061)
		
		Label(f1,text='Timestamp format:').grid(row=2,column=0,sticky='W',pady=(5,0))
		self.TimeStamp = MyStringVar(PreferencesDialog.DefaultTimestampFormat)
		e = ttk.Entry(f1,width=25,textvariable=self.TimeStamp)
		e.grid(row=2,column=1,sticky='W',pady=(5,0))
		ToolTip(e,6050)
		image = PIL.Image.open('Assets/help.png')
		self.helpimage = ImageTk.PhotoImage(image.resize((12,12),Image.ANTIALIAS))
		b = ttk.Button(f1,image=self.helpimage,width=10,command=self.FormatHelp,padding=(2,2,4,2))
		b.grid(row=2,column=2,padx=5,pady=(5,0))
		ToolTip(b,6052)
		
		Label(f1,text='Sample timestamp:').grid(row=3,column=0,sticky='W',pady=(5,0))
		self.TimestampLabel = MyStringVar(datetime.datetime.now() \
			.strftime(PreferencesDialog.DefaultTimestampFormat))
		self.tsl = Label(f1,textvariable=self.TimestampLabel,foreground='#0000FF')
		self.tsl.grid(row=3,column=1,sticky='W',pady=(5,0))
		ToolTip(self.tsl,6051)
		self.after(1000,self.UpdateTimestamp)
		
	def ChangeDirectory ( self, defaultDir, label, text ):
		oldDir = os.getcwd()
		
		try:
			newDir = defaultDir
			os.chdir(defaultDir)
			# I hate that it doesn't allow you set set the initial directory!
			dirname = FileDialog.askdirectory()#self, initialdir="/home/pi/Pictures",
						 #title='Select Photo Directory')
			if dirname:
				print(dirname)
				# Check if exists, if not... create it
				if not os.path.isdir(dirname):
					print("Trying to create ",dirname)
					# try to create it... if fails or exception
					os.makedirs(dirname)
					print("Made directory ",dirname)
				else:
					print("Path %s exists" % dirname)
				label['text'] = dirname
			else: 
				print("Cancelled")
				dirname = defaultDir
		except:
			print ( "Preferences dialog error setting/creating directory")
			dirname = defaultDir
		finally:
			os.chdir(oldDir)
			
		return dirname
	def SelectFilesDirectory ( self ):
		PreferencesDialog.DefaultFilesDir = \
			self.ChangeDirectory(PreferencesDialog.DefaultFilesDir,self.FilesDirLabel,"Files")
	def SelectScreenshotDirectory ( self ):
		PreferencesDialog.DefaultScreenShotDir = \
			self.ChangeDirectory(PreferencesDialog.DefaultScreenShotDir,self.ScreenshotDirLabel,"Screenshots")
		PreferencesDialog.RCParams['savefig.directory'] = PreferencesDialog.DefaultScreenShotDir
	def CheckTimestamp ( self, text ):
		try:
			self.TimestampLabel.set(datetime.datetime.now().strftime(text))
			self.tsl['foreground'] ='#0000FF'
			PreferencesDialog.DefaultTimestampFormat = text
		except:
			self.TimestampLabel.set("Error in format string")
			self.tsl['foreground'] ='#FF0000'
	def UpdateTimestamp ( self ):
		self.CheckTimestamp(self.TimeStamp.get())
		self.after(1000,self.UpdateTimestamp)
	def FormatHelp ( self ):
		webbrowser.open_new_tab('https://docs.python.org/2/library/datetime.html')
	def SaveChanges ( self ):
		if len(self.DefaultFilename.get()) == 0:
			return False
		if len(self.DefaultPlotFilename.get()) == 0:
			return False
		PreferencesDialog.DefaultFilename = self.DefaultFilename.get()
		PreferencesDialog.DefaultScreenshotName = self.DefaultPlotFilename.get()
		return True

# Handle Interface preferences
class Interface ( BasicNotepage ):
	
	def BuildPage ( self ):
		self.iconMonitor = ImageTk.PhotoImage( \
			PIL.Image.open("Assets/computer-monitor.png").resize((64,64),Image.ANTIALIAS))
		Label(self,image=self.iconMonitor).grid(row=0,column=0,sticky='W')

		f = MyLabelFrame(self,'Interface themes',0,1)
		f.columnconfigure(1,weight=1)
		Label(f,text='Set theme').grid(row=0,column=0,sticky='W',pady=(5,5))
		self.themes = Combobox(f,height=10,state='readonly')
		self.themes.grid(row=0,column=1,sticky='W',padx=(10,0))
		self.themes['values'] = Style().theme_names()
		self.themes.set(PreferencesDialog.DefaultTheme)
		self.themes.bind('<<ComboboxSelected>>',self.ThemesSelected)
		ToolTip(self.themes,6100)

		f = MyLabelFrame(self,'Tooltips',1,0,span=2)
		self.ShowTooltips = MyBooleanVar(ToolTip.ShowToolTips)
		self.ShowTipsButton = ttk.Checkbutton(f,text='Show those annoying tooltips',
			variable=self.ShowTooltips, command=self.ShowTooltipsChecked)#,padding=(5,5,5,5))
		self.ShowTipsButton.grid(row=1,column=0,columnspan=2,sticky='W')
		ToolTip(self.ShowTipsButton,6110)

		self.ShowTipNumber = MyBooleanVar(ToolTip.ShowTipNumber)
		self.ShowTipNumButton = ttk.Checkbutton(f,text='Show tip number in tip (debug)',
			variable=self.ShowTipNumber, command=self.ShowTooltipNumChecked,
			padding=(25,5,5,5))
		self.ShowTipNumButton.grid(row=2,column=0,columnspan=2,sticky='W')
		ToolTip(self.ShowTipNumButton,6111)

		ttk.Label(f,text='Delay before tip',padding=(25,0,0,0)).grid(row=3,column=0,sticky='W')
		scale = ttk.Scale(f,value=ToolTip.ShowTipDelay,
			from_=0.1,to=5.0,orient='horizontal',
			command=self.TipDelayChanged)
		scale.grid(row=3,column=1,sticky='W')
		ToolTip(scale,6112)
		self.DelayText = MyStringVar("")
		l = Label(f,textvariable=self.DelayText,foreground='#0000FF')
		l.grid(row=3,column=2,sticky='W')
		ToolTip(l,6113)

		self.TipDelayChanged(ToolTip.ShowTipDelay)	# Force display update
	def ThemesSelected ( self, event ):
		PreferencesDialog.DefaultTheme = self.themes.get()
		Style().theme_use(PreferencesDialog.DefaultTheme)
	def ShowTooltipsChecked ( self ):
		ToolTip.ShowToolTips = self.ShowTooltips.get()
	def ShowTooltipNumChecked ( self ):
		ToolTip.ShowTipNumber = self.ShowTipNumber.get()
	def TipDelayChanged (self, val ):
		ToolTip.ShowTipDelay = float(val)
		self.DelayText.set('{:.1f} sec'.format(float(val)))
	def SaveChanges ( self ):
		pass

# Handle Other preferences
class Other ( BasicNotepage ):
	pass


