# Copyright 2006,2016 Sony Corporation
# Modified by Khoi Nguyen and Kyle Arango
# Date : 4-14-2017

#!/usr/bin/python
# vim: set ts=4 sw=4 noet :
#
# grabserial - program to read a serial port and send the data to stdout
# This program is provided under the Gnu General Public License (GPL)
# version 2 ONLY. This program is distributed WITHOUT ANY WARRANTY.
# See the LICENSE file, which should have accompanied this program,
# for the text of the license.
#
# 2016-05-10 by Tim Bird <tim.bird@am.sony.com>
# 2006-09-07 by Tim Bird
#
# To do:
#  * buffer output chars??
#
# CHANGELOG:
#  2016.09.29 - Version 1.9.4 - add thread for sending user input to target
#    by zqb-all on github
#  2016.09.06 - clean up tabs, and add vim modeline for 4-column tabs
#               grabserial should always run with python -tt grabserial
#  2016.08.31 - add microsecond precision when using system Time (-T) option
#  2016.08.30 - Version 1.9.3 - allow forcing the baudrate with -B
#  2016.07.01 - Version 1.9.2 - change how version is stored
#  2016.05.10 - Version 1.9.1 - allow skipping the tty check with -S
#  2016.05.10 - Version 1.9.0 - support use as a python module
#    Note that the main module routine will be grabserial.grab(args,[outputfd])
#      where args is a list of command-line-style args
#      as they would be passed using the standalone program.  e.g.
#      grabserial.grab(None, ["-d", "/dev/ttyUSB0", "-v"])
#      output from the serial port (with timing data) is sent to outputfd
#  2015.04.23 - Version 1.8.1 - remove instructions for applying LICENSE text
#    to new files, and add no-warranty language to grabserial.
#  2015.03.10 - Version 1.8.0 - add -o option for saving output to a file
#    add -T option for absolute times. Both contributed by ramaxlo
#  2015.03.10 - Version 1.7.1 - add line feed to instantpat result line
#  2014.09.28 - Version 1.7.0 - add option for force reset for USB serial
#    contributed by John Mehaffey <mehaf@gedanken.com>
#  2014.01.07 - Version 1.6.0 - add option for exiting based on a
#    mid-line pattern (quitpat). Simeon Miteff <simeon.miteff@gmail.com>
#  2013.12.19 - Version 1.5.2 - verify Windows ports w/ serial.tools.list_ports
#   (thanks to Yegor Yefromov for the idea and code)
#  2013.12.16 - Version 1.5.1 - Change my e-mail address
#  2011.12.19 - Version 1.5.0 - add options for mid-line time capture
#    (instantpat) and base time from launch of program instead of
#    first char seen (launchtime) - contributed by Kent Borg
#  2011-09-24 - better time output and time delta
#    Constantine Shulyupin <const@makelinux.com>
#  2008-06-02 - Version 1.1.0 add support for sending a command to
#    the serial port before grabbing output

VERSION=(1,9,4)

import os, sys
import getopt
import serial
import time
import datetime
import re
import thread
verbose = 0
cmdinput = ""

def vprint(message):
	if verbose:
		print(message)

def usage(rcode):
	cmd = "grabserial"

	print("""%s : Serial line reader
	Usage: %s [options] <config_file>
options:
    -h, --help             Print this message
    -d, --device=<devpath> Set the device to read (default '/dev/ttyS0')
    -b, --baudrate=<val>   Set the baudrate (default 115200)
    -B <val>               Force the baudrate to the indicated value
                             (grabserial won't check that the baudrate is legal)
    -w, --width=<val>      Set the data bit width (default 8)
    -p, --parity=<val>     Set the parity (default N)
    -s, --stopbits=<val>   Set the stopbits (default 1)
    -x, --xonxoff          Enable software flow control (default off)
    -r, --rtscts           Enable RTS/CTS flow control (default off)
    -f, --force-reset      Force pyserial to reset device parameters
    -e, --endtime=<secs>   End the program after the specified seconds have
                           elapsed.
    -c, --command=<cmd>    Send a command to the port before reading
    -t, --time             Print time for each line received.  The time is
                           when the first character of each line is
                           received by %s
    -T, --systime          Print system time for each line received. The time
                           is the absolute local time when the first character
                           of each line is received by %s
    -m, --match=<pat>      Specify a regular expression pattern to match to
                           set a base time.  Time values for lines after the
                           line matching the pattern will be relative to
                           this base time.
    -i, --instantpat=<pat> Specify a regular expression pattern to have its time
                           reported at end of run.  Works mid-line.
    -q, --quitpat=<pat>    Specify a regular expression pattern to end the
                           program.  Works mid-line.
    -l, --launchtime       Set base time from launch of program.
    -o, --output=<name>    Output data to the named file.
    -v, --verbose          Show verbose runtime messages
    -V, --version          Show version number and exit
    -S, --skip             Skip sanity checking of the serial device.
                           May be needed for some devices.

Ex: %s -e 30 -t -m "^Linux version.*"
This will grab serial input for 30 seconds, displaying the time for
each line, and re-setting the base time when the line starting with
"Linux version" is seen.
""" % (cmd, cmd, cmd, cmd, cmd))
	sys.exit(rcode)

def device_exists(device):
	try:
		from serial.tools import list_ports

		for port in list_ports.comports():
			if port[0] == device:
				return True

		return False
	except:
		return os.path.exists(device)

def read_input():
	global cmdinput
	while (1):
		cmdinput = raw_input()

# grab - main routine to grab a serial port and time the output of each line
# takes a list of arguments, as they would have been passed in sys.argv
# that is, a list of strings.
# also can take an optional file descriptor for where to send the data
# by default, data read from the serial port is sent to sys.stdout, but
# you can specify your own (already open) file descriptor, or None.  This
# would only make sense if you specified another outputfile with
#    "-o","myoutputfile"
def grab(arglist, outputfd=sys.stdout):
	global verbose
	global cmdinput

	# parse the command line options
	try:
		opts, args = getopt.getopt(arglist,
                        "hli:d:b:B:w:p:s:xrfc:tTm:e:o:vVq:S", [
				"help",
				"launchtime",
				"instantpat=",
				"device=",
				"baudrate=",
				"width=",
				"parity=",
				"stopbits=",
				"xonxoff",
				"rtscts",
				"force-reset",
				"command=",
				"time",
				"systime",
				"match=",
				"endtime=",
				"output=",
				"verbose",
				"version",
				"quitpat=",
				"skip"])
	except:
		# print help info and exit
		print("Error parsing command line options")
		usage(2)

	sd = serial.Serial()
	#sd.port="/dev/ttyS0"
	#sd.port="/dev/ttyUSB0"
	device="/dev/rfcomm0"
	sd.port=device
	sd.baudrate=115200
	#sd.baudrate=9600
	sd.bytesize=serial.EIGHTBITS
	sd.parity=serial.PARITY_NONE
	sd.stopbits=serial.STOPBITS_ONE
	sd.xonxoff=False
	sd.rtscts=False
	sd.dsrdtr=False
	# specify a read timeout of 1 second
	sd.timeout=1
	force = False
	show_time = 0
	show_systime = 0
	basepat = ""
	instantpat = ''
	quitpat = ''
	basetime = 0
	instanttime = None
	endtime = 0
	outputfile = None
	command = ""
	skip_device_check = 0

	for opt, arg in opts:
		if opt in ["-h", "--help"]:
			usage(0)
		if opt in ["-d", "--device"]:
			device = arg
			if not skip_device_check and not device_exists(device):
				print("Error: serial device '%s' does not exist, aborting." % device)
				print("  If you think this port really exists, then try using the -S option")
				print("  to skip the serial device check. (put it before the -d argument)")
				sd.close()
				usage(2)
			sd.port = device
		if opt in ["-b", "--baudrate"]:
			baud = int(arg)
			if baud not in sd.BAUDRATES:
				print("Error: invalid baud rate '%d' specified" % baud)
				print("Valid baud rates are: %s" % str(sd.BAUDRATES))
				print("You can force the baud rate using the -B option")
				sd.close()
				sys.exit(3)
			sd.baudrate = baud
		if opt == "-B":
			sd.baudrate = int(arg)
		if opt in ["-p", "--parity"]:
			par = arg.upper()
			if par not in sd.PARITIES:
				print("Error: invalid parity '%s' specified" % par)
				print("Valid parities are: %s" % str(sd.PARITIES))
				sd.close()
				sys.exit(3)
			sd.parity = par
		if opt in ["-w", "--width"]:
			width = int(arg)
			if width not in sd.BYTESIZES:
				print("Error: invalid data bit width '%d' specified" % width)
				print("Valid data bit widths are: %s" % str(sd.BYTESIZES))
				sd.close()
				sys.exit(3)
			sd.bytesize = width
		if opt in ["-s", "--stopbits"]:
			stop = int(arg)
			if stop not in sd.STOPBITS:
				print("Error: invalid stopbits '%d' specified" % stop)
				print("Valid stopbits are: %s" % str(sd.STOPBITS))
				sd.close()
				sys.exit(3)
			sd.stopbits = stop
		if opt in ["-c", "--command"]:
			command = arg
		if opt in ["-x", "--xonxoff"]:
			sd.xonxoff = True
		if opt in ["-r", "--rtscts"]:
			sd.rtscts = True
		if opt in ["-f", "--force-set"]:
			force = True
		if opt in ["-t", "--time"]:
			show_time=1
			show_systime=0
		if opt in ["-T", "--systime"]:
			show_time=0
			show_systime=1
		if opt in ["-m", "--match"]:
			basepat=arg
		if opt in ["-i", "--instantpat"]:
			instantpat=arg
		if opt in ["-q", "--quitpat"]:
			quitpat=arg
		if opt in ["-l", "--launchtime"]:
			print('setting basetime to time of program launch')
			basetime = time.time()
		if opt in ["-e", "--endtime"]:
			endstr=arg
			try:
				endtime = time.time()+float(endstr)
			except:
				print("Error: invalid endtime %s specified" % arg)
				sd.close()
				sys.exit(3)
		if opt in ["-o", "--output"]:
			outputfile = arg
		if opt in ["-v", "--verbose"]:
			verbose=1
		if opt in ["-V", "--version"]:
			print("grabserial version %d.%d.%d" % VERSION)
			sd.close()
			sys.exit(0)
		if opt in ["-S"]:
			skip_device_check=1

	# if verbose, show what our settings are
	vprint("Opening serial port %s" % sd.port)
	vprint("%d:%d%s%s:xonxoff=%d:rtscts=%d" % (sd.baudrate, sd.bytesize,
		 sd.parity, sd.stopbits, sd.xonxoff, sd.rtscts))
	if endtime:
		vprint("Program will end in %s seconds" % endstr)
	if show_time:
		vprint("Printing timing information for each line")
	if show_systime:
		vprint("Printing absolute timing information for each line")
	if basepat:
		vprint("Matching pattern '%s' to set base time" % basepat)
	if instantpat:
		vprint("Instant pattern '%s' to set base time" % instantpat)
	if quitpat:
		vprint("Instant pattern '%s' to exit program" % quitpat)
	if skip_device_check:
		vprint("Skipping check of serial device")
	if outputfile:
		try:
			out = open(outputfile, "wb")
		except IOError:
			print("Can't open output file '%s'" % outputfile)
			sys.exit(1)
		vprint("Saving data to '%s'" % outputfile)

	prev1 = 0
	linetime = 0
	newline = 1
	curline = ""
	vprint("Use Control-C to stop...")

	if force:
	# pyserial does not reconfigure the device if the settings
	# don't change from the previous ones.  This causes issues
	# with (at least) some USB serial converters
		toggle = sd.xonxoff
		sd.xonxoff = not toggle
		sd.open()
		sd.close()
		sd.xonxoff = toggle
	sd.open()
	sd.flushInput()
	sd.flushOutput()

	if command:
		sd.write(command + "\n")
		sd.flush()

	# capture stdin to send to serial port
	try:
		thread.start_new_thread(read_input, ())
	except:
		print("Error starting thread for read input\n")

	GS_Serial = open('GS_Serial.log', 'wb')
	# read from the serial port until something stops the program
	fp = []
	#fp.append(open('dummyFile', 'wb'))
	GS_Serial.write('Opening temp files\n')
	GS_Serial.flush()
	for i in range(0,7):
		#testfile.write('Opening: file' + str(i)+ '\n')
		f = open('temp' + str(i) + '.txt', 'w')
		fp.append(f)
	#fp1.flush()
	#nCounter = [0 for i in range(1,9)]
	while(1): 
		#print("In loop")
		line = sd.readline()
		#time.sleep(0.1)
		#if line and not line.isspace():
		#testfile.write('Reading First line:' + line + '\n')

		#print(line)
		if 'Done' in line:
			GS_Serial.write('Closing Files\n')
			GS_Serial.close()
			for i in range(0,7):
				fp[i].close()
			sd.close()
			break
		x=line.split(', ')
		#print len(x)
		if (len(x) == 4):
			fp[6].write(x[1] + ', ' + x[2] + ', ' + x[3] )
		else:
			for i in range(0,6):
				#print('File' +str(i))
				if 'File' + str(i) in x and len(x) == 3 :
				#print('Found File' + str(i))
					fp[i].write(x[1] + ', ' + x[2])
					break
	if instanttime:
		instanttime_str = '%4.6f' % (instanttime-basetime)
		msg = '\nThe instantpat: "%s" was matched at %s\n' % \
			(instantpat, instanttime_str)
		sys.stdout.write(msg)
		sys.stdout.flush()
		if outputfile:
			out.write(msg)
			out.flush()

	if outputfile:
		out.close()

	sys.stdout.flush()

if __name__=="__main__":
	grab(sys.argv[1:])