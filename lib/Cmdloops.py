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
import re
import os
import sys
from email.utils import parseaddr

class DS_base(cmd.Cmd,object):
	"""DNS-Shell base command loop Class"""

	__version__ = '0.0.1'

	def __init__(self):
		super(DS_base,self).__init__()
		cmd.Cmd.__init__(self)
		self.doc_header="Available commands (type ?<topic>):"
		self.prompt="> "
		self.intro=""
		self.intro+="\nuse ? for help."

	def get_version(self):
		return __version__

	def do_help(self, args):
		"""Get help on commands
		"""
		## The only reason to define this method is for the help text in the doc string
		cmd.Cmd.do_help(self, args)

	def print_topics(self, header, cmds, cmdlen, maxcol):
		if cmds:
			self.stdout.write("%s\n"%str(header))
			if self.ruler:
				self.stdout.write("%s\n"%str(self.ruler * len(header)))

				for nrows in range(0, len(cmds)):
					try:
						doc=str(getattr(self, 'do_' + cmds[nrows]).__doc__).strip().partition('\n')[0]
						if not doc:
							doc=""
					except AttributeError:
						pass

					print "  %-15s - %s " % (cmds[nrows],doc)

				self.stdout.write("\n")

	def do_history(self, args):
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

	def completenames(self, text, *ignored):
		dotext = 'do_'+text
		return [(a[3:]+" ") for a in self.get_names() if a.startswith(dotext)]


class DNSShell(DS_base):
	"""DNS-Shell main command loop"""

	def __init__(self):
		super(DNSShell,self).__init__()
		self.intro="Welcome to dnsshell %s" % DS_base.__version__
		self.intro+="\nEnter ? for help."

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
		#TODO: get them from conf and show 'em

	def postloop(self):
		print "Goodbye."



class DS_enable(DS_base):
	"""DNS-Shell main command loop"""

	def __init__(self):
		super(DS_enable,self).__init__()
		self.intro="You are now in enable mode"
		self.prompt="enable> "

	def do_return(self, line):
		"exits the shell without saving."
		return True

	def do_baseconfig(self,args):
		"set your name and contact info"
		c = DS_config()
		c.cmdloop()

class DS_config(DS_base):

	def __init__(self):
		super(DS_config,self).__init__()
		self.intro="You may change your settings here. \nPlease use save to make changes permanent,\nuse show to list settings."
		self.prompt="config> "
		self.doc_leader+="\nBasic Settings Menu\n\nConfiguration of your contact data.\n"
		self.firstname=None
		self.phone=None
		self.lastname=None
		self.email=None
		c = Config()
		if c.is_configured():
			self.firstname=c.get('BaseConfig','firstname',required=False)
			self.phone=c.get('BaseConfig','phone',required=False)
			self.lastname=c.get('BaseConfig','lastname',required=False)
			self.email=c.get('BaseConfig','email',required=False)


	def setBaseConfig(self,initialconf):

		if not isinstance(initialconf, InitialConfig):
			raise TypeError("InitialConfig expected as argument, got "+str(initialconf.__class__))
		self.firstname = initialconf.firstname
		self.phone     = initialconf.phone
		self.lastname  = initialconf.lastname
		self.email     = initialconf.email

	def do_save(self,args):
		"saves the values to config"
		try:
			Config().add_section('BaseConfig')
		except ConfigParser.DuplicateSectionError:
			pass

		Config().set('BaseConfig', 'phone', self.phone)
		Config().set('BaseConfig', 'firstname', self.firstname)
		Config().set('BaseConfig', 'lastname', self.lastname)
		Config().set('BaseConfig', 'email', self.email)
		Config().write()

	def do_quit(self,args):
		"Exit immedeately without saving."
		Config().unlink()
		sys.exit(1)
		return True

	def do_show(self,args):
		"view settigs."

		print "Basic settings:"
		print "---------------\n"
		print " Firstname..: %s " % self.firstname
		print " Lastname...: %s " % self.lastname
		print " Email......: %s " % self.email
		print " Phone......: %s " % self.phone
		print "."

	def do_phone(self,args):
		"set emergency phone."
		self.phone=str(args).strip()
		print "setting phone to '%s'" % self.phone

	def do_firstname(self,args):
		"set firstname."
		self.firstname=str(args).strip()
		print "setting firstname to '%s'" % self.firstname

	def do_lastname(self,args):
		"set lastname."
		self.lastname=str(args).strip()
		print "setting lastname to '%s'" % self.lastname

	def do_email(self,args):
		"set email."
		line = str(args).strip()
		if not re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", line):
			print "invalid email address: "+line
			return
		self.email=line
		print "setting email to '%s'" % self.email


class InitialConfig():

	def __init__(self):
		self.phone = None
		self.firstname = None
		self.lastname = None
		self.email = None

	def wizard(self):
		print "Initial configuration dialog"
		print "----------------------------"

		self.firstname = self._askStr("First Name.: ")
		self.lastname  = self._askStr("Last Name..: ")
		self.email     = self._askStr("Email......: ",tpe="email")
		self.phone     = self._askStr("Phone......: ",tpe="phone")


	def _askStr(self,question,tpe="any"):
		answer=None
		while (not answer):
			answer=raw_input(question)
			if (not answer):
				print("Value required")
			elif (tpe=="email"):
				if not self._check_email(answer):
					print("Illegal Email address:" + answer)
					answer=None
		return answer


	def _check_email(self,email_str):
		return re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email_str)


class Config(object):

	_configparser = None
	_readonly = False
	_filename = None
	_is_empty = True
	_is_configured = False

	def __init__(self):
		if not Config._configparser:
			Config._configparser = ConfigParser.RawConfigParser()

	def getRawConfigParser(self):
		if not Config._configparser:
			raise ValueError("Configuration not loaded.") # probably not the right one
		return Config._configparser

	def add_section(self,section):
		Config._configparser.add_section(section)
		Config._is_configured = True

	def set(self,section,key,value):
		Config._configparser.set(section, key, value)
		Config._is_configured = True

	def get(self,section,key,required=False):
		retval=None
		if (required):
			retval=Config._configparser.get(section, key)
		else:
			try:
				retval=Config._configparser.get(section, key)
			except ConfigParser.NoOptionError:
				pass
		return retval


	def openRO(self,filename):
		if not os.path.isfile(filename):
			raise IOError(99,"File does not exist: "+filename)
		Config._readonly=True
		Config._configparser.read(filename)
		Config._filename=filename
		Config._is_configured = True
		Config._is_empty = False

	def openRW(self,filename):
		if not os.path.isfile(filename):
			raise IOError(99,"File does not exist: "+filename)
		Config._configparser.read(filename)
		Config._filename=filename
		Config._is_configured = True
		Config._is_empty = False

	def openCR(self,filename):
		if os.path.isfile(filename):
			raise IOError(99,"File already exists: "+filename)
		Config._filename=filename

	def unlink(self):
		if Config._readonly:
			return
		if Config._is_empty:
			if not os.path.getsize(Config._filename) < 1:
				raise IOError(99,"Refusing to delete non-empty configfile: "+Config._filename)
			os.unlink(Config._filename)
			Config._filename = None

	def write(self):

		if not Config._filename:
			raise ValueError("Configuration file not set.") # probably not the right one to raise

		if Config._readonly:
			print "Cannot write config, read only mode!"
			return

		configfile=open(Config._filename,"wb")
		Config._configparser.write(configfile)
		Config._is_empty = False
		Config._is_configured = True

	def is_configured(self):
		return Config._is_configured



