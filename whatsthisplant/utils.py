import sys, locale, codecs

def fix_stdout_encoding():
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
