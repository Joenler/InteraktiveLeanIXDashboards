import json
import requests
import pandas as pd
import datetime
import re

def get_auth(config_file: str) -> tuple:
    with open(config_file) as f:
        data = json.load(f)
        return data["api_token"], data["auth_url"], data["request_url"]


def query_leanix(query: str, auth: str) -> requests.Response:
    authentication = get_auth(auth)
    response = requests.post(authentication[1],
                             auth=('apitoken', authentication[0]),
                             data={'grant_type': 'client_credentials'})
    access_token = response.json()['access_token']

    data = {"query": query}
    json_data = json.dumps(data)
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}

    return requests.post(url=authentication[2], headers=header, data=json_data)


def response_to_df(response: requests.Response) -> pd.DataFrame:
    return pd.json_normalize(response.json()['data']['allFactSheets']['edges'])


def get_completion_percentages(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["node.name", "node.completion.percentage"]]
    return df.rename(columns={"node.name": "Name", "node.completion.percentage": "Completion"})


def get_avg_completion(df: pd.DataFrame) -> float:
    return df["Completion"].mean()


def get_system_owners(df: pd.DataFrame):
    regex2 = r'(\w+\@\w+\.\w+\.\w+)'
    regex = r'(Systemejer:) (\w+) (\w+|\w\.) (\w+|\w\.| )*(\<)(\w+\@\w+\.\w+\.\w+)( |\>)+'
    df = df.rename(columns={"node.displayName": "Name", "node.relApplicationToUserGroup.edges": "User Group"})
    user_group = df["User Group"]
    li = []
    length = len(user_group)
    for i in range(length):
        for j in range(len(user_group[i])):
            if user_group[i][j]["node"]["usageType"] == "owner":
                li.append(user_group[i][j]['node']['description'])
            elif user_group[i][j]["node"]["usageType"] == "user":
                break
            else:
                li.append("None")
                break

    df["Owner"] = li
    return df


def insert_into_csv(fp: str, data):
    with open(fp) as f:
        f.write(str(data) + str(datetime.datetime.now()) + "\n")


