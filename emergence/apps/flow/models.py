from django.db import models
from django.contrib.auth.models import User, Group
from flow.executor import run
#from celery.result import AsyncResult

"""
The purpose of the classes within the 'flow' application is to allow users to run
commands and string them together to form complex 'flows'.  These flows can be built
into complex structures and executed locally or in a distributed manner.

I'll provide quick explanations of each of the main classes here, and you can find more
details on any of them within their class definitions below.

At the very high level, CommandBlueprint and FlowBlueprint objects describe the design
of any given command along with all the options/parameters it has.  These are used to
create specific Command objects, which can be organized into Flows (like pipelines.)

  Step           StepBlueprint
  Command        CommandBlueprint
                 CommandBlueprintParam
  Flow           FlowBlueprint

CommandBlueprint: This describes how any given command can be run.  It stores the path
to the installation of a tool and a formal description of every possible parameter
that tool accepts.  Think of these as menu items of things you can run.

Command: You use a CommandBlueprint with a set of parameters (CommandBlueprintParam objects)
to generate an actual executable Command.  These represent every individual command you
actually run.

Flow: These serve as storage containers for Command and Flow objects, and can be specified
to run them serially or in parallel.  These can be nested.


==============================
Some temporary developer notes

All can be accomplished via sequence, selection and repetition, so provide these
and unlimited nesting of them.

From Jonathan:

So if I wanted to design an OO model to handle both these "requirements" I would have a
single class called "Command", and that class would link to something called
ExecutionEnvironment (or hopefully a better less verbose name!) via a "has-a" relationship.
ExecutionEnvironment could have 2 subclasses, one called "LocalExecutionEnvironment" and
one called "DistributedExecutionEnvironment".  Switching a particular command instance from
distributed to local would then entail swapping out the execution environment object, but
wouldn't make you change the class of the Command itself.

This is all under the assumption that you really want to use inheritance to model local
vs distribution execution.  Or if local execution is something that can be made totally
explicit then you could simply make a Command have a DistributedExecutionEnvironment
object which is null in the case of local execution.

I don't know offhand all the stuff that's in the Distributed command object, but like
you say you could always just leave those fields null for a local command.  Right, so
in my suggestion you don't necessarily have to have an explicit LocalCommand class.

Main classes:

Command
Flow
Iterator
Conditional

Major happy thoughts to FunkyBob on IRC:Freenode:django for the modeling help

"""

class Step(models.Model):
    parent      = models.ForeignKey('self', null=True, related_name='children')
    name        = models.CharField( max_length=100 )
    start_time  = models.DateTimeField(null=True)
    end_time    = models.DateTimeField(null=True)
    #owner       = User()


    STATES = (
        ('u', 'unrun'),
        ('p', 'pending'),
        ('r', 'running'),
        ('c', 'complete'),
        ('e', 'error'),     # couldn't even execute, error building command
        ('f', 'failed'),    # executed correctly, failure returned by command
        ('k', 'killed'),
    )

    state = models.CharField( max_length=1, choices=STATES, default='u' )

    def __str__(self):
        return self.name

    def has_executed(self):
        """
        This doesn't imply success or failure.  Rather, it returns True if an execution has been attempted
        and a terminal state has been received.
        """
        if self.state == 'c' or self.state == 'e' or self.state == 'f' or self.state == 'k':
            return True
        else:
            return False

    def is_executing(self):
        if self.state == 'p' or self.state == 'r':
            return True
        else:
            return False
    

class StepBlueprint(models.Model):
    """
    The Steps of a flow are first defined as StepBlueprints, then instantiated as actual Steps,
    which have many more attributes to track.
    """
    parent = models.ForeignKey('self', null=True, related_name='children')
    name   = models.CharField( max_length=100 )

    def __str__(self):
        return self.name


class FlowBlueprint(StepBlueprint):
    """
    description - Long description to describe a stored Flow, usually added by the
    Flows author in the load script.
    """
    description = models.TextField()

    # should we use this instead?
    #  https://github.com/chrisspen/django-python-code-field
    conditional_code = models.TextField()
    
    TYPES = (
        ('s', 'serial'),
        ('p', 'parallel'),
    )

    type  = models.CharField( max_length=1, choices=TYPES, default='s' )


    def build(self):
        flow = Flow( blueprint=self, name=self.name, parent=self.parent, type=self.type )
        flow.save()

        ## process all children
        for child in self.get_children():
            if isinstance(child, FlowBlueprint):
                subflow = child.build()
            elif isinstance(child, CommandBlueprint):
                command = child.build(parent=flow)
            else:
                raise Exception("ERROR: Encountered something other than a FlowBlueprint or CommandBlueprint when processing a FlowBlueprint's children")

        return flow

    def get_command(self, name):
        command = CommandBlueprint.objects.get(parent=self, name=name)
        return command
    

    def get_children(self):
        # Get a list of all the attrs relating to Child models.
        child_attrs = dict(
            (rel.var_name, rel.get_cache_name())
            for rel in StepBlueprint._meta.get_all_related_objects()
            if issubclass(rel.field.model, StepBlueprint) and isinstance(rel.field, models.OneToOneField)
        )

        objs = []
        for obj in self.children.all().select_related(*child_attrs.keys()):
            # Try to find any children...
            for child in child_attrs.values():
                sobj = obj.__dict__.get(child)
                if sobj is not None:
                    break
            objs.append(sobj)
        return objs      
      

class Flow(Step):
    blueprint = models.ForeignKey( FlowBlueprint )

    # This should usually be set by the user to describe their own particular instance of the pipeline.
    description = models.TextField()

    # This will be the code from the blueprint but with any variables replaced
    conditional_code = models.TextField()
    
    # This will be "None" unless this is a conditional flow    conditional_result = models.BooleanField( default = None )
  
    TYPES = (
        ('s', 'serial'),
        ('p', 'parallel'),
    )

    type  = models.CharField( max_length=1, choices=TYPES, default='s' )

    def check_child_states(self):
        """
        This checks all the children of the flow and, depending on their state, sets the state
        of the flow itself.  If they're all complete, for example, the flow is marked as complete.

        Current rules:
        
        1.  If any child is 'running' or 'pending' the parent is running
        2.  If no children are being executed, and any children are in failed state, the parent has failed
        3.  If no children are being executed, and any children have been killed, the parent is killed
        4.  If all children have completed, 
        """
        child_count = 0
        children_executing = 0
        children_complete = 0
        children_killed = 0
        children_unrun = 0
        children_failed = 0
        new_state = None
        
        for child in self.get_children():
            child_count += 1
            
            # any child in a running state means this remains in a running state
            if child.is_executing():
                children_executing += 1
                break
            elif child.state == 'c':
                children_complete += 1
            elif child.state == 'f':
                children_failed += 1
            elif child.state == 'k':
                children_killed += 1
            elif child.state == 'u':
                children_unrun += 1
    
        if children_executing > 0:
            new_state = 'r'
        elif child_count == children_complete:
            new_state = 'c'
        else:
            if children_unrun == 0:
                if children_killed > 0:
                    new_state = 'k'
                if children_failed > 0:
                    new_state = 'f'
            
        ## only save a new state when we need to
        if new_state is not None and new_state != self.state:
            self.state = new_state
            self.save()

        ## if completed, report to parent
        if new_state == 'c' and self.parent is not None:
            self.parent.flow.child_child_states()

    def get_children(self):
        # Get a list of all the attrs relating to Child models.
        # http://musings.tinbrain.net/blog/2013/jun/24/django-and-model-inheritance/
        child_attrs = dict(
            (rel.var_name, rel.get_cache_name())
            for rel in Step._meta.get_all_related_objects()
            if issubclass(rel.field.model, Step) and isinstance(rel.field, models.OneToOneField)
        )

        objs = []
        for obj in self.children.all().select_related(*child_attrs.keys()):
            # Try to find any children...
            for child in child_attrs.values():
                sobj = obj.__dict__.get(child)
                if sobj is not None:
                    break
            objs.append(sobj)
        return objs

    def get_command(self, name):
        command = Command.objects.get(parent=self, name=name)
        return command
    
    def run(self, wait=None):

        self.state = 'r'
        self.save()

        if wait is None:
            wait = True

        for child in self.get_children():
            # don't re-run anything that's already complete
            if child.state == 'c':
                continue
            
            # sanity check, for now
            if not isinstance(child, Flow) and not isinstance(child, Command):
                raise Exception("ERROR: Encountered something other than a Flow or Command when processing a Flow's children")

            if self.type == 's':
                child.run(wait=True)
            else:
                # must be parallel
                child.run(wait=False)
                raise Exception("ERROR: parallel flows not currently handled")

              

class CommandBlueprint(StepBlueprint):
    ## The binary or script to execute only (no options/parameters)
    exec_path = models.TextField()

    def build(self, parent):
        #print("DEBUG: Building a Command with name={0} and parent={1}".format(self.name, self.parent))
        command = Command(parent=parent, blueprint=self, name=self.name)
        exec_string = self.exec_path

        for param in CommandBlueprintParam.objects.filter(command=self).order_by('position'):
            ## TODO: deal with param.has_quoted_value
            param_string = " {0}{1}".format(param.prefix, param.default_value)
            exec_string += param_string

        command.exec_string = exec_string
        command.save()

        return command


        
class Command(Step):
    exec_string = models.TextField()
    blueprint = models.ForeignKey(CommandBlueprint)

    ## This can be used to check the state of the task, wait for the task to finish or
    #  get its return value (or if the task failed, the exception and traceback)
    #  http://docs.celeryproject.org/en/latest/reference/celery.result.html#celery.result.AsyncResult
    #  The ID values look like: d09f8528-f471-4125-8b58-82fce932d59e
    task_id = models.CharField(max_length=50, null=True)
    
    def build_exec_string(self):
        cmd = self.blueprint.exec_path
        
        for param_bp in CommandBlueprintParam.objects.filter(command=self.blueprint).order_by('position'):
            ## as we iterate through each param of the blueprint, we see if the corresponding setting
            #   has been made manually for the command, else only add it if it's required.
            try:
                ## has a command parameter been set for this blueprint param?
                param = CommandParam.objects.get(command=self, blueprint=param_bp)
                param_value = param_bp.build_param_value(value=param.value)
                param_string = " {0}{1}".format(param.prefix, param_value)
                cmd += param_string
                
            except CommandParam.DoesNotExist:
                ## only add this one from the blueprint if it's a required one
                if not param_bp.is_optional:
                    param_value = param_bp.build_param_value()
                    param_string = " {0}{1}".format(param_bp.prefix, param_value)
                    cmd += param_string
                
            except CommandParam.MultipleObjectsReturned:
                pass
              
        return cmd
    
    
    def has_already_been_run(self):
        """ Defines how we determine whether a command has been run before."""
        if self.start_time is None:
            return False
        else:
            return True
    
    def run(self, wait=None):
        self.exec_string = self.build_exec_string()
        self.state = 'r'

        if wait is None:
            # this is a safer default
            wait = True

        ## TODO: this needs to be abstracted out to execution environments.  Testing like
        #   this for now.
        # http://docs.celeryproject.org/en/latest/userguide/calling.html#guide-calling
        # generate task id myself? request_id=str(uuid.uuid4()).replace('-','')
        task = run.delay( self )
        self.task_id = task.id
        self.save()

        if wait is True:
            task.wait()
        

    def get_param(self, name=None):
        param = CommandParam.objects.get(command=self, name=name)
        return param
        
            
    def set_param(self, name, val):
        ## get the blueprint for the passed param name
        bp = CommandBlueprintParam.objects.get(command=self.blueprint, name=name)
        param = CommandParam(command=self, blueprint=bp, name=name, prefix=bp.prefix, value=val)
        param.save()
    
       
class CommandBlueprintParam(models.Model):
    command = models.ForeignKey(CommandBlueprint)

    ## This is the label you want to give for the parameter.  This is most often the
    #   parameter string itself but without the whitespace or = symbols included in
    #   the prefix attribute.
    name = models.CharField( max_length=200 )

    ## There is a wide variety of ways to send parameters to a command.  Essentially,
    #  you want to enter whatever here goes before the actual value of the parameter,
    #  if anything at all.  Note the use of trailing spaces when needed.  Examples include:
    #   tool -i foo.fna                 prefix = "-i "
    #   tool -ifoo.fna                  prefix = "-i"
    #   tool --input foo.fna            prefix = "--input "
    #   tool --input=foo.fna            prefix = "--input="
    #   tool foo.fna                    prefix = None or ''
    prefix =  models.CharField( max_length=200, null=True )

    ## Some tools require their parameters to be in a specific order
    ## These don't to be unique but are only guaranteed to be sorted by this field.
    position = models.PositiveSmallIntegerField( blank=True )

    ## For those areas where a short description is needed (<= 100 characters)
    short_desc = models.CharField( max_length=100 )

    ## Here you should put a verbose description of your option
    long_desc = models.TextField( blank=True )

    ## Is this parameter optional?
    is_optional = models.BooleanField( default=True )

    ## This is rather subjective, but if a program provides an enormous number of
    #   options mark the ones that would only rarely be used as False here.  Interface
    #   bits only show the primary options at first, allowing users to expand their
    #   configuration view if they want to see all other options too.
    is_primary_option = models.BooleanField( default=True )

    ## This should be set to True for those parameters which are an option/prefix
    #   only with no corresponding value to pass.  Example:  wc -l
    has_no_value = models.BooleanField( default=False )

    ## Should the value of the option be wrapped in quotes?
    #   By default double quotes will be used unless they are detected
    #   within the value string.
    has_quoted_value = models.BooleanField( default=False )

    ## Specify any default value for an option here
    default_value = models.CharField( max_length=200, blank=True )

    class Meta:
        unique_together = (('command', 'name'),)


    def build_param_value(self, value=None):
        param_value = None
        
        ## if a value wasn't passed, use the default one
        if value is None:
            value = self.default_value
        
        if not self.has_no_value:
            if self.has_quoted_value:
                if '"' in value:
                    param_value = "'{0}'".format(value)
                else:
                    param_value = "\"{0}\"".format(value)
            else:
                param_value = "{0}".format(value)
        
        return param_value
        

class CommandParam(models.Model):
    """
    These should be generated only by CommandBlueprint.build(), which reads a store
    of parameter definitions to generate this.  For descriptions of what each of these
    attributes are, please see the documentation for CommandBlueprintParam
    """
    command = models.ForeignKey(Command)
    blueprint = models.ForeignKey(CommandBlueprintParam)
    name = models.CharField( max_length=200 )   ## this is redundant, but might be kept for ease of use
    prefix =  models.CharField( max_length=200 )
    value = models.CharField( max_length=200 )
    











