import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

df = pd.read_csv('assets/output/raw.csv')
df['start'] = pd.to_datetime(df['start'])
df['ende'] = pd.to_datetime(df['ende'])


def get_options(list_machine):
    list_machine = np.sort(list_machine)
    dict_list = []
    for i in list_machine:
        dict_list.append({'label': i, 'value': i})

    return dict_list


def remap(value, inMin=0, inMax=5, outMin=0, outMax=50):
    inSpan = inMax - inMin
    outSpan = outMax - outMin

    valueScaled = float(value - inMin) / float(inSpan)
    result = outMin + (valueScaled * outSpan)

    return int(result)


def layout():
    return html.Div(children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2('sConv - PCS7 Dashboard'),
                                  html.P('Visualising time series Data from sConv.'),
                                  html.P('Pick one or more machines from the dropdown below.'),
                                  html.Br(),
                                  html.H3('Zeit'),
                                  html.Div(className='div-for-dropdown', children=[
                                      dcc.DatePickerRange(
                                          id='date-picker',
                                          display_format='YYYY-MM-DD',
                                          clearable=True,
                                          start_date=df['start'].min(),
                                          end_date=df['start'].max(),
                                          min_date_allowed=df['start'].min(),
                                          max_date_allowed=df['start'].max(),
                                          start_date_id='sdid',
                                          end_date_id='edid',
                                          style={'background-color': '#1E1E1E'}
                                          )
                                  ]),
                                  html.Br(),
                                  html.H3('Chart #1'),
                                  html.Div(className='div-for-dropdown',
                                           children=[
                                               dcc.Dropdown(id='stockselector', options=get_options(df['anlage'].unique()),
                                                            multi=True, value=[df['anlage'].sort_values()[0]],
                                                            style={'background-color': '#1E1E1E'},
                                                            className='stockselector'
                                                            )],
                                           style={'color': '#1E1E1E'}),
                                  html.Div(className='div-for-slider',
                                           children=[
                                               dcc.Slider(id='smoothslider',
                                                          min=1, max=5,
                                                          marks={i: '{}'.format(i) for i in range(1, 6)},
                                                          value=2)
                                               ]),
                                  html.Div(className='div-for-slider',
                                           children=[
                                               dcc.RadioItems(id='radio',
                                                              options=[
                                                                  {'label': 'Line', 'value': 'line'},
                                                                  {'label': 'Line Range', 'value': 'liner'},
                                                                  {'label': 'Violin', 'value': 'violin'},
                                                                  {'label': 'Stats', 'value': 'table'}
                                                                  ], value='line',
                                                              labelStyle={'display': 'inline-block'}
                                                              )
                                               ]),
                                  html.Br(),
                                  html.H3('Chart #2'),
                                  html.Div(className='div-for-dropdown',
                                           children=[
                                               dcc.Dropdown(id='stockselector2', options=get_options(df['anlage'].unique()),
                                                            multi=True, value=[df['anlage'].sort_values()[0]],
                                                            style={'background-color': '#1E1E1E'},
                                                            className='stockselector2'
                                                            )
                                               ],
                                           style={'color': '#1E1E1E'}),
                                  html.Div(className='div-for-slider',
                                           children=[
                                               dcc.Slider(id='smoothslider2',
                                                          min=1, max=5,
                                                          marks={i: '{}'.format(i) for i in range(1, 6)},
                                                          value=2)
                                               ]),
                                  html.Div(className='div-for-slider',
                                           children=[
                                               dcc.RadioItems(id='radio2',
                                                              options=[
                                                                  {'label': 'Line', 'value': 'line'},
                                                                  {'label': 'Line Range', 'value': 'liner'},
                                                                  {'label': 'Violin', 'value': 'violin'},
                                                                  {'label': 'Stats', 'value': 'table'}
                                                                  ], value='violin',
                                                              labelStyle={'display': 'inline-block'}
                                                              )
                                               ]),
                                  ]),
                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  html.Div(id='output', className='div-for-charts')
                              ])
                     ])
        ])


def callback(app):
    @app.callback(Output('output', 'children'),
                  [Input('stockselector', 'value'), Input('smoothslider', 'value'),
                   Input('stockselector2', 'value'), Input('smoothslider2', 'value'),
                   Input('date-picker', 'start_date'), Input('date-picker', 'end_date'),
                   Input('radio', 'value'), Input('radio2', 'value')])
    def display_graphs(selected_values, slider, selected_values2, slider2, start_date, end_date, radio, radio2):
        graphs = []
        df_sub = df

        if not start_date:
            start_date = df_sub['start'].min()

        if not end_date:
            end_date = df_sub['start'].max()

        if start_date and end_date:
            df_time = df_sub[(df_sub.start > start_date) & (df_sub.start <= end_date)]

        if selected_values:
            if radio == 'line':
                graphs.append(lineplot(df_time, selected_values, slider))
            elif radio == 'liner':
                graphs.append(line_rangeplot(df_time, selected_values, slider))
            elif radio == 'violin':
                graphs.append(violinplot(df_time, selected_values, slider))
            elif radio == 'table':
                graphs.append(stattable(df_time, selected_values, slider))

        if selected_values2:
            if radio2 == 'line':
                graphs.append(lineplot(df_time, selected_values2, slider2))
            elif radio2 == 'liner':
                graphs.append(line_rangeplot(df_time, selected_values2, slider2))
            elif radio2 == 'violin':
                graphs.append(violinplot(df_time, selected_values2, slider2))
            elif radio == 'table':
                graphs.append(stattable(df_time, selected_values, slider))

        return graphs


def lineplot(df, values, slider):
    trace = []
    for value in values:
        df_filter = df[df.anlage == value].set_index('start').diffm.rolling(window=remap(slider)).mean()
        trace.append(go.Scatter(x=df_filter.index,
                                y=df_filter.values,
                                mode='lines', opacity=0.7, name=value,
                                textposition='bottom center'))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data, 'layout': go.Layout(
        template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15}, hovermode='x', autosize=True, yaxis={'title': 'Laufzeit [ min ]'}
    )}

    return html.Div(dcc.Graph(figure=figure, config={'displayModeBar': False}, animate=False))


def line_rangeplot(df, values, slider):
    trace = []
    for value in values:
        df_filter = df[df.anlage == value].set_index('start').diffm.rolling(window=remap(slider)).mean()
        trace.append(go.Scatter(x=df_filter.index,
                                y=df_filter.values,
                                mode='lines', opacity=0.7, name=value,
                                textposition='bottom center'))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data, 'layout': go.Layout(
        template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15}, hovermode='x', autosize=True,
        xaxis={'rangeslider': {'visible': True}}, yaxis={'title': 'Laufzeit [ min ]'}
    )}

    return html.Div(dcc.Graph(figure=figure, config={'displayModeBar': False}, animate=False))


def violinplot(df, values, slider):
    trace = []
    for value in values:
        df_filter = df[df.anlage == value].set_index('start').diffm.rolling(window=remap(slider)).mean()
        trace.append(go.Violin(x=df_filter.values,
                               name=value,
                               box_visible=True,
                               meanline_visible=True))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data, 'layout': go.Layout(
        template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15}, autosize=True, barmode='overlay', xaxis={'title': 'Laufzeit [ min ]'}
    )}

    return html.Div(dcc.Graph(figure=figure, config={'displayModeBar': False}, animate=False))


def stattable(df, values, slider):
    head = ['Stats']
    val = [['Mittelwert', 'Min', 'Max', 'Median', 'StdAbw', 'Varianz']]
    for value in values:
        df_filter = df[df.anlage == value].set_index('start').diffm.rolling(window=remap(slider)).mean()
        df_filter = df_filter[~np.isnan(df_filter)]
        if df_filter.size != 0:
            head.append(value)
            val.append([f'{int(round(np.nanmean(df_filter.values)))} min',
                        f'{int(round(np.nanmin(df_filter.values)))} min',
                        f'{int(round(np.nanmax(df_filter.values)))} min',
                        f'{int(round(np.nanmedian(df_filter.values)))} min',
                        f'{int(round(np.nanstd(df_filter.values)))} min',
                        f'{int(round(np.nanvar(df_filter.values)))} min'])

    data = [go.Table(header=dict(values=head), cells=dict(values=val))]
    fig = {'data': data, 'layout': go.Layout(
        template='plotly_dark', paper_bgcolor='rgba(0, 0, 0, 0)', plot_bgcolor='rgba(0, 0, 0, 0)',
        margin={'b': 15}, hovermode='x', autosize=True)}

    return html.Div(dcc.Graph(figure=fig, config={'displayModeBar': False}, animate=False))



app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
app.layout = layout()
callback(app)

if __name__ == "__main__":
    app.run_server(debug=False)
