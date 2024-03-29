#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# bindconsole  - allows Zone-configuration of BIND by untrusted users
#
# Download: https://github.com/mutax/bindconsole
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

import signal
import argparse
import cmd
import sys
import ConfigParser

from lib import Cmdloops
from lib import Configuration

def handler(signum, frame):
	"""Just do nothing"""

def main():


	parser = argparse.ArgumentParser(description='Shell to edit BIND-Zones by untrusted users.')
	parser.add_argument('-v','--version', action='version', version='%(prog)s ' + "  version " +Cmdloops.DS_base.__version__,
						help="displays version and exits.")
	parser.add_argument('-r', '--readonly', action="store_true", default=False, \
                        help="readonly access to config.",dest='readonly')
	parser.add_argument('-c', '--createconf', action="store_true", default=False, \
                        help="create sample config in <file>.",dest='createconf')
	parser.add_argument('configfile', metavar='<file>', type=str,\
						help="configfile, will be created if -c given.")

	args = parser.parse_args()

	configfile=args.configfile

	# Install Ctrl+C Handler
	signal.signal(signal.SIGINT, handler)


	try:
		if args.readonly:
			Configuration.Config().openRO(configfile)
		elif (args.createconf): 
			Configuration.Config().openCR(configfile)
			#Create a new, template config
			print "Writing empty config in '%s'\n" %configfile
			u = Configuration.InitialConfig()
			u.wizard()
			u.save()
		else:
			Configuration.Config().openRW(configfile)

	except IOError as (errno, strerror):
		print "I/O error(%i) opening '%s': %s" %(errno, configfile, strerror)
		sys.exit(1)

	d = Cmdloops.DNSShell()
	d.cmdloop()


if __name__ == '__main__':
	main()
