import pandas as pd
import plotly.express as px
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

#####################
# Read data into df #
#####################


df = pd.read_csv("systemOwners.csv", names=["Date", "No_System_owner", "Has_System_owner"])


######################
#  Dashboard Layout  #
######################

app.layout = html.Div([
    html.H1("Percentage of application fact sheets with a system owner", id="Title"),

    dcc.DatePickerSingle(
        id="date-picker-single",
        min_date_allowed=date(2021, 3, 19),  # Here we will have the earliest date in the database.
        max_date_allowed=date(2021, 4, 24),  # Here we will have the latest date in the database.
        initial_visible_month=date(2021, 3, 19),  # Here we will have the current date
        date=date(2021, 3, 19),  # Here we will have the earliest date in the database.
        style={"width": "415", "height": "40", "text-align": "left"}
    ),
    dcc.Graph(id="pie-chart", figure={}, style={"width": "415", "height": "200", "text-align": "left"}),

     html.Div(
         dcc.Graph(id="bar-plot", figure={}, style={"width": "415", "height": "240", "text-align": "center"})

     )


], style={"width": "1252", "height": "240"})



######################
# Dashboard Callback #
######################

@app.callback([Output(component_id="pie-chart", component_property="figure"),
               Output(component_id="bar-plot", component_property="figure")],
               [Input(component_id="date-picker-single", component_property="date")]
              )
def update_graphs(input_date):
    dff = df.copy()
    dff = dff[dff.Date == input_date]
    dff = dff[["No_System_owner", "Has_System_owner"]].head(1)
    print(dff)
    fig1 = px.pie(dff ,values=["No_System_owner", "Has_System_owner"])
    fig2 = px.bar(data_frame=dff)

    return [fig1, fig2]

if __name__ == '__main__':
    app.run_server(debug=True)
