from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.core.properties import value
from utils.dictdiffer import *
from bokeh.palettes import Viridis256
from bokeh.models import HoverTool, BoxSelectTool, Legend
from utils.db_cass import getJoinCntDFClients
from utils.logger import *
import random

log = create_logger(__name__)

source = ColumnDataSource()
ct = 0  # seconds counter on X-axis for columndatasource

# get args (pub, sub) from http request
args = curdoc().session_context.request.arguments
pub = ""
sub = ""
try:
    pub = args.get('pub')[0]
    sub = args.get('sub')[0]
    pub = pub.decode(encoding="utf-8", errors="strict")
    sub = sub.decode(encoding="utf-8", errors="strict")
except TypeError:
    log.error("Unable to parse pub and sub")

# Figure configs
hover = HoverTool(  # hover box config
    tooltips=[
        ("Count", "$data_y"),
    ], line_policy="nearest"
)
TOOLS = [BoxSelectTool(), hover]  # fig's tools
fig = Figure(title="{}   ->   {}".format(str(pub), str(sub)),
             toolbar_location="below",
             plot_width=1000,
             plot_height=650,
             tools=TOOLS)
fig.add_layout(Legend(location=(0, -30)), 'right')


# callback function for periodic update on document
def update_data():
    if pub == "" or sub == "":
        return

    # generate latest datasource
    global ct, source, fig
    ct += 1
    pd = getJoinCntDFClients(pub, sub)
    dt = dict(x=[ct])
    for cnt, topic in pd[['cnt', 'topic']].values:
        dt[topic] = [cnt]

    dictDiff = DictDiffer(dt, source.data)  # compare old datasource and new datasource
    dictDiffAdded = dictDiff.added()

    if len(dictDiffAdded) > 0:  # if new data source > old data source
        for key in dt.keys():
            if key in dictDiffAdded:  # filter any new columndatasource
                source.add(data=[None]*len(dt['x']), name=key)  # add new datasource column
                if key in pd['topic'].tolist():  # filter only topic
                    # add new line in figure
                    fig.line(source=source, x='x',
                             y=key,
                             line_width=1,
                             alpha=.85,
                             legend=value(key),
                             color=Viridis256[random.randrange(256)])
                    log.info("New Topic Added: {} , Total Topic: {}".format(key, len(pd['topic'].tolist())))

    if len(dt) == len(source.data):  # stream only same coloumndatasource size to prevent error
        source.stream(dt, 10)


curdoc().add_periodic_callback(update_data, 600)
curdoc().add_root(fig)
