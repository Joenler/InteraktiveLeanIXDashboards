import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#####################
# Read data into df #
#####################

app = dash.Dash(__name__)

df = pd.read_csv("completions.csv", names=["Date", "Completion"])

######################
#  Dashboard Layout  #
######################

app.layout = html.Div([
    html.H1("Average completion percentage of the application fact sheets", style={'text-align': 'center'}),

    dcc.DatePickerRange(
        id="choose-period",
        min_date_allowed=date(2021, 3, 19),
        max_date_allowed=date(2021, 4, 24),
        initial_visible_month=date(2021, 3, 19),
        start_date=date(2021, 3, 19),
        end_date=date(2021, 4, 24),
        style={"width": "500px", 'text-align': 'center'}

    ),

    dcc.Graph(id='completions', figure={})

], style={'width': "500px", 'height': "500px"})

######################
# Dashboard Callback #
######################

@app.callback(
    Output('completions', "figure"),
    [Input("choose-period", "start_date"),
     Input("choose-period", "end_date")])
def update_output(start_date, end_date):

    dff = df.copy()
    dff = dff[(dff['Date'] > start_date) & (dff['Date'] <= end_date)]
    fig = px.line(
        x=dff["Date"],
        y=dff["Completion"],
        labels={"x": "Date", "y": "Completion"}

        )


    return fig



if __name__ == '__main__':
    app.run_server(debug=True)



