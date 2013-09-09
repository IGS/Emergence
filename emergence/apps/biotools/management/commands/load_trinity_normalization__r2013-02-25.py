
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_trinity_normalization__r2013-02-25
#


import configparser
import os
from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam, FlowBlueprint

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Trinity\'s in silico read normalization r2013-02-25'

    def handle(self, *args, **options):
        tool_name = 'Trinity in silico read normalization'
        tool_version = 'r2013-02-25'
        
        if self.already_exists(tool_name, tool_version):
            print("INFO: tool {0} {1} already exists.  Skipping.".format(tool_name, tool_version) )
            return True

        settings = configparser.ConfigParser()
        settings.read( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../../settings.ini') )

        tool_settings = settings[ "{0} {1}".format('Trinity', tool_version) ]

        flow_bp = FlowBlueprint( type='s', \
                                 description='Large RNA-Seq data sets, such as those exceeding 300M pairs, are best suited for in silico normalization prior to running Trinity, in order to reduce memory requirements and greatly improve upon runtimes. Before running the normalization, be sure that in the case of paired reads, the left read names end with suffix /1 and the right read names end with /2')
        flow_bp.save()

        tool = StandaloneTool( name=tool_name, \
                               version=tool_version, \
                               primary_site='http://trinityrnaseq.sourceforge.net/trinity_insilico_normalization.html', \
                               flow_bp=flow_bp )
        tool.save()


        command_bp = CommandBlueprint( parent = flow_bp, \
                                       name = 'Run Trinity read normalization', \
                                       exec_path = tool_settings['normalization_script'] )
        command_bp.save()


        CommandBlueprintParam( command=command_bp, name='--seqType', prefix='--seqType ', position=1, \
            is_optional=False, short_desc='Type of reads: (fa, or fq)' ).save()

        CommandBlueprintParam( command=command_bp, name='--JM', prefix='--JM ', position=2, \
            is_optional=False, short_desc='Number of GB of system memory to use for k-mer counting by jellyfish (eg. 10G).  Include the G character.' ).save()

        CommandBlueprintParam( command=command_bp, name='--left', prefix='--left ', position=3, \
            short_desc='Left reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--right', prefix='--right ', position=4, \
            short_desc='Right reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--single', prefix='--single ', position=5, \
            short_desc='Single (unpaired) reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--left_list', prefix='--left_list ', position=3, \
            short_desc='Left reads, if using a list file.  One file path per line', \
            long_desc='If you have read collections in different files you can use list files, where each line in a list file is the full path to an input file.  This saves you the time of combining them just so you can pass a single file for each direction.').save()

        CommandBlueprintParam( command=command_bp, name='--right_list', prefix='--right_list ', position=4, \
            short_desc='Right reads, if using a list file.  One file path per line', \
            long_desc='If you have read collections in different files you can use list files, where each line in a list file is the full path to an input file.  This saves you the time of combining them just so you can pass a single file for each direction.').save()

        CommandBlueprintParam( command=command_bp, name='--pairs_together', prefix='--pairs_together ', position=6, \
            has_no_value=True, short_desc='Process paired reads by averaging stats between pairs and retaining linking info' ).save()

        CommandBlueprintParam( command=command_bp, name='--SS_lib_type', prefix='--SS_lib_type ', position=7, \
            short_desc='Strand-specific RNA-Seq read orientation.  if paired: RF or FR, if single: F or R.  (dUTP method = RF)' ).save()

        CommandBlueprintParam( command=command_bp, name='--output', prefix='--output ', position=8, \
            short_desc='Name of directory for output (will be created if doesn\'t already exist.', \
            default_value='normalized_reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--JELLY_CPU', prefix='--JELLY_CPU ', position=9, \
            short_desc='Number of threads for Jellyfish to use', default_value='2' ).save()

        CommandBlueprintParam( command=command_bp, name='--PARALLEL_STATS', prefix='--PARALLEL_STATS ', position=10, \
            has_no_value=True, short_desc='Generate read stats in parallel for paired reads (Figure 2X Inchworm memory requirement)' ).save()

        CommandBlueprintParam( command=command_bp, name='--KMER_SIZE', prefix='--KMER_SIZE ', position=11, \
            short_desc='K-mer size for de Bruijn graph construction', default_value='25' ).save()

        CommandBlueprintParam( command=command_bp, name='--min_kmer_cov', prefix='--min_kmer_cov ', \
            position=12, short_desc='Minimum kmer coverage for catalog construction', default_value='1' ).save()

        CommandBlueprintParam( command=command_bp, name='--max_pct_stdev', prefix='--max_pct_stdev ', position=13, \
            short_desc='Maximum pct of mean for stdev of kmer coverage across read', default_value='100' ).save()

        # TODO: parameter grouping needs to be applied here.
        tool.can_use( filetype_name='FASTQ (Sanger, paired reads, left)', via_command=command_bp, via_param='--left' )
        tool.can_use( filetype_name='FASTQ (Sanger, paired reads, right)', via_command=command_bp, via_param='--right' )
        tool.can_use( filetype_name='FASTQ (Sanger, unpaired reads)', via_command=command_bp, via_param='--single' )

        # TODO: parameter grouping needs to be applied here.
        # TODO: needs improving.  Unfortunately, Trinity currently only supports output definition
        #  at the directory level, and the file names under that are created by convention.
        #  I've written Brian to see if I can add this
        tool.can_create( filetype_name='FASTQ (Sanger, paired reads, left)', via_command=command_bp, via_param='--output' )
        tool.can_create( filetype_name='FASTQ (Sanger, paired reads, right)', via_command=command_bp, via_param='--output' )
        tool.can_create( filetype_name='FASTQ (Sanger, unpaired reads)', via_command=command_bp, via_param='--output' )


    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

