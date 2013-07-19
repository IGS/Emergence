from __future__ import absolute_import

import os
import sys
import subprocess

## having this means the user doesn't have to modify their ENV
self_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append( os.path.join(self_dir, '../../../') )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emergence.settings.dev")

from flow.celery import celery


@celery.task
def run( cmd ):
    print("Running: {0}".format(cmd.exec_string) )

    ## LOTS more to do here.  Let's just get things running first
    #   http://sharats.me/the-ever-useful-and-neat-subprocess-module.html
    #   http://docs.python.org/3.3/library/subprocess.html
    subprocess.call(cmd.exec_string, shell=True)



#@celery.task
#def mul(x, y):
#    return x * y


#@celery.task
#def xsum(numbers):
#    return sum(numbers)
