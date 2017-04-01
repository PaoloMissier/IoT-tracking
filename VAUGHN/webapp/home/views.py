
from src.utils import database_mysql as database
from django.shortcuts import render
from home.src.home import *
from django.http import HttpResponse
import datetime
import json

def cubes(request):
    if request.method == 'GET':

        print(request.GET)
        minTS = request.GET.get('mints', '')
        maxTS = request.GET.get('maxts', '')
        print(minTS)
        print(maxTS)
        minTS = datetime.datetime.strptime(minTS, '%m/%d/%Y%H:%M%p')
        maxTS = datetime.datetime.strptime(maxTS, '%m/%d/%Y%H:%M%p')
        print(minTS)
        print(maxTS)
        l = generateAllCubes(minTS=minTS, maxTS=maxTS)
        data = {'data': l}

        return HttpResponse(json.dumps(data))


def home(request):

    data = {'topic': ["t1","t2","t3"] , 'publisher':["p1","p2","p3","p4"], 'subscriber':["s1","s2","s3"] }
    subheadingL1 = "Enter min, max time interval."

    # generate data. call db
    data['topic'] = database.getTopics()
    data['publisher'] = database.getPublisher()
    data['subscriber'] = database.getSubscribers()

    if request.method == 'POST':

        sMinDT = minDT = request.POST.get('minDT')
        sMaxDT = maxDT =request.POST.get('maxDT')
        sInterval = interval = request.POST.get('int')
        topic = request.POST.getlist('topics')
        pub = request.POST.getlist('pub')
        sub = request.POST.getlist('sub')

        if sMinDT == "" or \
            sMaxDT == "" or \
            sInterval == "" or \
            len(topic) == 0 or \
            len(pub) == 0 or \
            len(sub) == 0:
                subheadingL1 = "Please check required inputs."
                return render(request, 'home/home.html', {"the_script": "",
                                                          "the_div": "",
                                                          "subheadingL1": subheadingL1,
                                                          "subheadingL2": "",
                                                          "data": data})



        # generate graph
        script, div = submit(minDT, maxDT, pub, sub, topic, interval)

        # fault tolerance
        if minDT is None or maxDT is None or interval is None:
            subheadingL2 = "*Some value not given. Default value for min time is earliest possible, " \
                           "maximum time is latest possible and interval is 3600 secs*"
        else:
            subheadingL2 = ""

        subheadingL1 = "Below are the counter cubes from {} to {} at interval {}".format(sMinDT, sMaxDT, sInterval)
        return render(request, 'home/home.html', {"the_script": script,
                                                  "the_div": div,
                                                  "subheadingL1":subheadingL1,
                                                  "subheadingL2":subheadingL2,
                                                  "data":data})

    return render(request, 'home/home.html', {"the_script": "", "the_div": "", "subheadingL1":subheadingL1, "data":data})
