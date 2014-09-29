#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import re

from lib.core.data import Result
from lib.core.requests import requestUrl

_INNER_IPADDR = re.compile(r"\b((?:10\.\d|172\.(1[6-9]|2\d|3[0-1])|192\.168)(?:\.\d+){2})\b")
def run_url(req,rule):
    """
    req:
        url: http://www.example.com
        method: get/post
        params: name=skycrab&age24
        referer: http://www.example.com/refer.html
    rule:
        domain: http://www.example.com/ (scheme+host+basepath)
    """
    req = requestUrl(req)
    if req:
        details = [match.group(1) for line in req.iter_lines() for match in _INNER_IPADDR.finditer(line) if all(0<=int(x)<=255 for x in match.group(1).split('.'))]
        if details:
            return Result(req, details)






    