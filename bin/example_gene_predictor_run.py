#!/usr/bin/env python3

"""
This is an example script that uses the Emergence API to do the following:

1. Upload a genomic sample file (E. coli)
2. Configure and run Prodigal
3. Check execution status until complete
4. Show output file path

Notes:
This test execution takes about 6 seconds locally on my laptop.

Author: Joshua Orvis (jorvis@gmail.com)
"""

import os
import sys
from time import sleep

## having this means the user doesn't have to modify their ENV
bin_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append( os.path.join(bin_dir, '..') )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emergence.settings.dev")

from emergence.apps.fileserver.models import LocalFile
from emergence.apps.biotools.models import StandaloneTool
from emergence.apps.flow.models import Flow

example_dir = os.path.join(bin_dir, '..', 'emergence', 'data', 'examples')
SAMPLE_GENOME = os.path.join(example_dir, 'Escherichia_coli_K12_DH10B', \
                             'e_coli_k12_dh10b.fna')


def main():
    genome_file = LocalFile( label = 'E. coli K12 DH10B genome', \
                             path  = SAMPLE_GENOME )
    genome_file.save()

    ## This gives a reference to the tool (which you probably don't want to modify.)
    prodigal = StandaloneTool.objects.get( name='Prodigal', version='2.60' )

    ## this should actually instantiate the entire flow and children, with blueprints
    #   never being seen by the user.
    ## All commands and subflows are instantiated and saved to the database, and the
    #  parent flow is returned.  This will almost never pass an is_ready() check since
    #  no required parameters have been set yet.
    flow = prodigal.new_flow()
    flow.save()

    command = flow.get_command(name='Run prodigal')
    command.set_param(name='-i', val=genome_file.path)
    command.set_param(name='-o', val='/tmp/prodigal.test.out' )
    command.set_param(name='-g', val='10' )

    flow.run()
    
    while flow.is_executing():
        flow = Flow.objects.get(id=flow.id)
        print("Gene prediction state is: {0}".format(flow.get_state_display()) )
        sleep(1)
        
    output = command.get_param( name='-o' )
    print("{0} completed.  Output written to: {1}".format(command.name, output.value))

    

    


if __name__ == '__main__':
    main()
