import pandas as pd
import plotly.express as px
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#####################
# Read data into df #
#####################

app = dash.Dash(__name__)

# This is going to be replaced with some database call
df = pd.read_csv("../datasets/completions.csv", names=["Date", "Completion"])

######################
#  Dashboard Layout  #
######################

app.layout = html.Div([
    html.H1("Average completion percentage of the application fact sheets", style={'text-align': 'center'}),

    dcc.DatePickerRange(
        id="choose-period",
        min_date_allowed=date(2021, 3, 19),  # Here we will have the earliest date in the database.
        max_date_allowed=date(2021, 4, 24),  # Here we will have the latest date in the database.
        initial_visible_month=date(2021, 3, 19),  # Here we will have the current date
        start_date=date(2021, 3, 19),  # Here we will have the earliest date in the database.
        end_date=date(2021, 4, 24),  # Here we will have the latest date in the database.
        style={"width": "648px", 'text-align': 'center'}

    ),

    dcc.Graph(id='completions', figure={})

], style={'width': "648px", 'height': "384px"})

######################
# Dashboard Callback #
######################

'''
Fremgang for afdelingerne vist ved hover. Find data i Excel Arket.
'''


@app.callback(
    Output('completions', "figure"),
    [Input("choose-period", "start_date"),
     Input("choose-period", "end_date")])
def update_output(start_date, end_date):

    dff = df.copy()  # In the future we will fetch the relevant data from a database instead.
    dff = dff[(dff['Date'] > start_date) & (dff['Date'] <= end_date)]
    fig = px.line(
        x=dff["Date"],
        y=dff["Completion"],
        labels={"x": "Date", "y": "Completion in %"}

        )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)



