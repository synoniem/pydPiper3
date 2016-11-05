# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings

PAGES_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"Artist",
        'duration':8,
		'hidewhenempty':'any',
        'hidewhenemptyvars': [ "artist" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "artist" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Blank",
        'duration':0.25,
        'lines': [
          {
            'name':"top",
            'format':"",
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Album",
        'duration':8,
		'hidewhenempty':'any',
        'hidewhenemptyvars': [ "album" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "album" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Blank",
        'duration':0.25,
        'lines': [
          {
            'name':"top",
            'format':"",
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Title",
        'duration':10,
		'hidewhenempty':'any',
        'hidewhenemptyvars': [ "title" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "title" ],
            'format':"{0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Blank",
        'duration':0.25,
        'lines': [
          {
            'name':"top",
            'format':"",
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "elapsed_formatted" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      }
    ]
}

PAGES_Stop = {
  'name':"Stop",
  'pages':
    [
      {
        'name':"Ready",
        'duration':15,
        'lines': [
          {
            'name':"top",
            'variables': [ ],
            'format':"Ready",
            'justification':"center",
            'scroll':False
          },
          {
            'name':"bottom",
            'variables': [ "time_formatted" ],
            'strftime':"%a %b %-d %H:%M",
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"SYSTEMVARS",
        'duration':10,
        'lines': [
          {
            'name':"top",
            'variables': [ "system_temp", "disk_usedp" ],
            'format':"Temp: {0}c / Disk {1}% full",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "time_formatted" ],
            'strftime':"%a %b %-d %H:%M",
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"WEATHER",
        'duration':10,
        'lines': [
          {
            'name':"top",
            'variables': [ "outside_temp", "outside_conditions" ],
            'format':"Weather: {0} {1}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "time_formatted" ],
            'strftime':"%a %b %-d %H:%M",
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      }
    ]
}

ALERT_Volume = {
 	'name':"Volume",
	'alert': {
  		'variable': "volume",
		'type': "change",
		'suppressonstatechange':True,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Volume",
		'font':'size5x8.speaker',
        	'duration':2,
        	'lines': [
          		{
            		'name':"top",
            		'variables': ["volume" ],
            		'format':"\x00\x01   Volume {0}",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "volume_bar_big" ],
            		'format':"\x02\x03 {0}",
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_Play = {
 	'name':"Play",
	'alert': {
  		'variable': "state",
		'type': "change",
		'values': [ 'play' ],
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Play",
		'font':'size5x8.player',
        	'duration':1.5,
        	'lines': [
          		{
            		'name':"top",
            		'format':"\x01 Play",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
			'format':'',
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_Stop = {
 	'name':"Stop",
	'alert': {
  		'variable': "state",
		'type': "change",
		'values': [ 'stop' ],
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.player',
        	'duration':1.5,
        	'lines': [
          		{
            		'name':"top",
            		'format':"\x00 Stop",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
			'format':'',
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_RepeatOnce = {
 	'name':"RepeatOnce",
	'alert': {
  		'variable': "single",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.repeat_once',
        	'duration':1.5,
        	'lines': [
          		{
            		'name':"top",
            		'format':"\x00\x01 Repeat",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "single|onoff" ],
            		'format':"\x02\x03 Once {0}",
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_RepeatAll = {
 	'name':"RepeatAll",
	'alert': {
  		'variable': "repeat",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.repeat_all',
        	'duration':1.5,
        	'lines': [
          		{
            		'name':"top",
            		'format':"\x00\x01 Repeat",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "repeat|onoff" ],
            		'format':"\x02\x03 All {0}",
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_Shuffle = {
 	'name':"Shuffle",
	'alert': {
  		'variable': "random",
		'type': "change",
		'suppressonstatechange':False,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
		'name':"Stop",
		'font':'size5x8.shuffle',
        	'duration':1.5,
        	'lines': [
          		{
            		'name':"top",
            		'format':"\x00\x01 Random",
            		'justification':"left",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "random|onoff" ],
            		'format':"\x02\x03 Play {0}",
            		'justification':"left",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_TempTooHigh = {
 	'name':"TempTooHigh",
	'alert': {
  		'variable': "system_tempc",
		'type': "above",
		'values': [ 85 ],
		'suppressonstatechange':False,
		'coolingperiod': 30
	},
	'interruptible':False,
	'pages': [
		{
			'name':"TempTooHigh",
        	'duration':8,
        	'lines': [
          		{
            		'name':"top",
            		'variables': [ ],
            		'format':"Temp Too High",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "system_tempc" ],
            		'format':"Temp: {0}c",
            		'justification':"center",
            		'scroll':False
          		}
        	]
      	}
    ]
}


ALERT_LIST = [ ALERT_Volume, ALERT_Play, ALERT_Stop, ALERT_RepeatOnce, ALERT_RepeatAll, ALERT_Shuffle, ALERT_TempTooHigh ]