from django.db import models
from biotools.models import Tool
from flow.models import Flow
from fileserver.models import DataSource


"""
The workspace app ties together the more independent apps like 'flow' and 'biotools', extending
these to provide functionality for a complete project workspace.  These include:

    - Flows
    - Input collections
    - Documentation and notes

As with all other portions of Emergence, the focus is first on the back-end development with 
API support with web interface work to follow.
"""

from django.db import models
from django.contrib.auth.models import User, Group


class Workspace(models.Model):
    name    = models.CharField(max_length=100)
    flows   = models.ManyToManyField( Flow )
    data    = models.ManyToManyField( DataSource )
    # user = User()
    
    def __str__(self):
        return self.name

    def add_data(self, data_source):
        self.data.add(data_source)

    def get_available_tools(self):
        # Iterate through all tools here.  In the future we'll want to do some
        #  intelligent sorting here, such as by tool popularity
        tools = Tool.objects.all()
        return tools

        #for tool in tools:
            
