from django.db import models
from flow.models import FlowBlueprint, CommandBlueprint, CommandBlueprintParam

"""
This module is used to describe bioinformatics tools, their formats, and interdependencies.
"""

class Filetype( models.Model ):
    """
    Base class for the different bioinformatics file types, such as GFF3, GBK, BAM, etc.

    Attributes:

    - name: This is essentially a label, but needs to be unique.
    - format: The main identity of a format (GFF3, BAM, etc.)
    - variant: Should be considered dialects of the primary format (either because there is a
               disagreement on the standard or for the tools which just get it wrong.  If not
               specified) or can describe content-specific versions.  The default value is
               "canonical".
    - spec_url: A URL most accepted as describing the format specification for this file type.
    """
    name      = models.CharField( max_length=100, unique=True )
    format    = models.CharField( max_length=100 )
    variant   = models.CharField( max_length=100, default="canonical" )
    spec_url  = models.URLField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('format', 'variant'),)



class Tool( models.Model ):
    """
    A 'tool' is an extremely generic term within this framework.  It can represent a single
    executable such as blastn or a more complete analysis pipeline implemented in workflow
    frameworks like Galaxy or Ergatis.  (Of course, this means tools can be made up of other tools.)

    Most simply, a tool should be thought of us a unit of analysis that can require some number
    of inputs and generates at least one output.
    """

    ## Do not include version numbers in the name
    name = models.CharField( max_length=100 )

    ## Pretty open here - could be like '1.12.0' or 'beta5'
    version = models.CharField( max_length=50 )

    ## should be loaded from a discovery/conf file
    #exec_path = models.FilePathField( allow_folders=False )

    ## Usually the primary site of the tool by the author
    primary_site = models.CharField( max_length=200 )

    ## Publication (may or may not be peer-reviewed)
    publication = models.CharField( max_length=300 )

    ## note: https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    files = models.ManyToManyField( Filetype, through='ToolFiletype' )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'version'),)

    def can_create(self, filetype_name=None, via_command=None, via_param=None, via_params=None ):
        """
        Defines an optional output created by this tool.
        """
        ft = Filetype.objects.get( name=filetype_name )
        tft = ToolFiletype( tool=self, required=False, io_type='o', filetype=ft )
        tft.save()

        self._add_toolfiletypeparams( tft, via_command, via_param, via_params )

    def needs(self, filetype_name=None, via_command=None, via_param=None, via_params=None ):
        """
        Defines a required input of this tool, which corresponds to a loaded Filetype object.
        """
        ft = Filetype.objects.get( name=filetype_name )
        tft = ToolFiletype( tool=self, required=True, io_type='i', filetype=ft )
        tft.save()

        self._add_toolfiletypeparams( tft, via_command, via_param, via_params )


    def _add_toolfiletypeparams(self, tft, command_bp, via_param, via_params):
        # It doesn't make sense to define both via_param and via_params
        if via_param is not None and via_params is not None:
            raise Exception("ERROR: cannot pass both via_param and via_params")

        # these are the option strings which are parsed into param_tuples (below)
        param_strings = list()
        
        # these are the parsed versions of individual parameters, where each element is a
        #  tuple of [opt, value] where value can be None
        param_tuples = list()

        if via_param is not None:
            param_strings.append( via_param )
        
        elif via_params is not None:
            for via_param in via_params:
                param_strings.append( via_param )

        for param_string in param_strings:
           if "=" in param_string:
                parts = param_string.split("=")
                param_tuples.append( [ parts[0], parts[1] ] )
            else:
                param_tuples.append( [param_string, None] )

        for param in param_tuples:
            cbp_param = CommandBlueprintParam.objects.get( command=command_bp, name=param[0] )
            ToolFiletypeParam( toolfiletype=tft, \
                               command_bp=command_bp, \
                               commandblueprintparam=cbp_param, \
                               value=param[1] ).save()




class StandaloneTool( Tool ):
    ## This should only be toggled to True if all the dependencies for the tool
    #  are satisfied for any given installation.
    enabled = models.BooleanField( default=False )

    flow_bp = models.ForeignKey( FlowBlueprint )

    def new_flow(self):
        return self.flow_bp.build()
        

class ErgatisTool( Tool ):
    pass

class GalaxyTool( Tool ):
    pass



class ToolFiletype( models.Model ):
    """
    Model which links Tools and their associated file types, both input and output.

        relationships with FileTypes
        needs (input implied)
        can_use (input optional)
        creates (output implied)
        can_create (output optional)
        
    Each of the above relationships are usually implemented in the form of a flow.CommandParam, which doesn't
    add an additional cross-app dependency.  biotools was already aware of flow
    """
    tool = models.ForeignKey(Tool)
    filetype = models.ForeignKey(Filetype)
    description = models.CharField( max_length=200 )
    required = models.BooleanField()

    # Record which parameters control how this tool uses/generates this filetype
    via_params = models.ManyToManyField(CommandBlueprintParam, through='ToolFiletypeParam')

    IO_TYPES = (
        ('o', 'Output'),
        ('i', 'Input'),
    )
    io_type = models.CharField( max_length=1, choices=IO_TYPES )

    

class ToolFiletypeParam( models.Model ):
    """
    Defines which parameters can be used by a tool to generate which input/output filetypes.  For
    example, when running prodigal a user can generate GFF output using these options:

      -o <the path to an output file>
      -f gff

    If the param's blueprint says this is required and it's empty here, it means it must
    be defined by the user.
    """
    toolfiletype = models.ForeignKey( ToolFiletype )
    command_bp = models.ForeignKey( CommandBlueprint )
    commandblueprintparam = models.ForeignKey( CommandBlueprintParam )
    
    # There are warnings in the model docs about setting null=true on CharFields, but I couldn't get it to
    #  work otherwise.
    value = models.CharField( max_length=200, null=True )
    
