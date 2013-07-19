
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_all_biotools
#
## https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
from django.core.management import find_management_module, find_commands, load_command_class
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings


class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Looks through all local tools and runs their installers'


    def handle(self, *args, **options):
        app_names = [a for a in settings.INSTALLED_APPS if a.endswith(".biotools")]

        for app_name in app_names:
            command_names = find_commands(find_management_module(app_name))
            for command_name in command_names:
                if command_name == 'load_all_biotools':
                    continue

                command = load_command_class(app_name, command_name)

                self.stdout.write("INFO: {0} - {1}\n".format(command_name, command.help))
                command.handle()
