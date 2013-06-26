
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_prodigal__2.60
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Prodigal v2.60'

    def handle(self, *args, **options):
        tool = StandaloneTool( name='Prodigal', \
                               version='2.60', \
                               exec_path='/opt/prodigal-2.60/bin/prodigal', \
                               primary_site='https://code.google.com/p/prodigal/' )
        tool.save()

        add_toolfiletype( tool, 'i', 'FASTA (nucleotide)', True )
        add_toolfiletype( tool, 'o', 'GenBank Flat File Format', False )
        add_toolfiletype( tool, 'o', 'GFF3', False )



    def add_toolfiletype(tool, iotype, ft_name, req):
        ft = Filetype.objects.get( name=ft_name )
        ToolFiletype( tool=tool, required=req, io_type=iotype, filetype=ft ).save()
