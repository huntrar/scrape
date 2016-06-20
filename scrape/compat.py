"""Functions for Python 2 and 3 compatibility"""

from . import SYS_VERSION


if SYS_VERSION == 2:
    def iteritems(dct):
        """Python 2 dictionary iteritems()"""
        return dct.iteritems()

    def iterkeys(dct):
        """Python 2 dictionary iterkeys()"""
        return dct.iterkeys()

    def itervalues(dct):
        """Python 2 dictionary itervalues()"""
        return dct.itervalues()

    def uni(word):
        """Python 2 utf-8 encode"""
        return word.encode('utf-8')

    def asc(word):
        """Python 2 ascii-ignore encode"""
        return word.encode('ascii', 'ignore')
else:
    def iteritems(dct):
        """Python 3 dictionary iteritems()"""
        return iter(dct.items())

    def iterkeys(dct):
        """Python 3 dictionary iterkeys()"""
        return iter(dct.keys())

    def itervalues(dct):
        """Python 3 dictionary itervalues()"""
        return iter(dct.values())

    def uni(word):
        """Python 3 utf-8 encode"""
        return word

    def asc(word):
        """Python 3 ascii-ignore encode"""
        return word
