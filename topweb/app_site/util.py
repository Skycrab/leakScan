#!/usr/bin/env python
#-*-encoding=UTF-8-*-

import hmac
import json
import urlparse

import gevent
from gevent import monkey
monkey.patch_socket()

from app_site.models import Task, Url, Result, Rule

ADDR = ('localhost', 6667)

def get_domain(task_id):
    task = Task.objects.get(id=task_id)
    _ = urlparse.urlsplit(task.start_url)
    domain = "%s://%s%s" % ( _.scheme, _.netloc, task.base)
    return domain

def json_success(msg=''):
    data = {'success':True,'msg':msg}
    return json.dumps(data)

def json_error(msg):
    data = {'success':False,'msg':msg}
    return json.dumps(data)


def enum(*sequential, **named):
    start = named.pop('start',0)
    end = len(sequential) + start
    enums = dict(zip(sequential, range(start, end)), **named)
    return type('Enum', (), enums)


SECRE_KEY = {
    "SCAN_MODULE" : "_TOP-SEC_**_BEIJING-ANFU_"
    }

def send_request(module_name,request_headers):
    try:
        key = SECRE_KEY.get(module_name,'UNKNOWN_KEY')
        socket = gevent.socket.socket()
        socket.connect(ADDR)        
        request_headers['module'] = module_name
        request_headers['signature'] = hmac.new(key, module_name).hexdigest()
        h = ["%s:%s" %(k, v) for k,v in request_headers.iteritems()]
        h.append('\n')
        request = '\n'.join(h)
        socket.send(request)
        content = socket.recv(8192)
        socket.close()
        return json.loads(content)
    except Exception:
        return {'success':False,'msg':'send_request error'}



    #send_request('SCAN_MODULE',{'action':'start','task_ids':1})