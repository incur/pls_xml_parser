import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from outliers import smirnov_grubbs as grubbs
import plotly.io as pio


def machine_plots(df, plot_path):
    config = [
        {'name': 'Lösebehälter', 'idx1': '10', 'idx2': '11', 'label1': 'Lösebhälter CIP',
         'label2': 'Lösebehälter SIP', 'file': 'löse.html'},
        {'name': 'Partikelfiltration', 'idx1': '12', 'idx2': '13', 'label1': 'Partikelfiltration CIP',
         'label2': 'Partikelfiltration SIP', 'file': 'partikel.html'},
        {'name': 'Ansatz Transfer', 'idx1': '4', 'idx2': '5', 'label1': 'Transfer CIP',
         'label2': 'Transfer SIP', 'file': 'trans.html'},
        {'name': 'Abfüllbehälter CIP', 'idx1': '0', 'idx2': '2', 'label1': 'Abfüllbehälter 1 CIP',
         'label2': 'Abfüllbehälter 2 CIP', 'file': 'abCip.html'},
        {'name': 'Abfüllbehälter SIP', 'idx1': '1', 'idx2': '3', 'label1': 'Abfüllbehälter 1 SIP',
         'label2': 'Abfüllbehälter 2 SIP', 'file': 'abSip.html'},
        {'name': 'Keimfiltration CIP', 'idx1': '6', 'idx2': '8', 'label1': 'Keimfiltration 1 CIP',
         'label2': 'Keimfiltration 2 CIP', 'file': 'keimCip.html'},
        {'name': 'Keimfiltration SIP', 'idx1': '7', 'idx2': '9', 'label1': 'Keimfiltration 1 SIP',
         'label2': 'Keimfiltration 2 SIP', 'file': 'keimSip.html'},
        {'name': 'Abfüllknoten', 'idx1': '15', 'idx2': '16', 'label1': 'VK CIP',
         'label2': 'VK SIP', 'file': 'vk.html'}
    ]

    for plot in config:
        df_plot1 = make_data(df, int(plot['idx1']))
        df_plot2 = make_data(df, int(plot['idx2']))

        fig = make_subplots(rows=2, cols=3, column_widths=[0.8, 0.1, 0.1], horizontal_spacing=0.03,
                            vertical_spacing=0.08,
                            subplot_titles=(f'{plot["label1"]}', '', '', f'{plot["label2"]}'))

        fig.update_xaxes(linecolor="#BCCCDC", showgrid=False)
        fig.update_yaxes(linecolor="#BCCCDC", showgrid=False)
        fig.update_layout(plot_bgcolor="#FFF")

        fig.add_trace(
            go.Scatter(x=df_plot1['start'], y=df_plot1['y_avg'], name=plot['label1'],
                       line=dict(color='#636EFA', width=4)
                       ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=df_plot1['start'], y=df_plot1['y_orig'], visible='legendonly', name='data_original',
                       line=dict(color='#EF553B')
                       ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=df_plot1['start'], y=df_plot1['y_grubb'], visible='legendonly', name='data_grubb',
                       line=dict(color='#EF553B')
                       ),
            row=1, col=1
        )

        fig.add_trace(
            go.Violin(y=df_plot1['y_orig'], name='outliers',
                      fillcolor='#00CC96', line=dict(color='#00CC96'), hoverinfo='y+z'
                      ),
            row=1, col=2
        )

        fig.add_trace(
            go.Violin(y=df_plot1['y_grubb'], name='distribution',
                      fillcolor='#AB63FA', line=dict(color='#AB63FA'), hoverinfo='y+z'
                      ),
            row=1, col=3
        )

        fig.add_trace(
            go.Scatter(x=df_plot2['start'], y=df_plot2['y_avg'], name=plot['label2'],
                       line=dict(color='#636EFA', width=4)
                       ),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(x=df_plot2['start'], y=df_plot2['y_orig'], visible='legendonly', name='data_original',
                       line=dict(color='#EF553B')
                       ),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(x=df_plot2['start'], y=df_plot2['y_grubb'], visible='legendonly', name='data_grubb',
                       line=dict(color='#EF553B')
                       ),
            row=2, col=1
        )

        fig.add_trace(
            go.Violin(y=df_plot2['y_orig'], name='outliers',
                      fillcolor='#00CC96', line=dict(color='#00CC96'), hoverinfo='y+z'
                      ),
            row=2, col=2
        )

        fig.add_trace(
            go.Violin(y=df_plot2['y_grubb'], name='distribution',
                      fillcolor='#AB63FA', line=dict(color='#AB63FA'), hoverinfo='y+z'
                      ),
            row=2, col=3
        )

        fig.update_layout(title_text=f'{plot["name"]}')
        pio.write_html(fig, file=f'{plot_path}{plot["file"]}', auto_open=False)


def make_data(mf, idx=1):
    machines = features(mf)
    machine = machines[idx]
    df = mf.loc[mf['anlage'] == machine['value']].copy()
    df.reset_index(drop=True, inplace=True)

    y = df['diffm']
    x = df['start']

    # Remove Outlier
    df_avg = df.copy()
    median = df_avg.diffm.median()
    indices = grubbs.two_sided_test_indices(df_avg['diffm'].to_numpy(), alpha=.05)
    df_avg.loc[indices, 'diffm'] = median
    x_grubb = df_avg['start']
    y_grubb = df_avg['diffm']

    # Smooth
    grubb_filter = df_avg.set_index('start').diffm.rolling(window=remap(2)).mean()
    y_avg = grubb_filter.values
    x_avg = grubb_filter.index

    list_of_orig = list(zip(x, y))
    df_orig = pd.DataFrame(list_of_orig, columns=['start', 'y_orig'])

    list_of_avg = list(zip(x_avg, y_avg))
    df_avg = pd.DataFrame(list_of_avg, columns=['start', 'y_avg'])

    list_of_grubb = list(zip(x_grubb, y_grubb))
    df_grubb = pd.DataFrame(list_of_grubb, columns=['start', 'y_grubb'])

    df_data = pd.merge(df_orig, df_grubb, how='outer', on='start')
    df_data = pd.merge(df_data, df_avg, how='outer', on='start')

    return df_data


def features(df):
    options = list(np.sort(df['anlage'].unique()))
    dict_list = []

    for o in options:
        machine = list(df.loc[df['anlage'] == o].values[0])
        label = f'{machine[2]} {machine[3][:3]}'
        if machine[4] == 'RP23_CIP_FUELLER':
            label = f'{machine[2]} {machine[3][:3]} FUELLER'
        dict_list.append({'value': o, 'label': label})

    return dict_list


def remap(value, in_min=0, in_max=5, out_min=0, out_max=50):
    in_span = in_max - in_min
    out_span = out_max - out_min
    value_scaled = float(value - in_min) / float(in_span)
    result = out_min + (value_scaled * out_span)

    return int(result)
