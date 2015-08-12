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

	def __init__(self, mainScreen, cWidth = 70, cHeight = 20):
		self.mainScreen = mainScreen
		self.sHeight, self.sWidth = stdscr.getmaxyx()
		self.cWidth = cWidth
		self.cHeight = cHeight

		self.posCenterH = (self.sHeight / 2) - (self.cHeight / 2)
		self.posCenterW = (self.sWidth / 2) - (self.cWidth / 2)

		mainWin = cs.newwin(cHeight,cWidth+2,self.posCenterH,self.posCenterW-1)
		mainWin.bkgd(" ", cs.color_pair(1))

		contentWin = mainWin.derwin(cHeight, cWidth, 0, 1)
		contentWin.bkgd(" ", cs.color_pair(1))

		searchSection = contentWin.derwin(self.searchSectionHeight,cWidth,0,0)
		searchSection.bkgd(".", cs.color_pair(1))

		searchIconSection = searchSection.derwin(self.searchSectionHeight, self.searchIconWidth, 0,0)
		searchTextSection = searchSection.derwin(self.searchSectionHeight, cWidth - self.searchIconWidth, 0, self.searchIconWidth)
		winSearchText = searchTextSection.derwin(1, cWidth - self.searchIconWidth, 1, 0)
		winSearchText.bkgd(" ");

		winListSection = contentWin.derwin(cHeight - self.searchSectionHeight, cWidth, self.searchSectionHeight, 0)
		winListSection.bkgd("-", cs.color_pair(1))

		mainWin.refresh()
		contentWin.refresh()
		searchSection.refresh()
		searchIconSection.refresh()
		searchTextSection.refresh()
		winSearchText.refresh()
		winListSection.refresh()
		mainWin.getch()

		self.mainWin = mainWin
		self.searchSection = searchSection
		sys.exit(0)

		self.winSearchSection = cs.newwin(1,cWidth,2,0)
		self.winSearchSection.addstr(self.searchLine)
		self.winSearchSection.refresh()
		self.winSearch = cs.newwin(1,cWidth-2,2,2)

		self.winList = cs.newwin(cHeight,cWidth,4,0)

		self.winTitle.addstr("SSH Hosts")

		self.winSearch.refresh()
		self.winTitle.refresh()



	def highlighHost(self, pos):
		if self.curPointer > -1:
			self.winList.chgat(self.curPointer, 0, -1, cs.A_NORMAL)
		if pos < 0 and self.totalEntries > 0:
			pos = self.totalEntries
		if pos > -1:	
			if pos > self.totalEntries:
				pos = 0
			self.curPointer = pos
			self.winList.chgat(pos, 0, -1, cs.A_STANDOUT)

	def updateHostList(self):
		self.totalEntries = len(self.searchHosts) - 1
		print self.totalEntries
		self.winList.clear()
		for host in self.searchHosts:
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

ui = ui(stdscr)

#ui.searchHosts = hosts.getAllHostList()[0:]
#ui.updateHostList()
#ui.highlighHost(0)
#ui.navigate()

cs.endwin()

if exitHost != "":
	if ui.accessType == 0:
		os.execvp("ssh", ["ssh", ui.exitHost])
	if accessType == 1:
		os.execvp("telnet", ["telnet", ui.exitHost])
