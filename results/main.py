from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Toggle
from bokeh.plotting import figure

div_header = Div(text=open(join(dirname(__file__), "templates/main.html")
                           ).read(), sizing_mode="stretch_width", height_policy="fixed",
                 height=75, align=("center", "start"))

# Create Input controls
wieght_sow = Slider(title="Weight of style of wrtiting",
                    value=1, start=0, end=1, step=0.1)
wieght_sent = Slider(title="Weight of sentiment",
                     value=1, start=0, end=1, step=0.1)
wieght_ie = Slider(title="Weight of information extraction",
                   value=1, start=0, end=1, step=0.1)
# min_year = Slider(title="Articles from", start=2015,
#                   end=2020, value=2015, step=1)
# max_year = Slider(title="Articles till", start=2015,
#                   end=2020, value=2020, step=1)
show_logo = Toggle(label="Show publisher logo", button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data=dict(x=[], y=[], color=[], publisher=[]))

TOOLTIPS = [
    ("Publisher", "@publisher"),
]

p = figure(width_policy="fit", height_policy="fit",
           title="", toolbar_location=None, tooltips=TOOLTIPS,
           sizing_mode="stretch_both", margin=10)
p.circle(x="x", y="y", source=source, size=7,
         color="color", line_color=None)


def update():
    pass


controls = [wieght_sow, wieght_sent, wieght_ie, show_logo]

for control in controls:
    if "on_change" in control.__dict__:
        control.on_change('value', lambda attr, old, new: update())
    elif "on_click" in control.__dict__:
        control.on_change('on_click', lambda attr, old, new: update())

inputs = column(*controls, width=320, margin=20)
inputs.sizing_mode = "stretch_height"
l = layout([
    div_header,
    [inputs, p],
], sizing_mode="stretch_both", height_policy="fit")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "News Bias"
