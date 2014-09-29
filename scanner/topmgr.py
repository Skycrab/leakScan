#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import os
import sys
import time
import json
import hmac
import traceback
import logging
import inspect
from mimetools import Message

import win32serviceutil
import win32service
import win32event

import gevent
from gevent.server import StreamServer
from gevent.subprocess import Popen, call

HOST = '0.0.0.0'
PORT = 6667

CFN = inspect.getfile(inspect.currentframe())
CWD = os.path.abspath(os.path.dirname(CFN))

FORMATTER = logging.Formatter("\r[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
LOGNAME = os.path.join(CWD, 'topmgr.log')
LOGGER = logging.getLogger("TopMgr")
FILE_HANDLER = logging.FileHandler(LOGNAME)
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.DEBUG)

def _error(msg):
    if any(sys.exc_info()):
        LOGGER.error("\n".join((msg,traceback.format_exc())))
        sys.exc_clear()
    else:
        LOGGER.error(msg)

ERROR = _error
DEBUG = LOGGER.debug
INFO = LOGGER.info
WARN = LOGGER.warn


class TopMgrService(win32serviceutil.ServiceFramework): 
    """
    Usage: 'python topmgr.py install|remove|start|stop|restart'
    """
    #服务名
    _svc_name_ = "TopMgr"
    #服务显示名称
    _svc_display_name_ = "TopScanner Daemon Mgr"
    #服务描述
    _svc_description_ = "TopScanner Daemon Mgr"

    def __init__(self, args): 
        win32serviceutil.ServiceFramework.__init__(self, args) 
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        INFO("mgr startting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.start()
        # 等待服务被停止
        INFO("mgr waitting...")
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        INFO("mgr end")
        
    def SvcStop(self): 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        INFO("mgr stopping...")
        self.stop()
        INFO("mgr stopped")
        # 设置事件
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self): pass

    def stop(self): pass


MODULES = {           # module: handle module class
}

def module_register(module_name, handle_class):
    if module_name in MODULES:
        WARN('duplicate module_name:' + module_name)
    else:
        MODULES[module_name] = handle_class

#class TopEngine(object):
class TopEngine(TopMgrService):
    rbufsize = -1
    wbufsize = 0

    def start(self):
        INFO('wait connection')
        self.server = StreamServer((HOST, PORT), self.msg_handle)
        self.server.serve_forever()

    def msg_handle(self,socket,address):
        try:
            rfile = socket.makefile('rb', self.rbufsize)
            wfile = socket.makefile('wb', self.wbufsize)
            headers = Message(rfile).dict

            INFO('get a connection from:%s,headers:%s' % (str(address), headers))

            if 'module' in headers and headers['module'] in MODULES:
                MODULES[headers['module']].handle(wfile, headers)
        except Exception:
            ERROR('msg_handle exception,please check')

    def stop(self):
        if hasattr(self, server):
            self.server.stop()


class Module(object):
    SECRE_KEY = "_TOP-SEC_**_BEIJING-ANFU_"
    MODULE_NAME = "BASE_MODULE"
    PREFIX = "do_"  # method prefix

    def __init__(self, wfile, headers):
        self.wfile = wfile
        self.headers = headers

    def __getattr__(self, name):
        try:
            return self.headers[name]
        except Exception:
            ERROR("%s has no attr:%s,please check" %(self.MODULE_NAME, name))            

    @classmethod
    def handle(cls, wfile, headers):
        module_obj = cls(wfile, headers)
        module_obj.schedule_default()

    def verify(self):
        if hmac.new(self.SECRE_KEY, self.MODULE_NAME).hexdigest() == self.signature:
            return True
        else:
            WARN("client verify failed,signature:%s" % str(self.signature))

    def schedule_default(self):
        err_code = 0
        if self.verify() and self.action:
            func_name = self.PREFIX + self.action
            try:
                getattr(self, func_name)()
            except AttributeError:
                err_code = 1
                ERROR("%s has no method:%s" %(self.MODULE_NAME, name))
            except Exception:
                err_code = 2
                ERROR("module:%s,method:%s,exception" % (self.MODULE_NAME, func_name))              
        else:
            err_code = 3

        if err_code:
            self.send_error({'err_code':err_code})

    def send_success(self, msg=''):
        data = {'success':True,'msg':msg}
        self.wfile.write(json.dumps(data))

    def send_error(self, msg=''):
        data = {'success':False,'msg':msg}
        self.wfile.write(json.dumps(data))


TASK = {}  # task_id: pid
class ScanModule(Module):
    MODULE_NAME = "SCAN_MODULE"

    def do_start(self, cmd=None):
        self.send_success('start ok')
        DEBUG('------------task start------------')
        task_ids = [int(task_id) for task_id in self.task_ids.split(',') if int(task_id) not in TASK]

        for task_id in task_ids:
            try:
                if cmd is None:
                    cmd = 'python topscan.py -t %s' % task_id
                else:
                    cmd = 'python topscan.py -t %s %s' %(task_id, cmd)
                self.sub = Popen(cmd, shell=True, cwd=CWD)
                pid = int(self.sub.pid)
                TASK[task_id] = pid
                INFO('%s start a new task,task_id:%s,pid:%s' %(self.MODULE_NAME, task_id, pid))
            except Exception:
                ERROR('%s start a new task,task_id:%s failed' % (self.MODULE_NAME, task_id))

    def do_continue_start(self):
        self.do_start("--continue")

    def do_stop(self):
        self.send_success('stop ok')
        DEBUG('------------task stop------------')
        task_ids = [int(task_id) for task_id in self.task_ids.split(',') if int(task_id) in TASK]

        for task_id in task_ids:
            pid = TASK.pop(task_id)
            try:
                INFO('%s stop a new task,task_id:%s,pid:%s' %(self.MODULE_NAME, task_id, pid))
                call(['taskkill', '/F', '/T', '/PID', str(pid)])
            except Exception:
                ERROR('%s taskkill a task failed,task_id:%s,pid:%s' %(self.MODULE_NAME, task_id, pid))


module_register(ScanModule.MODULE_NAME, ScanModule)


def test():
    print 'test'
    t = TopEngine()
    t.start()
        
if __name__=='__main__':
    win32serviceutil.HandleCommandLine(TopEngine)
