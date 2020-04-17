from os.path import dirname, join

from bokeh.models import Div

STYLE_PATH = join(dirname(__file__), "templates/style.html")
HEADER_PATH = join(dirname(__file__), "templates/main.html")
DESCRIPTION_PATH = join(dirname(__file__), "templates/description.html")
INSTRUCTIONS_PATH = join(dirname(__file__), "templates/instructions.html")
LOADING_PATH = join(dirname(__file__), "templates/loading.html")

ARTICLES_COUNT_PLACEHOLDER = "$ARTICLES_COUNT$"
EVENTS_COUNT_PLACEHOLDER = "$EVENTS_COUNT$"
PUBLISHERS_STR_PLACEHOLDER = "$PUBLISHERS_STR$"
DEFAULT_ARTICLES_COUNT = "125,000"
DEFAULT_EVENTS_COUNT = "6,000"
DEFAULT_PUBLISHERS = ["Sky News", "Metro", "BBC News", "The Daily Mail", "The Independent",
                      "The Mirror", "The Guardian", "The Sun"]
DEFAULT_PUBLISHERS_STR = ", ".join(DEFAULT_PUBLISHERS[0:len(
    DEFAULT_PUBLISHERS) - 2]) + " and " + DEFAULT_PUBLISHERS[-1]


def get_style() -> str:
    return open(STYLE_PATH).read()


def get_header_div(path: str = HEADER_PATH) -> Div:
    html_str = get_style() + open(path).read()
    return Div(text=html_str,
               sizing_mode="stretch_width", height_policy="fixed",
               css_classes=["scroll"],
               height=75, align=("center", "center"))


def get_description_div(path: str = DESCRIPTION_PATH) -> Div:
    html_str = get_style() + open(path).read()

    html_str = html_str.replace(
        PUBLISHERS_STR_PLACEHOLDER, DEFAULT_PUBLISHERS_STR).replace(
        ARTICLES_COUNT_PLACEHOLDER, DEFAULT_ARTICLES_COUNT).replace(
            EVENTS_COUNT_PLACEHOLDER, DEFAULT_EVENTS_COUNT)

    return Div(text=html_str,
               sizing_mode="stretch_width",
               margin=(5, 20, 5, 20),
               height_policy="fixed",
               css_classes=["scroll", "margin"],
               height=170, align=("center", "start"))


def get_instructions_div(path: str = INSTRUCTIONS_PATH) -> Div:
    html_str = get_style() + open(path).read()
    return Div(text=html_str,
               sizing_mode="stretch_width", height_policy="fixed",
               margin=(5, 2, 20, 2),
               css_classes=["scroll"],
               height=60, align=("center", "start"))


def get_loading_div(path: str = LOADING_PATH) -> Div:
    html_str = get_style() + open(path).read()
    return Div(text=html_str,
               sizing_mode="stretch_both",
               margin=(20, 20, 20, 20),
               css_classes=["scroll", "center"],
               align=("center", "center"))
