from home.src import logger
from bokeh.embed import autoload_server

log = logger.create_logger(__name__)


def submit(pub, sub):

    script = autoload_server(model = None, app_path="/bokeh_server")
    script_list = script.split("\n")
    script_list[2] = script_list[2][:-1]

    request = {'pub': pub, 'sub': sub}

    for key in request.keys():
        script_list[2] += "&{}={}".format(key, request[key])
    script_list[2] += '"'
    script = "\n".join(script_list)

    return script


