import plotly.express as px
import pandas as pd

df1 = pd.read_csv("completions.csv")
df1 = df1.rename(columns={"2021-03-20": "date", "38.372": "percentage"})
fig1 = px.line(df1, x="date", y="percentage", title="Completion percentages over time.")
fig1.show()



df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_apple_stock.csv')

fig = px.line(df, x = 'AAPL_x', y = 'AAPL_y', title='Apple Share Prices over time (2014)')
fig.show()

