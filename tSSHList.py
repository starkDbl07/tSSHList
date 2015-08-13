#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses as cs
import locale
import os
import sys

locale.setlocale(locale.LC_ALL,"en_US.UTF-8")


# KEYS
key_tab = 9
key_enter = 10
key_backspace = 127


class hostData:
	hosts = []

	def __init__(self, limit=30):
		self.hosts = self.parseSSHConfig()
		self.limit = limit

	def parseSSHConfig(self):
		"""parse .ssh/config file to get hostlist """
		sshConfigFile = open("/Users/abhishek/.ssh/config", "r")
		sshConfig = sshConfigFile.read()
		sshConfigFile.close()
		return map(lambda host: host.replace("Host ",""), filter(lambda line: line.startswith("Host"), sshConfig.split("\n")))

	def getAllHostList(self):
		return self.hosts[0:self.limit]

	def searchHosts(self, searchString):
		if searchString != "":
			hostList = filter(lambda host: host.find(searchString) > -1, self.hosts)
		else:
			hostList = self.hosts
		return hostList[0:self.limit]

class ui:
	searchSectionHeight = 3
	searchIconWidth = 3
	totalEntries = 0
	hostListLimit = 0
	curPointer = -1
	searchIcon = u"\U0001F50D".encode('utf-8').strip()

	def __init__(self, winScreen, hostList=[], cWidth = 70, cHeight = 20):
		# Set content and screen height and widths
		self.cWidth = cWidth
		self.cHeight = cHeight
		self.sHeight, self.sWidth = winScreen.getmaxyx()

		# Initialize other object properties
		self.winScreen = winScreen

		# Call initialization functions
		self.placeWindows()
		self.updateHostList(hostList)
		self.nextHost()
		self.unhighlightSearch()

	def placeWindows(self):
		# Get object content/screen height and widths
		cWidth = self.cWidth
		cHeight = self.cHeight
		sWidth = self.sWidth
		sHeight = self.sHeight

		# Set center positions
		posCenterH = (sHeight / 2) - (cHeight / 2)
		posCenterW = (sWidth / 2) - (cWidth / 2)

		# Create winWrapper window
		winWrapper = cs.newwin(cHeight,cWidth+2,posCenterH,posCenterW-1)
		winWrapper.bkgd(" ", cs.color_pair(1))

		# Create winContent window
		winContent = winWrapper.derwin(cHeight, cWidth, 0, 1)
		winContent.bkgd(" ", cs.color_pair(1))

		# Create SearchSection Wrapper Window
		searchSection = winContent.derwin(self.searchSectionHeight,cWidth,0,0)
		searchSection.bkgd(" ", cs.color_pair(1))
		searchSection.addstr(2,0,"-" * (cWidth-1), cs.color_pair(3))


		# Create SearchIcon Window
		searchIconSection = searchSection.derwin(self.searchSectionHeight, self.searchIconWidth, 0,0)
		searchIconSection.addstr(1,0,self.searchIcon)

		# Create SearchText Wrapper Window
		searchTextSection = searchSection.derwin(self.searchSectionHeight, cWidth - self.searchIconWidth, 0, self.searchIconWidth)

		# Create SearchText Window
		winSearchText = searchTextSection.derwin(1, cWidth - self.searchIconWidth, 1, 0)
		#winSearchText.bkgd(" ");

		# Create HostList Window and its Properties
		self.hostListLimit = cHeight - self.searchSectionHeight
		winList = winContent.derwin(self.hostListLimit, cWidth-2, self.searchSectionHeight, 1)
		winList.bkgd(" ", cs.color_pair(1))

		# Refresh all windows
		winWrapper.refresh()
		winContent.refresh()
		searchSection.refresh()
		searchIconSection.refresh()
		searchTextSection.refresh()
		winSearchText.refresh()
		winList.refresh()

		# Set windows as object properties
		self.winWrapper = winWrapper
		self.winContent = winContent
		self.winSearchText = winSearchText
		self.winList = winList

	def highlightHost(self, pos):
		self.winWrapper.chgat(pos + self.searchSectionHeight,0,-1,cs.color_pair(2))
		self.winWrapper.refresh()

	def unhighlightHost(self, pos):
		self.winWrapper.chgat(pos + self.searchSectionHeight,0,-1,cs.color_pair(1))
		self.winWrapper.refresh()


	def nextHost(self):
		if self.curPointer > self.totalEntries -1:
			self.curPointer = -1
			self.unhighlightHost(self.totalEntries)
		if self.curPointer > -1:
			self.unhighlightHost(self.curPointer)
		self.curPointer = self.curPointer + 1
		self.highlightHost(self.curPointer)
		self.winWrapper.refresh()

	def prevHost(self):
		if self.curPointer > -1:
			self.unhighlightHost(self.curPointer)
		if self.curPointer < 1:
			self.curPointer = self.totalEntries + 1
		self.curPointer = self.curPointer - 1
		self.highlightHost(self.curPointer)
		self.winWrapper.refresh()

	def updateHostList(self, hosts):
		limitedHosts = hosts[0:self.hostListLimit-1]
		self.totalEntries = len(limitedHosts) - 1
		self.winList.clear()
		for host in limitedHosts:
			self.winList.addstr(host + "\n")
		self.winList.refresh()

	def highlightSearch(self):
		self.winSearchText.clear()
		self.winSearchText.refresh()

	def unhighlightSearch(self):
		self.winSearchText.addstr("Press 's' to start search")
		self.winSearchText.refresh()

	def initSearch(self):
		searchString = ""
		# Space
		self.winSearchText.move(0,0)
		cs.echo()
		self.highlightSearch()
		self.curPointer = 0

	def endSearch(self):
		self.highlightHost(self.curPointer)
		self.winWrapper.refresh()
		cs.noecho()


hosts = hostData()

stdscr = cs.initscr()
cs.noecho()
#cs.nocbreak()
cs.curs_set(0)

#self.stdscr = stdscr
cs.start_color()
#cs.use_default_colors()
#cs.init_color(cs.COLOR_RED, 100, 100, 100)
cs.init_pair(1, cs.COLOR_BLACK, cs.COLOR_WHITE)
cs.init_pair(2, cs.COLOR_WHITE, cs.COLOR_BLUE)
cs.init_pair(3, cs.COLOR_BLUE, cs.COLOR_WHITE)


ui = ui(stdscr, hosts.getAllHostList())
while True:
	key = ui.winList.getch()
	if key == ord('q'):
		break
	elif key == ord('j'):
		ui.nextHost()
	elif key == ord('k'):
		ui.prevHost()
	elif key == ord('s'):
		searchString = ""
		ui.initSearch()
		while True:
			keySearch = ui.winSearchText.getch()
			if keySearch == key_enter or keySearch == key_tab:
				ui.endSearch()
				if len(searchString) < 1:
					ui.unhighlightSearch()
				break
			elif keySearch == key_backspace:
				#ui.winList.addstr("entered")
				#ui.winList.refresh()
				cury, curx = ui.winSearchText.getyx()
				if curx > 2:
					ui.winSearchText.addstr(cury, curx - 3, "   ")
					ui.winSearchText.move(cury, curx - 3)
					searchString = searchString[0:-1]
				else:
					ui.winSearchText.clear()
					ui.winSearchText.move(0,0)
					ui.winSearchText.refresh()
			else:
				#ui.winList.addstr(str(keySearch))
				ui.winList.refresh()
				searchString = searchString + chr(keySearch)
			if len(searchString) > 1:
				searchedHosts = hosts.searchHosts(searchString)
				ui.updateHostList(searchedHosts)
				if len(searchedHosts) > 0:
					ui.highlightHost(0)
				else:
					ui.unhighlightHost(ui.curPointer)
			else:
				ui.updateHostList(hosts.getAllHostList())
				ui.highlightHost(0)

cs.endwin()
sys.exit(0)
if exitHost != "":
	if ui.accessType == 0:
		os.execvp("ssh", ["ssh", ui.exitHost])
	if accessType == 1:
		os.execvp("telnet", ["telnet", ui.exitHost])
