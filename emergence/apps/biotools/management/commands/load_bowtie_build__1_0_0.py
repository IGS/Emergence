
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_bowtie_build__1_0_0
#


import configparser
import os
from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam, FlowBlueprint

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Bowtie-build 1.0.0'

    def handle(self, *args, **options):
        tool_name = 'Bowtie-build'
        tool_version = '1.0.0'
        
        if self.already_exists(tool_name, tool_version):
            print("INFO: tool {0} {1} already exists.  Skipping.".format(tool_name, tool_version) )
            return True

        settings = configparser.ConfigParser()
        settings.read( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../../settings.ini') )

        tool_settings = settings[ "{0} {1}".format('Bowtie', tool_version) ]

        flow_bp = FlowBlueprint( type='s', \
                                 description='Bowtie is an ultrafast, memory-efficient short read aligner. It aligns short DNA sequences (reads) to the human genome at a rate of over 25 million 35-bp reads per hour. Bowtie indexes the genome with a Burrows-Wheeler index to keep its memory footprint small: typically about 2.2 GB for the human genome (2.9 GB for paired-end).')
        flow_bp.save()

        tool = StandaloneTool( name=tool_name, \
                               version=tool_version, \
                               primary_site='http://bowtie-bio.sourceforge.net/index.shtml', \
                               flow_bp=flow_bp )
        tool.save()

        command_bp = CommandBlueprint( parent = flow_bp, \
                                       name = 'Build an index for bowtie', \
                                       exec_path = tool_settings['bowtie_build_bin'] )
        command_bp.save()


        # bowtie-build [options]* <reference_in> <ebwt_outfile_base>

        CommandBlueprintParam( command=command_bp, name='-C', prefix='-C ', has_no_value=True, position=1, \
            short_desc='Build a colorspace index' ).save()
        
        CommandBlueprintParam( command=command_bp, name='-a', prefix='-a ', has_no_value=True, position=2, \
            short_desc='Disable automatic -p/--bmax/--dcv memory-fitting' ).save()

        CommandBlueprintParam( command=command_bp, name='-p', prefix='-p ', has_no_value=True, position=3, \
            short_desc='Use packed strings internally; slower, uses less mem' ).save()

        CommandBlueprintParam( command=command_bp, name='-B', prefix='-B ', has_no_value=True, position=4, \
            short_desc='Build both letter- and colorspace indexes' ).save()
        
        CommandBlueprintParam( command=command_bp, name='--bmax', prefix='--bmax ', position=5, \
            short_desc='Max bucket sz for blockwise suffix-array builder' ).save()

        CommandBlueprintParam( command=command_bp, name='--bmaxdivn', prefix='--bmaxdivn ', position=6, default_value='4', \
            short_desc='Max bucket sz as divisor of ref len' ).save()

        CommandBlueprintParam( command=command_bp, name='--dcv', prefix='--dcv ', position=7, default_value='1024', \
            short_desc='Diff-cover period for blockwise' ).save()

        CommandBlueprintParam( command=command_bp, name='--nodc', prefix='--nodc ', has_no_value=True, position=8, \
            short_desc='Disable diff-cover (algorithm becomes quadratic)' ).save()

        CommandBlueprintParam( command=command_bp, name='-r', prefix='-r ', has_no_value=True, position=9, \
            short_desc='Do not build .3/.4.ebwt (packed reference) portion' ).save()
        
        CommandBlueprintParam( command=command_bp, name='-3', prefix='-3 ', has_no_value=True, position=10, \
            short_desc='Just build .3/.4.ebwt (packed reference) portion' ).save()

        CommandBlueprintParam( command=command_bp, name='-o', prefix='-o ', position=11, default_value='5', \
            short_desc='SA is sampled every 2^offRate BWT chars' ).save()

        CommandBlueprintParam( command=command_bp, name='-t', prefix='-t ', position=12, default_value='10', \
            short_desc='# of chars consumed in initial lookup' ).save()

        CommandBlueprintParam( command=command_bp, name='--ntoa', prefix='--ntoa ', has_no_value=True, position=13, \
            short_desc='Convert Ns in reference to As' ).save()

        CommandBlueprintParam( command=command_bp, name='--seed', prefix='--seed ', position=14, \
            short_desc='Seed for random number generator' ).save()

        CommandBlueprintParam( command=command_bp, name='<reference_in>', prefix=None, position=15, is_optional=False, \
            short_desc='Input reference FASTA file' ).save()

        CommandBlueprintParam( command=command_bp, name='<ebwt_outfile_base>', prefix=None, position=16, is_optional=False, \
            short_desc='Path to the basename of the ebwt files to be created' ).save()

        tool.needs( filetype_name='FASTA (nucleotide)', via_command=command_bp, via_param='<reference_in>' )
        tool.creates( filetype_name='Bowtie 1.0 index', via_command=command_bp, via_param='<ebwt_outfile_base>' )
        

    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

