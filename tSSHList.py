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


	def nextHost(self):
		if self.curPointer > self.totalEntries -1:
			self.curPointer = -1
			self.winWrapper.chgat(self.totalEntries + self.searchSectionHeight,0,-1,cs.color_pair(1))
		if self.curPointer > -1:
			self.winWrapper.chgat(self.curPointer + self.searchSectionHeight,0,-1,cs.color_pair(1))
		self.curPointer = self.curPointer + 1
		self.winWrapper.chgat(self.curPointer + self.searchSectionHeight,0,-1,cs.color_pair(2))
		self.winWrapper.refresh()

	def prevHost(self):
		if self.curPointer > -1:
			self.winWrapper.chgat(self.curPointer + self.searchSectionHeight,0,-1,cs.color_pair(1))
		if self.curPointer < 1:
			self.curPointer = self.totalEntries + 1
		self.curPointer = self.curPointer - 1
		self.winWrapper.chgat(self.curPointer + self.searchSectionHeight,0,-1,cs.color_pair(2))
		self.winWrapper.refresh()

	def updateHostList(self, hosts):
		limitedHosts = hosts[0:self.hostListLimit-1]
		self.totalEntries = len(limitedHosts) - 1
		self.winList.clear()
		for host in limitedHosts:
			self.winList.addstr(host + "\n")
		self.winList.refresh()

	def search(self):
		searchString = ""
		# Space
		if self.curPointer >= 0:
			self.winList.chgat(self.curPointer, 0, -1, cs.A_NORMAL)
		self.winList.refresh()
		cs.echo()
		self.winSearch.move(0,0)
		self.winSearch.attron(cs.A_STANDOUT)
		self.winSearch.chgat(0, 0, -1, cs.A_STANDOUT)
		self.winSearch.refresh()
		while True:
			key = self.winSearch.getch()
			if key == key_enter or key == key_tab:
				self.winSearch.attroff(cs.A_STANDOUT)
				self.winSearch.clear()
				self.winSearch.refresh()
				cs.noecho()

				# if search list is empty,list all hosts
				if len(self.searchHosts) <= 0:
					self.searchHosts = self.dataObj.getAllHostList()
					self.updateHostList()
				break
			elif key == key_backspace:
				#winList.addstr("entered")
				#winList.refresh()
				cury, curx = self.winSearch.getyx()
				if curx > 2:
					self.winSearch.addstr(cury, curx - 3, "   ")
					self.winSearch.move(cury, curx - 3)
					searchString = searchString[0:-1]
				else:
					self.winSearch.clear()
					self.winSearch.move(0,0)
					self.winSearch.attron(cs.A_STANDOUT)
					self.winSearch.chgat(0, 0, -1, cs.A_STANDOUT)
					self.winSearch.refresh()
			else:
				self.winList.addstr(str(key))
				self.winList.refresh()
				searchString = searchString + chr(key)
			if len(searchString) > 1:
				self.searchHosts = self.dataObj.searchHosts(searchString)
				self.updateHostList()
			else:
				self.searchHosts = self.dataObj.getAllHostList()
				self.updateHostList()


	def navigateDown(self):
		self.highlighHost(self.curPointer+1)

	def navigateUp(self):
		self.highlighHost(self.curPointer-1)

	def navigate(self):
		self.search()
		self.winList.move(0,0)
		self.winList.chgat(0,0,-1,cs.A_STANDOUT)
		while True:
			key=self.winList.getch()
			if key == ord("s") or key == key_tab:
			    self.search()
			    self.winList.move(0,0)
			    self.winList.chgat(0,0,-1,cs.A_STANDOUT)
			if key == ord("j"):
				self.navigateDown()
			if key == ord("k"):
				self.navigateUp()
			if key == key_enter or key == ord("a"):
				self.exitHost = searchHosts[winList.getyx()[0]]
				break
			if key == ord("t"):
				self.accessType = 1
				self.exitHost = searchHosts[winList.getyx()[0]]
				break
			if key == ord("q"):
				break


hosts = hostData()

stdscr = cs.initscr()
cs.noecho()
#cs.nocbreak()
cs.curs_set(0)

#self.stdscr = stdscr
cs.start_color()
cs.init_pair(1, cs.COLOR_BLACK, cs.COLOR_WHITE)
cs.init_pair(2, cs.COLOR_WHITE, cs.COLOR_BLUE)

ui = ui(stdscr, hosts.getAllHostList())
while True:
	key = ui.winList.getch()
	if key == ord('q'):
		break
	elif key == ord('j'):
		ui.nextHost()
	elif key == ord('k'):
		ui.prevHost()

#ui.searchHosts = hosts.getAllHostList()[0:]
#ui.updateHostList()
#ui.highlighHost(0)
#ui.navigate()

cs.endwin()
sys.exit(0)
if exitHost != "":
	if ui.accessType == 0:
		os.execvp("ssh", ["ssh", ui.exitHost])
	if accessType == 1:
		os.execvp("telnet", ["telnet", ui.exitHost])
