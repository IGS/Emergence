
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_trinity__r2013-02-25
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/


import configparser
import os
from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam, FlowBlueprint

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Trinity r2013-02-25'

    def handle(self, *args, **options):
        tool_name = 'Trinity'
        tool_version = 'r2013-02-25'
        
        if self.already_exists(tool_name, tool_version):
            print("INFO: tool {0} {1} already exists.  Skipping.".format(tool_name, tool_version) )
            return True

        settings = configparser.ConfigParser()
        settings.read( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../../settings.ini') )

        tool_settings = settings[ "{0} {1}".format(tool_name, tool_version) ]

        flow_bp = FlowBlueprint( type='s' )
        flow_bp.save()

        tool = StandaloneTool( name=tool_name, \
                               version=tool_version, \
                               primary_site='http://trinityrnaseq.sourceforge.net/', \
                               flow_bp=flow_bp )
        tool.save()


        command_bp = CommandBlueprint( parent = flow_bp, \
                                       name = 'Run Trinity', \
                                       exec_path = tool_settings['exec_path'] )
        command_bp.save()


        CommandBlueprintParam( command=command_bp, name='--seqType', prefix='--seqType ', position=1, \
            is_optional=False, short_desc='Type of reads: (cfa, cfq, fa, or fq)' ).save()

        CommandBlueprintParam( command=command_bp, name='--JM', prefix='--JM ', position=2, \
            is_optional=False, short_desc='Number of GB of system memory to use for k-mer counting by jellyfish (eg. 10G).  Include the G character.' ).save()

        CommandBlueprintParam( command=command_bp, name='--left', prefix='--left ', position=3, \
            short_desc='Left reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--right', prefix='--right ', position=4, \
            short_desc='Right reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--single', prefix='--single ', position=5, \
            short_desc='Single (unpaired) reads' ).save()

        CommandBlueprintParam( command=command_bp, name='--SS_lib_type', prefix='--SS_lib_type ', position=6, \
            short_desc='Strand-specific RNA-Seq read orientation.  if paired: RF or FR, if single: F or R.  (dUTP method = RF)' ).save()

        CommandBlueprintParam( command=command_bp, name='--output', prefix='--output ', position=7, \
            short_desc='Name of directory for output (will be created if doesn\'t already exist.', \
            default_value='trinity_out_dir' ).save()

        CommandBlueprintParam( command=command_bp, name='--CPU', prefix='--CPU ', position=8, \
            short_desc='Number of CPUs to use', default_value='2' ).save()

        CommandBlueprintParam( command=command_bp, name='--min_contig_length', prefix='--min_contig_length ', \
            position=9, short_desc='Minimum assembled contig length to report', default_value='200' ).save()

        CommandBlueprintParam( command=command_bp, name='--jaccard_clip', prefix='--jaccard_clip ', position=10, \
            has_no_value=True, short_desc='Set if you have paired reads and expect high gene density with UTR overlap.  This is an expensive operation.' ).save()

        CommandBlueprintParam( command=command_bp, name='--no_cleanup', prefix='--no_cleanup ', position=11, \
            has_no_value=True, short_desc='Retain all intermediate input files' ).save()


        ####################################################
        # Inchworm and K-mer counting-related options: #####

        CommandBlueprintParam( command=command_bp, name='--min_kmer_cov', prefix='--min_kmer_cov ', position=12, \
            short_desc='Min count for K-mers to be assembled by Inchworm', default_value='1' ).save()

        ## Should later add the --no_run_quantifygraph option and process the rest via an iterator

        #####################################
        ###  Butterfly-related options:  ####
        
        CommandBlueprintParam( command=command_bp, name='--max_number_of_paths_per_node', prefix='--max_number_of_paths_per_node ', \
            position=13, short_desc='Only most supported (N) paths are extended from node A->B, mitigating combinatoric path explorations', \
            default_value='10' ).save()
        
        CommandBlueprintParam( command=command_bp, name='--group_pairs_distance', prefix='--group_pairs_distance ', \
            position=14, short_desc='Maximum length expected between fragment pairs.  Reads outside this will be treated as single-end', \
            default_value='500' ).save()

        CommandBlueprintParam( command=command_bp, name='--path_reinforcement_distance', prefix='--path_reinforcement_distance ', \
            position=15, short_desc='Minimum overlap of reads with growing transcript path (default: PE: 75, SE: 25)' ).save()

        CommandBlueprintParam( command=command_bp, name='--no_triplet_lock', prefix='--no_triplet_lock ', position=16, \
            has_no_value=True, short_desc='Do not lock triplet-supported nodes' ).save()
        
        CommandBlueprintParam( command=command_bp, name='--bflyHeapSpaceMax', prefix='--bflyHeapSpaceMax ', position=17, \
            default_value='20G', short_desc='Java max heap space setting for butterfly' ).save()

        CommandBlueprintParam( command=command_bp, name='--bflyHeapSpaceInit', prefix='--bflyHeapSpaceInit ', position=18, \
            default_value='1G', short_desc='Java initial heap space settings for butterfly' ).save()
        
        CommandBlueprintParam( command=command_bp, name='--bflyGCThreads', prefix='--bflyGCThreads ', position=19, \
            short_desc='Threads for garbage collection' ).save()

        CommandBlueprintParam( command=command_bp, name='--bflyCPU', prefix='--bflyCPU ', position=20, \
            short_desc='CPUs to use.  Default will match --CPU value' ).save()

        CommandBlueprintParam( command=command_bp, name='--bflyCalculateCPU', prefix='--bflyCalculateCPU ', position=21, \
            short_desc='Calculate CPUs based on 805 of max_memory divided by bflyHeapSpaceMax' ).save()

        # TODO: needs improving.  Unfortunately, Trinity currently only supports output definition
        #  at the directory level, and the file names under that are created by convention.
        #  I've written Brian to see if I can add this
        tool.creates( filetype_name='FASTA (nucleotide)', via_command=command_bp, via_param='--output' )
    
        # TODO: parameter grouping needs to be applied here.
        tool.can_use( filetype_name='FASTQ (Sanger, paired reads, left)', via_command=command_bp, via_param='--left' )
        tool.can_use( filetype_name='FASTQ (Sanger, paired reads, right)', via_command=command_bp, via_param='--right' )
        tool.can_use( filetype_name='FASTQ (Sanger, unpaired reads)', via_command=command_bp, via_param='--single' )

        # TODO: parameter grouping needs to be applied here.
        tool.can_use( filetype_name='FASTA (paired reads, left)', via_command=command_bp, via_param='--left' )
        tool.can_use( filetype_name='FASTA (paired reads, right)', via_command=command_bp, via_param='--right' )
        tool.can_use( filetype_name='FASTA (unpaired reads)', via_command=command_bp, via_param='--single' )



    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

