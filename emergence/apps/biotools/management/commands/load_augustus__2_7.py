
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_augustus_2.7
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Augustus v2.7'

    def handle(self, *args, **options):
        tool = StandaloneTool( name='Augustus', \
                               version='2.7', \
                               #exec_path='/opt/augustus-2.7/bin/augustus', \
                               primary_site='http://bioinf.uni-greifswald.de/augustus' )
        tool.save()

        self.add_toolfiletype( tool, 'i', 'FASTA (nucleotide)', True )
        self.add_toolfiletype( tool, 'o', 'GFF3', True )



    def add_toolfiletype(self, tool, iotype, ft_name, req):
        ft = Filetype.objects.get( name=ft_name )
        ToolFiletype( tool=tool, required=req, io_type=iotype, filetype=ft ).save()
