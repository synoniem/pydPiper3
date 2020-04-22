            # If using weerlive.nl, sample current condition date every hour
            if pydPiper_config.WEATHER_SERVICE == 'weerlive':
                logging.debug('Requesting current conditions from {0}'.format(pydPiper_config.WEATHER_SERVICE))
                querystr = 'http://weerlive.nl/api/json-data-10min.php?key=' + pydPiper_config.WEATHER_API + '&locatie=' + pydPiper_config.WEATHER_LOCATION
                r = requests.get(querystr)

                if self.checkaccuweatherreturn(r.status_code):
                    try:
                        res = r.json()
                        current_observation = res['weerlive'][0]

                        temp = current_observation['temp']
                        temp_formatted = u"{0}°{1}".format(int(temp),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        temp_max_f = round((current_observation['d0tmax']*1.8)+32,1)
                        temp_min_f = round((current_observation['d0tmin']*1.8)+32,1)
                        temp_max_c = round(float(current_observation['d0tmax'],1)
                        temp_min_c = round(float(current_observation['d0tmin'],1)
                        outside_temp_max = temp_max_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_max_c
                        outside_temp_min = temp_min_f if pydPiper_config.TEMPERATURE.lower() == 'fahrenheit' else temp_min_c
                        outside_temp_max_formatted = u"{0}°{1}".format(int(outside_temp_max),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_temp_min_formatted = u"{0}°{1}".format(int(outside_temp_min),{'fahrenheit':'F', 'celsius': 'C'}.get(pydPiper_config.TEMPERATURE.lower()))
                        outside_conditions = current_observation['samenv']                       
                        updateFlag = True
                    except (KeyError, IndexError, ValueError):
                        logging.warning('weerlive.nl provided a response in an unexpected format.  Received [{0}]'.format(res))

                    if updateFlag:
                        logging.debug('Current Temperature is {0}'.format(temp_formatted))
                        with self.musicdata_lock:
                            self.musicdata[u'outside_temp'] = temp
                            self.musicdata[u'outside_temp_formatted'] = temp_formatted
                            self.musicdata[u'outside_temp_max'] = outside_temp_max
                            self.musicdata[u'outside_temp_min'] = outside_temp_min
                            self.musicdata[u'outside_temp_max_formatted'] = outside_temp_max_formatted
                            self.musicdata[u'outside_temp_min_formatted'] = outside_temp_min_formatted
                            self.musicdata[u'outside_conditions'] = outside_conditions