from src.utils import logger
from bokeh.embed import autoload_server

log = logger.create_logger(__name__)


def submit(pub, sub):

    ## Load Bokeh Server, send request
    script = autoload_server(model=None,
                             app_path="/bokeh_server",
                             url="http://tharvester.eastus.cloudapp.azure.com:5006")
    script_list = script.split("\n")
    script_list[2] = script_list[2][:-1]

    ## Append args to Bokeh Server request
    request = {'pub': pub, 'sub': sub}
    for key in request.keys():
        script_list[2] += "&{}={}".format(key, request[key])
    script_list[2] += '"'
    script = "\n".join(script_list)

    return script


