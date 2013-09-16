
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_show_coords__3_23
#


import configparser
import os
from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam, FlowBlueprint

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs show-coords (MUMmer package) v3.23'

    def handle(self, *args, **options):
        tool_name = 'show-coords'
        tool_version = '3.23'
        
        if self.already_exists(tool_name, tool_version):
            print("INFO: tool {0} {1} already exists.  Skipping.".format(tool_name, tool_version) )
            return True

        settings = configparser.ConfigParser()
        settings.read( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../../settings.ini') )

        tool_settings = settings[ "{0} {1}".format('MUMmer', tool_version) ]

        flow_bp = FlowBlueprint( type='s' )
        flow_bp.save()

        tool = StandaloneTool( name=tool_name, \
                               version=tool_version, \
                               primary_site='http://mummer.sourceforge.net/manual/#coords', \
                               flow_bp=flow_bp )
        tool.save()


        command_bp = CommandBlueprint( parent = flow_bp, \
                                       name = 'Run show-coords', \
                                       exec_path = tool_settings['show_coords_bin'] )
        command_bp.save()

        # USAGE: show-coords  [options]  <deltafile>

        CommandBlueprintParam( command=command_bp, name='-b', prefix='-b ', has_no_value=True, position=1, \
            short_desc='Merges overlapping alignments', \
            long_desc='Merges overlapping alignments regardless of match dir or frame and does not display any idenitity information.' ).save()

        CommandBlueprintParam( command=command_bp, name='-B', prefix='-B ', has_no_value=True, position=2, \
            short_desc='Switch output to btab format' ).save()

        CommandBlueprintParam( command=command_bp, name='-c', prefix='-c ', has_no_value=True, position=3, \
            short_desc='Include percent coverage information in the output' ).save()

        CommandBlueprintParam( command=command_bp, name='-d', prefix='-d ', has_no_value=True, position=4, \
            short_desc='Display the alignment direction in the additional FRM columns (default for promer)' ).save()

        CommandBlueprintParam( command=command_bp, name='-H', prefix='-H ', has_no_value=True, position=5, \
            short_desc='Do not print the output header' ).save()

        CommandBlueprintParam( command=command_bp, name='-I', prefix='-I ', position=6, \
            short_desc='Set minimum percent identity to display' ).save()

        CommandBlueprintParam( command=command_bp, name='-k', prefix='-k ', has_no_value=True, position=7, \
            short_desc='Knockout 50/75 alignments', \
            long_desc='Knockout (do not display) alignments that overlap another alignment in a different frame by more than 50% of their length, AND have a smaller percent similarity or are less than 75% of the size of the other alignment (promer only)' ).save()

        CommandBlueprintParam( command=command_bp, name='-l', prefix='-l ', has_no_value=True, position=8, \
            short_desc='Include the sequence length information in the output' ).save()
        
        CommandBlueprintParam( command=command_bp, name='-L', prefix='-L ', position=9, \
            short_desc='Set minimum alignment length to display' ).save()

        CommandBlueprintParam( command=command_bp, name='-o', prefix='-o ', has_no_value=True, position=10, \
            short_desc='Annotate maximal alignments between two sequences', \
            long_desc='Annotate maximal alignments between two sequences, i.e. overlaps between reference and query sequences').save()

        CommandBlueprintParam( command=command_bp, name='-q', prefix='-q ', has_no_value=True, position=11, \
            short_desc='Sort output lines by query IDs and coordinates' ).save()

        CommandBlueprintParam( command=command_bp, name='-r', prefix='-r ', has_no_value=True, position=12, \
            short_desc='Sort output lines by reference IDs and coordinates' ).save()

        CommandBlueprintParam( command=command_bp, name='-T', prefix='-T ', has_no_value=True, position=13, \
            short_desc='Switch output to tab-delimited format' ).save()

        CommandBlueprintParam( command=command_bp, name='<deltafile>', prefix=None, position=14, is_optional=False, \
            short_desc='Input reference FASTA file' ).save()

        
        tool.needs( filetype_name='MUMmer delta file', via_command=command_bp, via_param='<deltafile>' )
        #tool.creates( filetype_name='MUMmer delta file', via_command=command_bp, via_param='-p' )

    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

