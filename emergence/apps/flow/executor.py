from __future__ import absolute_import

"""
Note to prevent you from shoving your laptop across the table in frustration:  If you
change this in any way, you have to restart your Celery worker  - Jorvis
"""

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

    # subprocess waits for the call to end
    returncode = subprocess.call(cmd.exec_string, shell=True)

    if returncode == 0:
        cmd.state = 'c'
    else:
        cmd.state = 'f'

    cmd.save()
        
    ## phone home to the parent flow that the task is finished
    if cmd.parent is not None:
        cmd.parent.flow.check_child_states()



#@celery.task
#def mul(x, y):
#    return x * y


#@celery.task
#def xsum(numbers):
#    return sum(numbers)
