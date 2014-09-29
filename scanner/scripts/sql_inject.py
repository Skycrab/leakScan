#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import re
import random
import difflib
import itertools

from lib.core.data import PARAMS_PATTERN, Result, TITLE_PATTERN, GET, POST
from lib.core.requests import requestUrl
from lib.core.log import ERROR, DEBUG, INFO

PREFIXES = (" ", ") ", "' ", "') ", "\"")               # prefix values used for building testing blind payloads
SUFFIXES = ("", "-- ", "#", "%%00", "%%16")             # suffix values used for building testing blind payloads
TAMPER_SQL_CHAR_POOL = ('(', ')', '\'', '"')            # characters used for SQL tampering/poisoning of parameter values
BOOLEAN_TESTS = ("AND %d=%d", "OR NOT (%d=%d)")         # boolean tests used for building testing blind payloads
RESPONSE, TEXT, HTTPCODE, TITLE, HTML = range(5)        # enumerator-like values used for marking content type
FUZZY_THRESHOLD = 0.95                                  # ratio value in range (0,1) used for distinguishing True from False responses

TEXT_PATTERN = re.compile(r"(?si)<script.+?</script>|<!--.+?-->|<style.+?</style>|<[^>]+>|\s+")

DBMS_ERRORS = {
    "MySQL": (r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"valid MySQL result", r"MySqlClient\.", r"com\.mysql\.jdbc\.exceptions"),
    "PostgreSQL": (r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"valid PostgreSQL result", r"Npgsql\.",r"org\.postgresql\.util\.PSQLException"),
    "Microsoft SQL Server": (r"Driver.* SQL[\-\_\ ]*Server", r"OLE DB.* SQL Server", r"(\W|\A)SQL Server.*Driver", r"Warning.*mssql_.*", r"(\W|\A)SQL Server.*[0-9a-fA-F]{8}", r"(?s)Exception.*\WSystem\.Data\.SqlClient\.", r"(?s)Exception.*\WRoadhouse\.Cms\."),
    "Microsoft Access": (r"Microsoft Access (\d+ )?Driver", r"JET Database Engine", r"Access Database Engine"),
    "Oracle": (r"ORA-[0-9][0-9][0-9][0-9]", r"Oracle error", r"Oracle.*Driver", r"Warning.*\Woci_.*", r"Warning.*\Wora_.*"),
    "IBM DB2": (r"CLI Driver.*DB2", r"DB2 SQL error", r"db2_\w+\("),
    "Informix": (r"Exception.*Informix",),
    "Firebird": (r"Dynamic SQL Error", r"Warning.*ibase_.*"),
    "SQLite": (r"SQLite/JDBCDriver", r"SQLite.Exception", r"System.Data.SQLite.SQLiteException", r"Warning.*sqlite_.*", r"Warning.*SQLite3::", r"\[SQLITE_ERROR\]"),
    "SAP MaxDB": (r"SQL error.*POS([0-9]+).*", r"Warning.*maxdb.*"),
    "Sybase": (r"(?i)Warning.*sybase.*", r"Sybase message", r"Sybase.*Server message.*"),
    "Ingres": (r"Warning.*ingres_", r"Ingres SQLSTATE", r"Ingres\W.*Driver"),
    "Frontbase": (r"Exception (condition )?\d+. Transaction rollback.",),
    "HSQLDB": (r"org\.hsqldb\.jdbc",)
}

def retrieve_content(req, payloads=None, **kwargs):
    retval = None
    res = requestUrl(req, payloads, **kwargs)
    if res:
        retval = {}
        retval[RESPONSE] = res
        retval[HTTPCODE] = res.status_code
        retval[HTML] = res.text
        match = TITLE_PATTERN.search(retval[HTML])
        retval[TITLE] = match.group('title') if match else None
        retval[TEXT] = TEXT_PATTERN.sub(" ", retval[HTML])
    return retval

def sql_error_check(content):
    for (dbms, regex) in ((dbms, regex) for dbms in DBMS_ERRORS for regex in DBMS_ERRORS[dbms]):
        if re.search(regex, content, re.I):
            # print '***********'
            # print regex,dbms
            # print '***************'
            return dbms

def run_url(req,rule):
    vulnerable = False
    details = []
    response = None
    params = req.params
    for match in PARAMS_PATTERN.finditer(params):
        # sql error 
        tampered = params.replace(match.group('value'), "%s%s" % (match.group('value'), "".join(random.sample(TAMPER_SQL_CHAR_POOL, len(TAMPER_SQL_CHAR_POOL)))))
        content = retrieve_content(req,tampered)
        if content is not None:
            dbms = sql_error_check(content[HTML])
            if dbms:
                details.append(u"错误模式注入，数据库类型：%s，注入参数：%s" % (dbms, match.group('key')))
                if response is None:
                    response = content[RESPONSE]
                continue

        # cookie inject 

        # referer inject

        # blind sql inject
        original = retrieve_content(req)
        if original is None:
            continue
        left, right = random.sample(xrange(256), 2)
        vulnerable = False
        for prefix, boolean, suffix in itertools.product(PREFIXES, BOOLEAN_TESTS, SUFFIXES):
            if not vulnerable:
                template = "%s%s%s" % (prefix, boolean, suffix)
                payloads = dict((x, params.replace(match.group('value'), "%s%s" % (match.group('value'), (template % (left, left if x else right))))) for x in (True, False))
                contents = dict((x, retrieve_content(req, payloads[x])) for x in (True, False))

                if any(contents[x] is None for x in (True, False)):
                    continue

                if any(original[x] == contents[True][x] != contents[False][x] for x in (HTTPCODE, TITLE)) or len(original[TEXT]) == len(contents[True][TEXT]) != len(contents[False][TEXT]):
                    vulnerable = True
                else:
                    ratios = dict((x, difflib.SequenceMatcher(None, original[TEXT], contents[x][TEXT]).quick_ratio()) for x in (True, False))
                    vulnerable = ratios[True] > FUZZY_THRESHOLD and ratios[False] < FUZZY_THRESHOLD
                if vulnerable:
                    details.append(u"盲注,注入参数：%s" % match.group('key'))
                    if response is None:
                        response = contents[False][RESPONSE]
        #end for
    #end for

    if response is not None:
        return Result(response,details)





