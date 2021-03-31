import json
import requests
import pandas as pd
import datetime
import re
import csv
from collections.abc import Iterable
from constants import ROUNDING_PRECISION


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


def get_system_owners(df: pd.DataFrame) -> pd.DataFrame:
    regex = r'(\w+\@\w+\.\w+\.\w+)'
    df = df.rename(columns={"node.displayName": "Name", "node.relApplicationToUserGroup.edges": "System Owner"})
    user_group = df["System Owner"]
    length = len(user_group)
    for i in range(length):
        try:
            if user_group[i][0]["node"]["usageType"] == "owner":
                if re.search(regex, user_group.iloc[i][0]["node"]["description"]) is not None:
                    match = re.search(regex, user_group.iloc[i][0]["node"]["description"]).group()
                    df["System Owner"].iloc[i] = match
                else:
                    df["System Owner"].iloc[i] = ""
            elif user_group[i][0]["node"]["usageType"] == "user":
                df["System Owner"].iloc[i] = ""
        except IndexError:
            df["System Owner"].iloc[i] = ""
    return df


def get_completion_percentages(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["node.name", "node.completion.percentage"]]
    return df.rename(columns={"node.name": "Name", "node.completion.percentage": "Completion"})


def get_avg_completion(df: pd.DataFrame) -> float:
    return round(df["Completion"].mean(), ROUNDING_PRECISION)


def get_percent_system_owners(df: pd.DataFrame) -> tuple:
    has_system_owners = len(df[df["System Owner"] != ""])/len(df)
    no_system_owners = len(df[df["System Owner"] == ""]/len(df))
    return round(has_system_owners, ROUNDING_PRECISION), round(no_system_owners, ROUNDING_PRECISION)


def insert_into_csv(fp: str, data):
    if not isinstance(data, Iterable):
        data = [data]
    row = [f"{datetime.date.today()}"] + [f"{i}" for i in data]

    with open(fp, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(row)




