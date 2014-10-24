#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import os
import copy
import hashlib
from cStringIO import StringIO
from mimetools import Message

from thirdparty import requests
from thirdparty.requests.models import Response
from thirdparty.requests.utils import get_encoding_from_headers

from lib.core.log import ERROR, DEBUG, INFO
from lib.core.data import conf, paths, DEFAULT_METHOD

from lib.core.settings import DEFAULT_PAGE_ENCODING, HEADER_BODY_BOUNDRY

HEADERS = {
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0'
}


def cacheFileName(url,method,kw):
    _ = '*'.join((url,method,str(kw)))
    return os.path.join(conf.requestCache,hashlib.md5(_).hexdigest())


class FileResponse(object):
    def __init__(self,filename,url,method,**kwargs):
        self.filename = filename
        self.url = url
        self.method = method
        self.kwargs = kwargs

    def load(self):
        buff = None
        with open(self.filename,'r') as f:
            buff = StringIO(f.read())
        if not buff:
            return None
        version, status, reason = buff.readline().split(' ',2)
        headers = Message(buff).dict

        response = Response()

        response.status_code = int(status)

        response.headers = headers
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = buff
        response.reason = reason

        if isinstance(self.url, str):
            response.url = self.url.decode('utf-8')
        else:
            response.url = self.url

        return response

        
    def store(self,response):
        r = response
        def headers():
            statusLine = "%s %s %s" % ("HTTP/1.1",r.status_code,r.reason)
            headers = ["%s: %s" %(k,v) for k,v in r.headers.iteritems()]
            return '\n'.join((statusLine,'\n'.join(headers)))
        buff = '\n'.join((headers(),HEADER_BODY_BOUNDRY,r.content))
        #del r
        with open(self.filename,'w') as f:
            f.write(buff)
        
def request(url,**kwargs):
    """
    quick start: 
        http://blog.csdn.net/iloveyin/article/details/21444613
        http://www.zhidaow.com/post/python-requests-install-and-brief-introduction
    :param method: method for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) Float describing the timeout of the request in seconds.
    :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param encode: (optional),if none,return unicode,else return encode str
    """

    def checkCharset(response):
        if response.encoding == "ISO-8859-1":#requests default header encoding
            encoding = requests.utils.get_encodings_from_content(response.content)
            if encoding:
                response.encoding = encoding[0]
        return response

    kwargs.setdefault('headers',{})
    kwargs.setdefault('timeout',conf.timeout)
    method = kwargs.pop('method') if kwargs.has_key('method') else DEFAULT_METHOD
    decode = kwargs.pop('decode') if kwargs.has_key('decode') else None
    if conf.cookie:
        kwargs.setdefault('cookies',conf.cookie)
    if method.upper() in ("GET","POST","options"):
        kwargs.setdefault('allow_redirects', True)
    else:
        kwargs.setdefault('allow_redirects', False)

    # key = cacheFileName(url,method,kwargs)
    # exist = os.path.isfile(key)
    # try:
    #     if exist:
    #         DEBUG("%s in cache" % url)
    #         res = FileResponse(key,url,method,**kwargs).load()
    #         if res:
    #             return checkCharset(res)
    # except IOError,e:
    #     ERROR("cache file read exception,url:%s,method:%s,kwargs:%s" %(url,method,str(kwargs)))

    h = [ k.title() for k in kwargs['headers'].iterkeys() ]
    kwargs['headers'].update(dict( [ (k,v) for k,v in HEADERS.iteritems() if k not in h ] ))
    try:
        response = requests.request(method,url,**kwargs)
        # try:
        #     FileResponse(key,url,method,**kwargs).store(response)
        # except IOError,e:
        #     ERROR("cache file write exception,url:%s,method:%s,kwargs:%s" %(url,method,str(kwargs)))
        response = checkCharset(response)
        if decode:
            _ = response.text
            assert isinstance(_, unicode)
            try:
                _e = _.encode(decode)
            except UnicodeEncodeError:
                ERROR("encodePage error,charset:%s,url:%s" %(response.encoding,url))
                _e = _.encode(decode,'replace')
            response.text_encoded = _e
        return response
    except Exception,e:
        ERROR("request exception,url:"+url)


def requestUrl(req,payload=None,**kwargs):
    kwargs.setdefault('method',req.method)
    p = req.params if payload is None else payload
    if req.method == DEFAULT_METHOD:
        kwargs.setdefault('params',p)
    else:
        kwargs.setdefault('data',p)
    return request(req.url,**kwargs)
  