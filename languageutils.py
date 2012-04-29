import re

def getCompatibleCodes(language):
    languages = list()
    while True:
        languages.append(language)
        if '-' not in language:
            break
        language = re.sub('-[^-]*$', '', language)
    return languages

def matches(baseLanguage, specificLanguage):
    return baseLanguage in getCompatibleCodes(specificLanguage)
