import pandas as pd
from helpers import *

query = """{
      allFactSheets(factSheetType: Application) {
        edges {
          node {
            name
            completion {
              completion
              percentage
                        }
            }
          }
        }
    }"""


# df = response_to_df(query_leanix(query, "authentification.json"))
# df = df[["node.name", "node.completion.percentage"]]
# below25 = df[df["node.completion.percentage"] < 25]
# below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
# above50 = df[df["node.completion.percentage"] > 50]
# description = df.describe()


from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "This is the main page!"

if __name__ == "__main__":
    app.run()