from django.db import models
from django.contrib.auth.models import User, Group

class DataSource( models.Model ):
    label       = models.CharField( max_length=100 )
    added_by    = User()

class LocalFile( DataSource ):
    ## https://docs.djangoproject.com/en/1.5/topics/files/
    ## might look into using django-filer here
    path = models.FileField( upload_to='%Y/%m/%d' )

class DataCollection( models.Model ):
    name        = models.CharField( max_length=100 )
    created_by  = User()
    path        = models.FilePathField(allow_folders=True)
    sources     = models.ManyToManyField( DataSource, through='CollectionContents' )

class CollectionContents( models.Model ):
    """
    Model which groups DataSource object (and subclasses) into DataCollections.
    Stored via the through relationship here to allow for extra fields.
    """
    source = models.ForeignKey(DataSource)
    collection = models.ForeignKey(DataCollection)
    
