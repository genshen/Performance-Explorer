#!/usr/bin/env python3
import base64
import datetime
import io
import time

from dash import Dash, html, dcc, dash_table, ctx
from dash.dependencies import Input, Output, State
import dash
import plotly.express as px
import pandas as pd

from speedup_versus import *

colors = {
    'background': '#111111',
    'text': '#0969da'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(children=[
    html.H1(
        children='Performance Explorer',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Performance Explorer: A plot application for HPC performance optimization.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=[
            html.Div(id="output-file-metadata"),
            html.Div([
                html.Hr(),
                html.Div(className = "row", children = [
                    html.Div(className = "three columns", children = [
                        html.Label("Matrix Name Column:"),
                        dcc.Dropdown(id='header-selector-mtx-name', placeholder="Select a Column for Matrix name", style={'margin-top': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("X Axis Column:"),
                        dcc.Dropdown(id='header-selector-x_axis', placeholder="Select a Column for x axis", style={'margin-top': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Y Axis Column:"),
                        dcc.Dropdown(id='header-selector-y_axis', placeholder="Select a Column for y axis", style={'margin-top': '0.3rem'}),
                    ]),
                ]),
                html.Div(className = "row", children = [
                    html.Div(className = "three columns", children = [
                        html.Label("Algorithm Column:"),
                        dcc.Dropdown(id='header-selector-strategy', placeholder="Select a Column for Algorithms", style={'margin-top': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Algorithm 1:"),
                        dcc.Dropdown(id='inp_alg_1', placeholder="Select a Column for Algorithm A", style={'margin-top': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Algorithm 2:"),
                        dcc.Dropdown(id='inp_alg_2', placeholder="Select a Column for Algorithm B", style={'margin-bottom': '0.3rem'}),
                    ]),
                ]),
                html.P("Plot Style:", style={'margin-top': '0.3rem', "margin-bottom": "0.1rem"}),
                html.Div(className = "row", children = [
                    html.Div(className = "three columns", children = [
                        html.Label("X Axis Title:"),
                        dcc.Input(id="plot_style_xaxis_title", value="NNZ", placeholder="xaxis title", style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Y Axis Title:"),
                        dcc.Input(id="plot_style_yaxis_title", value="FLOPS", placeholder="yaxis title", style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Plot Width:"),
                        dcc.Input(id="plot_style_width", value="1200", placeholder="Plot width", style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Plot Height:"),
                        dcc.Input(id="plot_style_height", value="600", placeholder="Plot height", style={'margin': '0.3rem'}),
                    ]),
                ]),
                html.Div(className = "row", children = [
                    html.Div(className = "three columns", children = [
                        html.Label("Color in Plot:"),
                        dcc.Input(id="plot_style_color", value="rgba(0,100,80, 0.75)", placeholder="Color in plot, e.g. #efefef or rgba(0,100,80, 0.75)", style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Font Color:"),
                        dcc.Input(id="plot_style_font_color", value="#000000", placeholder="Font color. e.g. #efefef or rgba(0,100,80, 0.75)", style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Font Size:"),
                        dcc.Input(id="plot_style_font_size", value="18", placeholder="Font size. e.g. 18", style={'margin': '0.3rem'}),
                    ]),
                ]),
                html.Div(className = "row", children = [
                    html.Div(className = "three columns", children = [
                        html.Label("Show Legend?:"),
                        dcc.RadioItems(id="plot_style_showlegend", options=[{'label': 'Show legend', 'value': 'yes'}, {'label': 'Hide legend', 'value': 'no'}], value='yes', style={'margin': '0.3rem'}),
                    ]),
                    html.Div(className = "three columns", children = [
                        html.Label("Legend Title:"),
                        dcc.Input(id="plot_style_legend_title", value="Algorithms", placeholder="legend title", style={'margin': '0.3rem'}),
                    ]),
                ]),
            ]),
            html.Button(id='submit-button-state', n_clicks=0, children='Show Plot', className='button-primary', style={'margin': '0.3rem'}), 
            html.Button(id='dl-button', n_clicks=0, children='📎 Download pdf', style={'margin': '0.3rem'}), 
            html.Hr(),
            html.Div(id='output-state')
        ]
    ),

    dcc.Loading(
        id="loading-2",
        type="default",
        children=html.Div(id="output-data-upload")
    ),
    dcc.Download(id="download-plot"),
])

# parse the csv performance file and retuen dataframe.
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df

# set strategy dropdown options
@app.callback(
    Output('inp_alg_1', 'options'),
    Output('inp_alg_2', 'options'),
    Input('header-selector-strategy', 'value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'))
def set_algorithm_options(selected_csv_col, list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is None:
        return [], []
    else:
        # 
        # todo: parse multiple input files.
        df = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0])
        
        # todo: check the algorithm cloumn exists.
        unique_keys = pd.unique(df[selected_csv_col]).tolist()
        unique_keys.sort()
        options = [{'label': k, 'value': k} for k in unique_keys[:32]] # we allow max 32 different strategy.
        return options, options

# on buttion click, download the performance figure.
@app.callback(Output("download-plot", "data"),
              Input('dl-button', 'n_clicks'),
              State('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('header-selector-mtx-name', 'value'),
              State('header-selector-x_axis', 'value'),
              State('header-selector-y_axis', 'value'),
              State('inp_alg_1', 'value'),
              State('inp_alg_2', 'value'),
              # plot style:
              State("plot_style_color", 'value'),
              State("plot_style_font_color", 'value'),
              State("plot_style_font_size", 'value'),
              State("plot_style_xaxis_title", 'value'),
              State("plot_style_yaxis_title", 'value'),
              State("plot_style_showlegend", 'value'),
              State("plot_style_legend_title", 'value'),
              State("plot_style_width", 'value'),
              State("plot_style_height", 'value'),
            )
def dl_plot(n_clicks, list_of_contents, list_of_names, list_of_dates, mtx_name_key, x_axis, y_axis, alg_1, alg_2,
    plot_color, plot_font_color, plot_font_size, plot_xaxis_title, plot_yaxis_title, plot_showlegend,
    plot_legend_title, plot_width, plot_height):
    button_id = ctx.triggered_id
    if button_id == None:
        return dash.no_update

    if button_id == "dl-button":
        # todo: parse multiple input files.
        df = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0])
        conf_showlegend = True if plot_showlegend == "yes" else False
        config = PlotConfig(plot_color, plot_font_color, int(plot_font_size), plot_xaxis_title, plot_yaxis_title, conf_showlegend, plot_legend_title, int(plot_width), int(plot_height))
        fig = gen_plot_speedup(df, alg_1, alg_2, mtx_name_key, x_axis, y_axis, config)
        output_path = "./fig-plot.pdf" # todo: file conflict if we have more than 1 user.
        fig.write_image(output_path)
        # download fig
        return dcc.send_file(output_path)
    return dash.no_update

# on buttion click, draw the performance figure.
@app.callback(Output('output-data-upload', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('header-selector-mtx-name', 'value'),
              State('header-selector-x_axis', 'value'),
              State('header-selector-y_axis', 'value'),
              State('inp_alg_1', 'value'),
              State('inp_alg_2', 'value'),
              # plot style:
              State("plot_style_color", 'value'),
              State("plot_style_font_color", 'value'),
              State("plot_style_font_size", 'value'),
              State("plot_style_xaxis_title", 'value'),
              State("plot_style_yaxis_title", 'value'),
              State("plot_style_showlegend", 'value'),
              State("plot_style_legend_title", 'value'),
              State("plot_style_width", 'value'),
              State("plot_style_height", 'value'),
            )
def update_output(n_clicks, list_of_contents, list_of_names, list_of_dates, mtx_name_key, x_axis, y_axis, alg_1, alg_2,
    plot_color, plot_font_color, plot_font_size, plot_xaxis_title, plot_yaxis_title, plot_showlegend,
    plot_legend_title, plot_width, plot_height):
    if list_of_contents is None:
        print("NONE")
    else:
        # todo: parse multiple input files.
        df = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0])
        conf_showlegend = True if plot_showlegend == "yes" else False
        config = PlotConfig(plot_color, plot_font_color, int(plot_font_size), plot_xaxis_title, plot_yaxis_title, conf_showlegend, plot_legend_title, int(plot_width), int(plot_height))
        fig = gen_plot_speedup(df, alg_1, alg_2, mtx_name_key, x_axis, y_axis, config)
        # render fig
        return html.Div([
            dcc.Graph(
                id='perf-graph',
                figure=fig
            ),
            dash_table.DataTable(
                df.to_dict('records'),
                [{'name': i, 'id': i} for i in df.columns]
            ),

            html.Hr(),  # horizontal line
        ])
        

@app.callback(Output('header-selector-mtx-name', 'options'),
              Output('header-selector-x_axis', 'options'),
              Output('header-selector-y_axis', 'options'),
              Output('header-selector-strategy', 'options'),
              Output('output-file-metadata', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        headers = [parse_contents(c, n, d).columns.tolist() for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        dropdown_header = [{'label': header_item, 'value': header_item} for header_item in headers[0]]
        filename = list_of_names[0] # todo: more files?
        file_date = list_of_dates[0]
        file_meta_component = html.Div([html.P(filename), html.P(datetime.datetime.fromtimestamp(file_date))])
        return dropdown_header, dropdown_header, dropdown_header, dropdown_header, file_meta_component
    else:
        return [], [], [], [], None

if __name__ == '__main__':
    app.run_server(debug=True)
