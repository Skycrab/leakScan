#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import os
import sys
import urlparse
import gevent
from gevent.monkey import patch_all

from optparse import OptParseError
from optparse import OptionParser

from lib.core.data import cmdLineOptions ,conf ,paths , SITETYPES
from lib.core.settings import CONNECTION_TIMEOUT, NETWORK_TIMEOUT, TASK_TABLE
from lib.core.log import ERROR, DEBUG, INFO
from lib.core.common import mkdir, set_unreachable_flag
from lib.core.crawler import CrawlEngine
from lib.core.requests import request
from lib.core.failure import TopException, DestinationUnReachable
from lib.util import db

def get_target(task_id):
    sql = 'SELECT * FROM %s WHERE `ID`=%s' %(TASK_TABLE, task_id)
    task = db.get(sql)
    if not conf.url:
        conf.url = task.start_url
        conf.base = task.base
        conf.count = task.url_count
    conf.finished_progress = task.progress.split('|') if conf.goon else []
    conf.robots_parsed = task.robots_parsed if conf.goon else False
    conf.sitemap_parsed = task.sitemap_parsed if conf.goon else False
    conf.spider_finish = True if conf.goon and task.spider_flag == 3 else False


def _confsetting():
    conf.update(cmdLineOptions)
   
    if not conf.connect_timeout:
        conf.connect_timeout = CONNECTION_TIMEOUT
    if not conf.timeout:
        conf.timeout = NETWORK_TIMEOUT

    get_target(conf.taskid)

    parser = urlparse.urlsplit(conf.url)
    conf.host = parser.netloc
    conf.scheme = parser.scheme
    conf.domain = "%s://%s%s" % (parser.scheme, parser.netloc,conf.base)
    conf.requestCache = os.path.join(paths.TEMP,conf.host)
    conf.site_type = None
    print conf

def _geventpatch():
    """
    do monkey.patch_all carefully
    """
    patch_all(socket=True, dns=True, time=True, select=True, thread=False, os=True, ssl=True, httplib=False,
              subprocess=False, sys=False, aggressive=True, Event=False)

_dnscache = {}
def _setDnsCache():
    """
    set dns cache for socket.getaddrinfo and gevent to avoid subsequent DNS requests 
    """
    def _getaddrinfo(*args, **kwargs):
        if args in _dnscache:
            #DEBUG(str(args)+' in cache')
            return _dnscache[args]

        else:
            #DEBUG(str(args)+' not in cache')
            _dnscache[args] = gevent.socket._getaddrinfo(*args, **kwargs)
            return _dnscache[args]

    if not hasattr(gevent.socket, '_getaddrinfo'):
        gevent.socket._getaddrinfo = gevent.socket.getaddrinfo
        gevent.socket.getaddrinfo = _getaddrinfo

def _mkcachedir():
    mkdir(conf.requestCache)

def changesysEncoding(encodeing='utf-8'):
    import sys
    reload(sys)
    sys.setdefaultencoding(encodeing)

def destReachable(dest=None):
    if not dest:
        dest = conf.url

    response = request(dest,timeout=conf.connect_timeout)
    if response is None:
        set_unreachable_flag(conf.taskid)
        raise DestinationUnReachable(dest)
    else:
        conf.site_type = sitetype_check(response)

def check_type(msg):
    for k in SITETYPES.iterkeys():
        if msg.find(k) != -1:
            return k

def sitetype_check(response):
    site_type = None
    if 'x-powered-by' in response.headers:
        site_type = check_type(response.headers['x-powered-by'].upper())
    if site_type is None:
        if 'server' in response.headers:
            site_type = check_type(response.headers['server'].upper())
    return site_type
    
def init():
    _confsetting()
    _mkcachedir()
    _geventpatch()
    _setDnsCache()
    changesysEncoding()
    destReachable()

def run():
    CrawlEngine.start()


def parseCmdline():
    """
    parse command line parameters and arguments and store in cmdLineOptions
    """
    usage = "%s %s [options]" %("python",sys.argv[0])
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--task",dest="taskid",help="task id")
    parser.add_option("-u","--url",dest="url",help="target url")
    parser.add_option("-b","--base",dest="base",default="/",help="the base directory of the domain")
    parser.add_option("-d","--depth",dest="depth",type="int",default=0,help="crawl depth")
    parser.add_option("-c","--count",dest="count",type="int",default=0,help="crawl url max count")
    parser.add_option("--cookie",dest="cookie",help="http cookie header")
    parser.add_option("--connect_timeout",dest="connect_timeout",help="set connect timeout")
    parser.add_option("--timeout",dest="timeout",help="network timeout")
    parser.add_option("--continue",action="store_true",dest="goon",help="task continue run")
    try:
        args,_ = parser.parse_args(sys.argv[1:])
        cmdLineOptions.update(args.__dict__)
        print cmdLineOptions
    except OptParseError:
        print parser.error()
        

