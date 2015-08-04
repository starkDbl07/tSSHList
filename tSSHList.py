#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses as cs
import locale
import os

locale.setlocale(locale.LC_ALL,"en_US.UTF-8")

wWidth = 40
searchLine = "S:"
searchLine="⧃ "
curPointer = -1
totalEntries = 0
exitHost = ""
accessType = 0

# KEYS
key_tab = 9
key_enter = 10
key_backspace = 127

stdscr = cs.initscr()
cs.noecho()
#cs.nocbreak()
cs.curs_set(0)

winTitle = cs.newwin(1,wWidth,0,0)
#winTitle.bkgd("*")

winSearchSection = cs.newwin(1,wWidth,2,0)
winSearchSection.addstr(searchLine)
winSearchSection.refresh()
winSearch = cs.newwin(1,wWidth-2,2,2)
winSearch.bkgd("-")

winList = cs.newwin(40,wWidth,4,0)
#winList.bkgd("*")

winTitle.addstr("SSH Hosts")
#winList.addstr("test" + "\n")
#totalEntries = totalEntries + 1

winSearch.refresh()
winTitle.refresh()

def parseSSHConfig():
	"""parse .ssh/config file to get hostlist """
	sshConfigFile = open("/Users/abhishek/.ssh/config", "r")
	sshConfig = sshConfigFile.read()
	sshConfigFile.close()
	return map(lambda host: host.replace("Host ",""), filter(lambda line: line.startswith("Host"), sshConfig.split("\n")))

def highlighHost(pos):
	global curPointer, totalEntries
	if curPointer > -1:
		winList.chgat(curPointer, 0, -1, cs.A_NORMAL)
	if pos < 0 and totalEntries > 0:
		pos = totalEntries
	if pos > -1:	
		if pos > totalEntries:
			pos = 0
		curPointer = pos
		winList.chgat(pos, 0, -1, cs.A_STANDOUT)

def updateHostList():
	global searchHosts, hosts
	totalEntries = len(searchHosts) - 1
	winList.clear()
	for host in searchHosts:
		winList.addstr(host + "\n")
	winList.refresh()

def search():
	global searchHosts, totalEntries
	searchString = ""
	# Space
	if curPointer >= 0:
		winList.chgat(curPointer, 0, -1, cs.A_NORMAL)
	winList.refresh()
	cs.echo()
	winSearch.bkgd(" ")
	winSearch.move(0,0)
	winSearch.attron(cs.A_STANDOUT)
	winSearch.chgat(0, 0, -1, cs.A_STANDOUT)
	winSearch.refresh()
	while True:
		key = winSearch.getch()
		if key == key_enter or key == key_tab:
			winSearch.attroff(cs.A_STANDOUT)
			winSearch.clear()
			winSearch.refresh()
			cs.noecho()
			if len(searchHosts) <= 0:
				searchHosts = hosts[0:35]
				updateHostList()
			break
		elif key == key_backspace:
			#winList.addstr("entered")
			#winList.refresh()
			cury, curx = winSearch.getyx()
			if curx > 2:
				winSearch.addstr(cury, curx - 3, "   ")
				winSearch.move(cury, curx - 3)
				searchString = searchString[0:-1]
			else:
				winSearch.clear()
				winSearch.move(0,0)
				winSearch.attron(cs.A_STANDOUT)
				winSearch.chgat(0, 0, -1, cs.A_STANDOUT)
				winSearch.refresh()
		else:
			winList.addstr(str(key))
			winList.refresh()
			searchString = searchString + chr(key)
		if len(searchString) > 1:
			searchHosts = filter(lambda host: host.find(searchString) > -1, hosts)[0:35]
			totalEntries = len(searchHosts) - 1
			updateHostList()
		else:
			searchHosts = hosts[0:35]
			updateHostList()


def navigateDown():
	global curPointer
	highlighHost(curPointer+1)

def navigateUp():
	global curPointer
	highlighHost(curPointer-1)

def navigate():
	global totalEntries, hosts, lastPointer, exitHost, searchHosts, accessType
	while True:
		key=winList.getch()
		if key == ord("s") or key == key_tab:
		    search()
		    winList.move(0,0)
		    winList.chgat(0,0,-1,cs.A_STANDOUT)
		if key == ord("j"):
			navigateDown()
		if key == ord("k"):
			navigateUp()
		if key == key_enter or key == ord("a"):
			exitHost = searchHosts[winList.getyx()[0]]
			break
		if key == ord("t"):
			accessType = 1
			exitHost = searchHosts[winList.getyx()[0]]
			break
		if key == ord("q"):
			break


hosts = parseSSHConfig()
searchHosts = hosts[0:35]
totalEntries = len(searchHosts) - 1

updateHostList()
highlighHost(0)
navigate()

cs.endwin()

if exitHost != "":
	if accessType == 0:
		os.execvp("ssh", ["ssh", exitHost])
	if accessType == 1:
		os.execvp("telnet", ["telnet", exitHost])
