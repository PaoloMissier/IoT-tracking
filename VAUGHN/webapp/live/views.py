from django.shortcuts import render
from django.http import HttpResponse
from live.src.live import *
from src.utils.database_mysql import getPublisher, getSubscribers

log = logger.create_logger(__name__)


def live(request):

    data = {'publisher': getPublisher(), 'subscriber': getSubscribers()}

    if request.method == 'POST':
        pub = request.POST.get('pub')
        sub = request.POST.get('sub')

        script = submit(pub, sub)

        return render(request, 'live/live.html', {"the_script": script, "the_div": "", "data":data})

    return render(request, 'live/live.html', {"the_script": "", "the_div": "", "data":data})


def file(request):

    response = HttpResponse(open('log/log.txt'), content_type='text/plain')
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
