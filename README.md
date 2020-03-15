# microLogger
Data logging for the Raspberry PI

## Motivation

This work is a result of a collaboration between myself and Michael Axelsson, Professor, University of Gothenburg, Department of Biological and Environmental Sciences (http://www.bioenv.gu.se/personal/Axelsson_Michael/). Professor Axelsson has been investigating using inexpensive hardware to perform low-rate (50 SPS or less) data logging.

## Design

This version of **microLogger** 

## Version History

Refer to **Preferences \| About \| About** for the version number of **microLogger**.

| Version    | Notes                               |
| :--------- | :----------------------------------------------------- |
| 0.1 | <ul><li>Initial release. Tested under Python 3.7.3. Note Python 3.7.3 is **required**</li><li> |
| | |

## Known Issues

| Issue      | Description / Workaround                               |
| :--------- | :----------------------------------------------------- |
| | |

## TODO List (future enhancements)

| TODO       | Description                               |
| :--------- | :----------------------------------------------------- |
| | ||

## API Reference

**microLogger** has been developed using Python ver 3.7.3 (minimum version 3.7.3 is required) on the Raspberry Pi 4. In addition, it uses the following additonal Python libraries. Refer to **Preferences \| About \| About** for the exact versions used.

| Library    | Usage                                               |
| :--------- | :-------------------------------------------------- |
| PIL / Pillow | The Pillow fork of the Python Image Library. One issue is with PIL ImageTk under Python 3.x. It was not installed on my RPI. If you have similar PIL Import Errors use:  **sudo apt-get install python3-pil.imagetk**. |
| netifaces | Library to help discover IP addresses. Install using **sudo pip3 install netifaces** |

## Installation

Download the zip file and extract to a directory of your choosing. To run, open a terminal, change to the directory containing the source files, and enter **sudo python3 microLogger.py**.

### Installation on a Fresh Image

On a fresh install of Raspbian

(1) Update software sources. Open the terminal and enter:

	sudo apt-get update

(2) Once the update is complete, update everything to the latest version by entering:

	sudo apt-get upgrade

(3) Then install ImageTk for python3 by entering:

	sudo apt-get install python3-pil.imagetk

(4) Finally, install netifaces by entering:

	sudo pip3 install netifaces

(5) If there is a black border of unused pixels around the screen display, you’ll need to disable overscan, otherwise the button overlays won’t line up with the actual buttons underneath the preview. Edit the /boot/config.txt file by opening up a terminal and entering the following command:

	sudo nano /boot/config.txt

(5.1) Find and uncomment the disable_overscan=1 line by deleting the ‘#’ character:

	disable_overscan=1

(5.2) Save then exit by entering Ctrl+X and then pressing Y to save the file.

(6) Reboot your RPI. The black border should be gone. After changing to the directory containing **microLogger**, it should start up using the command:

	sudo python3 microLogger.py

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
