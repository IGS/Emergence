
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_nucmer__3_23
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
    help = 'Installs NUCmer (MUMmer package) v3.23'

    def handle(self, *args, **options):
        tool_name = 'NUCmer'
        tool_version = '3.23'
        
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
                               primary_site='http://mummer.sourceforge.net/manual/#nucmer', \
                               flow_bp=flow_bp )
        tool.save()


        command_bp = CommandBlueprint( parent = flow_bp, \
                                       name = 'Run NUCmer', \
                                       exec_path = tool_settings['nucmer_bin'] )
        command_bp.save()

        # USAGE: nucmer  [options]  <Reference>  <Query>

        CommandBlueprintParam( command=command_bp, name='--mum', prefix='--mum ', has_no_value=True, position=1, \
            short_desc='Use anchor matches that are unique in both the reference and query' ).save()

        CommandBlueprintParam( command=command_bp, name='--mumreference', prefix='--mumreference ', has_no_value=True, position=2, \
            short_desc='Use anchor matches that are unique in the reference but not necessarily unique in the query' ).save()

        CommandBlueprintParam( command=command_bp, name='-b', prefix='-b ', position=3, default_value='200', \
            short_desc='Alignment extension distance', \
            long_desc='Distance an alignment extension will attempt to extend poor scoring regions before giving up').save()

        CommandBlueprintParam( command=command_bp, name='-c', prefix='-c ', default_value='65', position=4, \
            short_desc='Minimum length of a cluster of matches' ).save()

        CommandBlueprintParam( command=command_bp, name='--nodelta', prefix='--nodelta ', has_no_value=True, position=5, \
            short_desc='Toggles off creation of delta file' ).save()

        CommandBlueprintParam( command=command_bp, name='-D', prefix='-D ', default_value='5', position=6, \
            short_desc='Maximum diagonal difference between two adjacent anchors in a cluster' ).save()

        CommandBlueprintParam( command=command_bp, name='-d', prefix='-d ', default_value='0.12', position=7, \
            short_desc='Maximum diagonal difference ratio', \
            long_desc='Maximum diagonal difference between two adjacent anchors in a cluster as a differential fraction of the gap length ' ).save()

        CommandBlueprintParam( command=command_bp, name='--noextend', prefix='--noextend ', has_no_value=True, position=8, \
            short_desc='Toggles off the cluster extension step' ).save()

        CommandBlueprintParam( command=command_bp, name='--forward', prefix='--forward ', has_no_value=True, position=9, \
            short_desc='Use only the forward strand of the Query sequences' ).save()

        CommandBlueprintParam( command=command_bp, name='-g', prefix='-g ', default_value='90', position=10, \
            short_desc='Maximum gap between two adjacent matches in a cluster' ).save()

        CommandBlueprintParam( command=command_bp, name='-l', prefix='-l ', default_value='20', position=11, \
            short_desc='Minimum length of a single match' ).save()
        
        CommandBlueprintParam( command=command_bp, name='--nooptimize', prefix='--nooptimize ', has_no_value=True, position=12, \
            short_desc='Toggle off alignment score optimization', \
            long_desc='Toggles off alignment score optimization, i.e. if an alignment extension reaches the end of a sequence, it will backtrack to optimize the alignment score instead of terminating the alignment at the end of the sequence').save()
        
        CommandBlueprintParam( command=command_bp, name='--reverse', prefix='--reverse ', has_no_value=True, position=13, \
            short_desc='Use only the reverse complement of the Query sequences' ).save()

        CommandBlueprintParam( command=command_bp, name='--nosimplify', prefix='--nosimplify ', has_no_value=True, position=14, \
            short_desc='Removes shadowed clusters', \
            long_desc='Simplify alignments by removing shadowed clusters. Turn this option off if aligning a sequence to itself to look for repeats' ).save()

        CommandBlueprintParam( command=command_bp, name='<reference_in>', prefix=None, position=15, is_optional=False, \
            short_desc='Input reference FASTA file' ).save()

        CommandBlueprintParam( command=command_bp, name='<query_in>', prefix=None, position=16, is_optional=False, \
            short_desc='Input query FASTA file' ).save()
        
        tool.needs( filetype_name='FASTA (nucleotide)', via_command=command_bp, via_param='<reference_in>' )
        tool.needs( filetype_name='FASTA (nucleotide)', via_command=command_bp, via_param='<query_in>' )
        #tool.creates( filetype_name='MUMmer delta file', via_command=command_bp, via_param='-p' )

    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

