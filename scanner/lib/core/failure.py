#!/usr/bin/env python
#-*-encoding:UTF-8-*-

class TopException(Exception):
    pass

class DestinationUnReachable(TopException):
    def __init__(self,dest):
        self.args = dest
        self.dest = dest





