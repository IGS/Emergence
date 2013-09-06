#!/usr/bin/env python3

"""
This is an example script that uses the Emergence API to do a series of events, listed below,
whose purpose is to both show the execution of a series of tools which weren't pre-built in
a flow as well as illustrate the tool discovery process and how it shows different analyses
available depending on the data types you have.

1. Upload a directional FASTQ read files (left and right)
2. Query available analyses
3. Run Trinity's read normalization
4. Upload a reference genome
5. Re-query available analyses

Note:  This also uses the 'workspaces' portion of the API to save all input, output and flows
into a named, retrievable workspace.

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
from emergence.apps.workspace.models import Workspace

example_dir = os.path.join(bin_dir, '..', 'emergence', 'data', 'examples')

SAMPLE_LEFT_READS  = os.path.join(example_dir, 'fastq_samples', 'trinity.reads.left.fq.gz')
SAMPLE_RIGHT_READS = os.path.join(example_dir, 'fastq_samples', 'trinity.reads.right.fq.gz')
SAMPLE_GENOME      = os.path.join(example_dir, 'Escherichia_coli_K12_DH10B', 'e_coli_k12_dh10b.fna')


def main():

    workspace = Workspace( name = 'Example tool discovery and diginorm' )
    workspace.save()

    left_reads  = LocalFile( label = 'Left sample reads',  path = SAMPLE_LEFT_READS )
    left_reads.save()
    
    right_reads = LocalFile( label = 'Right sample reads', path = SAMPLE_RIGHT_READS )
    right_reads.save()

    #workspace.add( left_reads, right_reads )
    workspace.add_data( left_reads )
    workspace.add_data( right_reads )

    tools_available = workspace.get_available_tools()

    for tool in tools_available:
        print("{0}".format(tool))



    
    #genome_file = LocalFile( label = 'E. coli K12 DH10B genome', \
    #                         path  = SAMPLE_GENOME )
    #genome_file.save()

    ## This gives a reference to the tool (which you probably don't want to modify.)
    #prodigal = StandaloneTool.objects.get( name='Prodigal', version='2.60' )

    ## this should actually instantiate the entire flow and children, with blueprints
    #   never being seen by the user.
    ## All commands and subflows are instantiated and saved to the database, and the
    #  parent flow is returned.  This will almost never pass an is_ready() check since
    #  no required parameters have been set yet.
    #flow = prodigal.new_flow()

    #command = flow.get_command(name='Run prodigal')
    #command.set_param(name='-i', val=genome_file.path)
    #command.set_param(name='-o', val='/tmp/prodigal.test.out' )
    #command.set_param(name='-g', val='10' )

    #flow.run()
    





if __name__ == '__main__':
    main()
