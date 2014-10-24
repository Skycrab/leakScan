#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import re
from collections import namedtuple

GET, POST   = "GET", "POST"
DEFAULT_METHOD = "GET"
PARAMS_PATTERN = re.compile(r"(?P<key>[^&=]+)(?:=(?P<value>[^&=]*))?")
TITLE_PATTERN = re.compile(r"<title>(?P<title>[^<]+)</title>", re.I)

SITETYPES = {'PHP':'.php', 'JSP':'.jsp', 'ASP.NET':'.asp', 'ASP':'.asp'}
IPADDRESS_PATTERN = re.compile(r"")


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

#store path info,e.g. "script path"
paths = ObjectDict()

#store cmdline options
cmdLineOptions = ObjectDict()

#store basic configuration,e.g. default timeout:10s
conf = ObjectDict()


class Url(object):
    def __init__(self,url,method,params,referer):
        self.url = url
        self.method = method.upper()
        self.params = params
        self.referer = referer

    @classmethod
    def fromUrl(cls,url,referer=''):
        """
        provide http://www.example.com/?q=..
        """
        url, params = url.split('?',1) if url.find('?') != -1 else (url,'')
        return cls(url,DEFAULT_METHOD,params,referer)

    @property    
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return "<%s(%s,%s,%s,%s)>" %(self.name,self.url,self.method,self.params,self.referer)
    __repr__ = __str__


Result = namedtuple('Result','response details')



