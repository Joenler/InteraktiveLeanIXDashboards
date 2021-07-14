import pandas as pd
import plotly.express as px
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pathlib import Path
from entities.constants import *
from core.helpers import make_tag_groups, filter_tag_group, response_to_df, query_leanix

#############
#  HELPERS  #
#############


#############
# Read data #
#############

app = dash.Dash(__name__)
df = response_to_df(query_leanix(QUERY_TAGS, auth="../authentication.json"), field="tag_groups")
tag_groups = make_tag_groups(df)
names = tag_groups.name
######################
#  Dashboard Layout  #
######################

app.layout = html.Div([
    html.H1("Tag grupper... ", style={'text_align': 'center'}),
    dcc.Dropdown(id='dropdown',
                 options=[{"label": v, "value": v} for v in names],
                 searchable=False,
                 clearable=False,
                 value=names.head(1)[0],
                 placeholder="Vælg en tag gruppe"),
    dcc.Graph(id="tag_group_pie", figure={})
])

######################
# Dashboard Callback #
######################

@app.callback(
    Output('tag_group_pie', 'figure'),
    [Input('dropdown', 'value')]
)
def update_output(value):
    selected_value = filter_tag_group(tag_groups, value)
    fig = px.pie(selected_value, values=selected_value.fact_sheets.dropna(),
                 names=selected_value.tag_name.dropna())
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
