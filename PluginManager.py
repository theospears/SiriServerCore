from plugin import Plugin, __criteria_key__, NecessaryModuleNotFound, \
    ApiKeyNotFoundException
from types import FunctionType
import logging
import os
import re
import languageutils



logger = logging.getLogger("logger")
pluginPath = "plugins"

__config_file__ = "plugins.conf"
__apikeys_file__ = "apiKeys.conf"



plugins = list()
prioritizedPlugins = dict()
apiKeys = dict()

def load_plugins():
    with open(__config_file__, "r") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            # just load the whole shit...
            try:
                __import__(pluginPath+"."+line,  globals(), locals(), [], -1)
            except NecessaryModuleNotFound as e:
                logger.critical("Failed loading plugin due to missing module: "+str(e))
            except ApiKeyNotFoundException as e:
                logger.critical("Failed loading plugin due to missing API key: "+str(e))
            except:
                logger.exception("Plugin loading failed")
            
    # as they are loaded in the order in the file we will have the same order in __subclasses__()... I hope

    for clazz in Plugin.__subclasses__():
        plugin_actions = dict()
        # look at all functions of a class lets filter them first
        methods = filter(lambda x: type(x) == FunctionType, clazz.__dict__.values())
        # now we check if the method is decorated by register
        for method in methods:
            if __criteria_key__ in method.__dict__:
                criterias = method.__dict__[__criteria_key__]
                for lang, regex in criterias.items():
                    if not lang in plugin_actions:
                        plugin_actions[lang] = []
                    # yeah... save the regex, the clazz and the method, shit just got loaded...
                    plugin_actions[lang].append((regex, method))
        plugins.append((clazz, plugin_actions))


def reload_api_keys():
    global apiKeys
    apiKeys = dict()
    load_api_keys()

def load_api_keys():
    with open(__apikeys_file__, "r") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            kv = line.split("=", 1)
            try:
                apiName = str.lower(kv[0]).strip()
                kv[1] = kv[1].strip()
                apiKey = kv[1][1:-1] #stip the ""
                apiKeys[apiName] = apiKey
            except:
                logger.critical("There was an error parsing an API in the line: "+ line)

def getAPIKeyForAPI(APIname):
    apiName = str.lower(APIname) 
    if apiName in apiKeys:
        return apiKeys[apiName]
    return None

def getPlugin(speech, languages):
    for (clazz, plugin_actions) in plugins:
        for language in languages:
            if language in plugin_actions:
                for (regex, method) in plugin_actions[language]:
                    match = regex.match(speech)
                    if match != None:
                        return (clazz, method, match)
    return (None, None, None)

def clearPriorityFor(assistantId):
    if assistantId in prioritizedPlugins:
        del prioritizedPlugins[assistantId]

def prioritizePluginObject(pluginObj, assistantId):
    clearPriorityFor(assistantId)
    for (clazz, plugin_actions) in plugins:
      if pluginObj.__class__ == clazz:
        prioritizedPlugins[assistantId] = (pluginObj, plugin_actions)
        break

def searchPrioritizedPlugin(assistantId, speech, languages):
    if assistantId in prioritizedPlugins:
        (pluginObj, plugin_actions) = prioritizedPlugins[assistantId]
        for language in languages:
            if language in plugin_actions:
                for (regex, method) in plugin_actions[language]:
                    match = regex.match(speech)
                    if match != None:
                        return (pluginObj, method, match)
    return (None, None, None)

def getPluginForImmediateExecution(assistantId, speech, language, otherPluginParams):
    (sendObj, sendPlist, assistant, location) = otherPluginParams
    languages = languageutils.getCompatibleCodes(language)

    (pluginObj, method, match) = searchPrioritizedPlugin(assistantId, speech, languages)
    if pluginObj == None and method == None:
        (clazz, method, match) = getPlugin(speech, languages)
        if clazz != None and method != None:
            logger.debug("Instantiating plugin and method: {0}.{1}".format(clazz.__name__, method.__name__))
            pluginObj = clazz()
            pluginObj.initialize(method, speech, language, sendObj, sendPlist, assistant, location, match)
            #prioritizePluginObject(pluginObj, assistantId)
    else:
        #reinitialize it
        logger.info("Found a matching prioritized plugin")
        pluginObj.initialize(method, speech, language, sendObj, sendPlist, assistant, location, match)
    
    return pluginObj
        



