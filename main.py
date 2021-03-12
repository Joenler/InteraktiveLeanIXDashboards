import json
import requests
import pandas as pd
import datetime
from helpers import *
auth_url, api_token, request_url = get_auth("authentification.json")

response = requests.post(auth_url,
                         auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status()
access_token = response.json()['access_token']
graphql_query = """{
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

data = {"query": graphql_query}
json_data = json.dumps(data)
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

response = requests.post(url=request_url, headers=header, data=json_data)
response.raise_for_status()
df = pd.json_normalize(response.json()['data']['allFactSheets']['edges'])
df = df[["node.name", "node.completion.percentage"]]
below25 = df[df["node.completion.percentage"] < 25]
below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
above50 = df[df["node.completion.percentage"] > 50]
description = df.describe()
with open("data.csv", 'a') as f:
    f.write(f"Dato: {datetime.date.today()} \n")
    f.write(f"Gennemsnitlig completion procent: {description.iloc[1, :].values[0].round(2)}% \n")

# df.to_excel('my_graphql_data.xlsx', index=False)
