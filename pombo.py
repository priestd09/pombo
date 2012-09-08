#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pombo
# Theft-recovery tracking opensource software
# http://sebsauvage.net/pombo
# http://bobotig.fr/contenu/projets/pombo

# This program is distributed under the OSI-certified zlib/libpnglicense .
# http://www.opensource.org/licenses/zlib-license.php
# 
# This software is provided 'as-is', without any express or implied warranty.
# In no event will the authors be held liable for any damages arising from
# the use of this software.
# 
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it freely,
# subject to the following restrictions:
# 
#	 1. The origin of this software must not be misrepresented; you must not
#		claim that you wrote the original software. If you use this software
#		in a product, an acknowledgment in the product documentation would be
#		appreciated but is not required.
# 
#	 2. Altered source versions must be plainly marked as such, and must not
#		be misrepresented as being the original software.
# 
#	 3. This notice may not be removed or altered from any source distribution.

PROGRAMNAME = 'Pombo'
PROGRAMVERSION = '0.0.10-a5'
VCVERSION = '0.9.5'

import base64,ConfigParser,datetime,hashlib,hmac,locale,os,platform,\
       random,re,subprocess,sys,tempfile,time,urllib,urllib2,zipfile


# ----------------------------------------------------------------------
# --- [ Variables ] ----------------------------------------------------
# ----------------------------------------------------------------------

# Current running OS specifities
OS      = 'GNULINUX'
SEP     = '/'
CONF    = '/etc/pombo.conf'
IPFILE  = '/var/local/pombo'
LOGFILE = '/var/log/pombo.log'
CLRF    = "\n"
if os.name == 'nt':
	os.chdir(sys.path[0])
	OS      = 'WINDOWS'
	SEP     = '\\'
	CONF    = 'pombo.conf'
	IPFILE  = 'pombo'
	LOGFILE = 'pombo.log'
	CLRF    = "\r\n"

# Console encoding
encoding = sys.stdin.encoding or locale.getdefaultlocale()[1]
if not encoding:
	encoding = 'utf-8'

# Output
LOG = True # Enable logging - should be at True only for dev.
DEBUG = False
if 'check' in sys.argv:
	DEBUG = True
if LOG:
	F = open(LOGFILE, 'a+b')

# Get the configuration options
if not os.access(CONF, os.R_OK):
	print ' ! Impossible to read the config file.'
	sys.exit(1)
CONFIG = {}

# Others
TMP = tempfile.gettempdir()
PUBLIC_IP = FILENAME = T = None


# ----------------------------------------------------------------------
# --- [ Functions ] ----------------------------------------------------
# ----------------------------------------------------------------------

def config():
	config = ConfigParser.SafeConfigParser()
	config.read(CONF)

	global CONFIG
	CONFIG = {
		# Pombo related
		'gpgkeyid'      :config.get('GENERAL','gpgkeyid').strip(),
		'password'      :config.get('GENERAL','password').strip(),
		'serverurl'     :config.get('GENERAL','serverurl').strip(),
		'onlyonipchange':config.get('GENERAL','onlyonipchange').strip(),
		'checkfile'     :config.get('GENERAL','checkfile').strip(),
		
		# Additional tools
		'network_config'    :config.get(OS,'network_config').strip(),
		'wifi_access_points':config.get(OS,'wifi_access_points').strip(),
		'traceroute'        :config.get(OS,'traceroute').strip(),
		'network_trafic'    :config.get(OS,'network_trafic').strip(),
		'screenshot'        :config.get(OS,'screenshot').strip(),
		'camshot'           :config.get(OS,'camshot').strip(),
		'camshot_filetype'  :''
	}
	
	if CONFIG['onlyonipchange'] != 'True' and CONFIG['onlyonipchange'] != 'False':
		print ' ! Config file error: wrong "onlyonipchange" parameter, should be True or False.'
		print '   Assuming False.'
		CONFIG['onlyonipchange'] = 'False'
	if CONFIG['serverurl'] == '':
		print ' ! Please specifiy at least one server for serverurl option.'
	if OS == 'GNULINUX':
		CONFIG['camshot_filetype'] = config.get(OS,'camshot_filetype').strip()

def current_network_connections():
	''' Returns the addresses and ports to which this computer is 
	    currently connected to. '''
	if CONFIG['network_trafic'] == 'False':
		return 'Disabled.'
	return runprocess(CONFIG['network_trafic'].split(' '))

def currentuser():
	''' Return the user who is currently logged in and uses the X 
	    session. None if could not be determined.
	'''
	user = None
	if OS == 'WINDOWS':
		user = runprocess(['echo', '%USERNAME%'], useshell = True)
	else:
		for line in runprocess(['who','-s']).split('\n'):
			if '(:0)' in line:
				user = line.split(' ')[0]
	return user

def file_size(file):
	''' Get file to send size '''
	num = os.path.getsize(file)
	for x in ['B','KB','MB','GB']:
		if num < 1024.0 and num > -1024.0:
			return '%3.1f%s' % (num, x)
		num /= 1024.0
	return '%3.1f%s' % (num, 'TB')

def ip_hash(ip):
	''' IP hash methods - could be easily modifed. '''
	return hashlib.sha256(ip.strip()).hexdigest()

def network_config():
	''' Returns the network configuration, both wired and wireless '''
	if CONFIG['network_config'] == 'False':
		return 'Disabled.'
	return runprocess(CONFIG['network_config'].split(' '))

def network_route():
	''' Returns a traceroute to a public server in order to detect ISPs
	    and nearby routeurs.
	'''
	if CONFIG['traceroute'] == 'False':
		return 'Disabled.'
	return runprocess(CONFIG['traceroute'].split(' '))

def _print(string):
	string = '%s %s' % (datetime.datetime.now(), string)
	if DEBUG:
		print string
	if LOG:
		F.write(string + CLRF)
		if string[-1] == CLRF:
			F.close()
	return

def public_ip():
	''' Returns your public IP address.
		Output: The IP address in string format.
				None if not internet connection is available.
	'''
	_print(' - Retrieving IP address ... ')
	ip_regex = re.compile('(([0-9]{1,3}\.){3}[0-9]{1,3})')
	for distant in CONFIG['serverurl'].split(','):
		domain = distant.split('/')[2]
		try:
			_print('     from %s' % domain)
			request = urllib2.Request(distant + '?' + urllib.urlencode({'myip':'1'}))
			response = urllib2.urlopen(request)
			ip = response.read(256)
			if ip_regex.match(ip):
				return ip
		except Exception as ex:
			pass
	return None

def runprocess(commandline,useshell=False):
	''' Runs a sub-process, wait for termination and returns
		the process output (both stdout and stderr, concatenated).

		Input: commandline : string or list of strings. First string is 
		                     command, items are command-line options.
			   useshell: If true, system shell will be used to run the 
			             program. Otherwise, the program will be run 
			             directly with popen(). (Some program need to 
			             have a full shell environment in order to run 
			             properly.)

		Ouput; The output of the commande (stdout and stderr concatenated)
			   Empty string in case of failure.

		Example:
			print runprocess(['ifconfig','-a'])
			print runprocess('DISPLAY=:0 su %s -c "scrot %s"' 
							 % (user,filepath),useshell=True)
	'''
	try:
		myprocess = subprocess.Popen(commandline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=useshell)
		(sout,serr) = myprocess.communicate()
		myprocess.wait()
		if not sout:
			sout = ''
		if not serr:
			serr = ''
		return unicode(sout, encoding).encode('utf-8') + "\n" + unicode(serr, encoding).encode('utf-8')
	except Exception as ex:  # Yeah, I know this is bad
		_print(' ! Process failed: %s (%s)' % (commandline, ex))
		return ''

def screenshot():
	''' Takes a screenshot and returns the path to the saved image 
	    (in /tmp). None if could not take the screenshot. 
	'''
	if CONFIG['screenshot'] == 'False':
		_print(' . Skipping screenshot.')
		return None

	_print(' - Taking screenshot.')
	filepath = '%s%c%s_screenshot.jpg' % (TMP, SEP, FILENAME)
	user = currentuser()
	if not user:
		_print(' ! Could not determine current user. Cannot take screenshot.')
		return None

	if OS == 'WINDOWS':
		from PIL import ImageGrab
		img = ImageGrab.grab() 
		img.save(filepath, 'JPEG')
	else:
		os.system(CONFIG['screenshot'] % filepath)
	if not os.path.isfile(filepath):
		return None
	return filepath

def snapshot(stolen):
	''' Make a global snapshot of the system (ip, screenshot, webcam...)
		and sends it to the internet.
		If not internet connexion is available, will exit.
	'''
	# Note: when making a snapshot, we will try each and every type
	# of snapshot (screenshot, webcam, etc.)
	# If a particular snapshot fails, it will simply skip it.

	# Initialisations
	global PUBLIC_IP, FILENAME, T, F
	F = open(LOGFILE, 'a+b')
	FILENAME = platform.node() + time.strftime('_%Y%m%d_%H%M%S')
	PUBLIC_IP = public_ip()
	filestozip = []

	# Make sure we are connected to the internet:
	# (If the computer has no connexion to the internet, it's no use 
	# accumulating snapshots.)
	if PUBLIC_IP is None:
		_print(' - Computer does not seem to be connected to the internet. Aborting.' + CLRF)
		return

	if not stolen and CONFIG['onlyonipchange'] == 'True':
		# Read previous IP
		if not os.path.isfile(IPFILE):
			_print(' + First run, writing down IP in pombo.')
			f = open(IPFILE, 'w+b')
			f.write(ip_hash(PUBLIC_IP))
			f.close()
		else:
			f = open(IPFILE, 'rb')
			previous_ips = f.readlines()
			f.close()
			if ip_hash(PUBLIC_IP) in [s.strip() for s in previous_ips]:
				_print(' - IP has not changed. Aborting.' + CLRF)
				return
			_print(' + IP has changed.')

	# Create the system report (IP, date/hour...)
	_print(' - Filename: %s' % FILENAME)
	_print(' - Collecting system info.')
	filepath = '%s%c%s.txt' % (TMP, SEP, FILENAME)
	f = open(filepath, 'ab')
	f.write(systemreport())
	f.close()
	filestozip.append(filepath)

	# Take a screenshot
	screen = screenshot()
	if screen:
		filestozip.append(screen)

	# Take a webcam snapshot
	webcam = webcamshot()
	if webcam:
		filestozip.append(webcam)

	# Zip files:
	_print(' - Zipping files.')
	os.chdir(TMP)
	zipfilepath = '%s%c%s.zip' % (TMP, SEP, FILENAME)
	f = zipfile.ZipFile(zipfilepath, 'w', zipfile.ZIP_DEFLATED)
	for filepath in filestozip:
		f.write(os.path.basename(filepath))
	f.close()

	# Remove temporary files.
	for filepath in filestozip:
		os.remove(filepath)

	# Encrypt using gpg with a specified public key
	_print(' - Encrypting zip with GnuPG.')
	os.system('gpg --batch --no-default-keyring --trust-model always -r %s -e "%s"' % (CONFIG['gpgkeyid'], zipfilepath))
	os.remove(zipfilepath)
	gpgfilepath = zipfilepath + '.gpg'
	if not os.path.isfile(gpgfilepath):
		_print(' ! GPG encryption failed. Aborting.' + CLRF)
		return

	# Read GPG file and compute authentication token
	f = open(gpgfilepath, 'r+b')
	filedata = base64.b64encode(f.read())
	f.close()
	filesize = file_size(gpgfilepath)
	os.remove(gpgfilepath)
	gpgfilename = os.path.basename(gpgfilepath)
	authtoken = hmac.new(CONFIG['password'], filedata + '***' + gpgfilename, hashlib.sha1).hexdigest()

	# Send to the webserver (HTTP POST).
	_print(' - Sending file (%s) ... ' % filesize)
	for distant in CONFIG['serverurl'].split(','):
		domain = distant.split('/')[2]
		_print('     to %s' % (domain))
		parameters = {'filename':gpgfilename, 'filedata':filedata, 'token':authtoken}
		request = urllib2.Request(distant, urllib.urlencode(parameters))
		try:
			response = urllib2.urlopen(request)
			page = response.read(2000)
			_print('       > %s' % page.strip())
		except Exception as ex:
			_print('       ! failed: %s' % ex)
			pass
	_print(' ^ Done.' + CLRF)
	return

def stolen():
	''' Returns True is the computer was stolen. '''
	# Initialisations
	global T
	T = time.time()
	salt = 'just check if I am a stolen one'
	authtoken = hmac.new(CONFIG['password'], salt + '***' + CONFIG['checkfile'], 
						 hashlib.sha1).hexdigest()
	_print('<> Checking status ... ')
	for distant in CONFIG['serverurl'].split(','):
		domain = distant.split('/')[2]
		_print('     on %s' % domain)
		parameters = {'filename':CONFIG['checkfile'], 'filedata':salt, 'verify':authtoken}
		request = urllib2.Request(distant, urllib.urlencode(parameters))
		try:
			response = urllib2.urlopen(request)
			page = response.read(2000)
			if page.strip() == '1':
				_print('       <<!>> Stolen computer <<!>>')
				return True
		except Exception as ex:
			_print('       ! failed: %s' % ex)
	return False

def systemreport():
	''' Returns a system report: computer name, date/time, public IP,
		list of wired and wireless interfaces and their configuration, etc.
	'''
	report = ['%s %s report' % (PROGRAMNAME, PROGRAMVERSION)]
	report.append('Computer : ' +  ' '.join(platform.uname()))
	report.append('Public IP: %s ( Approximate geolocation: http://www.geoiptool.com/?IP=%s )' % (PUBLIC_IP, PUBLIC_IP))
	report.append('Date/time: %s (local time)' % datetime.datetime.now())
	report.append("Network config:\n" + network_config())
	report.append("Nearby wireless access points:\n" + wifiaccesspoints())
	report.append("Network routes:\n" + network_route())
	report.append("Current network connections:\n" + current_network_connections())
	separator = "\n" + 75 * "-" + "\n"
	return separator.join(report)

def webcamshot():
	''' Takes a snapshot with the webcam and returns the path to the 
	    saved image (in TMP). None if could not take the snapshot. 
	'''
	if CONFIG['camshot'] == 'False':
		_print(' . Skipping webcamshot.')
		return None

	_print(' - Taking webcamshot.')
	if OS == 'WINDOWS':
		try:
			filepath = '%s%c%s_webcam.jpg' % (TMP, SEP, FILENAME)
			from VideoCapture import Device
			cam = Device(devnum=0)
			if not cam:
				cam = Device(devnum=1)
				if not cam:
					_print(' ! Error while taking webcamshot: no device available.')
					return None
			#cam.setResolution(768, 576) # Here you can modify the picture resolution
			camshot = cam.getImage()
			time.sleep(1)
			cam.saveSnapshot(filepath)
		except Exception as ex:
			_print(' ! Error while taking webcamshot: %s' % ex[0])
			return None
	else:
		filepath = '%s%c%s_webcam.%s' % (TMP, SEP, FILENAME, CONFIG['camshot_filetype'])
		try:
			os.system(CONFIG['camshot'] % filepath)
			time.sleep(1)
		except Exception as ex:
			_print(' ! Error while taking webcamshot: %s' % ex[0])
			return None
		if os.path.isfile(filepath):
			if CONFIG['camshot_filetype'] == 'ppm':
				new_filepath = '%s%c%s_webcam.jpg' % (TMP, SEP, FILENAME)
				os.system('/usr/bin/convert %s %s' % (filepath, new_filepath))
				os.unlink(filepath)
				filepath = new_filepath
	if not os.path.isfile(filepath):
		return None
	return filepath

def wifiaccesspoints():
	''' Returns a list of nearby wifi access points (AP). '''
	if CONFIG['wifi_access_points'] == 'False':
		return 'Disabled.'
	return runprocess(CONFIG['wifi_access_points'].split(' '))


# ----------------------------------------------------------------------
# --- [ C'est parti mon kiki ! ] ---------------------------------------
# ----------------------------------------------------------------------

if __name__ == '__main__':
	_print('%s %s' % (PROGRAMNAME, PROGRAMVERSION))
	
	# Load configuration
	config()
	
	argv = sys.argv[1:]
	if 'add' in argv:
		ip = public_ip()
		if not ip:
			print 'Computer does not seem to be connected to the internet. Aborting.'
		else:
			known = False
			if os.path.isfile(IPFILE):
				# Read previous IP
				f = open(IPFILE, 'rb')
				previous_ips = f.readlines()
				f.close()
				if ip_hash(ip) in [s.strip() for s in previous_ips]:
					print 'IP already known.'
					known = True
			if known is False:
				print 'Adding current ip %s to %s.' % (ip, IPFILE)
				f = open(IPFILE, 'a+b')
				f.write(ip_hash(ip) + "\n")
				f.close()
	elif 'help' in argv:
		print '%s %s' % (PROGRAMNAME, PROGRAMVERSION)
		print 'Options ---'
		print '   add      add the current IP to %s' % IPFILE
		print '   help     show this message'
		print '   ip       show current IP'
		print '   list     list known IP'
		print '   version  show %s, python and versions' % PROGRAMNAME
	elif 'ip' in argv:
		ip = public_ip()
		if not ip:
			print 'Computer does not seem to be connected to the internet. Aborting.'
		else:
			print 'IP  : %s' % ip
			iphash = ip_hash(ip)
			print 'Hash: %s...%s' % (iphash[:20], iphash[-20:])
	elif 'list' in argv:
		if not os.path.isfile(IPFILE):
			print '%s does not exist!' % IPFILE
		else:
			f = open(IPFILE, 'rb')
			print 'IP hashes in %s:' % IPFILE
			for s in f.readlines():
				print '   %s...%s' % (s[:20], s.strip()[-20:])
			f.close()
	elif 'version' in argv:
		v = sys.version_info;
		print '%s %s' % (PROGRAMNAME, PROGRAMVERSION)
		print 'I am using python %s.%s.%s' % (v.major, v.minor, v.micro)
		if OS == 'WINDOWS':
			from PIL import Image
			print 'with VideoCapture %s' % VCVERSION
			print '          and PIL %s' % Image.VERSION
		sys.exit(0)
	else:
		if OS == 'WINDOWS':
			# Cron job like for Windows :s
			while True:
				if stolen():
					snapshot(True)
					time.sleep(300 - (time.time() - T)) # < 5 minutes
				else:
					snapshot(False)
					time.sleep(900 - (time.time() - T)) # < 15 minutes
				# Reload configuration
				config()
		else:
			if stolen():
				for i in range(0, 2):
					snapshot(True)
					time.sleep(300 - (time.time() - T)) # < 5 minutes
					config()
			else:
				snapshot(False)