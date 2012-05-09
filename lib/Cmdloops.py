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
import Configuration

class DS_base(cmd.Cmd,object):
	"""DNS-Shell base command loop Class"""

	__version__ = '0.0.1'

	_hist = []      ## No history yet

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
		for line in DS_base._hist:
			print " "+line

	def emptyline(self):
		"""Do nothing on empty input line"""
		pass

	def preloop(self):
		"""Initialize command history and call parent class func"""
		cmd.Cmd.preloop(self)   ## sets up command completion
		#DS_base._hist    = []      ## No history yet

	def precmd(self, line):
		command = line.strip()
		if line.strip():
			DS_base._hist += [ line.strip() ]
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
		"returns without saving."
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
		self.dnsmasterV4 = None
		self.dnsmasterV6 = None

		c = Configuration.Config()
		if c.is_configured():
			self.firstname=c.get('BaseConfig','firstname',required=False)
			self.phone=c.get('BaseConfig','phone',required=False)
			self.lastname=c.get('BaseConfig','lastname',required=False)
			self.email=c.get('BaseConfig','email',required=False)
			self.dnsmasterV4=c.get('BaseConfig','default DNS IPv4',required=False)
			self.dnsmasterV6=c.get('BaseConfig','default DNS IPv6',required=False)

	def do_return(self, line):
		"returns without saving."
		return True

	def do_save(self,args):
		"saves the values to config"
		Configuration.Config().add_or_create_section('BaseConfig')
		Configuration.Config().set('BaseConfig', 'phone', self.phone)
		Configuration.Config().set('BaseConfig', 'firstname', self.firstname)
		Configuration.Config().set('BaseConfig', 'lastname', self.lastname)
		Configuration.Config().set('BaseConfig', 'email', self.email)
		Configuration.Config().set('BaseConfig', 'default DNS IPv4', self.dnsmasterV4)
		Configuration.Config().set('BaseConfig', 'default DNS IPv6', self.dnsmasterV6)
		Configuration.Config().write()

	def do_quit(self,args):
		"Exit immediately without saving."
		# not needed here anymore. wizard already saves file.
		# Configuration.Config().unlink()
		sys.exit(1)
		return True

	def do_show(self,args):
		"view settigs."

		print "Basic settings:"
		print "---------------\n"
		print "Contact:"
		print " Firstname..: %s " % self.firstname
		print " Lastname...: %s " % self.lastname
		print " Email......: %s " % self.email
		print " Phone......: %s " % self.phone
		print "\n"
		print "Default DNS Settings:"
		print "---------------------"
		print " Default IPv4 DNS Master: %s " % self.dnsmasterV4
		print " Default IPv6 DNS Master: %s " % self.dnsmasterV6
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

	def do_ipv4master(self,args):
		"set default IPv4 DNS master."
		arg = str(args).strip()
		if not Configuration.Validator.is_valid_ipv4_address(arg):
			print "Invalid IPv4 address: %s" % arg
			return
		self.dnsmasterV4=arg
		print "setting default IPv4 DNS to '%s'" % self.dnsmasterV4

	def do_ipv6master(self,args):
		"set default IPv6 DNS master."
		arg = str(args).strip()
		if not Configuration.Validator.is_valid_ipv6_address(arg):
			print "Invalid IPv6 address: %s" % arg
			return
		self.dnsmasterV6=arg
		print "setting default IPv6 DNS to '%s'" % self.dnsmasterV6


	def do_email(self,args):
		"set email."
		arg = str(args).strip()
		if not Configuration.Validator.is_valid_email_address(arg):
			print "Invalid Email address: %s" % arg
			return
		self.email=arg
		print "setting email to '%s'" % self.email
