
from home.src.home import *
from django.shortcuts import render


def home(request):

    subheadingL1 = "Enter min, max time interval."

    if request.method == 'POST':

        sMinTS = minTS = request.POST.get('min')
        sMaxTS = maxTS =request.POST.get('max')
        sInterval = interval = request.POST.get('int')

        if sMinTS == "":
            sMinTS = "minimum"
            minTS = None
        if sMaxTS == "":
            sMaxTS = "maximum"
            maxTS = None
        if sInterval == "":
            sInterval = "one hour"
            interval = None

        # generate graph
        script, div = submit(minTS, maxTS, interval)

        # fault tolerance
        if minTS is None or maxTS is None or interval is None:
            subheadingL2 = "*Some value not given. Default value for min time is earliest possible, " \
                           "maximum time is latest possible and interval is 3600 secs*"
        else:
            subheadingL2 = ""

        subheadingL1 = "Below are the counter cubes from {} to {} at interval {}".format(sMinTS, sMaxTS, sInterval)
        return render(request, 'home/home.html', {"the_script": script,
                                                  "the_div": div,
                                                  "subheadingL1":subheadingL1,
                                                  "subheadingL2":subheadingL2})

    return render(request, 'home/home.html', {"the_script": "", "the_div": "", "subheadingL1":subheadingL1})
