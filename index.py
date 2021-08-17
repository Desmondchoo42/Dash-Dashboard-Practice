
import dash_bootstrap_components as dbc
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from app import app

# Connect to the layout and callbacks of each tab
from overview_1 import overview_layout
# from analysis import analysis_layout

# our app's Tabs *********************************************************
app_tabs = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Overview", tab_id="tab-overview", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                dbc.Tab(label="Analysis", tab_id="tab-anaylsis", labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
            ],
            id="tabs",
            active_tab="tab-overview",
        ),
    ], className="mt-3"
)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("TopiKchat App",
                            style={"textAlign": "center"}), width=12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    html.Div(id='content', children=[])
],fluid=True)

@app.callback(
    Output("content", "children"),
    [Input("tabs", "active_tab")]
)
def switch_tab(tab_chosen):
    if tab_chosen == "tab-overview":
        return overview_layout
    elif tab_chosen == "tab-analysis":
        return analysis_layout
    return html.P("This shouldn't be displayed for now...")

if __name__=='__main__':
    app.run_server(debug=True)
