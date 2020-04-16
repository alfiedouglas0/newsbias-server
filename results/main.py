from htmlhelper import get_header_div, get_description_div, get_instructions_div, get_loading_div

from os.path import dirname, join
import json
from datetime import datetime
import io
from PIL import Image
import requests
import functools
import operator
# from threading import Thread

import numpy as np
from sklearn import manifold

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Toggle
from bokeh.plotting import figure

# curdoc(). add_root(get_loading_div())
# curdoc().title = "Loading..."

MDS = manifold.MDS(n_components=2, random_state=1)
TARGET_LOGO_HEIGHT = 15
TOOLTIPS = [
    ("Publisher", "@publisher"),
]
TOOLS = ["pan", "wheel_zoom", "box_zoom", "save"]
SLIDER_STEP = 0.025
DATA_PATH = join(dirname(__file__), "data/all_results.json")
DEFAULT_WIDTH_HEIGHT = 450
DATA = {}
with open(DATA_PATH, "r") as f:
    DATA = json.load(f)

div_header = get_header_div()
div_description = get_description_div()
div_instructions = get_instructions_div()

# Create Input controls

wieght_sow = Slider(title="Influence of style of wrtiting",
                    value=1, start=0, end=1, step=SLIDER_STEP)
wieght_sent = Slider(title="Influence of emotive language",
                     value=1, start=0, end=1, step=SLIDER_STEP)
wieght_ie = Slider(title="Influence of facts presented",
                   value=1, start=0, end=1, step=SLIDER_STEP)
wieght_ambig = Slider(title="Influence of the ambiguity of the articles",
                      value=1, start=0, end=1, step=SLIDER_STEP)
# min_year = Slider(title="Articles from", start=2015,
#                   end=2020, value=2015, step=1)
# max_year = Slider(title="Articles till", start=2015,
#                   end=2020, value=2020, step=1)
show_logo = Toggle(label="Hide publisher logo",
                   button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data=dict(x=[], y=[], color=[], publisher=[], url=[], imageW=[], imageH=[]))

p = figure(width_policy="fit", height_policy="fit", tools=TOOLS,
           title="", toolbar_location="right", tooltips=TOOLTIPS,
           sizing_mode="stretch_both", margin=10,
           plot_width=DEFAULT_WIDTH_HEIGHT, plot_height=DEFAULT_WIDTH_HEIGHT,
           min_width=600, min_height=450,
           active_scroll="wheel_zoom")
glyph_cirles = p.circle(x="x", y="y", source=source, size=7,
                        #  color="color",
                        line_color=None, visible=False)
glyph_images = p.image_url(url="url", x="x", y="y", anchor="center",
                           source=source, w="imageW", h=TARGET_LOGO_HEIGHT,
                           visible=True)


def set_defaults():
    DATA["imageW"] = [0.12] * len(DATA["urls"])


def get_images():
    for index, url in enumerate(DATA["urls"]):
        try:
            size = Image.open(io.BytesIO(requests.get(url).content)).size
            DATA["imageW"][index] = TARGET_LOGO_HEIGHT * (size[0] / size[1])
        except:
            print("ERROR: downloading the image: '{}'".format(url))
            continue


def get_mds_data():
    data = []
    if "SENTIMENT" in DATA:
        data.append(
            [[d[0] * wieght_sent.value, d[1] * wieght_sent.value]
             for d in DATA["SENTIMENT"]]
        )
    if "UNMASKING" in DATA:
        data.append(
            [[d[0] * wieght_sow.value, d[1] * wieght_sow.value]
             for d in DATA["UNMASKING"]]
        )
    if "FACTS" in DATA:
        data.append(
            [[d[0] * wieght_ie.value, d[1] * wieght_ie.value]
             for d in DATA["FACTS"]]
        )
    if "AMBIGUITY" in DATA:
        data.append(
            [[d[0] * wieght_ambig.value, d[1] * wieght_ambig.value]
             for d in DATA["AMBIGUITY"]]
        )

    if len(data) <= 0:
        return []

    return MDS.fit_transform(
        [functools.reduce(operator.add, [*d])
         for d in zip(*data)]  # concat the arrays
    )


def update_markers():
    if (show_logo.active):
        glyph_cirles.visible = True
        glyph_images.visible = False
    else:
        glyph_images.visible = True
        glyph_cirles.visible = False


def update_positions():
    dataMDS = get_mds_data()
    if len(dataMDS) <= 0:
        return

    source.data = dict(
        x=[d[0] for d in dataMDS],
        y=[d[1] for d in dataMDS],
        publisher=DATA["publisherNames"],
        url=DATA["urls"],
        imageW=DATA["imageW"],
    )


def resize_graph(atrr, old, new):
    old = DEFAULT_WIDTH_HEIGHT if old == None else old
    if atrr == 'outer_width':
        newWidthRatio = new / old
        plotRange = p.x_range.end - p.x_range.start
        newPlotRange = plotRange * newWidthRatio
        pointsToAdd = (newPlotRange - plotRange) / 2
        p.x_range.update(start=p.x_range.start - pointsToAdd,
                         end=p.x_range.end + pointsToAdd)
    elif atrr == 'outer_height':
        newHeightRatio = new / old
        plotRange = p.y_range.end - p.y_range.start
        newPlotRange = plotRange * newHeightRatio
        pointsToAdd = (newPlotRange - plotRange) / 2
        p.y_range.update(start=p.y_range.start - pointsToAdd,
                         end=p.y_range.end + pointsToAdd)


controls = [wieght_sow, wieght_sent, wieght_ie, wieght_ambig, show_logo]

for control in controls:
    if hasattr(control, "value"):
        control.on_change('value', lambda attr, old, new: update_positions())
    elif hasattr(control, "on_click"):
        control.on_change('active', lambda attr, old, new: update_markers())

p.on_change('outer_width', resize_graph)
p.on_change('outer_height', resize_graph)


inputs = column(div_instructions, *controls,
                width=320, margin=20, max_width=320)
inputs.sizing_mode = "stretch_height"
l = layout([
    div_header,
    div_description,
    [inputs, p],
], sizing_mode="stretch_both", height_policy="fit")

set_defaults()
get_images()  # get the aspect ratios for the images
update_positions()  # initial load of the data
update_markers()  # show plot
# Thread(target=get_images).start()  # get the aspect ratios for the images

curdoc().clear()
curdoc().title = "News Bias"
curdoc().add_root(l)
