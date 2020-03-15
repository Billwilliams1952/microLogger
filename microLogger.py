#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
microLogger.py - a data logging application written in Python/tkinter
  
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

import  sys
assert  sys.version_info >= (3, 7, 3)   # Python ver 3.7.3 or greater is required

import  ctypes
from    ctypes import *
import  os

import  matplotlib
#from    matplotlib import lines.Line2D
matplotlib.use("TkAgg")
from    matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from    matplotlib.figure import Figure

import  numpy as np

import  tkinter as tk
from    tkinter import *	# Python 3.X
from	tkinter import ttk
from 	tkinter.ttk import *
import	tkinter.font
import  PIL
from    PIL import Image, ExifTags

from    random import *
import  threading
from    threading import Thread, Lock
import  queue
import  time
import  math

from    Globals             import *
from    ConfigFile          import *
from	BasicControls       import *
from	Advanced            import *
from	Acquisition         import *
from	Display             import *
from	Logging             import *
from    Calibration         import *
from    PreferencesDialog   import *
from    Tooltip	            import *
from	Utils               import *
from    Mapping             import *
from 	AboutDialog         import *


class ReadDataThread(Thread):
	'''
	This thread does the majority of the heavy listing for the data logging.
	Note that the majority of the ADC code is written in C++ in the shared
	library ADCReadData.so
	'''
	def __init__(self, queue, Gain, MuxInputs, SampleRate, ADC_CS, ADC_RDY, SYNC_PWRDN):
		Thread.__init__(self)

		self.queue = queue
		self.lock = Lock()
		self.stop = threading.Event()   # MUST do it this way since Event() by
										# itself is a tkinter defined object
		self.ADCLib = 'Library/ADCReadData.so'
		self.Fail = False
		try:
			# Open shared CPP library:
			self.cpplib = CDLL(self.ADCLib)
			self.cppobj = self.cpplib.CPPClass_py()
		
			self.SetLibMuxChannels = self.cpplib.SetMuxChannels
			self.ReadLibData = self.cpplib.ReadData
			self.SetLibRestart = self.cpplib.SetRestart
			self.SetLibPauseRestart =  self.cpplib.SetPauseRestart
			self.SetLibVRef = self.cpplib.SetVRef
			self.SetLibVRef.argtypes = [c_void_p,c_double] # (all defined by ctypes)
			self.SetLibGain = self.cpplib.SetGain
			self.SetLibGain.argtypes = [c_void_p,c_ubyte] # (all defined by ctypes)
			self.GetLibReading = self.cpplib.GetReading
			self.SetLibSampleTime = self.cpplib.SetSampleTime
			self.SetLibSampleTime.argtypes = [c_void_p,c_double] # (all defined by ctypes)
			self.GetLibReading.restype = ctypes.c_double
			self.GetLibTimeStamp = self.cpplib.GetTimeStamp
			self.GetLibTimeStamp.restype = ctypes.c_double
			self.GetLibDeltaTime = self.cpplib.GetDeltaTime
			self.GetLibDeltaTime.restype = ctypes.c_double  
			self.GetLibRealDelay = self.cpplib.GetRealDelay
			self.GetLibRealDelay.restype = ctypes.c_double   
			self.GetLibUpdateTime = self.cpplib.GetUpdateTime
			self.GetLibUpdateTime.restype = ctypes.c_double  
			self.LibOffsetAndGainCal = self.cpplib.OffsetAndGainCal  
			self.LibReturnRPIBoardNumber = self.cpplib.ReturnRPIBoardNumber 
		except:
			print("Failure initializing ",ADCLib)
			self.Fail = True

		self.NumMuxInputs = len(MuxInputs)
		self.pause = False
		self.ADC_CS = ADC_CS
		self.ADC_RDY = ADC_RDY
		self.SYNC_PWRDN = SYNC_PWRDN
		self.OutputFile = None  # In case a real file is never used.
		self.Logging = False
		 
		self.SetMuxInputs(MuxInputs)
		self.RealDelay = 1.0 / SampleRate
		self.SetLibSampleTime(self.cppobj,self.RealDelay)       
		self.SetLibGain(self.cppobj,Gain) 
		
		self.cpplib.Init(self.cppobj)

	def Calibration (self):
		pass
		# self.AcquireDataThread.AcquireLock()
		# print("Short all inputs to Ground... press any key when ready")
		# input()
		# self.SPI_OUT([0xF0])
		# GPIO.output(self.ADC_CS,False)
		# self.spi.xfer([0xF3])        # System Offset Cal - short inputs
		# time.sleep(0.2)
		# GPIO.output(self.ADC_CS,True)
		# time.sleep(2.0)

		# print("Apply 5VDC to AD0+ GND to AD1+...press any key when ready")
		# input()
		# GPIO.output(self.ADC_CS,False)
		# self.spi.xfer([0xF4])        # System Offset Cal - short inputs
		# time.sleep(0.2)
		# GPIO.output(self.ADC_CS,True)
		# self.AcquireDataThread.ReleaseLock()
		# time.sleep(2.0)
		# print("System Calibration is complete")
		# self.AcquireDataThread.ReleaseLock()        
	def GetRPIBoardNumber(self):
		return self.LibReturnRPIBoardNumber(self.cppobj) 
	def SetLogging(self, logging):
		if not self.pause: self.lock.acquire()
		self.Logging = logging
		if not self.pause: self.lock.release()
	def OffsetAndGainCal ( self):
		if not self.pause: self.lock.acquire()
		self.LibOffsetAndGainCal(self.cppobj) 
		if not self.pause: self.lock.release()
	def SetFile ( self, FileHandle):
		if not self.pause: self.lock.acquire()
		self.OutputFile = FileHandle
		if not self.pause: self.lock.release()
	def PauseRestart(self):
		if not self.pause: self.lock.acquire()  
		self.SetLibPauseRestart(self.cppobj); 
		if not self.pause: self.lock.release() 
	def RestartCapture(self):
		if not self.pause: self.lock.acquire() 
		self.SetLibRestart(self.cppobj); 
		if not self.pause: self.lock.release()    
	def SetSampleRate(self, SampleRate):
		if not self.pause: self.lock.acquire()
		self.RealDelay = 1.0 / SampleRate
		self.SetLibSampleTime(self.cppobj,self.RealDelay)
		if not self.pause: self.lock.release()
	def SetGain(self, Gain):
		if not self.pause: self.lock.acquire()
		self.SetLibGain(self.cppobj,Gain)     
		if not self.pause: self.lock.release()
	def SetVref(self, Vref):
		if not self.pause: self.lock.acquire()
		self.SetLibVRef(self.cppobj,self.Vref)
		if not self.pause: self.lock.release()
	def SetMuxInputs(self,M):
		# Hack until I can figure out how to send lists to the Library
		if not self.pause: self.lock.acquire()
		#print("MuxInputs = ",M)
		self.MuxInputs = M
		self.NumMuxInputs = len(M)
		if self.NumMuxInputs == 1:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], 0xFF, 0, 0, 0, 0, 0, 0);
		elif self.NumMuxInputs == 2:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], 0xFF, 0, 0, 0, 0, 0);
		elif self.NumMuxInputs == 3:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], 0xFF, 0, 0, 0, 0);
		elif self.NumMuxInputs == 4:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], M[3], 0xFF, 0, 0, 0);
		elif self.NumMuxInputs == 5:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], M[3], M[4], 0xFF, 0, 0);
		elif self.NumMuxInputs == 6:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], M[3], M[4], M[5], 0xFF, 0);
		elif self.NumMuxInputs == 7:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], M[3], M[4], M[5], M[6], 0xFF);
		elif self.NumMuxInputs == 8:
			self.cpplib.SetMuxChannels(self.cppobj,M[0], M[1], M[2], M[3], M[4], M[5], M[6], M[7]);
		else:
			self.SetLibMuxChannels(self.cppobj,0x01, 0x23, 0xFF, 0, 0, 0, 0, 0);
		if not self.pause: self.lock.release()

	def IsPaused(self): return self.pause
	def Pause(self,pause):
		self.pause = pause
		if self.pause: self.lock.acquire()
		else: self.lock.release()     
	def TogglePause(self):
		self.Pause(not self.pause)
		return self.pause
	def ReleaseLock(self):
		self.lock.release()
	def AcquireLock(self):
		self.lock.acquire()
	def Shutdown(self):
		self.stop.set()
	def run(self):
		if self.Fail: return
		
		print("ReadDataThread running...")

		while not self.stop.wait(self.GetLibRealDelay(self.cppobj)): #self.RealDelay):
			self.lock.acquire() # Block here
			
			# The main library function to acquire a set of data
			self.ReadLibData(self.cppobj)
			vals = [self.GetLibReading(self.cppobj,i) for i in range(0,self.NumMuxInputs)]
			update = self.GetLibUpdateTime(self.cppobj)
			
			if self.Logging and self.OutputFile != None:
				# The Header containing the names has already been written
				self.OutputFile.write(str.format("%0.4f, " % update) + 
					"".join(['%0.10f,' % val for val in vals]) + "\n")
				
			self.lock.release()
			# Add to list of items to plot...
			self.queue.put([update,vals])
			
			# Account for processing time - shave off from requested Sample Rate
			#self.RealDelay = self.GetLibRealDelay(self.cppobj)
			
			#print("Delta Time: %0.4e" % self.GetLibDeltaTime(self.cppobj))
			
		print("ReadDataThread shutting down...")

class microLogger ( Frame ):
	'''
	The main application.
	'''
	RCParams = None
	colors = ['#FF0000', '#0000FF', '#FF00FF', '#008000',
			  '#FF0000', '#0000FF', '#FF00FF', '#008000' ]
	styles = ['-','-','-','-','--','--','--','--']
	widths = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
	markers = ['','','','','','','','']
	markerSize = [2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0]
	markerFillStyle = ['none','none','none','none','none','none','none','none']

	def __init__(self, root, title):
		Frame.__init__(self, root)
		self.root = root
		self.title = title
		self.root.title(title)
		
		self.root = root
		self.root.rowconfigure(0,weight=1)     # First row expands vert
		self.root.columnconfigure(1,weight=1)  # Plot side expands horz
		
		self.ControlMapping = ControlMapping()  # Styles for controls
		ToolTip.LoadToolTips()

		self.queue = queue.Queue()      
		
		self.OutputFile = None
			   
		#----------------------- The Main Thread -----------------------
		self.SYNC_PWRDN = 27        # Probably dont need these anymore
		self.DAC_CS = 23
		self.ADC_CS = 22
		self.ADC_DRDY = 17
		self.AcquireDataThread = ReadDataThread(self.queue,
												BasicControls.Gain,
												BasicControls.ADCInputs,
												BasicControls.SampleRate,
												self.ADC_CS,self.ADC_DRDY,self.SYNC_PWRDN)
		self.AcquireDataThread.Pause(True)      # Initially NOT running
		
		#----------- Icons for Menu and Buttons ------------------------
		self.iconClose = GetPhotoImage("Assets/window-close.png")
		# image = PIL.Image.open('Assets/camera-icon.png')
		# self.iconCameraBig = GetPhotoImage(image.resize((22,22),Image.ANTIALIAS))
		# self.iconCamera = GetPhotoImage(image.resize((16,16),Image.ANTIALIAS))
		
		image = PIL.Image.open('Assets/stop.png')
		self.StopImage = ImageTk.PhotoImage(image.resize((22,22),Image.ANTIALIAS))
		#self.StopImage = GetPhotoImage(image.resize((22,22),Image.ANTIALIAS))
		image = PIL.Image.open('Assets/run.png')
		self.RunImage = GetPhotoImage(image.resize((22,22),Image.ANTIALIAS))
		self.ResetImage = GetPhotoImage(PIL.Image.open('Assets/reset.png').resize((22,22),Image.ANTIALIAS))
		self.CreateNewLogfileImage = GetPhotoImage(PIL.Image.open('Assets/folders.png').resize((22,22),Image.ANTIALIAS))
		self.StopNewLogfileImage = GetPhotoImage(PIL.Image.open('Assets/stop3.png').resize((22,22),Image.ANTIALIAS))
		#self.CreateNewLogfile = GetPhotoImage(PIL.Image.open('Assets/files.png').resize((22,22),Image.ANTIALIAS))
		self.PauseLogImage = GetPhotoImage(PIL.Image.open('Assets/pause2.png').resize((22,22),Image.ANTIALIAS))

		#------- Create the notebook side (left side) with tabs --------
		self.NotebookFrame = ttk.Frame(self.root,padding=(5,5,5,5))
		self.NotebookFrame.grid(row=0,column=0,sticky=NSEW)
		self.NotebookFrame.rowconfigure(2,weight=1)
		self.NotebookFrame.columnconfigure(0,weight=1)

		n = Notebook(self.NotebookFrame)
		n.grid(row=1,column=0,rowspan=2,sticky=NSEW)
		n.columnconfigure(0,weight=1)
		n.enable_traversal()

		self.BasicControlsFrame = BasicControls(n)
		self.BasicControlsFrame.DataThread(self.AcquireDataThread, self.queue)
		self.BasicControlsFrame.ConfirmMuxChanges()
		n.add(self.BasicControlsFrame ,text='Inputs',underline=0)

		self.DisplayFrame = Display(n)
		n.add(self.DisplayFrame ,text='Display/Plot',underline=0) 

		#self.LoggingFrame = Logging(n)
		#n.add(self.LoggingFrame ,text='Logging',underline=0)  
		
		#self.AdvancedFrame = Advanced(n)
		#n.add(self.AdvancedFrame ,text='Advanced',underline=0)  
		
		# self.CalibrationFrame = Calibration(n)
		# n.add(self.CalibrationFrame ,text='Calibration',underline=0)  

		#----- The actual plot on the right side of the main frame -----
		self.PlotFrame = tk.Frame(self.root) #,bg='#f0f0f0')
		self.PlotFrame.grid(row=0,column=1,sticky=NSEW)
		self.PlotFrame.rowconfigure(0,weight=1)
		self.PlotFrame.columnconfigure(0,weight=1)

		#------------ Create the MatPlotLib Figure ---------------------
		PreferencesDialog.RCParams = matplotlib.rcParams
		
		PreferencesDialog.RCParams['savefig.directory'] = PreferencesDialog.DefaultScreenShotDir
		
		self.figure = Figure()      #figsize=(5,5), dpi=100)
		self.axes = self.figure.add_subplot(111)
		# Create multiple plots - assign Lines to each one.
		#self.axes1 = self.figure.add_subplot(212)

		# Create an array of 8 plot lines
		self.PlotLines = []
		for i in range(0,PreferencesDialog.MaxInputsOnADC):
			self.PlotLines.append(
				matplotlib.lines.Line2D([],[],
					linewidth=microLogger.widths[i],
					linestyle=microLogger.styles[i], 
					color=microLogger.colors[i], 
					marker=microLogger.markers[i], 
					markersize=microLogger.markerSize[i],
					fillstyle=microLogger.markerFillStyle[i], 
					label=BasicControls.ADCNames[i]) )
				
		Globals.PlotLines = self.PlotLines  # Give access to others

		self.DefaultXMinVal = -2.0 * Calibration.Vref / BasicControls.Gain
		self.DefaultXMaxVal =  2.0 * Calibration.Vref / BasicControls.Gain
		self.axes.set_ylim(self.DefaultXMinVal,self.DefaultXMaxVal)
		self.axes.set_xlim(0,-int(Display.XAxisTimePeriod))
		
		self.axes.grid(b=True, which='both', color='0.65', linestyle='--')
			
		self.axes.set_title(Display.PlotTitle,fontsize=Display.PlotTitleFontSize)
		self.axes.set_xlabel(Display.XAxisText,fontsize=Display.XAxisFontSize)
		self.axes.set_ylabel(Display.YAxisText,fontsize=Display.YAxisFontSize)

		self.canvas = FigureCanvasTkAgg(self.figure, self.PlotFrame)
		#ToolTip(self.figure,1)
		self.canvas.get_default_filename = lambda: "microLogger.png"
		self.canvas.get_tk_widget().grid(row=0,column = 0,sticky="NSEW",padx=(0,5),pady=(5,5))
		self.canvas.draw()
		
		#-------------------- Create the Plot toolbar ------------------
		self.ToolbarFrame = tk.Frame(self.PlotFrame,bg='#f0f0f0')
		self.ToolbarFrame.grid(row=1,column=0,sticky="W")
		self.Toolbar = NavigationToolbar2Tk(self.canvas, self.ToolbarFrame)
		#self.Toolbar.get_tk_widget().grid(row=1,column = 0,sticky="NSEW") #pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		#-----
		self.RunPlot = True
		self.UpdateGraph()         
		self.DisplayFrame.SetPlotInfo(self.figure, self.canvas, self.axes)
		#-----
		
		#----------- New frame for buttons underneath the plot ---------
		f10 = Frame(self.PlotFrame)
		f10.grid(row=2,column=0,columnspan=3,sticky=NSEW,pady=(5,0))
		for i in range(0,5):
			f10.columnconfigure(i,weight=20)    # Equal size for all buttons
		# f10.columnconfigure(1,weight=25)
		# f10.columnconfigure(2,weight=25)
		# f10.columnconfigure(3,weight=25)
		#----- First row of buttons
		self.RunStop = ttk.Button(f10,command=self.RunStopClicked,image=self.RunImage,
			compound='left',style='BigText.TButton',text="RUN")#,ipadx=(2,2))
		self.RunStop.grid(row=0,column=0,rowspan=2,sticky='EW',padx=(5,5))
		ToolTip(self.RunStop,30)
		self.StartStopLog = ttk.Button(f10,text="START NEW LOG",image=self.CreateNewLogfileImage,
			compound='left',style='BigText.TButton',command=self.StartStopLogClicked)#,ipadx=(0,2))
		self.StartStopLog.grid(row=0,column=3,sticky='NSEW',padx=(0,5))
		ToolTip(self.StartStopLog,31)
		self.Logging = False
		self.LoggingPaused = False
		self.PauseLogFile = ttk.Button(f10,text="PAUSE LOG",image=self.PauseLogImage,
			compound='left',style='BigText.TButton',command=self.PauseLogFileClicked)#,ipadx=(0,2))
		ToolTip(self.PauseLogFile,32)
		self.PauseLogFile.grid(row=0,column=4,sticky='NSEW',padx=(0,5))
		#---- Second row of buttons
		self.ClearPlot = ttk.Button(f10,text="CLEAR PLOT",image=self.ResetImage,
			compound='left',style='BigText.TButton',command=self.ClearPlotClicked)#,ipadx=(0,2))
		self.ClearPlot.grid(row=1,column=3,sticky='NSEW',padx=(0,5),pady=(5,5)) 
		ToolTip(self.ClearPlot,33)      
		self.RunPlot = True
		self.RunPausePlot = ttk.Button(f10,text="PAUSE PLOT",image=self.PauseLogImage,
			compound='left',style='BigText.TButton',command=self.RunPausePlotClicked)#,ipadx=(0,2))
		self.RunPausePlot.grid(row=1,column=4,sticky='NSEW',padx=(0,5),pady=(5,5))
		ToolTip(self.RunPausePlot,34)
		
		#---------------------------- Menu -----------------------------
		menubar = Menu(root,
			foreground='black',background='#F0F0F0',activebackground='#86ABD9',
			activeforeground='white')
		#----- File
		filemenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		filemenu.add_command(label="Preferences...",underline=0,
			#image=self.iconPrefs, compound='left',
			command=lambda e=None:self.SystemPreferences(e))
		filemenu.add_separator()
		filemenu.add_command(label="Quit",underline=0,image=self.iconClose,
			compound='left',accelerator='Ctrl+Q',
			command=lambda e=None:self.quitProgram(e))
		self.DefineAccelerators('c','q',lambda e=None:self.quitProgram(e))
		menubar.add("cascade",label='File',underline=0,menu=filemenu)
		#----- View
		viewmenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')

		self.viewPlotPane = MyBooleanVar(True) 
		viewmenu.add_checkbutton(label="Plot",underline=0,
			accelerator='Ctrl+Shift+P',
			onvalue=True,offvalue=False,variable=self.viewPlotPane,
			command=lambda e='Menu':self.ViewPlotPane(e))
		self.DefineAccelerators('cs','p',self.ViewPlotPane)        

		self.viewNotebookPane = MyBooleanVar(True)       
		viewmenu.add_checkbutton(label="Controls",underline=0,
			accelerator='Ctrl+Shift+C',
			onvalue=True,offvalue=False,variable=self.viewNotebookPane,
			command=lambda e='Menu':self.ViewNotebookPane(e))
		self.DefineAccelerators('cs','c',self.ViewNotebookPane)

		self.ViewStatusBarBoolean = MyBooleanVar(True)
		viewmenu.add_checkbutton(label="Status bar",underline=0,
			onvalue=True,offvalue=False,variable=self.ViewStatusBarBoolean,
			command=lambda e='Menu':self.ViewStatusBar(e))

		menubar.add("cascade",label='View',underline=0,menu=viewmenu)        
		#----- Hardware
		hardwaremenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		hardwaremenu.add_command(label="Calibration...",underline=0,
			#image=self.iconPrefs, compound='left',
			command=lambda e=None:self.Calibration(e))   
		
		menubar.add("cascade",label='Hardware',underline=0,menu=hardwaremenu)

		#----- Help
		helpmenu = Menu(menubar,tearoff=0,foreground='black',background='#F0F0F0',
		activebackground='#86ABD9',activeforeground='white')
		#helpmenu.add_command(label="Keyboard shortcuts...",underline=0,
		#    command=lambda e=None:self.KeyboardShortcuts(e))
		helpmenu.add_separator()
		helpmenu.add_command(label="About...",underline=0,command=lambda e=None:self.HelpAbout(e))
		
		menubar.add("cascade",label='Help',underline=0,menu=helpmenu)
		
		root.config(menu=menubar)
		
		#-------------------------- Status Bar -------------------------
		# Use tk instead of ttk to access background color 
		self.StatusBarFrame = tk.Frame(self.root,height=20,bg='#f0f0ff')
		self.StatusBarFrame.grid(row=1,column=0,columnspan=2,sticky=NSEW,padx=5,pady=(0,5))
		self.StatusBarFrame.columnconfigure(5,weight=1)
		
		#----- Add Queue size -----
		self.QueueSize = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,font=('Arial',9),
			textvariable=self.QueueSize,style='StatusBar.TLabel', width=13)
		l.grid(row=0,column=0,sticky='W')
		ToolTip(l,40)
		#----- Add Write -----
		self.FlushFile = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,font=('Arial',9),
			textvariable=self.FlushFile,style='StatusBar.TLabel', width=13)
		l.grid(row=0,column=1,sticky='W')
		ToolTip(l,41)
		#----- Add Filesize -----
		self.Filesize = StringVar()
		l = ttk.Label(self.StatusBarFrame,anchor=CENTER,font=('Arial',9),
			textvariable=self.Filesize,style='StatusBar.TLabel', width=25)
		l.grid(row=0,column=2,sticky='W')
		ToolTip(l,42)
		
		root.protocol("WM_DELETE_WINDOW", lambda e=None:self.quitProgram(e))
		
		#-------------------- Some initializing ------------------------
		self.ToggleRunState(False)
		
		''' ------------------  START ME UP   --------------------------
		  Note, initially, the thread will be blocked because Pause has 
		  been previously set to true
		'''
		self.AcquireDataThread.start()
		
		# Setup to automatically update status and flush log file
		self.after(10000,self.AutoFlushFile)

	def RunStopClicked(self):
		paused = self.AcquireDataThread.IsPaused()
		self.ToggleRunState(paused)
		self.AcquireDataThread.TogglePause()
	def ToggleRunState(self,paused):
		if paused:
			self.AcquireDataThread.PauseRestart()
			self.RunStop['image'] = self.StopImage
			self.RunStop['text'] = "STOP"
		else:
			self.RunStop['image'] = self.RunImage
			self.RunStop['text'] = "RUN"
		
		state = '!disabled' if paused else 'disabled'
		self.RunPausePlot['state'] = state
		self.StartStopLog['state'] = state
		self.PauseLogFile['state'] = '!disabled' if self.Logging and paused else 'disabled'

		# True = Disable
		self.BasicControlsFrame.DisableMuxChanges(paused and self.Logging)
		
	def BuildLogfileName(self):
		try:
			self.LoggingFilename = PreferencesDialog.DefaultFilesDir + \
				"/" + PreferencesDialog.DefaultFilename 
			if PreferencesDialog.LoggingTimestamp:
				self.LoggingFilename = self.LoggingFilename + \
					datetime.datetime.now(). \
					strftime(PreferencesDialog.DefaultTimestampFormat) + ".csv"
			else:
				# Should we ask for the filename if LoggingTimestamp = False?
				# How does this work in the real world?
				self.LoggingFilename = self.LoggingFilename + ".csv" 
			# If file exists - overwrite it
			self.OutputFile = open(self.LoggingFilename,"w") 
			self.OutputFile.write("Timestamp,")
			
			Names = [x for i, x in enumerate(BasicControls.ADCNames) if BasicControls.ADCInputList[i] < 255]
			self.OutputFile.write("".join([('%s,' % val) for val in Names]) + "\n") 
			self.AcquireDataThread.SetFile(self.OutputFile)
		except:
			MessageBox.showerror("Logging Error",
							 "Unexpected error creating a new logfile.\n\n"\
							 "Make sure the Default filename and Timestamp formats " \
							 "are valid. See File | Preferences.")
			self.OutputFile = None
			self.AcquireDataThread.SetFile(None)
			self.Logging = False
			return False
		return True

	def StartStopLogClicked(self):
		'''
		If we're Running, Close the file and set SetLogging = False
		If we're Stopped, Open new file, write header, and set SetLogging = True
		'''
		InPause = self.AcquireDataThread.IsPaused()
		if not InPause:
		   self.AcquireDataThread.TogglePause()
		   
		self.Logging = not self.Logging
		self.LoggingPaused = False
		if self.Logging:    # Starting a new Log File
			if self.BuildLogfileName():
				self.StartStopLog['text'] = ' END LOGGING ' 
				self.StartStopLog['image'] = self.StopNewLogfileImage
				self.AcquireDataThread.RestartCapture() # This is ok?
				self.ClearPlotClicked()
				self.PauseLogFile['state'] = '!disabled'
		else:               # Shutdown Current logfile
			self.StartStopLog['text'] = 'START NEW LOG'
			self.StartStopLog['image'] = self.CreateNewLogfileImage
			self.PauseLogFile['state'] = 'disabled' 
			if not self.OutputFile == None: 
				self.OutputFile.close()
			self.OutputFile = None
			
		# True = Disable
		self.BasicControlsFrame.DisableMuxChanges(self.Logging)
		
		self.PauseLogFile['text'] = "PAUSE LOG"  
		self.PauseLogFile['image'] = self.PauseLogImage 
		self.AcquireDataThread.SetLogging(self.Logging)
			
		if not InPause:
		   self.AcquireDataThread.TogglePause() 

	def PauseLogFileClicked(self):
		'''
		Just toggle the state of the SetLogging flag to the thread
		This button is only enabled if self.Logging = True
		'''
		self.LoggingPaused = not self.LoggingPaused
		if self.LoggingPaused:
			self.PauseLogFile['text'] = "RESUME LOG"
			self.PauseLogFile['image'] = self.CreateNewLogfileImage
		else:
			self.PauseLogFile['text'] = "PAUSE LOG"
			self.PauseLogFile['image'] = self.PauseLogImage
		self.AcquireDataThread.SetLogging(not self.LoggingPaused)
		   
	def RunPausePlotClicked(self):
		self.RunPlot = not self.RunPlot
		if self.RunPlot:
			self.RunPausePlot['text'] = "PAUSE PLOT" 
			self.RunPausePlot['image'] = self.PauseLogImage
		else:
			self.RunPausePlot['text'] = "RUN PLOT"
			self.RunPausePlot['image'] = self.RunImage

	def ClearPlotClicked(self):
		# Still picks up at the last Timestamp from the thread
		for line in self.PlotLines:
			line.set_xdata([])
			line.set_ydata([])
		# Now clear queue
		InPause = self.AcquireDataThread.IsPaused()
		if not InPause:
			self.AcquireDataThread.TogglePause()
			try:    
				while True:
					self.queue.get(false)   # force exception if empty
			except: pass                    # OK - empty queue
		self.canvas.draw()      # Finally blit the new plot
		if not InPause:
		   self.AcquireDataThread.TogglePause()

	def AutoFlushFile(self):
		self.QueueSize.set("Queue: %d" % self.queue.qsize()) # Statusbar
		try:
			data = ""
			if self.Logging:
				#self.AcquireDataThread.TogglePause()
				self.OutputFile.flush()
				self.FlushFile.set("Saving Log")        # Statusbar
				self.after(1000,lambda e="": self.FlushFile.set(e))
				#self.AcquireDataThread.TogglePause()
				size = float(os.path.getsize(self.LoggingFilename))
				if size > 1073741824.0:
					data = str.format("Log filesize: %0.1f GiB" % (size / 1073741824.0) )
				elif size > 1048576.0:
					data = str.format("Log filesize: %0.1f MiB" % (size / 1048576.0) )
				elif size > 1024.0:
					data = str.format("Log filesize: %0.1f KiB" % (size / 1024.0) )
				else:
					data = str.format("Log filesize: %d Bytes" % int(size) )
			else:
				data = "Not logging" 
			self.Filesize.set(data)        # Statusbar
		except: pass
		self.after(10000,self.AutoFlushFile)

	def UpdateGraph(self):
		'''
			OK, how can we dynamically update he plot? We dont want to
			read the file since its being updated in the background.
			
			Use a queue - The thread puts data into the queue and we check it
			here. A lot of the code is manipulating the eight possible arrays
			of X/Y data, inserting data into the arrays in a LIFO manner. 
			Also, the size of the arrays are dynamically adjusted to keep memory
			allocation under some control.
		'''
		if self.AcquireDataThread.IsPaused() == False:
			changed = False
			if self.BasicControlsFrame.HaveMuxInputsChanged():
				# Legend may not exist at first
				try:    self.axes.get_legend().remove()
				except: pass    # Ok here
				for line in self.axes.lines:
					line.remove()
				# Now load the lines we are going to use at this time
				self.CurrentPlots = [self.PlotLines[idx] for idx in BasicControls.CurrentPlots]
				changed = True
				
			NumPlots = len(self.CurrentPlots)
			
			# Using XInputs and YInputs just to keep typing under control
			Yinputs = [plot.get_ydata() for plot in self.CurrentPlots ]
			Xinputs = [plot.get_xdata() for plot in self.CurrentPlots ]

			while self.queue.qsize() > 0:
				data = self.queue.get()
				# Loop through active lines and update using np.insert
				if len(data[1]) == NumPlots:
					for i, yval in enumerate(data[1]):
						Yinputs[i] = np.insert(Yinputs[i],0,yval)
						Xinputs[i] = np.insert(Xinputs[i],0,data[0])
			
			# Check size of arrays, if greater than some value, purge
			# Loop through each active line and determine if MaxSize exceeded
			MaxBufferSize = int(Display.SavePlotLength * BasicControls.SampleRate)
			overflow = 100  # Add code to adjust the overflow number
			for i in range(0,NumPlots):
				if len(Xinputs[i]) > MaxBufferSize + overflow:
					Xinputs[i] = np.resize(Xinputs[i],MaxBufferSize)
					Yinputs[i] = np.resize(Yinputs[i],MaxBufferSize)
			
			try:    # Hack instead of checking for arrays not there....
				self.axes.set_xlim(Xinputs[0][0], Xinputs[0][0]-int(Display.XAxisTimePeriod) )
			except:
				self.axes.set_xlim(0.0,-int(Display.XAxisTimePeriod) )
				
			# If the ADC gain has changed, update the y axes
			if self.BasicControlsFrame.HasGainChanged():                        
				self.DefaultXMinVal = -2.0 * Calibration.Vref / BasicControls.Gain
				self.DefaultXMaxVal =  2.0 * Calibration.Vref / BasicControls.Gain
				self.axes.set_ylim(self.DefaultXMinVal,self.DefaultXMaxVal)
			
			# Loop through all active lines and set_xdata and set_ydata
			for i, plot in enumerate(self.CurrentPlots):
				plot.set_ydata(Yinputs[i])
				plot.set_xdata(Xinputs[i])
				
			if changed:
				for line in self.CurrentPlots:
					self.axes.add_line(line)
				self.axes.legend(self.CurrentPlots,BasicControls.ADCInputNames,loc='upper right',
					bbox_to_anchor=(1.0, 1.0), shadow=False, ncol=1)
			# Test of visibility -- works!!!
			#self.PlotLines[1].set_visible(not self.PlotLines[1].get_visible())

			if self.RunPlot:
				self.canvas.draw()      # Finally blit the new plot
				
		self.after(int(1000 / Display.DisplayUpdateRate),self.UpdateGraph)

	def DefineAccelerators ( self, keys, char, callFunc ):
		commandDic = {'c':'Control-','a':'Alt-','s':'Shift-','f':''}
		cmd = '<'
		for c in keys.lower():	# need to handle function keys too...
			cmd = cmd + commandDic[c]
		cmd1 = cmd
		cmd = cmd + char.upper() + ">"
		self.root.bind(cmd,callFunc)
		if len(char) == 1:
			cmd1 = cmd1 + char.lower() + ">"
			self.root.bind(cmd1,callFunc)
			
	def SystemPreferences ( self, event ):
		PreferencesDialog(self,title='%s Preferences' % self.title,
			minwidth=400,minheight=550,okonly=True)
		self.ControlMapping.SetControlMapping()
		
	def quitProgram (self, event):
		if MessageBox.askyesno("Quit %s" % self.title,"Exit %s?" % self.title):
			if self.AcquireDataThread.IsPaused():
				self.AcquireDataThread.Pause(False)
			self.AcquireDataThread.Shutdown()
			self.AcquireDataThread.join()
			try:
				self.OutputFile.close()
			except: pass
			self.root.destroy()
			
	def ViewPlotPane(self, event):
		if self.viewPlotPane.get():
			self.PlotFrame.grid()
		else:
			self.PlotFrame.grid_remove()

	def ViewNotebookPane(self,event):
		if self.viewNotebookPane.get():
			self.NotebookFrame.grid()
		else:
			self.NotebookFrame.grid_remove()

	def ViewStatusBar ( self, event ):
		if self.ViewStatusBarBoolean.get():
			self.StatusBarFrame.grid()
		else:
			self.StatusBarFrame.grid_remove()
	 
	def Calibration(self,event):
		MessageBox.showinfo("Not Implemented",
							"Calibration not implemented yet")
		
	def KeyboardShortcuts(self,event):
		pass
		
	def HelpAbout(self,event):
		About.RPIBoardNumber = self.AcquireDataThread.GetRPIBoardNumber()
		AboutDialog(self,title="About "+self.title,minwidth=400,minheight=550,okonly=True)

def Run ():
	appTitle = "microLogger"
	INIfile = "%s.INI" % appTitle
	LoadPreferences(INIfile)	# First thing to do!

	try:
		win = Tk()
	except:
		print ( "Error initializing Tkinter!\n\nShutting down\n\nPress any key" )
		raw_input()
		return

	Style().theme_use(PreferencesDialog.DefaultTheme)

	win.minsize(800,600)
	app = microLogger(win,title=appTitle)
	win.mainloop()

	SavePreferences(INIfile,False)		# Last thing to do!

if __name__ == '__main__':
	print ( 'running....' )
	Run()

