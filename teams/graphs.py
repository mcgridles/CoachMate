from datetime import date
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import FuncTickFormatter, HoverTool
from bokeh.models.sources import ColumnDataSource
from bokeh.resources import CDN

from teams.models import Event

def date_time_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
      <div>
        <span class="hover-tooltip">@date</span>
      </div>
      <div>
        <span class="hover-tooltip">@time</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)

def graph_event(swimmer, event):
    results = Event.objects.filter(swimmer=swimmer).filter(event=event).order_by('date')

    if results.exists():
        x = []
        y = []
        date = []
        time = []
        for r in results:
            d = r.date
            t = r.time.total_seconds()
            x.append(d)
            y.append(t)
            date.append(d.strftime('%m/%d/%y'))
            time.append('{:d}:{:.2f}'.format(int(t)/60, t))

        source = ColumnDataSource(data=dict(x=x, y=y, date=date, time=time))

        title = ' '.join([w.capitalize() for w in event.split()])

        hover_tool = date_time_hover_tool()
        tools = ['pan', 'box_zoom', hover_tool, 'reset', 'save']
        plot = figure(
            title=title,
            x_axis_label='Date',
            y_axis_label='Time',
            x_axis_type='datetime',
            plot_width=400,
            plot_height=200,
            tools=tools,
            responsive=True,
        )

        plot.line('x', 'y', line_width=2, source=source)
        plot.circle('x', 'y', size=10, source=source)
        plot.yaxis.formatter = FuncTickFormatter(code=
            """
            return Math.floor(tick/60) + ":" + tick.toFixed(2)
            """
        )

        return components(plot)

    else:
        return None, None
