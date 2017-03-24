## Getting Started

These instructions will get you bokeh server running.

## Prerequisites and Deployment

Install Prerequisites through terminal

```
$pip install bokeh

```
Run bokeh server, allow request from default port 5006 and port 8000 from django web app.
```
1. $cd /bokeh_server
2. bokeh serve . --host=localhost:5006 --host=localhost:8000 

```

## Reference
* [Link](http://bokeh.pydata.org/en/latest/docs/user_guide/server.html#userguide-server) - Bokeh Server User Guide
* [Bokeh](http://bokeh.pydata.org/en/latest/) - Python Interactive Visualization Library
