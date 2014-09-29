#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import re

from lib.core.data import Result
from lib.core.requests import requestUrl

_FILE_UPLOAD = re.compile(r"<input[^</>]+?type\s*=\s*(([\'\"])file\2|file)",re.I|re.M)
def run_url(req,rule):
    req = requestUrl(req)
    if req and _FILE_UPLOAD.search(req.text):
        #print '--------------_FILE_UPLOAD------------------'
        return Result(req,'')
