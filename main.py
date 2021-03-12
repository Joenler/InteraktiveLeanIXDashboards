import pandas as pd
from helpers import *




df = pd.json_normalize(query_leanix( """{
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
    }""", "authentification.json").json()['data']['allFactSheets']['edges'])
df = df[["node.name", "node.completion.percentage"]]
below25 = df[df["node.completion.percentage"] < 25]
below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
above50 = df[df["node.completion.percentage"] > 50]
description = df.describe()
