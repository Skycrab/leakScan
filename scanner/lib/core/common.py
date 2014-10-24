#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import os
import shutil
from urlparse import urlsplit, urlunsplit, urljoin as _urljoin
from posixpath import normpath
from datetime import datetime

from lib.core.log import ERROR, DEBUG, INFO
from lib.core.data import paths, conf
from lib.core.settings import IGNORE_DEFAULT_FILE_SUFFIX
from lib.util import db


def urljoin(base, url, allow_fragments=True):
    """
    >>>urljoin("http://www.baidu.com","../../../dd")
    'http://www.baidu.com/dd'
    >>>urljoin("http://www.baidu.com","/dd/./././")
    'http://www.baidu.com/dd
    """
    _ = _urljoin(base, url, allow_fragments=True)
    p = urlsplit(_)
    path = p.path + '/' if p.path.endswith('/') else p.path
    return urlunsplit((p.scheme,p.netloc,normpath(p.path),p.query,p.fragment))


def banner():
    pass

def showpaths():
    """
    print paths for convenient debugging
    """
    print paths

def mkdir(path,remove=True):
    if os.path.isdir(path):
        if remove:
            try:
                shutil.rmtree(path)
                os.mkdir(path)
            except Exception:
                ERROR("rmtree except,path"+path)
    else:
        os.mkdir(path)

def discard(url):
    index = url.rfind('.')
    if index != -1 and url[index+1:] in IGNORE_DEFAULT_FILE_SUFFIX:
        return True
    return False


def set_unreachable_flag(task_id):
    sql = "UPDATE task SET `reachable`=0 WHERE id=%s" % task_id
    try:
        db.execute(sql)
    except Exception:
        ERROR('set_unreachable failed,task_id:%s,please check' % task_id)

def update_task_status(task_id):
    sql = "UPDATE task SET `status`=3 WHERE id=%s" % task_id
    try:
        db.execute(sql)
    except Exception:
        ERROR('update_task_status failed,task_id:%s,please check' % task_id)

def update_end_time(task_id):
    sql = "UPDATE task SET `end_time`=%s WHERE id=%s"
    try: 
        db.execute(sql, datetime.now(), task_id)
    except Exception:
        ERROR('update_end_time failed,task_id:%s,please check' % task_id)


def task_finsh_clean(task_id=None):
    if task_id is None:
        task_id = conf.taskid

    update_task_status(task_id)
    update_end_time(task_id)



    