
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_prodigal__2.60
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Prodigal v2.60'

    def handle(self, *args, **options):
        tool = StandaloneTool( name='Prodigal', \
                               version='2.60', \
                               primary_site='https://code.google.com/p/prodigal/' )
        tool.save()

        self.add_toolfiletype( tool, 'i', 'FASTA (nucleotide)', True )
        self.add_toolfiletype( tool, 'o', 'GenBank Flat File Format', False )
        self.add_toolfiletype( tool, 'o', 'GFF3', False )

        command_bp = CommandBlueprint( exec_path = '/opt/prodigal-2.60/bin/prodigal' )
        command_bp.save()
        
        CommandBlueprintParam( command=command_bp, prefix='-a ', position=1, \
            short_desc='Write protein translations to the selected file' ).save()

        CommandBlueprintParam( command=command_bp, prefix='-c ', position=2, has_no_value=True, \
            short_desc='Closed ends.  Do not allow genes to run off edges' ).save()

        CommandBlueprintParam( command=command_bp, prefix='-d ', position=3, \
            short_desc='Write nucleotide sequences of genes to the selected file' ).save()

        ## TODO: limit choices to (gbk, gff, or sco)
        CommandBlueprintParam( command=command_bp, prefix='-f ', position=4, default_value='gbk', \
            short_desc='Select output format (gbk, gff, or sco).  Default is gbk' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-g ', position=5, default_value='11', \
            short_desc='Specify a translation table to use (default 11)' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-i ', position=6, is_optional=False, \
            short_desc='Specify input file (default reads from stdin).' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-m ', position=7, has_no_value=True, \
            short_desc='Treat runs of Ns as masked sequence and do not build genes across them' ).save()

        CommandBlueprintParam( command=command_bp, prefix='-n ', position=8, has_no_value=True, \
            short_desc='Bypass the Shine-Dalgarno trainer and force the program to scan for motifs' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-o ', position=9, is_optional=False, \
            short_desc='Specify output file' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-p ', position=10, default_value='single', \
            short_desc='Select procedure (single or meta).  Default is single.' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-s ', position=11, \
            short_desc='Write all potential genes (with scores) to the selected file' ).save()
        
        CommandBlueprintParam( command=command_bp, prefix='-t ', position=12, \
            short_desc='Write or read the specified training file', \
            long_desc='Write a training file (if none exists); otherwise, read and use the specified training file' ).save()

        
        
    def add_toolfiletype(self, tool, iotype, ft_name, req):
        ft = Filetype.objects.get( name=ft_name )
        ToolFiletype( tool=tool, required=req, io_type=iotype, filetype=ft ).save()
