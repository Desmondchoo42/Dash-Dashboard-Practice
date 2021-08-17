import plotly.express as px
import dash_bootstrap_components as dbc
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import dash_table

import pandas as pd
import json
from app import app

import base64
import datetime
import io

overview_layout = html.Div(
    [
        dbc.Row(
            [
                ## For upload box and filters
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.Strong("Data Upload"),
                                dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files')
                                    ]),
                                    style={
                                        'width': '90%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px',
                                        "background-color": "#f8f9fa",
                                    },
                                    # Allow multiple files to be uploaded
                                    multiple=True
                                ),
                                html.Div(id='output-data-upload'),
                                html.Br(),
                                html.Div(id='output-data-filters'),
                            ],style={"background-color": "#f8f9fa",}
                        )
                    ],width=2
                ),
                dbc.Col(
                    [
                    ## for table
                    html.Div(id='output-data-table')
                    ],
                    width=8
                ),
            ]
        ),
        ## Save the df here
        dcc.Store(id='stored-df')
    ]
)

@app.callback(
            Output('stored-df', 'data'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified')
            )

def to_store_df(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        small_dfs = []
        for c,n in zip(list_of_contents,list_of_names):
            small_dfs.append(parse_contents(c, n))

        df = pd.concat(small_dfs, ignore_index=True)

        # Date
        # Format checkin Time
        df["Date"] = pd.to_datetime(df["Date"])

        return df.to_json()
    else:
        return ""

@app.callback(
            [
                Output('output-data-upload', 'children'),
                Output('output-data-filters', 'children'),
                #Output('stored-df', 'data'),
            ],
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified')
            )

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        small_dfs = []
        for c,n in zip(list_of_contents,list_of_names):
            small_dfs.append(parse_contents(c, n))

        df = pd.concat(small_dfs, ignore_index=True)

        # Date
        # Format checkin Time
        df["Date"] = pd.to_datetime(df["Date"])
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        # User list
        user_list = df["User"].unique().tolist()
        options_user = [{'label':c,'value':c} for c in sorted(df.User.unique())]

        file_info = html.Div([html.Br(),
                    html.Strong("Uploaded File Info"),
                    html.Br(),
                    html.Label("File name: "+list_of_names[0]),
                    html.Br(),
                    html.Label("Time uploaded: "+str(datetime.datetime.fromtimestamp(list_of_dates[0]))) ],style={"background-color": "#f8f9fa",})

        filters = html.Div([
                    html.Strong("Select Filters"),
                    html.Br(),
                    html.Br(),
                    html.Label("Choose Time period"),
                    dcc.DatePickerRange(
                        id="date-picker-select",
                        start_date=min_date,
                        end_date=max_date,
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        initial_visible_month=min_date,
                    ),
                    html.Br(),
                    html.Br(),
                    html.Label("Filter by users"),
                    dcc.Dropdown(
                        id='user-select',
                        style={
                            'height': '150px',
                            'width': '250px',
                            'display': 'inline-block',
                        },
                        options=options_user,
                        value=user_list[:],
                        multi=True
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        id="submit-btn-outer",
                        children=html.Button(id="submit-btn", children="Submit", n_clicks=0),
                        #justify="center"
                    ),
                    html.Br(),
                    html.Br(),
                ],style={"background-color": "#f8f9fa",})
        return  file_info,  filters
    else:
        return "",""

@app.callback(
            Output('output-data-table', 'children'),
            Input('stored-df', 'data'),
            Input('submit-btn', 'n_clicks'),
            Input('user-select', 'value'),
            Input("date-picker-select", "start_date"),
            Input("date-picker-select", "end_date"),
            )

def update_table(data_json,n_clicks,user,start,end):
    df = pd.read_json(data_json)
    if n_clicks == 0:
        table = html.Div([
                    dash_table.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'lineHeight': '15px'
                        },
                        data=df.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in df.columns]
                    )
                ])
    else:
        dff = df[
                (df["Date"]>=start) &
                (df["Date"]<=end) &
                (df["User"].isin(user))
                ]
        table = html.Div([
                    dash_table.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'lineHeight': '15px'
                        },
                        data=dff.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in df.columns]
                    )
                ])
    return table

def parse_contents(contents, filename):
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

        df["filename"] = filename

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df
