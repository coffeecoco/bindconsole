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


class InitialConfig():

	def __init__(self):
		self.phone = None
		self.firstname = None
		self.lastname = None
		self.email = None
		self.dnsmasterV4 = None
		self.dnsmasterV6 = None

	def wizard(self):
		print "Initial configuration dialog"
		print "----------------------------"
		print
		print "Contact Information:"
		self.firstname = self._askStr("First Name.: ")
		self.lastname  = self._askStr("Last Name..: ")
		self.email     = self._askStr("Email......: ",tpe="email")
		self.phone     = self._askStr("Phone......: ",tpe="phone")
		print
		print "Default DNS-Settings: "
		self.dnsmasterV4 = self._askStr("Master DNS IPv4: ",tpe="ipv4")
		self.dnsmasterV6 = self._askStr("Master DNS IPv6: ",tpe="ipv6")

	def save(self):
		print "saving settings..."

		Config().add_or_create_section('BaseConfig')
		Config().set('BaseConfig', 'firstname', self.firstname)
		Config().set('BaseConfig', 'lastname', self.lastname)
		Config().set('BaseConfig', 'phone', self.phone)
		Config().set('BaseConfig', 'email', self.email)
		Config().set('BaseConfig', 'default DNS IPv4', self.dnsmasterV4)
		Config().set('BaseConfig', 'default DNS IPv6', self.dnsmasterV6)
		Config().write()

		print "DONE."


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
			elif (tpe=="ipv6"):
				if not self._check_ipv6(answer):
					print("Illegal IPv6 address:" + answer)
					answer=None
			elif (tpe=="ipv4"):
				if not self._check_ipv4(answer):
					print("Illegal IPv4 address:" + answer)
					answer=None
		return answer


	def _check_email(self,email_str):
		return re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email_str)

	#FIXME
	def _check_ipv4(self,email_str):
		return True

	#FIXME
	def _check_ipv6(self,email_str):
		return True



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

	def add_or_create_section(self,section):

		try:
			self.add_section(section)
		except ConfigParser.DuplicateSectionError:
			pass


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



