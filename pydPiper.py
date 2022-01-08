#!/usr/bin/python.pydPiper3
# coding: UTF-8

# pydPiper service to display music data to LCD and OLED character displays
# Written by: Ron Ritchey
# Edited by: synoniem@hotmail.com
# Also edited by Saiyato
import json, threading, logging, queue, time, sys, getopt, moment, signal, subprocess, os, copy, datetime, math, requests
import pages
import displays
import sources
import pydPiper_config
import pause

#try:
#    import pyowm
#except ImportError:
#    pass


exitapp = [ False ]

class music_controller(threading.Thread):
    # Receives updates from music services
    # Determines what page to displays
    # Sends relevant updates to display_controller

    # musicdata variables.
    # Includes all from musicdata class plus environmentals
    musicdata_init = {
        'state':"stop",
        'musicdatasource':"",
        'actPlayer':"",
        'artist':"",
        'title':"",
        'album':"",
        'uri':"",
        'current':-1,
        'elapsed':-1,
        'remaining':"",
        'total_time':"",
        'duration':-1,
        'length':-1,
        'position':"",
        'elapsed_formatted':"",
        'elapsed_simple':"",
        'volume':-1,
        'repeat': 0,
        'single': 0,
        'random': 0,
        'channels':0,
        'bitdepth':"",
        'bitrate':"",
        'samplerate':"",
        'type':"",
        'tracktype':"",
        'repeat_onoff': "Off",
        'single_onoff': "Off",
        'random_onoff': "Off",
        'playlist_display':"",
        'playlist_position':-1,
        'playlist_count':-1,
        'playlist_length':-1,
        'current_tempc':0,
        'current_tempf':0,
        'disk_avail':0,
        'disk_availp':0,
        'current_time':"",
        'utc':moment.utcnow(),
        'localtime':moment.utcnow().timezone(pydPiper_config.TIMEZONE),
        'current_time_sec':"",
        'current_time_formatted':"",
        'time_formatted':"",
        'current_ip':"",
        'outside_conditions':'No data',
        'outside_temp_min':0,
        'outside_temp_max':0,
        'outside_temp_formatted':'',
        'system_temp_formatted':''
    }


    def __init__(self, servicelist, display_controller, showupdates=False):
        threading.Thread.__init__(self)

        self.daemon = True
        self.musicqueue = queue.Queue()
        self.image = None
        self.showupdates = showupdates
        self.display_controller = display_controller

        self.musicdata = copy.deepcopy(self.musicdata_init)
        self.musicdata_prev = copy.deepcopy(self.musicdata)
        self.servicelist = servicelist
        self.services = { }

        # Attempt to initialize services
        self.initservices()

        # Lock used to prevent simultaneous update of the musicdata dictionary
        self.musicdata_lock = threading.Lock()


    def initservices(self):

        # Make sure that if rune is selected that is is the only service that is selected
        if "rune" in self.servicelist and len(self.servicelist) > 1:
            logging.critical("Rune service can only be used alone")
            raise RuntimeError("Rune service can only be used alone")
        if "volumio" in self.servicelist and len(self.servicelist) > 1:
            logging.critical("Volumio service can only be used alone")
            raise RuntimeError("Volumio service can only be used alone")

        musicservice = None
        for s in self.servicelist:
            s = s.lower()
            try:
                if s == "mpd" or s == "moode":
                    musicservice = sources.musicdata_mpd.musicdata_mpd(self.musicqueue, pydPiper_config.MPD_SERVER, pydPiper_config.MPD_PORT, pydPiper_config.MPD_PASSWORD)
                elif s == "spop":
                    musicservice = sources.musicdata_spop.musicdata_spop(self.musicqueue, pydPiper_config.SPOP_SERVER, pydPiper_config.SPOP_PORT, pydPiper_config.SPOP_PASSWORD)
                elif s == "lms":
                    musicservice = sources.musicdata_lms.musicdata_lms(self.musicqueue, pydPiper_config.LMS_SERVER, pydPiper_config.LMS_PORT, pydPiper_config.LMS_USER, pydPiper_config.LMS_PASSWORD, pydPiper_config.LMS_PLAYER)
                elif s == "rune":
                    musicservice = sources.musicdata_rune.musicdata_rune(self.musicqueue, pydPiper_config.RUNE_SERVER, pydPiper_config.RUNE_PORT, pydPiper_config.RUNE_PASSWORD)
                elif s == "volumio":
                    musicservice = sources.musicdata_volumio2.musicdata_volumio2(self.musicqueue, pydPiper_config.VOLUMIO_SERVER, pydPiper_config.VOLUMIO_PORT, exitapp )
                else:
                    logging.debug("Unsupported music service {0} requested".format(s))
                    continue
            except NameError:
                # Missing dependency for requested servicelist
                logging.warning("Request for {0} failed due to missing dependencies".format(s))
                pass
            if musicservice != None:
                self.services[s] = musicservice

        if len(self.services) == 0:
            logging.critical("No music services succeeded in initializing")
            raise RuntimeError("No music services succeeded in initializing")

    def launch_update_thread(self, func):
        sv_t = threading.Thread(target=func)
        sv_t.daemon = True
        sv_t.start()

    def run(self):

        logging.debug("Music Controller Starting")

        self.launch_update_thread(self.updatesystemvars)
        self.launch_update_thread(self.updateconditions)
        self.launch_update_thread(self.updateforecast)

        timesongstarted = 0


        # Inform the system that we are starting up
        with self.musicdata_lock:
            self.musicdata_prev['state'] = ''
            self.musicdata['state'] = 'starting'
        self.starttime = time.time()

        lastupdate = 0 # Initialize variable to be used to force updates every second regardless of the receipt of a source update
        while not exitapp[0]:

            updates = { }

            # Check if we are starting up.  If yes, update pages to display any start message.
            if self.starttime + pydPiper_config.STARTUP_MSG_DURATION > time.time():
                time.sleep(pydPiper_config.STARTUP_MSG_DURATION)
                with self.musicdata_lock:
                    self.musicdata['state'] = 'stop'
                continue

            # Attempt to get an update from the queue
            try:
                updates = self.musicqueue.get_nowait()
                self.musicqueue.task_done()
            except queue.Empty:
                pass

            # Get current time
            try:
                utc = moment.utcnow()
                localtime = moment.utcnow().timezone(pydPiper_config.TIMEZONE)
                current_time_ampm = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%p").strip()
                if pydPiper_config.TIME24HOUR == True:
                    current_time = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%H:%M").strip()
                    current_time_sec = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%H:%M:%S").strip()
                    current_time_ampm = ''
                else:
                    current_time = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%-I:%M %p").strip()
                    current_time_sec = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime("%-I:%M:%S %p")
            except ValueError:
                # Don't know why but on exit, the moment code is occasionally throwing a ValueError
                current_time = "00:00"
                current_time_sec = "00:00:00"
                current_time_ampm = ''
                utc = None
                localtime = None

            with self.musicdata_lock:
                # Update musicdata based upon received message
                for item, value in updates.items():
                    self.musicdata[item] = value

                # Update song timing variables
                if 'elapsed' in updates:
                    self.musicdata['elapsed'] = self.musicdata['current'] = updates['elapsed']
                    timesongstarted = time.time() - self.musicdata['elapsed']

                if self.musicdata['state'] == 'play':
                    if 'elapsed' not in updates:
                        if timesongstarted > 0:
                            self.musicdata['elapsed'] = int(time.time() - timesongstarted)
                        else:
                            # We got here without timesongstarted being set which is a problem...
                            logging.debug("Trying to update current song position with an uninitialized start time")

                # If the value of current has changed then update the other related timing variables
                if self.musicdata['elapsed'] != self.musicdata_prev['elapsed']:
                    timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed']))
                    timepos_advanced = timepos
                    total_time = "00:00"                    
                    if self.musicdata['length'] > 0:
#                        timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed'])) + "/" + time.strftime("%-M:%S", time.gmtime(self.musicdata['length']))
                        timepos_advanced = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed'])) + "/" + time.strftime("%-M:%S", time.gmtime(self.musicdata['length']))
                        remaining = time.strftime("%-M:%S", time.gmtime(self.musicdata['length'] - self.musicdata['elapsed'] ) )
                        total_time = time.strftime("%-M:%S", time.gmtime(self.musicdata['length']))
                    else:
                        timepos = time.strftime("%-M:%S", time.gmtime(self.musicdata['elapsed']))
                        remaining = timepos
                    self.musicdata[u'elapsed_formatted'] = timepos_advanced
                    self.musicdata['remaining'] = remaining
#                    self.musicdata['elapsed_formatted'] = self.musicdata['position'] = timepos
                    self.musicdata[u'elapsed_simple'] = self.musicdata[u'position'] = timepos
                    self.musicdata[u'total_time'] = total_time
                # Update onoff variables (random, single, repeat)
                self.musicdata['random_onoff'] = "On" if self.musicdata['random'] else "Off"
                self.musicdata['single_onoff'] = "On" if self.musicdata['single'] else "Off"
                self.musicdata['repeat_onoff'] = "On" if self.musicdata['repeat'] else "Off"

                # update time variables
                self.musicdata['utc'] = utc
                self.musicdata['localtime'] = localtime
                self.musicdata['time'] = current_time
                self.musicdata['time_ampm'] = current_time_ampm
                # note: 'time_formatted' is computed during page processing as it needs the value of the strftime key contained on the line being displayed

                # For backwards compatibility
                self.musicdata['current_time'] = current_time
                self.musicdata['current_time_sec'] = current_time


            # If anything has changed, update pages ### probably unnecessary to check this now that time is being updated in this section
            if self.musicdata != self.musicdata_prev or lastupdate < time.time():

                # Set lastupdate time to 1 second in the future
                lastupdate = time.time()+1

                self.musicdata['time_formatted'] = moment.utcnow().timezone(pydPiper_config.TIMEZONE).strftime('%H:%M').strip()
                # To support previous key used for this purpose
                self.musicdata['current_time_formatted'] = self.musicdata['time_formatted']

                # Update display controller
                # The primary call to this routine is in main but this call is needed to catch variable changes before musicdata_prev is updated.
                next(self.display_controller)

                # Print the current contents of musicdata if showupdates is True
                if self.showupdates:

                    # Check to see if a variable has changed (except time variables)
                    shouldshowupdate = False
                    for item, value in self.musicdata.items():
                        try:
                            if item in ['utc', 'localtime', 'time', 'time_ampm', 'current_time', 'current_time_sec']:
                                continue
                            if self.musicdata_prev[item] != value:
                                shouldshowupdate = True
                                break
                        except KeyError:
                            shouldshowupdate = True
                            break


                    if shouldshowupdate:
                        ctime = current_time
                        print(("Status at time {0}".ctime))

                        with self.musicdata_lock:
                            for item,value in self.musicdata.items():
                                try:
                                    print(("    [{0}]={1} {2}".format(item,repr(value), type(value))))
                                except:
                                    print ("err")
                                    print(("[{0}] =".format(item)))
                                    print((type(value)))
                                    print((repr(value)))
                            print ("\n")

                # Update musicdata_prev
                with self.musicdata_lock:
                    for item, value in self.musicdata.items():
                        try:
                            if self.musicdata_prev[item] != value:
                                self.musicdata_prev[item] = value
                        except KeyError:
                            self.musicdata_prev[item] = value

            # Update display data every 1/4 second
            time.sleep(.25)

    def checkweatherconfiguration(self):
        if not pydPiper_config.WEATHER_SERVICE:
            logging.debug('Weather service not enabled')
            return False

        if pydPiper_config.WEATHER_SERVICE not in ['wunderground', 'accuweather', 'weerlive']:
            logging.warning('{0} is not a valid weather service'.format(pydPiper_config.WEATHER_SERVICE))
            return False

        if not pydPiper_config.WEATHER_API:
            logging.warning('Weather service requires an API key.  Weather services will not be available until one is provided')
            return False

        if not pydPiper_config.WEATHER_LOCATION:
            logging.warning('Weather service requires that a location be specified.  Weather services will not be available until one is provided')
            return False
        return True

    def checkaccuweatherreturn(self, status_code):
        if status_code == 400:
            logging.warning('Request had bad syntax or the parameters supplied were invalid.  Request was [{0}]'.format(querystr))
        elif status_code == 401:
            logging.warning('Unauthorized. API authorization failed.  API key is [{0}]'.format(pydPiper_config.WEATHER_API))
        elif status_code == 403:
            logging.warning('Unauthorized. You do not have permission to access this endpoint')
        elif status_code == 404:
            logging.warning('Server has not found a route matching the given URI.  Request was [{0}]'.format(querystr))
        elif status_code == 500:
            logging.warning('Server encountered an unexpected condition which prevented it from fulfilling the request.  Request was [{0}]'.format(querystr))
        elif status_code == 200:
            return True
        else:
            logging.warning('An unexpected return value was provide.  Value was [{0}]. Request was [{1}]'.format(status_code,querystr))
        return False


    def updateforecast(self):
        if not self.checkweatherconfiguration():
            return

        logging.debug('Initializing weather forecast update process.  Forecasts will update every 12 hours at noon and midnight')

        while not exitapp[0]:
            updateFlag = False

            logging.debug('Requesting weather forecast from {0}'.format(pydPiper_config.WEATHER_SERVICE))
            if pydPiper_config.WEATHER_SERVICE == 'accuweather':
                querystr = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/' + pydPiper_config.WEATHER_LOCATION
                r = requests.get(querystr, { 'apikey': pydPiper_config.WEATHER_API,  })

                if self.checkaccuweatherreturn(r.status_code):
                    try:
                        res = r.json()
                        todaysForecast = res['DailyForecasts'][0]

                        temp_max_f = todaysForecast['Temperature']['Maximum']['Value'] if todaysForecast['Temperature']['Maximum']['Unit'] == 'F' else round((todaysForecast['Temperature']['Maximum']['Value']*1.8)+32,1)
                        temp_min_f = todaysForecast['Temperature']['Minimum']['Value'] if todaysForecast['Temperature']['Minimum']['Unit'] == 'F' else round((todaysForecast['Temperature']['Minimum']['Value']*1.8)+32,1)
                        outside_temp_max = temp_max_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else round((temp_max_f-32)*0.55555556,1)
                        outside_temp_min = temp_min_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else round((temp_min_f-32)*0.55555556,1)
                        outside_temp_max_formatted = "{0}°{1}".format(int(outside_temp_max),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_temp_min_formatted = "{0}°{1}".format(int(outside_temp_min),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_conditions = todaysForecast['Day']['IconPhrase']
                        updateFlag = True
                    except (KeyError, IndexError, ValueError):
                        logging.warning('AccuWeather provided a response in an unexpected format.  Received [{0}]'.format(res))

            if updateFlag:
                logging.debug('Forecast calls for a high of {0}, a low of {1}.  Condition is {2}'.format(outside_temp_max_formatted, outside_temp_min_formatted, outside_conditions))
                with self.musicdata_lock:
                    self.musicdata['outside_temp_max'] = outside_temp_max
                    self.musicdata['outside_temp_min'] = outside_temp_min
                    self.musicdata['outside_temp_max_formatted'] = outside_temp_max_formatted
                    self.musicdata['outside_temp_min_formatted'] = outside_temp_min_formatted
                    self.musicdata['outside_conditions'] = outside_conditions

            # Sleep until next update which occurs every half day
            pause.sleepUntil(time.time()+pause.nextHalfday(60), exitapp)


    def updateconditions(self):
        if not self.checkweatherconfiguration():
            return

        logging.debug('Initializing weather current conditions update process.  Current conditions will update every hour')

        while not exitapp[0]:
            updateFlag = False
            # If using accuweather, sample current condition date every hour
            if pydPiper_config.WEATHER_SERVICE == 'accuweather':
                logging.debug('Requesting current conditions from {0}'.format(pydPiper_config.WEATHER_SERVICE))
                querystr = 'http://dataservice.accuweather.com/currentconditions/v1/' + pydPiper_config.WEATHER_LOCATION
                r = requests.get(querystr, { 'apikey': pydPiper_config.WEATHER_API })

                if self.checkaccuweatherreturn(r.status_code):
                    try:
                        res = r.json()
                        current_observation = res[0]

                        temp = current_observation['Temperature']['Imperial']['Value'] if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else current_observation['Temperature']['Metric']['Value']
                        temp_formatted = "{0}°{1}".format(int(temp),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        updateFlag = True
                    except (KeyError, IndexError, ValueError):
                        logging.warning('AccuWeather provided a response in an unexpected format.  Received [{0}]'.format(res))

                    if updateFlag:
                        logging.debug('Current Temperature is {0}'.format(temp_formatted))
                        with self.musicdata_lock:
                            self.musicdata['outside_temp'] = temp
                            self.musicdata['outside_temp_formatted'] = temp_formatted

            # If using Weather Undergroun, sample current and forecast condition date every hour
            elif pydPiper_config.WEATHER_SERVICE == 'wunderground':
                querystr = 'http://api.wunderground.com/api/' + pydPiper_config.WEATHER_API + '/geolookup/conditions/forecast/q/' + pydPiper_config.WEATHER_LOCATION + '.json'
                r = requests.get(querystr)

                if self.checkaccuweatherreturn(r.status_code):
                    try:
                        res = r.json()
                        if 'error' in res['response']:
                            logging.warning('Error occured retrieving forecast from Weather Underground.  Problem type was [{0}]:[{1}]'.format(res['response']['error']['type'],res['response']['error']['description']))
                        else:
                            todaysForecast = res['forecast']['simpleforecast']['forecastday'][0]
                            currentObservation = res['current_observation']

                            temp = currentObservation['temp_f'] if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else currentObservation['temp_c']
                            temp_formatted = "{0}°{1}".format(int(temp),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))

                            temp_max_f = round(float(todaysForecast['high']['fahrenheit']),1)
                            temp_min_f = round(float(todaysForecast['low']['fahrenheit']),1)
                            temp_max_c = round(float(todaysForecast['high']['celsius']),1)
                            temp_min_c = round(float(todaysForecast['low']['celsius']),1)
                            outside_temp_max = temp_max_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_max_c
                            outside_temp_min = temp_min_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_min_c
                            outside_temp_max_formatted = "{0}°{1}".format(int(outside_temp_max),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                            outside_temp_min_formatted = "{0}°{1}".format(int(outside_temp_min),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                            outside_conditions = currentObservation['weather']
                            updateFlag = True
                    except (KeyError, IndexError, ValueError):
                        logging.warning('Weather Underground provided a response in an unexpected format.  Received [{0}]'.format(res))

                    if updateFlag:
                        logging.debug('Current Temperature is {0}'.format(temp_formatted))
                        with self.musicdata_lock:
                            self.musicdata['outside_temp'] = temp
                            self.musicdata['outside_temp_formatted'] = temp_formatted
                            self.musicdata['outside_temp_max'] = outside_temp_max
                            self.musicdata['outside_temp_min'] = outside_temp_min
                            self.musicdata['outside_temp_max_formatted'] = outside_temp_max_formatted
                            self.musicdata['outside_temp_min_formatted'] = outside_temp_min_formatted
                            self.musicdata['outside_conditions'] = outside_conditions

            # If using weerlive.nl, sample current condition date every hour
            elif pydPiper_config.WEATHER_SERVICE == 'weerlive':
                logging.debug('Requesting current conditions from {0}'.format(pydPiper_config.WEATHER_SERVICE))
                querystr = 'http://weerlive.nl/api/json-data-10min.php?key=' + pydPiper_config.WEATHER_API + '&locatie=' + pydPiper_config.WEATHER_LOCATION
                r = requests.get(querystr)

                if self.checkaccuweatherreturn(r.status_code):
                    try:
                        res = r.json()
                        temp = res['liveweer'][0]['temp']
                        temp_formatted = "{0}°{1}".format(int(float(temp)),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        temp_max_f = round((float(res['liveweer'][0]['d0tmax'])*1.8)+32,1)
                        temp_min_f = round((float(res['liveweer'][0]['d0tmin'])*1.8)+32,1)
                        temp_max_c = float(res['liveweer'][0]['d0tmax'])
                        temp_min_c = float(res['liveweer'][0]['d0tmin'])
                        outside = pydPiper_config.WEATHER_OUTSIDE
                        outside_temp_max = temp_max_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_max_c
                        outside_temp_min = temp_min_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_min_c
                        outside_temp_max_formatted = "{0}°{1}".format(int(outside_temp_max),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_temp_min_formatted = "{0}°{1}".format(int(outside_temp_min),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_conditions = res['liveweer'][0]['samenv']                       
                        updateFlag = True
                    except (KeyError, IndexError, ValueError):
                        logging.warning('weerlive.nl provided a response in an unexpected format.  Received [{0}]'.format(res))
                        logging.warning(KeyError)
                        logging.warning(IndexError)
                        logging.warning(ValueError)
                    if updateFlag:
                        logging.debug('Current Temperature is {0}'.format(temp_formatted))
                        with self.musicdata_lock:
                            self.musicdata['outside_temp'] = temp
                            self.musicdata['outside_temp_formatted'] = temp_formatted
                            self.musicdata['outside_temp_max'] = outside_temp_max
                            self.musicdata['outside_temp_min'] = outside_temp_min
                            self.musicdata['outside_temp_max_formatted'] = outside_temp_max_formatted
                            self.musicdata['outside_temp_min_formatted'] = outside_temp_min_formatted
                            self.musicdata['outside_conditions'] = outside_conditions

            # Sleep until next update which occurs every hour
            pause.sleepUntil(time.time()+pause.nextHour(60), exitapp)


    def updatesystemvars(self):
        logging.debug('Initializing current system status update process.  System status will update every five minutes')

        while not exitapp[0]:

            current_ip = subprocess.getoutput("ip -4 route get 1 | head -1 | cut -d' ' -f8 | tr -d '\n'").strip()

            try:
                with open("/sys/class/thermal/thermal_zone0/temp") as file:
                    system_tempc = int(file.read())

                # Convert value to float and correct decimal place
                system_tempc = round(float(system_tempc) / 1000,1)

                # convert to fahrenheit
                system_tempf = round(system_tempc*9/5+32,1)

            except AttributeError:
                system_tempc = 0.0
                system_tempf = 0.0

            try:
                if pydPiper_config.TEMPERATURE.lower() == 'celsius':
                    system_temp = system_tempc
                    system_temp_formatted = "{0}°c".format(int(system_temp))
                else:
                    system_temp = system_tempf
                    system_temp_formatted = "{0}°f".format(int(system_temp))
            except:
                system_temp = system_tempf
                system_temp_formatted = "{0}°f".format(int(system_temp))

            try:
                # Check if running on OSX.  If yes, adjust df command
                with os.popen('cat /etc/os-release') as p:
                    releaseName = p.readline()


                if sys.platform == "darwin":
                    with os.popen("df /") as p:
                        p = os.popen("df /")
                        line = p.readline()
                        line = p.readline()

                    va = line.split()
                    line = "{0} {1}".format(va[3], va[4])

                    va = line.split()
                    avail = int(va[3])
                    usedp = int(va[4][:-1]) # Remove trailing % and convert to int
                    used = int(va[2])
                    availp = 100-usedp

                elif releaseName[6:12] == 'Alpine':
                    with os.popen("df /") as p:
                        p = os.popen("df -B 1 /")
                        line = p.readline()
                        line = p.readline()
                        line = p.readline()

                        va = line.split()
                       	avail = int(va[2])
                        usedp = int(va[3][:-1]) # Remove trailing % and convert to int
                        used = int(va[1])
                        availp = 100-usedp
                else:
                    # assume running on Raspberry linux
                    with os.popen("df -B 1 /") as p:
                        line = p.readline()
                        line = p.readline().strip()

                    va = line.split()
                    avail = int(va[3])
                    usedp = int(va[4][:-1]) # Remove trailing % and convert to int
                    used = int(va[2])
                    availp = 100-usedp

            except AttributeError:
                avail = 0
                availp = 0
                usedp = 0
                used = 0

            logging.debug('System status: Temp {0}, Disk space remaining {1}%, IP address {2}'.format(system_temp_formatted, availp, current_ip))
            with self.musicdata_lock:
                self.musicdata['system_temp'] = system_temp
                self.musicdata['system_temp_formatted'] = system_temp_formatted

                self.musicdata['system_tempc'] = system_tempc
                self.musicdata['system_tempf'] = system_tempf

                # For backward compatibility
                self.musicdata['current_tempc'] = self.musicdata['system_tempc']
                self.musicdata['current_tempf'] = self.musicdata['system_tempf']

                self.musicdata['disk_avail'] = avail
                self.musicdata['disk_availp'] = availp
                self.musicdata['disk_used'] = used
                self.musicdata['disk_usedp'] = usedp


                self.musicdata['ip'] = current_ip

                # For backwards compatibility
                self.musicdata['current_ip'] = current_ip

            # Sleep until next update which occurs every minutes
            pause.sleepUntil(time.time()+300, exitapp)

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == '__main__':
    import math
    signal.signal(signal.SIGTERM, sigterm_handler)

    # Changing the system encoding should no longer be needed
#    if sys.stdout.encoding != u'UTF-8':
#            sys.stdout = codecs.getwriter(u'utf-8')(sys.stdout, u'strict')

    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=pydPiper_config.LOGFILE, level=pydPiper_config.LOGLEVEL)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger('socketIO-client').setLevel(logging.WARNING)

    # Move unhandled exception messages to log file
    def handleuncaughtexceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        try:
            if len(mc.musicdata) > 0:
                logging.error("Player status at exception")
                logging.error(str(mc.musicdata))
        except NameError:
            # If this gets called before the music controller is instantiated, ignore it
            pass

        sys.__excepthook__(exc_type, exc_value, exc_traceback)


    sys.excepthook = handleuncaughtexceptions

    # Suppress MPD libraries INFO messages
    loggingMPD = logging.getLogger("mpd")
    loggingMPD.setLevel( logging.WARN )
    loggingPIL = logging.getLogger('PIL')
    loggingPIL.setLevel( logging.WARN )

    try:
        opts, args = getopt.getopt(sys.argv[1:],"d:",["driver=","devicetype=","width=","height=","rs=","e=","d4=","d5=","d6=","d7=","i2caddress=","i2cport=" ,"wapi=", "wlocale=", "timezone=", "temperature=", "lms","mpd","spop","rune","volumio","pages=", "lmsplayer=", "showupdates"])
    except getopt.GetoptError:
        print ('pydPiper.py -d <driver> --devicetype <devicetype (for LUMA devices)> --width <width in pixels> --height <height in pixels> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7> --i2caddress <i2c address> --i2cport <i2c port> --wapi <weather underground api key> --wlocale <weather location> --timezone <timezone> --temperature <fahrenheit or celsius> --mpd --spop --lms --rune --volumio --pages <pagefile> --lmsplayer <mac address of lms player> --showupdates')
        sys.exit(2)

    services_list = [ ]
    driver = ''
    devicetype = ''
    showupdates = False
    pagefile = 'pages.py'

    pin_rs = pydPiper_config.DISPLAY_PIN_RS
    pin_e = pydPiper_config.DISPLAY_PIN_E
    [pin_d4, pin_d5, pin_d6, pin_d7] = pydPiper_config.DISPLAY_PINS_DATA
    rows = pydPiper_config.DISPLAY_HEIGHT
    cols = pydPiper_config.DISPLAY_WIDTH
    i2c_address = pydPiper_config.DISPLAY_I2C_ADDRESS
    i2c_port = pydPiper_config.DISPLAY_I2C_PORT
    enable = pydPiper_config.DISPLAY_ENABLE_DURATION
    driver = pydPiper_config.DISPLAY_DRIVER
    pagefile = pydPiper_config.PAGEFILE
    services_list.append(pydPiper_config.MUSIC_SERVICE)


    for opt, arg in opts:
        if opt == '-h':
            print ('pydPiper.py -d <driver> --devicetype <devicetype e.g. ssd1306, sh1106> --width <width in pixels> --height <height in pixels> --rs <rs> --e <e> --d4 <d4> --d5 <d5> --d6 <d6> --d7 <d7> --i2caddress <i2c address> --i2cport <i2c port> --enable <enable duration> --wapi <weather underground api key> --wlocale <weather location> --timezone <timezone> --temperature <fahrenheit or celsius> --mpd --spop --lms --rune --volumio --pages <pagefile> --lmsplayer <mac address of lms player> --showupdates')
            sys.exit()
        elif opt in ("-d", "--driver"):
            driver = arg
        elif opt in ("--devicetype"):
            devicetype = arg
        elif opt in ("--rs"):
            pin_rs  = int(arg)
        elif opt in ("--e"):
            pin_e  = int(arg)
        elif opt in ("--d4"):
            pin_d4  = int(arg)
        elif opt in ("--d5"):
            pin_d5  = int(arg)
        elif opt in ("--d6"):
            pin_d6  = int(arg)
        elif opt in ("--d7"):
            pin_d7  = int(arg)
        elif opt in ("--i2caddress"):
            i2c_address = int(arg,0)
        elif opt in ("--i2cport"):
            i2c_port = int(arg,0)
        elif opt in ("--width"):
            cols = int(arg,0)
        elif opt in ("--height"):
            rows = int(arg,0)
        elif opt in ("--enable"):
            enable = int(arg)
        elif opt in ("--wapi"):
            pydPiper_config.WUNDER_API = arg
        elif opt in ("--wlocale"):
            pydPiper_config.WUNDER_LOCATION = arg
        elif opt in ("--timezone"):
            pydPiper_config.TIMEZONE = arg
        elif opt in (u"--time24hour"):
            pydPiper_config.TIME24HOUR = True
        elif opt in ("--temperature"):
            pydPiper_config.TEMPERATURE = arg
        elif opt in ("--mpd"):
            services_list.append('mpd')
        elif opt in ("--spop"):
            services_list.append('spop')
        elif opt in ("--lms"):
            services_list.append('lms')
        elif opt in ("--lmsplayer"):
            pydPiper_config.LMS_PLAYER = arg
        elif opt in ("--rune"):
            services_list.append('rune')
        elif opt in ("--volumio"):
            services_list.append('volumio')
        elif opt in ("--pages"):
            pagefile = arg
            # print u"Loading {0} as page file".format(arg)
            # If page file provided, try to load provided file on top of default pages file
            # try:
            #     newpages = imp.load_source(u'pages', arg)
            #     if validpages(newpages):
            #         pages = newpages
            #     else:
            #         print u"Invalid page file provided.  Using default pages."
            # except IOError:
            #     # Page file not found
            #     print u"Page file {0} not found.  Using default pages".format(arg)

        elif opt in ("--showupdates"):
            showupdates = True

    pydPiper_config.DISPLAY_SIZE = (cols, rows)

    pins_data = [pin_d4, pin_d5, pin_d6, pin_d7]

    if len(services_list) == 0:
        logging.critical("Must have at least one music service to monitor")
        sys.exit()

    logging.info('pydPiper starting')

    dq = queue.Queue()



    # Choose display

    if not driver:
        try:
            driver = pydPiper_config.DISPLAY_DRIVER
        except:
            drvier = ''

    if not devicetype:
        try:
            devicetype = pydPiper_config.DISPLAY_DEVICETYPE
        except:
            devicetype = ''


    if driver == "winstar_weg":
        lcd = displays.winstar_weg.winstar_weg(rows, cols, pin_rs, pin_e, pins_data, enable)
    elif driver == "hd44780":
        lcd = displays.hd44780.hd44780(rows, cols, pin_rs, pin_e, pins_data, enable)
    elif driver == "hd44780_i2c":
        lcd = displays.hd44780_i2c.hd44780_i2c(rows, cols, i2c_address, i2c_port, enable)
    elif driver == "hd44780_mcp23008":
        lcd = displays.hd44780_i2c.hd44780_mcp23008(rows, cols, i2c_address, i2c_port, enable)
    elif driver == "ssd1306_i2c":
        lcd = displays.ssd1306_i2c.ssd1306_i2c(rows, cols, i2c_address, i2c_port)
    elif driver == "luma_i2c":
        lcd = displays.luma_i2c.luma_i2c(rows, cols, i2c_address, i2c_port, devicetype)
    elif driver == "lcd_curses":
        lcd = displays.lcd_curses.lcd_curses(rows, cols)
    else:
        logging.critical("No valid display found")
        sys.exit()

    lcd.clear()


    logging.debug('Loading display controller')
    dc = displays.display.display_controller(pydPiper_config.DISPLAY_SIZE)

    logging.debug('Loading music controller')
    mc = music_controller(services_list, dc, showupdates)
    time.sleep(2)
    mc.start()
    dc.load(pagefile, mc.musicdata,mc.musicdata_prev )

    try:
        while True:
            # Get next image and send it to the display every .1 seconds
            with mc.musicdata_lock:
                img = next(dc)
#            displays.graphics.update(img)
            lcd.update(img)
            time.sleep(pydPiper_config.ANIMATION_SMOOTHING)


    except KeyboardInterrupt:
        pass

    finally:
        print ("Shutting down threads")
        exitapp[0] = True
        try:
            lcd.clear()
            lcd.message("Exiting...")
            time.sleep(3)
            lcd.clear()
            lcd.cleanup()
        except:
            pass
        mc.join()
        logging.info("Exiting...")
