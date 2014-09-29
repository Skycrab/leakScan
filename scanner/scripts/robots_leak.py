#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import re
from lib.core.data import Result
from lib.core.requests import request

_ROBOTS_KEY = re.compile(r"(user-agent|disallow|allow)",re.I)
def run_domain(rule):
    url = rule.domain + "robots.txt"
    response = request(url)
    if response and response.status_code == 200 and _ROBOTS_KEY.search(response.text):
        lines = response.text.splitlines()
        details = "\r\n".join([ lines[x] for x in range(min(len(lines),10))])
        return Result(response,details)

