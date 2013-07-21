from django.db import models

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
    name = models.CharField(max_length=100)
    # user = User()
    
    def __str__(self):
        return self.name
