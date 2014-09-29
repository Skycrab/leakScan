#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import os
import re
from lib.core.data import Result, SITETYPES
from lib.core.requests import request
from lib.core.data import paths, conf
from lib.core.settings import WEBSHELL_DIC_NAME

WEBSHELL_FEATURE = {
    'PHP':
    {
        '404.php':("<title>404 Not Found</title>", "<input type=password"),
        '2011.php':("input {font:11px Verdana;BACKGROUND: #FFFFFF;height: 18px",
                 '<span style="font:11px Verdana;">Password'),
        'Ani-Shell.php':('<body text="rgb(39,245,10)" bgcolor="black">',"--Ani Shell-")

    },
    'JSP':
    {

    },
    'ASP':
    {

    },
    'ASP.NET':
    {

    }
}


_INPUT_TYPE = re.compile(r"<input[^</>]+?(>|/>)",re.I|re.M)
_IP_PATTERN = re.compile(r"\D(\d{1,3}(?:.\d{1,3}){3})\D")
_INPUT_NAMR = re.compile(r"<input[^</>]+?name\s*=\s*[\'\"\w]",re.I)
_DIR_PATH = re.compile(r"[CDEFG]:|/\w",re.I)

def run_url(req, rule):
    print '**********webshell*******'
    print rule.site_type
    if req.params != '' or not req.url.endswith('/'):
        return None

    suffix = SITETYPES[rule.site_type] if rule.site_type is not None else None
    sure = []
    doubt = []
    response = None
    for line in open(os.path.join(paths.DIC, WEBSHELL_DIC_NAME)):
        line = line.strip() # remove \n
        if suffix is None:
            urls = ["%s%s" % (line, t) for t in SITETYPES.itervalues()]
        else:
            urls = ["%s%s" % (line, suffix)]

        for u in urls:
            url = "%s%s" %(req.url, u)
            print url
            res = request(url)
            if res and res.status_code == 200:
                text = res.text
                ## feature
                if rule.site_type is not None and rule.site_type in WEBSHELL_FEATURE:
                    features = WEBSHELL_FEATURE[rule.site_type]
                    if all(text.find(key) != -1 for keys in features.itervalues() for key in keys):
                        if response is None:
                            response = res
                        sure.append(url)
                        continue


                ## one input 
                match = _INPUT_TYPE.findall(text)
                if match and len(match) == 2:
                    if response is None:
                        response = res
                    doubt.append(url)
                    continue
                
                ## match regur expression
                if (match.group(1) for match in _IP_PATTERN.finditer(text) if all(0<=int(x)<=255 for x in match.group(1).split('.'))) \
                and _INPUT_NAMR.search(text) \
                and _DIR_PATH.search(text) :
                    if response is None:
                        response = res
                    doubt.append(url)


    if response is not None:
        if sure:
            sure.insert(0,u"下列url是WebShell，请及时清理")
        if doubt:
            doubt.insert(0,u"下列url疑是为WebShell，请仔细检查!")
        return Result(response,sure+doubt)

