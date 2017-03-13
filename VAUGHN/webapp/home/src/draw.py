import random
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from bokeh.embed import components
from bokeh.charts import Bar
from bokeh.layouts import gridplot
from . import home


def drawFigure():
    fig = Figure()
    ax = fig.add_subplot(111)
    x = []
    y = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now += delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    return canvas


def drawBar(dictPG):
    # dictPG format {'prodCnt': prodCnt,
    #               'maxConsCnt': maxConsCnt,
    #               'allTopics': allTopics,
    #               'plotGrid': plotGrid
    #               }

    prodCnt = dictPG['prodCnt']
    maxConsCnt = dictPG['maxConsCnt']
    allTopics = dictPG['allTopics']
    plotGrid = dictPG['plotGrid']
    bar_charts = list()

    for i in range(prodCnt):
        for j in range(maxConsCnt):
            (prodID, consID, topicsCnt) = plotGrid[i][j]

            for t in allTopics:
                if t not in topicsCnt:
                    topicsCnt[t] = 0  # set cnt = 0 for missing topics in this cell

            data = {'data': list(topicsCnt.values()),
                    'keys': list(topicsCnt.keys())
                    }

            bar = Bar(data, values='data', label='keys', title=prodID + "_" + consID,
                      bar_width=0.2, width=200, height=300, max_height=0.6, legend=False)
            bar_charts.append(bar)

    return bar_charts


def drawGrid(minTS, maxTS, pub, sub, topic, interval):
    gridList = list()

    for i in home.generatePlotGrid(minTS, maxTS, pub, sub, topic, interval):

        for k in drawBar(i):
            gridList.append(k)

    grid = gridplot(gridList, ncols=5, toolbar_location=None)

    return components(grid)
