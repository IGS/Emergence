## Introduction

With this project we're going the route of making code available very early on and letting people try the framework, both to get feedback as well as accepting contributions.

The goal is to narrow all the installation bits down to a single build script and then another to run the server, but this won't be done until the first release.

## Getting the code and requirements

The framework requires the following:

* Python 3.3
* Django 1.6 (or current dev)
* Celery 3.0.21
* rabbitmq-server >= 3.1.3

Get the code like this:

    $ svn export https://emergence.googlecode.com/svn/trunk Emergence

You might need to add the path to a subdirectory of Emergence to your PYTHONPATH environmental variable.  If you put the code in /opt, for example, this would be:

    $ export PYTHONPATH=/opt/Emergence/emergence/apps:$PYTHONPATH

Then two steps to initialize:

    $ cd Emergence
    $ python3.3 manage.py syncdb
    $ python3.3 manage.py load_all_biotools

Finally, you'll need to start your task manager (Celery worker) in another terminal:

    $ cd emergence/apps
    $ celery worker --app=flow -l info

Again, all this can be automatic later. If you're a build expert and would love nothing better than to spend your evenings helping out feel free to write me.

You can now try running a Prodigal (gene finding) pipeline with the example data provided. Go back to the root of the Emergence directory, then:

    $ ./bin/example_gene_predictor_run.py

Until the UI is ready you can watch the progress on the terminal where celery is running. This does gene prediction on the sample (E. coli) genome, but you can look into the code and the same complexity would be involved if you were instantiating a pipeline with 50 tools.
