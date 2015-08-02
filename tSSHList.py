#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses as cs
import locale
import os

locale.setlocale(locale.LC_ALL,"en_US.UTF-8")

wWidth = 40
searchLine = "S:"
searchLine="⧃ "
searchLineLength = len(searchLine)
curPointer = -1
totalEntries = 0
exitHost = ""

stdscr = cs.initscr()
cs.noecho()
#cs.nocbreak()
cs.curs_set(0)

winTitle = cs.newwin(1,wWidth,0,0)
#winTitle.bkgd("*")

winSearch = cs.newwin(1,wWidth,2,0)
winSearch.bkgd("-")
winSearch.addstr(searchLine)

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
	global searchLine, searchLineLength, searchHosts, totalEntries
	searchString = ""
	# Space
	if curPointer >= 0:
		winList.chgat(curPointer, 0, -1, cs.A_NORMAL)
	winList.refresh()
	cs.echo()
	winSearch.bkgd(" ")
	winSearch.move(0,searchLineLength)
	winSearch.attron(cs.A_STANDOUT)
	winSearch.chgat(0, searchLineLength, -1, cs.A_STANDOUT)
	winSearch.refresh()
	while True:
		key = winSearch.getch()
		if key == ord("q"):
			winSearch.attroff(cs.A_STANDOUT)
			winSearch.clear()
			winSearch.addstr(searchLine)
			winSearch.refresh()
			cs.noecho()
			break
		else:
			searchString = searchString + chr(key)
			if len(searchString) > 2:
				searchHosts = filter(lambda host: host.find(searchString) > -1, hosts)
				totalEntries = len(searchHosts) - 1
				updateHostList()


def navigateDown():
	global curPointer
	highlighHost(curPointer+1)

def navigateUp():
	global curPointer
	highlighHost(curPointer-1)

def navigate():
	global totalEntries, hosts, lastPointer, exitHost, searchHosts
	while True:
		key=winList.getch()
		if key == ord("s"):
		    search()
		if key == ord("j"):
			navigateDown()
		if key == ord("k"):
			navigateUp()
		if key == ord("a"):
			exitHost = searchHosts[winList.getyx()[0]]
			break
		if key == ord("q"):
			break


hosts = parseSSHConfig()
searchHosts = hosts[0:]
totalEntries = len(searchHosts) - 1

updateHostList()
highlighHost(0)
navigate()

cs.endwin()

if exitHost != "":
	os.execvp("ssh", ["ssh", exitHost])
