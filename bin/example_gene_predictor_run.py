#!/usr/bin/env python3

"""
This is an example script that uses the Emergence API to do the following:

1. Upload a genomic sample file (E. coli)
2. Configure and run Prodigal
3. Check execution status until complete
4. Download output file

Notes:
Fixtures can be dumped via: python3 manage.py dumpdata --indent=2 -e auth.permission

Author: Joshua Orvis (jorvis@gmail.com)
"""

import os
import sys

## having this means the user doesn't have to modify their ENV
bin_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append( os.path.join(bin_dir, '..') )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emergence.settings.dev")

from emergence.apps.fileserver.models import LocalFile
from emergence.apps.biotools.models import StandaloneTool
#from emergence.apps.flow.models import 

example_dir = os.path.join(bin_dir, '..', 'emergence', 'data', 'examples')
SAMPLE_GENOME = os.path.join(example_dir, 'Escherichia_coli_K12_DH10B genome', \
                             'e_coli_k12_dh10b.fna')


def main():
    genome_file = LocalFile( label = 'E. coli K12 DH10B genome', \
                             path  = SAMPLE_GENOME )
    genome_file.save()

    ## This gives a reference to the tool (which you probably don't want to modify.)
    prodigal = StandaloneTool.objects.get( name='Prodigal', version='2.60' )

    ## All the computation within this tool is represented by a Flow (like a workflow). 
    #   If you want to run/build, ask for a new one.  This will return a configurable
    #   blueprint.
    #
    #   1. Get blueprint for a new flow
    #   2. Configure flow
    #   3. Build a flow from the blueprint
    #   4. Run

#  Step           StepBlueprint
#  Command        CommandBlueprint
#                 CommandBlueprintParam
#  Flow           FlowBlueprint
  
    flow_bp = prodigal.new_flow()

    command_bp = flow_bp.get_command(name='Run prodigal')

    command_bp.set_param(name='-i', val=genome_file.path)
    command_bp.set_param(name='-o', val='/tmp/prodigal.test.out' )

    ## what saving and instantiation needs to happen here?
    #flow = flow_bp.build()
    #flow.run()
    





if __name__ == '__main__':
    main()
