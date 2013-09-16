
## This should not be run directly.  Instead, run as a command through manage.py like:
#   python3 manage.py biotools load_bowtie__1_0_0
#


import configparser
import os
from django.core.management.base import BaseCommand, CommandError
from emergence.apps.biotools.models import StandaloneTool, Filetype, ToolFiletype
from emergence.apps.flow.models import CommandBlueprint, CommandBlueprintParam, FlowBlueprint

class Command(BaseCommand):
    ## write messages via self.stdout.write and self.stderr.write
    args = 'None'
    help = 'Installs Bowtie 1.0.0 and tools'

    def handle(self, *args, **options):
        tool_name = 'Bowtie'
        tool_version = '1.0.0'
        
        if self.already_exists(tool_name, tool_version):
            print("INFO: tool {0} {1} already exists.  Skipping.".format(tool_name, tool_version) )
            return True

        settings = configparser.ConfigParser()
        settings.read( os.path.join( os.path.abspath(os.path.dirname(__file__)), '../../settings.ini') )

        tool_settings = settings[ "{0} {1}".format(tool_name, tool_version) ]

        flow_bp = FlowBlueprint( type='s', \
                                 description='Bowtie is an ultrafast, memory-efficient short read aligner. It aligns short DNA sequences (reads) to the human genome at a rate of over 25 million 35-bp reads per hour. Bowtie indexes the genome with a Burrows-Wheeler index to keep its memory footprint small: typically about 2.2 GB for the human genome (2.9 GB for paired-end).')
        flow_bp.save()

        tool = StandaloneTool( name=tool_name, \
                               version=tool_version, \
                               primary_site='http://bowtie-bio.sourceforge.net/index.shtml', \
                               flow_bp=flow_bp )
        tool.save()

        # the reference sequence
        #self.add_toolfiletype( tool, 'i', 'FASTA (nucleotide)', True, 'Nucleotide reference FASTA file' )

        #self.add_toolfiletype( tool, 'i', 'FASTQ (paired reads, left)', False )
        #self.add_toolfiletype( tool, 'i', 'FASTQ (paired reads, right)', False )
        #self.add_toolfiletype( tool, 'i', 'FASTQ (unpaired reads)', False )

        #self.add_toolfiletype( tool, 'i', 'FASTA (paired reads, left)', False )
        #self.add_toolfiletype( tool, 'i', 'FASTA (paired reads, right)', False )
        #self.add_toolfiletype( tool, 'i', 'FASTA (unpaired reads)', False )
        
        #self.add_toolfiletype( tool, 'o', 'FASTQ (paired reads, left)', False )
        #self.add_toolfiletype( tool, 'o', 'FASTQ (paired reads, right)', False )
        #self.add_toolfiletype( tool, 'o', 'FASTQ (unpaired reads)', False )

        # Add a conditional flow that will run if bowtie-build is needed.
        #  Perhaps crude, this is done by using the name of the reference input FASTA file
        #  and looking for a '.1.ebwt' suffix
        bowtie_build_flow_bp = FlowBlueprint( type='s', \
                                              description='Runs bowtie-build if an index file isn\'t detected.', \
                                              conditional_code='' )

        ## TODO: This tool definition is still under construction






        #command_bp = CommandBlueprint( parent = flow_bp, \
        #                               name = 'Run Trinity read normalization', \
        #                               exec_path = tool_settings['normalization_script'] )
        #command_bp.save()




        # bowtie [options]* <ebwt> {-1 <m1> -2 <m2> | --12 <r> | <s>} [<hit>]



    def already_exists(self, name, version):
        flt = StandaloneTool.objects.filter(name=name, version=version)
        if flt.count() > 0:
            return True
        else:
            return False

