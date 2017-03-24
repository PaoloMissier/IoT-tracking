from functools import partial
from bokeh.client import push_session
from bokeh.io import curdoc, set_curdoc, Document
from bokeh.models import ColumnDataSource, ColumnData, DataSource
from bokeh.plotting import Figure
from bokeh.properties import value
from utils.dictdiffer import *
from bokeh.palettes import Viridis256 #@UnresolvedImport
from bokeh.models import HoverTool, BoxSelectTool
from utils.db import getJoinCntDFClients
from utils.logger import *
import random
from types import *

source = ColumnDataSource()
logger = create_logger(__name__)
cts = []
ct = 0
args = curdoc().session_context.request.arguments
pub = ""
sub = ""
try:
    pub = args.get('pub')[0]
    sub = args.get('sub')[0]
except:
    logger.error("Unable to parse pub and sub")
hover = HoverTool(
    tooltips=[
        ("Topic", "$index"),
        ("Count", "$data_y"),
    ], line_policy="nearest"
)
TOOLS = [BoxSelectTool(), hover]
fig = Figure(title="{} -> {}".format(pub, sub), toolbar_location="below", plot_width=800, plot_height=800, tools=TOOLS)

def callBack(pub, sub):
    global source
    dt = update_data(pub, sub)
    source.stream(dt, 10)


def update_data(pub, sub):
    if pub == "" or sub == "":
        return

    # generate dt
    global ct, source, fig
    ct += 1
    cts.append(ct)
    pd = getJoinCntDFClients(pub, sub)
    cnts = pd['cnt'].tolist()
    # new_cnts = []
    # palletes = Inferno256[0:len(cnts)]
    # for cnt in cnts:
    #     new_cnts.append([cnt])
    # palletes = Inferno256[0:len(cnts)]
    dt = dict(x=[ct])
    for cnt, topic in pd[['cnt', 'topic']].values:
        dt[topic] = [cnt]
    logger.info("DT: {} vs Source {}".format(len(dt), len(source.data)))
    dictDiff = DictDiffer(dt, source.data)
    dictDiffAdded = dictDiff.added()
    logger.info("before if len dictDiffAdded ")
    if len(dictDiffAdded) > 0:
        logger.info("before for key in dtkeys ")
        for key in dt.keys():
            logger.info("before if len dictDiffAdded ")
            if key in dictDiffAdded:
            # logger.warning("Key {} ".format(key))
                source.add(data=[None]*len(dt['x']), name=key)
                # logger.info("Key: {}".format(key))
                # logger.info("PD topics {}".format(pd.topic))
                logger.info("before if key in pd ")
                if key in pd['topic'].tolist():
                    logger.info("Keyyyy {}".format(key))
                    fig.line(source=source, x='x', y=key, line_width=1, alpha=.85, legend=value(key), color=Viridis256[random.randrange(256)])
    # logger.info("AFter DT: {} vs Source {}".format(len(dt), len(source.data)))
    logger.warning("source data {}".format(source.data))
    # source = ColumnDataSource(dt)
    # logger.warning("len changed: {}".format(len(DictDiffer(dt, source.data).changed())))
    # logger.warning("Source {} vs DT {}".format(source.data, dt))
    # logger.warning("Set changed {}".format(str(DictDiffer(dt, source.data).changed())))
    # if len(DictDiffer(dt, source.data).changed()) > 0:
    #     logger.warning(" Enter if cond Source {} vs DT {}".format(len(source.data), len(dt)))
    #     new_dt = {}
    #     diffs = DictDiffer(dt, source.data)
    #     for diff in diffs.added():
    #         new_dt[diff] = dt.get(diff)
    #     # add = {'line_color': Spectral11[0:len(cnts)]}
    #     logger.warning("new_Source {} vs DT {}".format(source.data, dt))
    #     # multiline.data_source = source
    #     # multiline.color = Spectral11[0:len(cnts)]
    #     # set_curdoc(Document().add_root(reDrawFigure(source)))
    if len(dt) == len(source.data):
        source.stream(dt, 10)

# update_data(pub, sub)
# source = ColumnDataSource(dt)
# logger.warning("Source after update data{}".format(str(source.data)))
# logger.warning("dt : {}".format(pd))
# for topic in pd.topic:
#     fig.line(source=source, x='x', y=topic, line_width=2, alpha=.85, color='red')
curdoc().add_periodic_callback(partial(update_data, pub=pub, sub=sub), 600)
curdoc().add_root(fig)

# session.show()
# session.loop_until_closed()
