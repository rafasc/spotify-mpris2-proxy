#!/usr/bin/env python2
# -*- coding: utf-8 -*-
 
from PyQt4.QtCore import *
import sys
import signal
import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop


class SpotifyProxy(dbus.service.Object):
    
    MEDIAPLAYER2 = 'org.mpris.MediaPlayer2'
    MEDIAPLAYER2_PLAYER = 'org.mpris.MediaPlayer2.Player'
    OBJECT_PATH = '/org/mpris/MediaPlayer2'
    PROXYPLAYER_BUSNAME = 'org.mpris.MediaPlayer2.mpris2spotifyproxy'

    def __init__(self):     
        self.bus = dbus.SessionBus()
        answer = self.bus.request_name(self.PROXYPLAYER_BUSNAME)
        
        #FIXME handle request
        #print {dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER : 'got bus name',
        #       dbus.bus.REQUEST_NAME_REPLY_ALREADY_OWNER : 'already had bus name',
        #       dbus.bus.REQUEST_NAME_REPLY_IN_QUEUE : 'queued',
        #       dbus.bus.REQUEST_NAME_REPLY_EXISTS : 'alredy exists'}[answer]

        busName = dbus.service.BusName(self.PROXYPLAYER_BUSNAME, self.bus)
        dbus.service.Object.__init__(self, busName, self.OBJECT_PATH)

        self.spotify_iface, self.spotify_props = self._connect_to_spotify()
        self.state = self._init_player_state()

    def _init_player_state(self):
        #syncronize the playing status
        self.Play()
        #Grab spotify metadata
        metadata = self.spotify_props.Get(self.MEDIAPLAYER2_PLAYER,'Metadata')
        
        MP2_state = {'Identity': 'Player DBus Proxy',
		     'CanQuit' : True,
 		     'Fullscreen' : False,
		     'CanSetFullscreen' : False,
		     'CanRaise' : True,
		     'HasTrackList' : False,
		     'DesktopEntry' : '',
		     'SupportedUriSchemes': [''],
		     'SupportedMimeTypes': [''],
		    } 

        
        MP2Player_state = {'PlaybackStatus' : 'Playing',
			   'LoopStatus' : 'None',
			   'Rate' : 1.0,
			   'Shuffle' : False,
			   'Metadata' : dbus.Dictionary( metadata , signature='sv'),
			   'Volume' : 1.0,
			   'Position' : dbus.Int64(0),
			   'MinimumRate' : 1.0,
			   'MaximumRate' : 1.0,
		   	   'CanGoNext' : True,
			   'CanGoPrevious' : True,
			   'CanPlay' : True,
			   'CanPause' : True,
			   'CanSeek' : False,
			   'CanControl' : True, 
                           } 

        state = {}
        state[self.MEDIAPLAYER2] = MP2_state
        state[self.MEDIAPLAYER2_PLAYER] = MP2Player_state

        return state


    def _connect_to_spotify(self):
        #FIXME handle connection
        try:
            spotify = self.bus.get_object('org.mpris.MediaPlayer2.spotify', self.OBJECT_PATH)
        except:
            print "spotify mpris2 interface not found. Is spotify running?"
            sys.exit()
        interface = dbus.Interface(spotify, self.MEDIAPLAYER2_PLAYER)
        properties = dbus.Interface(spotify, dbus.PROPERTIES_IFACE)
        properties.connect_to_signal("PropertiesChanged", self.handler)
        return interface, properties
    
    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def Next(self):
        self.spotify_iface.Next()

    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def Previous(self):
        self.spotify_iface.Previous()

    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def Pause(self):
        self.spotify_iface.Pause()

    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def PlayPause(self):
        self.spotify_iface.PlayPause()
        pbsts = self.state[self.MEDIAPLAYER2_PLAYER]['PlaybackStatus']

        if pbsts == 'Playing':
            pbsts = 'Paused'
        else: 
            pbsts = 'Playing'

        self.state[self.MEDIAPLAYER2_PLAYER]['PlaybackStatus'] = pbsts
        self.PropertiesChanged(self.MEDIAPLAYER2_PLAYER, {'PlaybackStatus' : pbsts}, [])

    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def Stop(self):
        self.spotify_iface.Stop()

    @dbus.service.method(MEDIAPLAYER2_PLAYER)
    def Play(self):
        self.spotify_iface.Play()

    @dbus.service.method(MEDIAPLAYER2_PLAYER, in_signature='x' )
    def Seek(self, Offset):
        self.spotify_iface.Seek(Offset)

    @dbus.service.method(MEDIAPLAYER2_PLAYER, in_signature='ox')
    def SetPosition(self, trackid, position):
        self.spotify_iface.SetPosition(trackid, position)

    @dbus.service.method(MEDIAPLAYER2_PLAYER, in_signature='s')
    def OpenUri(self, Uri):
        self.spotify_iterface.OpenUri(Uri)

    #Signals

    @dbus.service.method(MEDIAPLAYER2_PLAYER, in_signature='x')
    def Seeked(self, Position):
        pass

    ### media player interface

    @dbus.service.method(MEDIAPLAYER2)
    def Raise(self):
        pass

    @dbus.service.method(MEDIAPLAYER2)
    def Quit(self):
        pass

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        return self.state[interface_name]
	
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        return self.state[interface_name][property_name]

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface_name, property_name, new_value):
        self.PropertiesChanged(interface_name, { property_name: new_value }, [])
     
    def handler(self, interface_name, changed_properties, invalidated_properties):
        self.PropertiesChanged(interface_name, changed_properties, invalidated_properties)
   
    @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        pass

DBusQtMainLoop(set_as_default = True)
app = QCoreApplication([])
signal.signal(signal.SIGINT, signal.SIG_DFL)
calc = SpotifyProxy() 
sys.exit(app.exec_())
