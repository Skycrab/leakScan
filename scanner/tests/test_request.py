#!/usr/bin/env python
#-*-encoding:UTF-8-*-

from lib.core.request import request
import unittest
from test import test_support

class RequestTest(unittest.TestCase):
    def test_basic(self):
        r = request("http://www.baidu.com/")
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.encoding,'utf-8')
        r = request("http://www.baidu.com/12")
        self.assertEqual(r.encoding,'gbk')

    def test_follow_redirect(self):
        r = request("http://www.sina.com/",allow_redirects=False)
        self.assertEqual(r.status_code,301)
        r = request("http://www.sina.com/")
        self.assertEqual(r.status_code,200)

    def test_unicode(self):
        r = request("http://www.baidu.com/")
        self.assertEqual(isinstance(r.text,unicode),True)
        self.assertEqual(r.text.find(u"百度")>0,True)
        r = request("http://www.baidu.com/12")
        self.assertEqual(r.text.find(u"访问出错")>0,True)


def test_main():
    test_support.run_unittest(RequestTest)

test_main()