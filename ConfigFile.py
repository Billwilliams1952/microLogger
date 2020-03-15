#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
ConfigFiles.py - a data logging application written in Python/tkinter
  
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
import 	subprocess
import 	sys
import 	configparser as ConfigParser

from	microLogger import *
from	BasicControls import *
from	Advanced import *
from	Acquisition import *
from	Display import *
from    Calibration import *
from    PreferencesDialog import *
from    Tooltip	import *
from	Utils import *
from    Mapping import *
from 	AboutDialog import *

def ReadConfigValue ( config, section, item, typeVal ):
	if typeVal is int:
		val = config[section].getint(item)
	elif typeVal is float:
		val = config[section].getfloat(item)
	elif typeVal is bool:
		val = config[section].getboolean(item)
	else:	# string
		val = config[section][item]
		'''
		TODO: 	Now check if the string is of the form 'file=path\filename'
				if so, then read the given file for the string text.
				Replace newlines with spaces and replace the '\n' string
				with a newline. Return the string.
		'''
	return val

def UpdateConfigValue ( config, section, item, val ):
	try:
		if type(val) is not str:
			val = str(val)
		config[section][item] = val
	except: pass

def LoadPreferences ( filename ):
	config = ConfigParser.SafeConfigParser()
	config.read(filename)

	if not config.sections():
		print (filename + " does not exist - creating file")
		SavePreferences(filename,True)	# Create default values
		return

	section = 'Preferences'
	
	PreferencesDialog.DefaultFilesDir = ReadConfigValue ( config, section, 'DefaultFilesDir', str )
	PreferencesDialog.DefaultScreenShotDir = ReadConfigValue ( config, section, 'DefaultScreenShotDir', str )
	PreferencesDialog.DefaultScreenshotName = ReadConfigValue ( config, section, 'DefaultScreenshotName', str )
	PreferencesDialog.DefaultFilename = ReadConfigValue ( config, section, 'DefaultFilename', str )
	# Need to convert to format for input
	s = ReadConfigValue ( config, section, 'DefaultTimestampFormat', str )
	PreferencesDialog.DefaultTimestampFormat = s.replace("&","%")
	PreferencesDialog.ScreenshotTimestamp = ReadConfigValue ( config, section, 'ScreenshotTimestamp', bool )
	PreferencesDialog.LoggingTimestamp = ReadConfigValue ( config, section, 'LoggingTimestamp', bool )
	PreferencesDialog.AutoCreateNewLogFile = ReadConfigValue ( config, section, 'AutoCreateNewLogFile', bool )
	
	PreferencesDialog.DefaultTheme = ReadConfigValue ( config, section, 'DefaultTheme', str )
	
	ToolTip.ShowToolTips = ReadConfigValue ( config, section, 'ShowToolTips', bool )
	ToolTip.ShowTipNumber = ReadConfigValue ( config, section, 'ShowTipNumber', bool )
	ToolTip.ShowTipDelay = ReadConfigValue ( config, section, 'ShowTipDelay', float )
	
	section = "Display"
	
	Display.DisplayUpdateRate = ReadConfigValue ( config, section, 'DisplayUpdateRate', float )
	Display.SavePlotLength = ReadConfigValue ( config, section, 'SavePlotLength', float )
	Display.PlotTitle = ReadConfigValue ( config, section, 'PlotTitle', str )
	Display.PlotTitleFontSize = ReadConfigValue ( config, section, 'PlotTitleFontSize', int )
	Display.XAxisText = ReadConfigValue ( config, section, 'XAxisText', str )
	Display.XAxisFontSize = ReadConfigValue ( config, section, 'XAxisFontSize', int )
	Display.YAxisText = ReadConfigValue ( config, section, 'YAxisText', str )
	Display.YAxisFontSize = ReadConfigValue ( config, section, 'YAxisFontSize', int )
	Display.PlotFactor = ReadConfigValue ( config, section, 'PlotFactor', float )
	Display.XAxisTimePeriod = ReadConfigValue ( config, section, 'XAxisTimePeriod', float )
	Display.ShowXAxisGrids = ReadConfigValue ( config, section, 'ShowXAxisGrids', bool )
	Display.ShowYAxisGrids = ReadConfigValue ( config, section, 'ShowYAxisGrids', bool )
	
	section = "BasicControls"
	
	# ADCInputList = 0x67,255,255,0x58,255,255,0x45,255
	s = ReadConfigValue ( config, section, 'ADCInputList', str )
	s = s.split(',')
	BasicControls.ADCInputList = [] # string is 1,35,etc....
	for val in s:
		BasicControls.ADCInputList.append(int(val))
	BasicControls.SampleRate = ReadConfigValue ( config, section, 'SampleRate', float )
	BasicControls.Gain = ReadConfigValue ( config, section, 'Gain', int )
	s = ReadConfigValue ( config, section, 'ADCNames', str )
	s = s.split(',')
	BasicControls.ADCNames = [] # string is Channel 1,Channel 2,Channel 3, etc...
	for val in s:
		BasicControls.ADCNames.append(val)

def SavePreferences ( filename, createNewFile ):
	config = ConfigParser.SafeConfigParser()
	config.read(filename)

	if createNewFile:
		config['Preferences'] = {}
		config['Display'] = {}
		config["BasicControls"] = {}

	section = 'Preferences'
	
	UpdateConfigValue ( config, section, 'DefaultFilesDir', PreferencesDialog.DefaultFilesDir )
	UpdateConfigValue ( config, section, 'DefaultScreenShotDir', PreferencesDialog.DefaultScreenShotDir )
	UpdateConfigValue ( config, section, 'DefaultScreenshotName', PreferencesDialog.DefaultScreenshotName )
	UpdateConfigValue ( config, section, 'DefaultFilename', PreferencesDialog.DefaultFilename )
	# Need to convert to format for output
	s = PreferencesDialog.DefaultTimestampFormat.replace("%","&")
	UpdateConfigValue ( config, section, 'DefaultTimestampFormat', s )
	UpdateConfigValue ( config, section, 'ScreenshotTimestamp', PreferencesDialog.ScreenshotTimestamp )
	UpdateConfigValue ( config, section, 'LoggingTimestamp', PreferencesDialog.LoggingTimestamp )
	UpdateConfigValue ( config, section, 'AutoCreateNewLogFile', PreferencesDialog.AutoCreateNewLogFile )
	
	UpdateConfigValue ( config, section, 'DefaultTheme', PreferencesDialog.DefaultTheme )
	UpdateConfigValue ( config, section, 'ShowToolTips', ToolTip.ShowToolTips )
	UpdateConfigValue ( config, section, 'ShowTipNumber', ToolTip.ShowTipNumber )
	UpdateConfigValue ( config, section, 'ShowTipDelay', ToolTip.ShowTipDelay )
	
	section = "Display"
	
	UpdateConfigValue ( config, section, 'DisplayUpdateRate', Display.DisplayUpdateRate )
	UpdateConfigValue ( config, section, 'SavePlotLength', Display.SavePlotLength )
	UpdateConfigValue ( config, section, 'PlotTitle', Display.PlotTitle  )
	UpdateConfigValue ( config, section, 'PlotTitleFontSize', Display.PlotTitleFontSize )
	UpdateConfigValue ( config, section, 'XAxisText', Display.XAxisText )
	UpdateConfigValue ( config, section, 'XAxisFontSize', Display.XAxisFontSize )
	UpdateConfigValue ( config, section, 'YAxisText', Display.YAxisText)
	UpdateConfigValue ( config, section, 'YAxisFontSize', Display.YAxisFontSize )
	UpdateConfigValue ( config, section, 'PlotFactor', Display.PlotFactor)
	UpdateConfigValue ( config, section, 'XAxisTimePeriod', Display.XAxisTimePeriod )
	UpdateConfigValue ( config, section, 'ShowXAxisGrids', Display.ShowXAxisGrids )
	UpdateConfigValue ( config, section, 'ShowYAxisGrids', Display.ShowYAxisGrids )
	
	section = "BasicControls"
	
	# ADCInputList = [0x67,255,255,0x58,255,255,0x45,255]
	s = ""
	for i, val in enumerate(BasicControls.ADCInputList):
		if i == len(BasicControls.ADCInputList) - 1:
			s = s + str(val)
		else:
			s = s + str(val) + ","
	UpdateConfigValue ( config, section, 'ADCInputList', s )
	UpdateConfigValue ( config, section, 'SampleRate', BasicControls.SampleRate )
	UpdateConfigValue ( config, section, 'Gain', BasicControls.Gain )
	# ADCNames = 'Channel 1','Channel 2','Channel 3','Channel 4',
				# 'Channel 5','Channel 6','Channel 7','Channel 8'
	s = ""
	for i, val in enumerate(BasicControls.ADCNames):
		if i == len(BasicControls.ADCNames) - 1:
			s = s + val
		else:
			s = s + val + ","
	UpdateConfigValue ( config, section, 'ADCNames', s )
			
	SaveConfigFile(filename, config )

def SaveConfigFile ( filename, config ):
	with open(filename, 'w+') as configfile:
		config.write(configfile)

	# now change its permissions so it can be edited by anyone
	# sudo chmod a+w microLogger.INI
	path = os.path.dirname(os.path.abspath(__file__)) + '/' + filename
	os.system('sudo chmod a+w %s' % (path))
