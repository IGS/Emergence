from django.shortcuts import render

# Create your views here.
def index( request ):

    context = {
        ## could put data here
    }

    return render( request, 'coreui/index.html', context )