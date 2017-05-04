from bokeh.embed import components
from bokeh.charts import Bar
from bokeh.layouts import gridplot
from bokeh.models import HoverTool, BoxSelectTool
from src.utils import tools
from plots.src import plots


def drawBar(dictPG):
    # plot = {'minTS': minTS,
    #         'maxTS': maxTS,
    #         'maxConsCnt': maxConsCnt,
    #         'prodCnt': prodCnt,
    #         'allTopics': allTopics,
    #         'plotGrid': plotGrid
    #         }

    prodCnt = dictPG['prodCnt']
    maxConsCnt = dictPG['maxConsCnt']
    allTopics = dictPG['allTopics']
    plotGrid = dictPG['plotGrid']
    minTS = tools.dtToStr(dictPG['minTS'])
    maxTS = tools.dtToStr(dictPG['maxTS'])
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

            # Tootips Init
            hover = HoverTool(
                tooltips=[
                    ("Pub", prodID),
                    ("Sub", consID),
                    ("Topic", "$x"),
                    ("Cnt", "@height"),
                    ("MinTS", minTS),
                    ("MaxTS", maxTS)
                ]
            )
            TOOLS = [BoxSelectTool(), hover]

            bar = Bar(data,
                      values='data',
                      label='keys',
                      title=prodID+" → "+consID,
                      title_text_font_size='8pt',
                      bar_width=0.2,
                      width=350,
                      height=350,
                      max_height=0.6,
                      legend=False,
                      tools=TOOLS)
            bar_charts.append(bar)

    return bar_charts


def drawGrid(minTS, maxTS, pub, sub, topic):
    gridList = list()

    for i in plots.generatePlotGrid(minTS, maxTS, pub, sub, topic):
        bars = []
        for k in drawBar(i):
            bars.append(k)

        script, div = components(gridplot(bars, ncols=3, toolbar_location=None))
        gridList.append({'the_script': script,
                         'the_div': div,
                         'time': tools.dtToStr(i['minTS']) + "-" + tools.dtToStr(i['maxTS'])})

    return gridList
