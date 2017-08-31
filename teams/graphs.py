import json

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, widgetbox
from bokeh.embed import components
from bokeh.models import FuncTickFormatter, HoverTool
from bokeh.models.sources import ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Select

from teams.models import Event, EVENT_CHOICE, Swimmer

class DatetimeEncoder(json.JSONEncoder):
    """
    Encodes Python datetime.date objects to make compatible with JSON serialization.
    """
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)

def date_time_hover_tool():
    """
    Generates the HTML for the Bokeh's hover data tool on our graph.
    """
    hover_html = """
      <div>
        <span class="hover-tooltip">@date</span>
      </div>
      <div>
        <span class="hover-tooltip">@time</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)

def graph_event(swimmer):
    hover_tool = date_time_hover_tool()
    tools = ['pan', 'box_zoom', hover_tool, 'reset', 'save']
    plot = figure(
        title='Event Progress',
        x_axis_label='Date',
        y_axis_label='Time',
        x_axis_type='datetime',
        plot_width=400,
        plot_height=200,
        tools=tools,
        responsive=True,
    )
    # format datetime.timedelta objects to MM:ss.mm
    plot.yaxis.formatter = FuncTickFormatter(code=
        """
        return Math.floor(tick/60) + ":" + tick.toFixed(2)
        """
    )

    data_source = {}
    events = []
    first_event = None
    for event in EVENT_CHOICE:
        e = '_'.join([word.lower() for word in event[0].split()])

        results = Event.objects.filter(swimmer=swimmer).filter(event=event[0]).order_by('date')
        if results.exists():
            if len(results) == 1: # one point will not display well on graph
                data_source['x_'+e] = None
                data_source['y_'+e] = None
                data_source['date_'+e] = None
                data_source['time_'+e] = None
                continue

            events.append(event[1])
            if first_event == None:
                first_event = e

            x, y = [], []
            date, time = [], []
            for r in results.iterator():
                d = r.date
                t = r.time.total_seconds()
                x.append(d)
                y.append(t)
                date.append(d.strftime('%m/%d/%y')) # date to string for hover
                time.append('{:d}:{:.2f}'.format(int(t)/60, t)) # time to string for hover

            data_source['x_'+e] = x
            data_source['y_'+e] = y
            data_source['date_'+e] = date
            data_source['time_'+e] = time

        else:
            # eliminates KeyError exceptions
            data_source['x_'+e] = None
            data_source['y_'+e] = None
            data_source['date_'+e] = None
            data_source['time_'+e] = None

    # set initial graph
    source = ColumnDataSource(data=dict(
        x=data_source['x_'+first_event],
        y=data_source['y_'+first_event],
        date=data_source['date_'+first_event],
        time=data_source['time_'+first_event]
    ))
    plot.line('x', 'y', source=source)

    # callback modifies data source depending on Select box
    callback = CustomJS(args=dict(source=source), code="""
            data = %s;
            f = cb_obj.value;

            if (f == "50 Freestyle") {
                source.data['x'] = data.x_50_free;
                source.data['y'] = data.y_50_free;
                source.data['date'] = data.date_50_free;
                source.data['time'] = data.time_50_free;
            } else if (f == "100 Freestyle") {
                source.data['x'] = data.x_100_free;
                source.data['y'] = data.y_100_free;
                source.data['date'] = data.date_100_free;
                source.data['time'] = data.time_100_free;
            } else if (f == "200 Freestyle") {
                source.data['x'] = data.x_200_free;
                source.data['y'] = data.y_200_free;
                source.data['date'] = data.date_200_free;
                source.data['time'] = data.time_200_free;
            } else if (f == "500 Freestyle") {
                source.data['x'] = data.x_500_free;
                source.data['y'] = data.y_500_free;
                source.data['date'] = data.date_500_free;
                source.data['time'] = data.time_500_free;
            } else if (f == "1000 Freestyle") {
                source.data['x'] = data.x_1000_free;
                source.data['y'] = data.y_1000_free;
                source.data['date'] = data.date_1000_free;
                source.data['time'] = data.time_1000_free;
            } else if (f == "50 Backstroke") {
                source.data['x'] = data.x_50_back;
                source.data['y'] = data.y_50_back;
                source.data['date'] = data.date_50_back;
                source.data['time'] = data.time_50_back;
            } else if (f == "100 Backstroke") {
                source.data['x'] = data.x_100_back;
                source.data['y'] = data.y_100_back;
                source.data['date'] = data.date_100_back;
                source.data['time'] = data.time_100_back;
            } else if (f == "200 Backstroke") {
                source.data['x'] = data.x_200_back;
                source.data['y'] = data.y_200_back;
                source.data['date'] = data.date_200_back;
                source.data['time'] = data.time_200_back;
            } else if (f == "50 Breaststroke") {
                source.data['x'] = data.x_50_breast;
                source.data['y'] = data.y_50_breast;
                source.data['date'] = data.date_50_breast;
                source.data['time'] = data.time_50_breast;
            } else if (f == "100 Breaststroke") {
                source.data['x'] = data.x_100_breast;
                source.data['y'] = data.y_100_breast;
                source.data['date'] = data.date_100_breast;
                source.data['time'] = data.time_100_breast;
            } else if (f == "200 Breaststroke") {
                source.data['x'] = data.x_200_breast;
                source.data['y'] = data.y_200_breast;
                source.data['date'] = data.date_200_breast;
                source.data['time'] = data.time_200_breast;
            } else if (f == "50 Butterfly") {
                source.data['x'] = data.x_50_fly;
                source.data['y'] = data.y_50_fly;
                source.data['date'] = data.date_50_fly;
                source.data['time'] = data.time_50_fly;
            } else if (f == "100 Butterfly") {
                source.data['x'] = data.x_100_fly;
                source.data['y'] = data.y_100_fly;
                source.data['date'] = data.date_100_fly;
                source.data['time'] = data.time_100_fly;
            } else if (f == "200 Butterfly") {
                source.data['x'] = data.x_200_fly;
                source.data['y'] = data.y_200_fly;
                source.data['date'] = data.date_200_fly;
                source.data['time'] = data.time_200_fly;
            } else if (f == "100 IM") {
                source.data['x'] = data.x_100_im;
                source.data['y'] = data.y_100_im;
                source.data['date'] = data.date_100_im;
                source.data['time'] = data.time_100_im;
            } else if (f == "200 IM") {
                source.data['x'] = data.x_200_im;
                source.data['y'] = data.y_200_im;
                source.data['date'] = data.date_200_im;
                source.data['time'] = data.time_200_im;
            } else if (f == "400 IM") {
                source.data['x'] = data.x_400_im;
                source.data['y'] = data.y_400_im;
                source.data['date'] = data.date_400_im;
                source.data['time'] = data.time_400_im;
            } else if (f == "Base Freestyle") {
                source.data['x'] = data.x_base_free;
                source.data['y'] = data.y_base_free;
                source.data['date'] = data.date_base_free;
                source.data['time'] = data.time_base_free;
            } else if (f == "Base Backstroke") {
                source.data['x'] = data.x_base_back;
                source.data['y'] = data.y_base_back;
                source.data['date'] = data.date_base_back;
                source.data['time'] = data.time_base_back;
            } else if (f == "Base Breaststroke") {
                source.data['x'] = data.x_base_breast;
                source.data['y'] = data.y_base_breast;
                source.data['date'] = data.date_base_breast;
                source.data['time'] = data.time_base_breast;
            } else if (f == "Base Butterfly") {
                source.data['x'] = data.x_base_fly;
                source.data['y'] = data.y_base_fly;
                source.data['date'] = data.date_base_fly;
                source.data['time'] = data.time_base_fly;
            } else if (f == "Base IM") {
                source.data['x'] = data.x_base_im;
                source.data['y'] = data.y_base_im;
                source.data['date'] = data.date_base_im;
                source.data['time'] = data.time_base_im;
            }

            source.change.emit();
    """ % json.dumps(data_source, cls=DatetimeEncoder))

    try:
        select = Select(
            title="Select Event:",
            value=events[0],
            options=events,
            callback=callback
        )
    except IndexError:
        return None, None

    return components(column(select, plot, responsive=True))
