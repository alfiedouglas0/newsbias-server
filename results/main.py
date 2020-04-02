from os.path import dirname, join

import numpy as np
from sklearn import manifold

import json
from datetime import datetime
import io
from PIL import Image
import requests
# from threading import Thread

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Toggle
from bokeh.plotting import figure

TARGET_LOGO_HEIGHT = 0.1
DATA_PATH = join(dirname(__file__), "data/all_results.json")
DATA = {}
with open(DATA_PATH, "r") as f:
    DATA = json.load(f)

div_header = Div(text=open(join(dirname(__file__), "templates/main.html")
                           ).read(), sizing_mode="stretch_width", height_policy="fixed",
                 height=75, align=("center", "start"))

# Create Input controls
wieght_sow = Slider(title="Weight of style of wrtiting",
                    value=1, start=0, end=1, step=0.025)
wieght_sent = Slider(title="Weight of sentiment",
                     value=1, start=0, end=1, step=0.025)
wieght_ie = Slider(title="Weight of information extraction",
                   value=1, start=0, end=1, step=0.025)
# min_year = Slider(title="Articles from", start=2015,
#                   end=2020, value=2015, step=1)
# max_year = Slider(title="Articles till", start=2015,
#                   end=2020, value=2020, step=1)
show_logo = Toggle(label="Hide publisher logo",
                   button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data=dict(x=[], y=[], color=[], publisher=[], url=[], imageW=[], imageH=[]))

TOOLTIPS = [
    ("Publisher", "@publisher"),
]

p = figure(width_policy="fit", height_policy="fit",
           title="", toolbar_location=None, tooltips=TOOLTIPS,
           sizing_mode="stretch_both", margin=10)
glyph_cirles = p.circle(x="x", y="y", source=source, size=7,
                        #  color="color",
                        line_color=None, visible=False)
glyph_images = p.image_url(url="url", x="x", y="y", anchor="center",
                           source=source, w="imageW", h=TARGET_LOGO_HEIGHT,
                           visible=False)


def set_defaults():
    DATA["imageW"] = [0.12] * len(DATA["urls"])


def get_images():
    for index, url in enumerate(DATA["urls"]):
        try:
            size = Image.open(io.BytesIO(requests.get(url).content)).size
            aspectRatio = size[0] / size[1]
            DATA["imageW"][index] = TARGET_LOGO_HEIGHT * (size[0] / size[1])
        except:
            continue


def update_markers():
    if (show_logo.active):
        glyph_cirles.visible = True
        glyph_images.visible = False
    else:
        glyph_images.visible = True
        glyph_cirles.visible = False


def update_positions():
    sentimentData = [[data[0] * wieght_sent.value, data[1] * wieght_sent.value]
                     for data in DATA["SENTIMENT"]]
    sowData = [[data[0] * wieght_sow.value, data[1] * wieght_sow.value]
               for data in DATA["SOW"]]

    data = manifold.MDS(n_components=2, random_state=1).fit_transform(
        [d1 + d2 for d1, d2 in zip(sentimentData, sowData)]
    )

    source.data = dict(
        x=[d[0] for d in data],
        y=[d[1] for d in data],
        # color=df["color"],
        publisher=DATA["publisherNames"],
        url=DATA["urls"],
        imageW=DATA["imageW"],
    )

    p.title.text = str(datetime.now())


controls = [wieght_sow, wieght_sent, wieght_ie, show_logo]

for control in controls:
    if hasattr(control, "value"):
        control.on_change('value', lambda attr, old, new: update_positions())
    elif hasattr(control, "on_click"):
        control.on_change('active', lambda attr, old, new: update_markers())

inputs = column(*controls, width=320, margin=20)
inputs.sizing_mode = "stretch_height"
l = layout([
    div_header,
    [inputs, p],
], sizing_mode="stretch_both", height_policy="fit")

set_defaults()

get_images()  # get the aspect ratios for the images
update_positions()  # initial load of the data
update_markers()  # show plot
# Thread(target=get_images).start()  # get the aspect ratios for the images


curdoc().add_root(l)
curdoc().title = "News Bias"
