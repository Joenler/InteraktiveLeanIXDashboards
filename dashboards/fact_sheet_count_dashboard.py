import pandas as pd
import plotly.express as px
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pathlib import Path

#####################
# Read data into df #
#####################

data_folder = Path("../datasets/")
fp = data_folder / "synth_counts.csv"

app = dash.Dash(__name__)

# This is going to be replaced with some database call
df = pd.read_csv(fp, names=["date", "applications", "business_capabilities", "user_groups",
                            "projects", "processes", "interfaces", "data_objects",
                            "it_components", "providers", "technical_stacks"])
first_date = df['date'][0]
last_date = df['date'][len(df['date']) - 1]

######################
#  Dashboard Layout  #
######################

app.layout = html.Div([
    html.H1(f"Udviklingen i antal fakta ark over perioden fra {first_date} til {last_date}",
            style={'text_align': 'center'}),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Applications', 'value': 'applications'},
            {'label': 'Business Capabilities', 'value': 'business_capabilities'},
            {'label': 'User Groups', 'value': 'user_groups'},
            {'label': 'Projects', 'value': 'projects'},
            {'label': 'Processes', 'value': 'processes'},
            {'label': 'Interfaces', 'value': 'interfaces'},
            {'label': 'Data Objects', 'value': 'data_objects'},
            {'label': 'IT Components', 'value': 'it_components'},
            {'label': 'Providers', 'value': 'providers'},
            {'label': 'Technical Stacks', 'value': 'technical_stacks'}
        ],
        value='applications',
        searchable=False,
        placeholder='Vælg en type af fakta ark',
        multi=True
    ),
    dcc.Graph(id="fact_sheet_counts", figure={}, config={'scrollZoom': False})
], style={'width': "1200px", 'height': "500px"}
)
# TODO: konfigurer menuen og begræns valgmulighederne som brugeren har..
# TODO: fix beskrivelser og tekst


######################
# Dashboard Callback #
######################

@app.callback(
    Output('fact_sheet_counts', "figure"),
    [Input('dropdown', 'value')]
)
def update_output(value):
    dff = df.copy()
    fig = px.bar(data_frame=dff, x='date', y=value,
                 labels={"date": 'dato', "y": 'Antal fakta ark'}
                 )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
