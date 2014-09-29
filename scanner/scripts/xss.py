#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import re
import string
import random

from lib.core.data import PARAMS_PATTERN, Result, TITLE_PATTERN, GET, POST
from lib.core.requests import requestUrl
from lib.core.log import ERROR, DEBUG, INFO


SMALLER_CHAR_POOL    = ('<', '>')                               # characters used for XSS tampering of parameter values (smaller set - for avoiding possible SQLi errors)
LARGER_CHAR_POOL     = ('\'', '"', '>', '<')                    # characters used for XSS tampering of parameter values (larger set)
PREFIX_SUFFIX_LENGTH = 5                                        # length of random prefix/suffix used in XSS tampering
CONTEXT_DISPLAY_OFFSET = 10                                     # offset outside the affected context for displaying in vulnerability report
REGEX_SPECIAL_CHARS = ('\\', '*', '.', '+', '[', ']', ')', '(') # characters reserved for regular expressions

XSS_PATTERNS = (                                                # each (pattern) item consists of ((context regex), (prerequisite unfiltered characters), "info text")
    (r'\A[^<>]*%(chars)s[^<>]*\Z', ('<', '>'), "\"...\", pure text response, %(filtering)s filtering"),
    (r"<script[^>]*>(?!.*<script).*'[^>']*%(chars)s[^>']*'.*</script>", ('\''), "\"<script>.'...'.</script>\", enclosed by script tags, inside single-quotes, %(filtering)s filtering"),
    (r'<script[^>]*>(?!.*<script).*"[^>"]*%(chars)s[^>"]*".*</script>', ('"'), "'<script>.\"...\".</script>', enclosed by script tags, inside double-quotes, %(filtering)s filtering"),
    (r'<script[^>]*>(?!.*<script).*?%(chars)s.*?</script>', (), "\"<script>...</script>\", enclosed by script tags, %s"),
    (r'>[^<]*%(chars)s[^<]*(<|\Z)', ('<', '>'), "\">...<\", outside tags, %(filtering)s filtering"),
    (r"<[^>]*'[^>']*%(chars)s[^>']*'[^>]*>", ('\'',), "\"<.'...'.>\", inside tag, inside single-quotes, %(filtering)s filtering"),
    (r'<[^>]*"[^>"]*%(chars)s[^>"]*"[^>]*>', ('"',), "'<.\"...\".>', inside tag, inside double-quotes, %(filtering)s filtering"),
    (r'<[^>]*%(chars)s[^>]*>', (), "\"<...>\", inside tag, %(filtering)s filtering")
)


def run_url(req, rule):
    def _contains(content, chars):
        content = re.sub(r"\\[%s]" % "".join(chars), "", content, re.S) if chars else content
        return all(char in content for char in chars)

    details = []
    response = None
    params = req.params
    for match in PARAMS_PATTERN.finditer(params):
        found = False
        prefix, suffix = ["".join(random.sample(string.ascii_lowercase, PREFIX_SUFFIX_LENGTH)) for i in xrange(2)]
        for pool in (LARGER_CHAR_POOL, SMALLER_CHAR_POOL):
            if not found:
                tampered = params.replace(match.group('value'), "%s%s%s%s" % (match.group('value'), prefix, "".join(random.sample(pool, len(pool))), suffix))
                res = requestUrl(req,tampered)
                if not res:
                    continue
                content = res.text
                for sample in re.finditer("%s(.+?)%s" % (prefix, suffix), content, re.I|re.S):
                    for regex, condition, info in XSS_PATTERNS:
                        context = re.search(regex % dict((("chars",reduce(lambda filtered, char: filtered.replace(char, "\\%s" % char), REGEX_SPECIAL_CHARS, sample.group(0))),)), content, re.I|re.S)
                        if context and not found and sample.group(1).strip():
                            #print sample.group(1),condition
                            if _contains(sample.group(1), condition):
                                msg = info % dict((("filtering", "no" if all(char in sample.group(1) for char in LARGER_CHAR_POOL) else "some"),))
                                DEBUG(msg)
                                found = True
                                if response is None:
                                    response = res
                                details.append(u"漏洞参数：%s" % match.group('key'))
                                break
                #end for
        #end for
    #end for
    if response is not None:
        return Result(response,details)

       



