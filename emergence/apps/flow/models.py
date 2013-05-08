from django.db import models
from django.contrib.auth.models import User, Group
#from emergence.flow.extras.

# Create your models here.

"""

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

WHERE TO PUT THESE CLASSES?

Command
Flow
Iterator
Conditional

"""

class Step( models.Model ):
    name        = models.CharField( max_length=100 )
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    owner       = User()
    
    STATES = (
        ('u', 'unrun'),
        ('p', 'pending'),
        ('r', 'running'),
        ('c', 'complete'),
        ('e', 'error'),
        ('f', 'failed'),
        ('k', 'killed'),
    )
    
    state = models.CharField( max_length=1, choices=STATES )
    
    def __str__(self):
        return self.name
    

        

class Command( Step ):
    exec_string = models.TextField()

    
    
    
class Flow( Step ):
    TYPES = (
        ('s', 'serial'),
        ('p', 'parallel'),
    )
    
    type  = models.CharField( max_length=1, choices=TYPES )
    steps = models.ManyToManyField(Step, through='FlowSteps', related_name="+")

    
    
    
class FlowSteps( models.Model ):
    # http://stackoverflow.com/questions/4658747/django-related-name-for-field-clashes
    flow     = models.ForeignKey(Flow, related_name="parentFlows")
    step     = models.ForeignKey(Step, related_name="stepsOfFlow")
  
    position = models.IntegerField()
