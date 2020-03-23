# Load the packages
import pandas as pd
from flask import Flask, render_template
# from bokeh.embed import components
# from bokeh.models import HoverTool
# from bokeh.plotting import figure

from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8
from bokeh.embed import components
# Connect the app
app = Flask(__name__)


def get_plot(source):
    #  Car list
    car_list = source.data['Car'].tolist()

    # Add plot
    p = figure(
        y_range=car_list,
        plot_width=800,
        plot_height=600,
        title='Cars With Top Horsepower',
        x_axis_label='Horsepower',
        tools="pan,box_select,zoom_in,zoom_out,save,reset"
    )

    # Render glyph
    p.hbar(
        y='Car',
        right='Horsepower',
        left=0,
        height=0.4,
        fill_color=factor_cmap(
            'Car',
            palette=Blues8,
            factors=car_list
        ),
        fill_alpha=0.9,
        source=source,
        legend='Car'
    )

    # Add Legend
    p.legend.orientation = 'vertical'
    p.legend.location = 'top_right'
    p.legend.label_text_font_size = '10px'

    # Add Tooltips
    hover = HoverTool()
    hover.tooltips = """
    <div>
        <h3>@Car</h3>
        <div><strong>Price: </strong>@Price</div>
        <div><strong>HP: </strong>@Horsepower</div>
        <div><img src="@Image" alt="" width="200" /></div>
    </div>
    """
    p.add_tools(hover)

    # Return the plot
    return(p)


@app.route('/')
def homepage():

    df = pd.read_csv('cars.csv')
    source = ColumnDataSource(df)

    # Setup plot
    p = get_plot(source)
    script, div = components(p)

    # Give some text for the bottom of the page
    example_string = 'Example web app built using python, Flask, and Bokeh!'

    # Render the page
    return render_template('index.html', script=script, div=div, example_string=example_string)


if __name__ == '__main__':
    app.run(debug=False)
