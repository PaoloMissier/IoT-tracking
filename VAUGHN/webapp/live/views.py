from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def live(request):
    if request.method == 'POST':
        return render(request, 'live/live.html', {"the_script": "", "the_div": ""})
    return render(request, 'live/live.html', {"the_script": "", "the_div": ""})


def file(request):

    response = HttpResponse(open('log/log.txt'), content_type='text/plain')
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
