from htmlhelper import get_header_div, get_description_div, get_instructions_div, get_loading_div
from utils import scale_2d_plot

from os.path import dirname, join
import json
import io
from PIL import Image
import requests

import numpy as np
from sklearn import manifold

from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Toggle
from bokeh.plotting import figure, output_file

# curdoc(). add_root(get_loading_div())
# curdoc().title = "Loading..."

MDS = manifold.MDS(n_components=2, random_state=1)
TARGET_LOGO_HEIGHT = 15
TOOLTIPS = [
    ("Publisher", "@publisher"),
]
TOOLS = []  # ["pan", "wheel_zoom", "box_zoom", "save"]
SLIDER_STEP = 0.1
DATA_PATH = join(dirname(__file__), "data/all_results.json")
DEFAULT_WIDTH_HEIGHT = 450
TARGET_GRAPH_RANGE = [200, 200]
RAW_DATA = {}
NUMERICAL_DATA = {"SENTIMENT": None, "UNMASKING": None, "FACTS": None,
                  "AMBIGUITY": None}
with open(DATA_PATH, "r") as f:
    RAW_DATA = json.load(f)

div_header = get_header_div()
div_description = get_description_div()
div_instructions = get_instructions_div()

# Create Input controls
wieght_sow = Slider(title="Influence of style of wrtiting",
                    value=1, start=0, end=1, step=SLIDER_STEP)
wieght_sent = Slider(title="Influence of emotive language",
                     value=0, start=0, end=1, step=SLIDER_STEP)
wieght_ie = Slider(title="Influence of facts presented",
                   value=0, start=0, end=1, step=SLIDER_STEP)
wieght_ambig = Slider(title="Influence of the ambiguity of the articles",
                      value=0, start=0, end=1, step=SLIDER_STEP)
# min_year = Slider(title="Articles from", start=2015,
#                   end=2020, value=2015, step=1)
# max_year = Slider(title="Articles till", start=2015,
#                   end=2020, value=2020, step=1)
show_logo = Toggle(label="Hide publisher logo",
                   button_type="success")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data=dict(x=[], y=[], color=[], publisher=[], url=[], imageW=[], imageH=[]))

p = figure(width_policy="fit", height_policy="fit", tooltips=TOOLTIPS,
           title="", toolbar_location=None,  tools=TOOLS,
           sizing_mode="stretch_both", margin=10,
           width=DEFAULT_WIDTH_HEIGHT, height=DEFAULT_WIDTH_HEIGHT,
           min_width=600, min_height=450,
           x_range=(TARGET_GRAPH_RANGE[0] * -0.625,
                    TARGET_GRAPH_RANGE[0] * 0.625),
           y_range=(TARGET_GRAPH_RANGE[1] * -0.625,
                    TARGET_GRAPH_RANGE[1] * 0.625))
p.yaxis.visible = False
p.xaxis.visible = False
glyph_cirles = p.circle(x="x", y="y", source=source, size=7,
                        line_color=None, visible=False)
glyph_images = p.image_url(url="url", x="x", y="y", anchor="center",
                           source=source, w="imageW", h=TARGET_LOGO_HEIGHT,
                           visible=True)


def set_defaults():
    RAW_DATA["imageW"] = [0.12] * len(RAW_DATA["urls"])
    for key in filter(lambda item: item in NUMERICAL_DATA, RAW_DATA):
        NUMERICAL_DATA[key] = np.array(RAW_DATA[key])


def get_images():
    for index, url in enumerate(RAW_DATA["urls"]):
        size = RAW_DATA["urlSizes"][index]
        try:
            size = Image.open(io.BytesIO(requests.get(url).content)).size
        except Exception as e:
            print("ERROR: downloading the image: '{}'".format(url))
            print(e)
            print("Using previously known size: {}, {}".format(
                size[0], size[1]))
        RAW_DATA["imageW"][index] = TARGET_LOGO_HEIGHT * \
            (size[0] / size[1])


def get_mds_data():
    data = []
    weightSum = wieght_sent.value + wieght_ie.value + \
        wieght_sow.value + wieght_ambig.value
    if not NUMERICAL_DATA["SENTIMENT"] is None and wieght_sent.value != 0:
        data.append(NUMERICAL_DATA["SENTIMENT"] *
                    (wieght_sent.value / weightSum))
    if not NUMERICAL_DATA["FACTS"] is None and wieght_ie.value != 0:
        data.append(NUMERICAL_DATA["FACTS"] *
                    (wieght_ie.value / weightSum))
    if not NUMERICAL_DATA["UNMASKING"] is None and wieght_sow.value != 0:
        data.append(NUMERICAL_DATA["UNMASKING"] *
                    (wieght_sow.value / weightSum))
    if not NUMERICAL_DATA["AMBIGUITY"] is None and wieght_ambig.value != 0:
        data.append(NUMERICAL_DATA["AMBIGUITY"] *
                    (wieght_ambig.value / weightSum))

    if len(data) <= 0:
        return data
    return MDS.fit_transform(np.concatenate(data, axis=1))


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
        dataMDS = np.zeros([len(RAW_DATA["publisherNames"]), 2])
    else:
        dataMDS = np.around(scale_2d_plot(dataMDS, TARGET_GRAPH_RANGE), 0)
    with open("temp.json", 'w') as f:
        f.write(json.dumps(dataMDS.tolist()))
    source.data = dict(
        x=dataMDS[:, 0],
        y=dataMDS[:, 1],
        publisher=RAW_DATA["publisherNames"],
        url=RAW_DATA["urls"],
        imageW=RAW_DATA["imageW"],
    )


def resize_graph(atrr, old, new):
    old = DEFAULT_WIDTH_HEIGHT if old == None or old == 0 else old
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
