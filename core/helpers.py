import json
import random
import requests
import pandas as pd
import time
import datetime
import re
import csv
from collections.abc import Iterable
from typing import Union
from entities.constants import *
from pandas.api.types import CategoricalDtype
from itertools import chain
from entities import tag_group

def generate_auth_config():
    """
    Denne funktion beder brugeren indtaste en API nøgle
    og genererer derefter en JSON konfigurationsfil.
    :return: None
    """
    api_token = input("Indsæt din API nøgle her: ")
    auth_url = "https://app.leanix.net/services/mtm/v1/oauth2/token"
    request_url = "https://app.leanix.net/services/pathfinder/v1/graphql"
    with open("authentication.json", 'w') as f:
        f.write(json.dumps({'api_token': api_token,
                            'auth_url': auth_url,
                            'request_url': request_url}))
    with open(".gitignore", 'a') as f:
        f.write("authentication.json \n")


def get_auth(config_file: str) -> tuple:
    """
    Denne funktion læser indholdet af JSON konfigurationsfilen, som brugeren har genereret.
    :param config_file: En sti til authentication filen i form af en streng.
    :return: En tuple bestående af tre strenge: API token, auth url og request url.
    """
    with open(config_file) as f:
        data = json.load(f)
        return data["api_token"], data["auth_url"], data["request_url"]


def query_leanix(query: str, auth: str = "authentication.json") -> requests.Response:
    """
    Denne funktion sender en forspørgsel til LeanIX's API
    og returnerer svaret i form af et response objekt.
    :param query: En GraphQL query i string format. Du kan finde query string i constants filen.
    :param auth: En sti til authentication filen i form af en streng. Denne fil skal du selv lave.
    :return: Et response objekt. Dette gives videre til response_to_df.
    """
    try:
        authentication = get_auth(auth)
    except FileNotFoundError:
        authentication = get_auth("../authentication.json")

    response = requests.post(authentication[1],
                             auth=('apitoken', authentication[0]),
                             data={'grant_type': 'client_credentials'})
    access_token = response.json()['access_token']

    data = {"query": query}
    json_data = json.dumps(data)
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}

    return requests.post(url=authentication[2], headers=header, data=json_data)


def response_to_count(response: requests.Response):
    return response.json()['data']['allFactSheets']['totalCount']


def get_fact_sheet_counts(queries: list[str]):
    keys = ["Applications", "Business Capabilities", "User Groups",
            "Projects", "Processes", "Interfaces", "Data Objects",
            "IT Components", "Providers", "Technical Stacks"]
    responses = [query_leanix(q, "authentication.json") for q in queries]
    values = [v for v in map(response_to_count, responses)]
    return dict(zip(keys, values))


def response_to_df(response: requests.Response, field="fact_sheets") -> pd.DataFrame:
    """
    Denne funktion laver et response objekt om til en pandas dataframe.
    Da GraphQL querien har mange lag, normaliseres data, allFactSheets og edges væk.
    :param response: Et response objekt med data fra LeanIX.
    :param field: Den type af field som query'et indeholder.
    :return: En dataframe som indeholder data fra LeanIX.
    """
    filter_key = ''
    if field == 'fact_sheets':
        filter_key = 'allFactSheets'
    elif field == 'tag_groups':
        filter_key = 'allTagGroups'
    elif field == 'tags':
        filter_key = 'allTags'
    elif field == 'tag':
        filter_key = 'tag'
    elif field == 'log_events':
        filter_key = 'allLogEvents'
    return pd.json_normalize(response.json()['data'][filter_key]['edges'])


def get_system_owners(df: pd.DataFrame) -> pd.DataFrame:
    regex = r'(\w+\@\w+\.\w+\.\w+)'
    df = df.rename(columns={"node.displayName": "Name",
                            "node.relApplicationToUserGroup.edges": "System Owner"})

    for i, user_grp in enumerate(df["System Owner"]):
        try:
            if user_grp[0]["node"]["usageType"] == "owner":
                if re.search(regex, user_grp[0]["node"]["description"]) is not None:
                    match = re.search(regex, user_grp[0]["node"]["description"]).group()
                    df["System Owner"].iloc[i] = match
                else:
                    df["System Owner"].iloc[i] = ""
            elif user_grp[i]["node"]["usageType"] == "user":
                df["System Owner"].iloc[i] = ""
        except IndexError:
            df["System Owner"].iloc[i] = ""
    return df


def create_column_names(df: pd.DataFrame) -> pd.DataFrame:
    column_names = ["ID", "Type", "Navn", "Display_Name",
                    "Alias", "Beskrivelse", "Systemejer",
                    "Systemforvalter"]
    underkategorier = ["UDS_", "DT_", "SS_", "TS_"]
    inddelinger = ["Økonomiklasse", "Manpower", "Eksterne_ydelser",
                   "Interne_ydelser", "Afdelingskontakt"]
    for k in underkategorier:
        for i in inddelinger:
            combined = k + i
            column_names.append(combined)
    remaining_names = ["Dataklassifikiation", "Økonomiklasse", "Persondata", "Hosting", "Livscyklus",
                       "Licensomkostninger", "Manpower", "Eksterne_ydelser", "Interne_ydelser",
                       "Total", "kommentarer", "Andet", "nan"]
    column_names += remaining_names
    df.columns = column_names

    return df


def parse_excel_sheet(fp: str) -> pd.DataFrame:
    df = create_column_names(pd.read_excel(fp)).drop(0)
    return df.drop(columns=["kommentarer", "Andet", "nan"])


def system_owner_count_from_excel(df: pd.DataFrame) -> int:
    return len(df[df["Systemejer"].notna()])


def reduce_df_to_relevant_cols(df: pd.DataFrame, cols: list[str] = None) -> pd.DataFrame:
    if not cols:
        cols = ["Navn", "Systemejer", "UDS_Økonomiklasse", "DT_Økonomiklasse",
                "SS_Økonomiklasse", "TS_Økonomiklasse", "Økonomiklasse"]
    return df[cols]


def categorize_cols(df: pd.DataFrame) -> pd.DataFrame:
    categories = CategoricalDtype(categories=["nan", "Ikke relevant", "Ukendt",
                                              "C økonomi", "B økonomi", "A økonomi"],
                                  ordered=True)
    cols_to_categorize = ["UDS_Økonomiklasse", "DT_Økonomiklasse",
                          "SS_Økonomiklasse", "TS_Økonomiklasse", "Økonomiklasse"]
    categorized_cols = df[cols_to_categorize].astype(categories)
    df[cols_to_categorize] = categorized_cols
    return df


def assign_economy_class_to(df: pd.DataFrame) -> pd.DataFrame:
    df = reduce_df_to_relevant_cols(df)
    df = categorize_cols(df)
    cols = ["UDS_Økonomiklasse", "DT_Økonomiklasse", "SS_Økonomiklasse", "TS_Økonomiklasse"]
    for i, _ in enumerate(df):
        df["Økonomiklasse"].iloc[i] = df[cols].iloc[i].max()

    return df


def count_economy_classes(df: pd.DataFrame) -> tuple[int, int, int]:
    a_ecos = df[df["Økonomiklasse"] == "A økonomi"].count()
    b_ecos = df[df["Økonomiklasse"] == "B økonomi"].count()
    c_ecos = df[df["Økonomiklasse"] == "C økonomi"].count()
    return a_ecos, b_ecos, c_ecos


def get_applications_not_in_leanix(df: pd.DataFrame, get_count: bool = False) -> Union[pd.DataFrame, int]:
    if get_count:
        return len(df[df["ID"].isna()])
    else:
        return df[df["ID"].isna()].reset_index(drop=True)


def get_completion_percentages(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["node.name", "node.completion.percentage"]]
    return df.rename(columns={"node.name": "Name", "node.completion.percentage": "Completion"})


def get_avg_completion(df: pd.DataFrame) -> float:
    return round(df["Completion"].mean(), ROUNDING_PRECISION)


def get_percent_system_owners(df: pd.DataFrame) -> tuple:
    total = len(df)
    has_system_owners = len(df[df["System Owner"] != ""]) / total
    no_system_owners = len(df[df["System Owner"] == ""]) / total
    return round(has_system_owners, ROUNDING_PRECISION), round(no_system_owners, ROUNDING_PRECISION)


def insert_into_csv(fp: str, data):
    if not isinstance(data, Iterable):
        data = [data]
    if isinstance(data, dict):
        row = [f"{datetime.date.today()}"] + [f"{i}" for i in data.values()]
    else:
        row = [f"{datetime.date.today()}"] + [f"{i}" for i in data]

    with open(fp, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(row)


def get_synth_dates(length):
    week = 21
    start_date = time.asctime(time.strptime('2021 %d 1' % week, '%Y %W %w'))
    start_date = datetime.datetime.strptime(start_date, '%a %b %d %H:%M:%S %Y').date()
    dates = [start_date]
    for i in range(1, length):
        dates.append(start_date + datetime.timedelta(days=i))
    dates = map(str, dates)
    return [*dates]


def generate_synth_data(length, data, variance=3, fp='./datasets/synth_counts.csv'):
    dates = get_synth_dates(length)
    with open(fp, 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        for d in dates:
            row = [d] + [f"{random.randrange(i - variance, i + variance)}" for i in data.values()]
            csv_writer.writerow(row)


def make_tag_groups(df):
    df.columns = ["name", "fact_sheet_types", "tags"]
    tag_groups = []
    for row in df.iterrows():
        inner_dicts = list(map(lambda x: x.pop("node"), row[1][2]))  # <- Jeg beklager mine manglende kompetencer.
        kvs = list(map(lambda x: x.values(), inner_dicts))           # <- Se ovenstående kommentar.
        kvs = list(map(list, kvs))
        df.tags[row[0]] = kvs
        df.fact_sheet_types[row[0]] = row[1][1][0] if len(row[1][1]) != 0 else None
    return df


def filter_tag_group(df, tag):
    value = tag
    selected_data = df.query('name == @value')
    values = [{"tag_name": v[0], "fact_sheets": v[1]} for v in selected_data.tags.values[0]]
    values.append({"tag_name": "none", "fact_sheets": get_factsheet_count(selected_data.fact_sheet_types.iloc[0])})
    tag_group_data = pd.DataFrame.from_records(values)

    return selected_data.append(tag_group_data).reset_index()


def get_factsheet_count(fact_sheet_type: str = None, auth = None) -> int:
    mapping = {"Application": APPLICATIONS, "BusinessCapability": BUSINESS_CAPABILITIES,
               "UserGroup": USER_GROUPS, "Project": PROJECTS, "Process": PROCESSES,
               "Interface": INTERFACES, "DataObject": DATA_OBJECTS, "ITComponent": IT_COMPONENTS,
               "Provider": PROVIDERS, "TechnicalStack": TECHNICAL_STACKS}
    if auth is None:
        if fact_sheet_type:
            return response_to_count(query_leanix(mapping[fact_sheet_type]))
        else:
            return response_to_count(query_leanix(ALL_SHEETS))
    else:
        if fact_sheet_type:
            return response_to_count(query_leanix(mapping[fact_sheet_type], auth=auth))
        else:
            return response_to_count(query_leanix(ALL_SHEETS,auth=auth))