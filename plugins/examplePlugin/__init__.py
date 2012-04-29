#!/usr/bin/python
# -*- coding: utf-8 -*-


from plugin import *
from siriObjects.systemObjects import ResultCallback
import uuid
import languageutils

class examplePlugin(Plugin):
    
    @register("de", ".*Sinn.*Leben.*")
    @register("en", ".*Meaning.*Life.*")
    def meaningOfLife(self, speech, language, matchedRegex):
        if languageutils.matches('de', language):
            answer = self.ask(u"Willst du das wirklich wissen?")
            self.say(u"Du hast \"{0}\" gesagt!".format(answer))
        else:
            self.say("I shouldn't tell you!")
        self.complete_request()

    @register("de", "(.*Hallo.*)|(.*Hi.*Siri.*)|(Hi)|(Hey)")
    @register("en", "(.*Hello.*)|(.*Hi.*Siri.*)|(Hi)|(Hey)")
    @register("fr", ".*(Bonjour|Coucou|Salut)( Siri)?.*")
    @register("nl", ".*(Hallo|Goeiedag|Heey)( Siri)?.*")
    def st_hello(self, speech, language):
        if languageutils.matches('de', language):
            self.say(u"Hallo {0}!".format(self.user_name()))
        elif languageutils.matches('fr', language):
            self.say(u"Bonjour {0}!".format(self.user_name()));
        elif languageutils.matches('nl', language):
            self.say(u"Hallo, {0}!".format(self.user_name()));
        else:
            self.say(u"Greetings, {0}!".format(self.user_name()))
        self.complete_request()
    
    @register("de", ".*standort.*test.*")
    @register("en", ".*location.*test.*")
    @register("nl", ".*locatie.*test.*")
    def locationTest(self, speech, language):
        location = self.getCurrentLocation(force_reload=True)
        self.say(u"lat: {0}, long: {1}".format(location.latitude, location.longitude))
        self.complete_request()
          
