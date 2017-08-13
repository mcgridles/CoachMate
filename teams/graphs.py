from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, widgetbox
from bokeh.embed import components
from bokeh.models import FuncTickFormatter, HoverTool
from bokeh.models.sources import ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Select

from teams.models import Event, EVENT_CHOICE, Swimmer

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

    plot_features = {}
    events = []
    first_event = True

    for event in EVENT_CHOICE:
        data_source = {}
        e = '_'.join(event[0].split())

        results = Event.objects.filter(swimmer=swimmer).filter(event=event[0]).order_by('date')
        if results.exists():
            if len(results) == 1:
                plot_features['line_'+e] = None
                continue

            events.append(event[1])
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

            data_source['x_'+e] = x
            data_source['y_'+e] = y
            data_source['date'] = date
            data_source['time'] = time

            source = ColumnDataSource(data_source)

            plot_features['line_'+e] = plot.line('x_'+e, 'y_'+e, line_width=2, source=source)

            if first_event == True:
                plot_features['line_'+e].visible = True
                first_event = False
            else:
                plot_features['line_'+e].visible = False

            plot.yaxis.formatter = FuncTickFormatter(code=
                """
                return Math.floor(tick/60) + ":" + tick.toFixed(2)
                """
            )

        else:
            plot_features['line_'+e] = None

    # callback shows and hides lines depending on Select box
    callback = CustomJS(args=dict(
            line_50_free=plot_features['line_50_free'],
            line_100_free=plot_features['line_100_free'],
            line_200_free=plot_features['line_200_free'],
            line_500_free=plot_features['line_500_free'],
            line_1000_free=plot_features['line_1000_free'],
            line_50_back=plot_features['line_50_back'],
            line_100_back=plot_features['line_100_back'],
            line_200_back=plot_features['line_200_back'],
            line_50_breast=plot_features['line_50_breast'],
            line_100_breast=plot_features['line_100_breast'],
            line_200_breast=plot_features['line_200_breast'],
            line_50_fly=plot_features['line_50_fly'],
            line_100_fly=plot_features['line_100_fly'],
            line_200_fly=plot_features['line_200_fly'],
            line_100_im=plot_features['line_100_im'],
            line_200_im=plot_features['line_200_im'],
            line_400_im=plot_features['line_400_im'],
            line_base_free=plot_features['line_base_free'],
            line_base_back=plot_features['line_base_back'],
            line_base_breast=plot_features['line_base_breast'],
            line_base_fly=plot_features['line_base_fly'],
            line_base_im=plot_features['line_base_IM'],
        ), code="""
            f = cb_obj.value;

            if (line_50_free) { line_50_free.visible = false; }
            if (line_100_free) { line_100_free.visible = false; }
            if (line_200_free)  { line_200_free.visible = false; }
            if (line_500_free)  { line_500_free.visible = false; }
            if (line_1000_free)  { line_1000_free.visible = false; }
            if (line_50_back)  { line_50_back.visible = false; }
            if (line_100_back)  { line_100_back.visible = false; }
            if (line_200_back)  { line_200_back.visible = false; }
            if (line_50_breast)  { line_50_breast.visible = false; }
            if (line_100_breast)  { line_100_breast.visible = false; }
            if (line_200_breast)  { line_200_breast.visible = false; }
            if (line_50_fly)  { line_50_fly.visible = false; }
            if (line_100_fly)  { line_100_fly.visible = false; }
            if (line_200_fly)  { line_200_fly.visible = false; }
            if (line_100_im)  { line_100_im.visible = false; }
            if (line_200_im)  { line_200_im.visible = false; }
            if (line_400_im)  { line_400_im.visible = false; }
            if (line_base_free)  { line_base_free.visible = false; }
            if (line_base_back)  { line_base_back.visible = false; }
            if (line_base_breast)  { line_base_breast.visible = false; }
            if (line_base_fly)  { line_base_fly.visible = false; }
            if (line_base_im)  { line_base_im.visible = false; }

            if (f == "50 Freestyle") { line_50_free.visible = true; }
            else if (f == "100 Freestyle") { line_100_free.visible = true; }
            else if (f == "200 Freestyle")  { line_200_free.visible = true; }
            else if (f == "500 Freestyle")  { line_500_free.visible = true; }
            else if (f == "1000 Freestyle")  { line_1000_free.visible = true; }
            else if (f == "50 Backstroke")  { line_50_back.visible = true; }
            else if (f == "100 Backstroke")  { line_100_back.visible = true; }
            else if (f == "200 Backstroke")  { line_200_back.visible = true; }
            else if (f == "50 Breaststroke")  { line_50_breast.visible = true; }
            else if (f == "100 Breaststroke")  { line_100_breast.visible = true; }
            else if (f == "200 Breaststroke")  { line_200_breast.visible = true; }
            else if (f == "50 Butterfly")  { line_50_fly.visible = true; }
            else if (f == "100 Butterfly")  { line_100_fly.visible = true; }
            else if (f == "200 Butterfly")  { line_200_fly.visible = true; }
            else if (f == "100 IM")  { line_100_im.visible = true; }
            else if (f == "200 IM")  { line_200_im.visible = true; }
            else if (f == "400 IM")  { line_400_im.visible = true; }
            else if (f == "Base Freestyle")  { line_base_free.visible = true; }
            else if (f == "Base Backstroke")  { line_base_back.visible = true; }
            else if (f == "Base Breaststroke")  { line_base_breast.visible = true; }
            else if (f == "Base Butterfly")  { line_base_fly.visible = true; }
            else if (f == "Base IM")  { line_base_im.visible = true; }
    """)

    try:
        multi_select = Select(title="Select Event:", value=events[0], options=events, callback=callback)
        multi_select = widgetbox(multi_select, responsive=True)
        return components(column(multi_select, plot, responsive=True))
    except IndexError:
        return None, None
