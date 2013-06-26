
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_all
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Looks through all local tools and runs their installers'

    def handle(self, *args, **options):
        pass
