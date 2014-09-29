#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import re
from lib.core.data import Result
from lib.core.requests import request

_PHPMYADMIN_VERSION = re.compile(r"<h2>.*?phpMyAdmin(.+?)</h2>",re.I)
def run_domain(rule):
    admin = ('phpmyadmin','phpMyAdmin','db')
    keys = ('<form method="post" action="index.php" name="login_form" target="_top">',
            '<input type="text" name="pma_username" value="" size="24" class="textfield"')
    for p in admin: 
        response = request(rule.domain + p)
        if response and response.status_code == 200 and all((response.text.find(k)!=-1 for k in keys)):
            match = _PHPMYADMIN_VERSION.search(response.text)
            details = u"phpMyAdmin版本:" + match.group(1).strip() if match and match.group(1).strip() else ''
            return Result(response,details)

