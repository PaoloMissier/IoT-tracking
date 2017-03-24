from django.db import models


class PlotSession(object):

    def __init__(self, plot_session_id, plot_thread):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.bokeh_session_id = plot_session_id
        self.thread = plot_thread


