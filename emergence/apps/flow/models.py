from django.db import models
from django.contrib.auth.models import User, Group

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
        ('e', 'error'),
        ('f', 'failed'),
        ('k', 'killed'),
    )

    state = models.CharField( max_length=1, choices=STATES, default='u' )

    def __str__(self):
        return self.name


class Flow(Step):
    TYPES = (
        ('s', 'serial'),
        ('p', 'parallel'),
    )

    type  = models.CharField( max_length=1, choices=TYPES )

    def getChildren(self):
        # Get a list of all the attrs relating to Child models.
        child_attrs = dict(
            (rel.var_name, rel.get_cache_name())
            for rel in Step._meta.get_all_related_objects()
            if issubclass(rel.field.model, Step) and isinstance(rel.field, models.OneToOneField)
        )

        objs = []
        for obj in self.children.all().select_related(*child_attrs.keys()):
            # Try to find any children... failing that, use the obj itself
            for child in child_attrs.values():
                sobj = obj.__dict__.get(child)
                if sobj is not None:
                    break
            objs.append(sobj)
        return objs


    def run(self):
      #print("DEBUG: run method processing children of a {0} called: ({1})".format(self.__class__.__name__, self.name) )
      for child in self.getChildren():
          ## if this is a flow, run it
          if isinstance(child, Flow):
              #print("\tDEBUG: is an instance of Flow")
              child.run()

          ## else if it's a command, execute it
          elif isinstance(child, Command):
              print("\tDEBUG: is an instance of Command.  Add Execute code here")

          elif hasattr(child, 'name'):
              raise Exception("ERROR: Encountered something other than a Flow or Command when processing a Flow's children")

class Command(Step):
    exec_string = models.TextField()





















