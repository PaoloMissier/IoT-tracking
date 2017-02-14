from . import draw, tools


def submit(minTS, maxTS, interval):
    if interval is not None: interval = int(interval)

    # convert minTS and maxTS /format 2017-01-30 05:34:26
    minTS = tools.strToDT(minTS)
    maxTS = tools.strToDT(maxTS)

    script, div = draw.drawGrid(minTS, maxTS, interval)
    return script, div
