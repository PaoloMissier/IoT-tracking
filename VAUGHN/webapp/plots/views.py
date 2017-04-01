from django.shortcuts import render
from plots.src import plots
from src.utils import database_cass as database

def plots(request):

    data = {'topic': ["t1","t2","t3"] , 'publisher':["p1","p2","p3","p4"] , 'subscriber':["s1","s2","s3"] }
    subheadingL1 = "Enter min, max time interval."

    # generate data. call db
    data['topic'] = database.getTopics()
    data['publisher'] = database.getPublisher()
    data['subscriber'] = database.getSubscribers()


    if request.method == 'POST':
        return render(request, 'plots/plots.html',
                      {"the_script": "", "the_div": "", "subheadingL1": subheadingL1, "data": data})

    return render(request, 'plots/plots.html', {"the_script": "", "the_div": "", "subheadingL1": subheadingL1, "data": data})
