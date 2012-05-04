#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Florian Streibelt <florian@freitagsrunde.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import ConfigParser
import argparse
import cmd
from email.utils import parseaddr

class DS_base(cmd.Cmd):
	"""DNS-Shell base command loop Class"""

	__version__ = '0.0.1'

	def __init__(self):
		self.doc_header="Available commands (type ?<topic>):"
		self.prompt="> "
		self.intro=""
		self.intro+="\nuse ? for help."

	def get_version(self):
		return __version__

	def do_help(self, args):
		"""Get help on commands
		'help' or '?' with no arguments prints a list of commands for which help is available
		'help <command>' or '? <command>' gives help on <command>
		"""
		## The only reason to define this method is for the help text in the doc string
		cmd.Cmd.do_help(self, args)

	def do_hist(self, args):
		"""Print a list of commands that have been entered"""
		for line in self._hist:
			print " "+line

	def emptyline(self):
		"""Do nothing on empty input line"""
		pass

	def preloop(self):
		"""Initialize command history and call parent class func"""
		cmd.Cmd.preloop(self)   ## sets up command completion
		self._hist    = []      ## No history yet

	def precmd(self, line):
		command = line.strip()
		if line.strip():
			self._hist += [ line.strip() ]
		return line


class DNSShell(DS_base):
	"""DNS-Shell main command loop"""

	def __init__(self):
		intro="Welcome to dnsshell %s" % DS_base.__version__

	def do_exit(self, line):
		"exits the shell without saving."
		return True

	def do_enable(self, line):
		"enters enable mode."
		es=DS_enable()
		es.cmdloop()

	def do_ls(self, line):
		"prints all configured domains"
		print "Domains configured: "

	def postloop(self):
		print "Goodbye."



class DS_enable(DS_base):
	"""DNS-Shell main command loop"""

	def __init__(self):
		intro="You are now in enable mode"
		prompt="enable> "

	def do_return(self, line):
		"exits the shell without saving."
		return True



class DS_config(DS_base):

	def __init__(self):
		intro="You may change your settings here. \nPlease use save to make changes permanent."
		prompt="config> "
		firstname=None
		lastname=None
		email=None

	def setBaseConfig(self,initialconf):
		if not isinstance(initialconf, InitialConfig):
			raise TypeError("InitialConfig expected as argument, got "+str(initialconf.__class__))
		self.firstname = initialconf.firstname
		self.lastname  = initialconf.lastname
		self.email     = initialconf.email



class InitialConfig():

	def __init__(self):
		firstname = None
		lastname = None
		email = None

	def wizard(self):
		print "Initial configuration dialog"
		print "----------------------------"

		self.firstname = self._askStr("First Name.: ")
		self.lastname  = self._askStr("Last Name..: ")
		self.email     = self._askStr("Email......: ",tpe="email")


	def _askStr(self,question,tpe="any"):
		answer=None
		while (not answer):
			answer=raw_input(question)
			if (not answer):
				print("Value required")
			elif (tpe=="email"):
					addr = parseaddr(answer)[1]
					if (addr):
						answer=addr
					else:
						print("Illegal Email address:" + answer)
						answer=None






