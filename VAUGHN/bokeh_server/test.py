from bokeh.embed import autoload_server


def test():
    script = autoload_server(model = None, app_path="/main")
    # this is pretty hacky -- flask can't pass its GET request parameters directly, so we have to do it this way
    # `script` is a string that looks like this (the first character is a newline):
    """
    <script
        src="http://localhost:5006/amped/autoload.js?bokeh-autoload-element=6b813263-05df-45a5-bd91-e25c5e53c020"
        id="6b813263-05df-45a5-bd91-e25c5e53c020"
        data-bokeh-model-id=""
        data-bokeh-doc-id=""
    ></script>
    """
    # so to add on the necessary parameters, we have to insert them manually.  hopefully we won't need to urlencode anything.
    # note that request.args = a MultiDict, so be careful of duplicate params
    # http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.MultiDict

    script_list = script.split("\n")
    script_list[2] = script_list[2][:-1]
    for key in request.args:
        script_list[2] = script_list[2] + "&{}={}".format(key, request.args[key])
    script_list[2] = script_list[2] + '"'
    script = "\n".join(script_list)
    return render_template("amped.html", script = script)