from django.shortcuts import render
from django.http import HttpResponse
from src.utils import database_cass as database
from plots.src.plots import *
import json
import datetime


## REST API CubesJSON
def cubesJSON(request):
    if request.method == 'GET':
        minTS = request.GET.get('mints', '')
        maxTS = request.GET.get('maxts', '')
        minTS = datetime.datetime.strptime(minTS, '%m/%d/%Y%H:%M:%S')
        maxTS = datetime.datetime.strptime(maxTS, '%m/%d/%Y%H:%M:%S')

        df = generateAllCubes(minTS=minTS, maxTS=maxTS)
        data = {'data': df.to_dict('records')}

        return HttpResponse(json.dumps(data))


## REST API CubesCSV
def cubesCSV(request):
    if request.method == 'GET':
        minTS = request.GET.get('mints', '')
        maxTS = request.GET.get('maxts', '')
        minTS = datetime.datetime.strptime(minTS, '%m/%d/%Y%H:%M:%S')
        maxTS = datetime.datetime.strptime(maxTS, '%m/%d/%Y%H:%M:%S')

        df = generateAllCubes(minTS=minTS, maxTS=maxTS)
        row_list = df.to_csv(None, header=False, index=False)

        return HttpResponse(row_list)


def plots(request):

    data = {}
    subheadingL1 = "Please select min time, max time, pub, sub and topic."

    # generate select list call db
    data['topic'] = database.getTopics()
    data['publisher'] = database.getPublisher()
    data['subscriber'] = database.getSubscribers()

    if request.method == 'POST':

        sMinDT = minDT = request.POST.get('minDT')
        sMaxDT = maxDT = request.POST.get('maxDT')
        topic = request.POST.getlist('topics')
        pub = request.POST.getlist('pub')
        sub = request.POST.getlist('sub')

        ## check for empty inputs
        if sMinDT == "" \
                or sMaxDT == "" \
                or len(topic) == 0 \
                or len(pub) == 0 \
                or len(sub) == 0:

                subheadingL1 = "Please check required inputs."
                return render(request, 'plots/plots.html',
                              {"the_script": "", "the_div": "", "subheadingL1": subheadingL1, "data": data})

        # generate graph
        gridList = submit(minTS=minDT, maxTS=maxDT, pub=pub, sub=sub, topic=topic)

        subheadingL1 = "Below are the counter cubes from {} (UTC) to {} (UTC)".format(sMinDT, sMaxDT)
        return render(request, 'plots/plots.html',
                      {"gridList": gridList,
                       "subheadingL1": subheadingL1,
                       "data": data})

    return render(request, 'plots/plots.html', {"the_script": "", "the_div": "", "subheadingL1": subheadingL1,
                                                "data": data})
