# meta - base class for collecting meta data from music sources


import abc,logging,urllib.request,urllib.error,urllib.parse,contextlib

class musicdata(metaclass=abc.ABCMeta):
	musicdata_init = {
		'state':"stop",
		'musicdatasource':"",
		'stream':"",
		'actPlayer':"",
		'artist':"",
		'title':"",
		'uri':"",
		'encoding':"",
		'tracktype':"",
		'bitdepth':"",
		'bitrate':"",
		'samplerate':"",
		'elapsed_formatted':"",
		'album':"",
		'elapsed':-1,
		'channels':0,
		'length':0,
		'remaining':"",
		'volume':-1,
		'repeat':False,
		'single':False,
		'random':False,
		'playlist_display':"",
		'playlist_position':-1,
		'playlist_length':-1,

		'my_name':"", # Volumio 2 only

		# Deprecated values
		'current':-1,
		'duration':-1,
		'position':"",
		'playlist_count':-1,
		'type':""
	}

	varcheck = {
		'unicode':
		[
			# Player state
			'state',
			'actPlayer',
			'musicdatasource',

			# Track information
			'album',
			'artist',
			'title',
			'uri',
			'encoding',
			'tracktype',
			'bitdepth',
			'bitrate',
			'samplerate',
			'elapsed_formatted',
			'remaining',
			'playlist_display',
			'my_name'
		],
		'bool':
		[
			# Player state
			'random',
			'single',
			'repeat'
		],
		'int':
		[
			# Player state
			'volume',

			# Track information
			'channels',
			'length',
			'elapsed',
			'playlist_position',
			'playlist_length'

		]
	}


	def __init__(self, q):
		self.musicdata = self.musicdata_init.copy()
		self.musicdata_prev = self.musicdata.copy()
		self.dataqueue = q

	def validatemusicvars(self, vars):

		for vtype, members in self.varcheck.items():

			if vtype == 'unicode':
				for v in members:
					try:
						if type(vars[v]) is str:
							continue
						if type(vars[v]) is None:
							vars[v] = ""
						elif type(vars[v]) is str:
							logging.debug("Received string in {0}.  Converting to Unicode".format(v))
							vars[v] = vars[v].decode()
						else:
							# This happens so often when playing from webradio that I'm disabling logging for now.
#							logging.debug(u"Received non-string type {0} in {1}.  Converting to null".format(type(vars[v]),v))
							vars[v] = ""
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = ""
			elif vtype == 'bool':
				for v in members:
					try:
						if type(vars[v]) is bool:
							continue
						if type(vars[v]) is None:
							vars[v] = False
						elif type(vars[v]) is int:
							logging.debug("Received integer in {0}.  Converting to boolean".format(v))
							vars[v] = bool(vars[v])
						else:
							logging.debug("Received non-bool type {0} in {1}.  Converting to False".format(type(vars[v]),v))
							vars[v] = False
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = False
			elif vtype == 'int':
				for v in members:
					try:
						if type(vars[v]) is int:
							continue
						if type(vars[v]) is None:
							vars[v] = 0
						elif type(vars[v]) is bool:
							logging.debug("Received boolean in {0}.  Converting to integer".format(v))
							vars[v] = int(vars[v])
						else:
							logging.debug("Received non-integer type {0} in {1}.  Converting to 0".format(type(vars[v]),v))
							vars[v] = 0
					except KeyError:
						logging.debug("Missing required value {0}.  Adding empty version".format(v))
						vars[v] = 0



	def webradioname(self,url):
		# Attempt to get name of webradio station
		# Requires station to send name using the M3U protocol
		# url - url of the station

		# Only check for a radio station name if you are actively playing a track
		if self.musicdata['state'] != 'play':
			return ''

		retval = ''
		with contextlib.closing(urllib.request.urlopen(url)) as page:
			cnt = 20
			try:
				for line in page:
					line = line.decode('utf-8')
					cnt -= 1
					if line.startswith('#EXTINF:'):
						try:
							retval = line.split('#EXTINF:')[1].split(',')[1].split(')')[1].strip()
						except IndexError:
							try:
								retval = line.split('#EXTINF:')[1].split(',')[0].split(')')[1].strip()
							except IndexError:
								retval = ''
						if retval != '':
							if retval is str:
								logging.debug("Found {0}".format(retval))
								return retval
							else:
								try:
									logging.debug("Found {0}".format(retval))
									return retval.decode()
								except:
									logging.debug("Not sure what I found {0}".format(retval))
									return ''
					elif line.startswith('Title1='):
						try:
							retval = line.split('Title1=')[1].split(':')[1:2][0]
						except:
							retval = line.split('Title1=')[0]
						retval = retval.split('(')[0].strip()
						return retval.decode()

					if cnt == 0: break
			except:
				# Likely got junk data.  Skip
				pass
			logging.debug("Didn't find an appropriate header at {0}".format(url))


	def sendUpdate(self):
		# Figure out what has changed and then send just those values across dataqueue
		md = { }
		for k, v in self.musicdata.items():
			pv = self.musicdata_prev[k] if k in self.musicdata_prev else None
			if pv != v:
				md[k] = v


		# Send md to queue if anything has changed
		if len(md) > 0:
			# elapsed is special as it needs to be sent to guarantee that the timer gets updated correctly.  Even if it hasn't changed, send it anyway
			md['elapsed'] = self.musicdata['elapsed']
			md['state'] = self.musicdata['state']
			self.dataqueue.put(md)

			# Update musicdata_prev
			self.musicdata_prev = self.musicdata.copy()

	def intn(self,val):
		# A version of int that returns 0 if the value is not convertable
		try:
			retval = int(val)
		except:
			retval = 0
		return retval

	def booln(self,val):
		# A version of bool that returns False if the value is not convertable
		try:
			retval = bool(val)
		except:
			retval = False
		return retval

	def floatn(self,val):
		# A version of float that returns 0.0 if the value is not convertable
		try:
			retval = float(val)
		except:
			retval = 0.0
		return retval


	def clear(self):
		# revert data back to init state
		self.musicdata = self.musicdata_init.copy()

	@abc.abstractmethod
	def run():
		# Start thread(s) to monitor music source
		# Threads must be run as daemons
		# Future state: start thread to issue commands to music source
		return

	#@abc.abstractmethod
	#def command(cmd):
		# Send command to music service
		# Throws NotImplementedError if music service does not support commands
	#	return
