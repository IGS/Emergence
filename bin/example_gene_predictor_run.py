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
from emergence.apps.biotools.models import Tool
from emergence.apps.flow.models import Flow, Command

example_dir = os.path.join(bin_dir, '..', 'emergence', 'data', 'examples')
SAMPLE_GENOME = os.path.join(example_dir, 'Escherichia_coli_K12_DH10B genome', \
                             'e_coli_k12_dh10b.fna')




def main():
    genome_file = LocalFile( label = 'E. coli K12 DH10B genome', \
                             path  = SAMPLE_GENOME )
    genome_file.save()

    prodigal = Tool.objects.get( name='Prodigal' )
    print("Prodigal's path is: {0}".format(prodigal.exec_path) )

    f = Flow( type='s', name='Prodigal test flow' )
    f.save()
    c = Command( parent=f, name='Prodigal', exec_string=prodigal.exec_path )
    c.save()
    
    #parent_flow = Flow.objects.get( name='Prodigal test flow' )
    #parent_flow.run()
    f.run()
    





if __name__ == '__main__':
    main()
