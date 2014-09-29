#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import os
import sys

from lib.core.data import paths
from lib.core.envinit import envinit
envinit(__file__)

from lib.core.log import ERROR,DEBUG,INFO,WARN
from lib.core.option import parseCmdline,init
from lib.core.failure import TopException,DestinationUnReachable
from lib.core.engine import run
from lib.core.common import task_finsh_clean

def main():
    try:
        parseCmdline()
        init()
        run()
        #user_test()
    except KeyboardInterrupt:
        INFO("User aborted,scan stop")
    except DestinationUnReachable as e:
        WARN("Destination:%s not reachable,please check" % e.dest)
    except TopException:
        ERROR("User define exception")
    except Exception as e:
        ERROR("Exception occur,scan stop")
    finally:
        task_finsh_clean()
        INFO("Scan finished!")

def test():
    sys.argv = ['python','topscan.py','-t','1','-u','http://127.0.0.1/vul/file_upload.php','-b','/vul/']
    main()

def user_test():
    from tests import test_request

if __name__ == "__main__":
    main()
    
# else:
# if 1:
#     print 'test'
#     test()