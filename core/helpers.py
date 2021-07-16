import json
import random
import requests
import pandas as pd
import time
import datetime
import re
import csv
from collections.abc import Iterable
from entities.constants import *


##################################
# Funktioner til query af LeanIx #
##################################


def query_leanix(query: str, auth: str = "authentication.json") -> requests.Response:
    """
    Denne funktion sender en forspørgsel til LeanIX's API
    og returnerer svaret i form af et response objekt.
    :param query: En GraphQL query i string format. Du kan finde query string i constants filen.
    :param auth: En sti til authentication filen i form af en streng. Denne fil skal du selv lave.
    :return: Et response objekt. Dette gives videre til response_to_df eller response_to_count.
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


def response_to_count(response: requests.Response) -> int:
    """
    Denne funktion slår op og finder totalCount i JSON strengen indeholdt i response objektet.
    :param response: Et response objekt som er returneret af query_leanix.
    :return: en integer fundet ved at slå op i totalCount.
    """
    return response.json()['data']['allFactSheets']['totalCount']


def get_fact_sheet_counts(queries: list[str]) -> dict[str, int]:
    """
    Denne funktion laver et dictionary med fakta ark typer som nøgler og antallet af en given fakta ark type som værdi.
    :param queries: en liste af graphQL queries fra constants.py.
    :return: et dictionary bestående af fakta ark typer og antallet af fakta ark med en given type.
    """
    keys = ["Applications", "Business Capabilities", "User Groups",
            "Projects", "Processes", "Interfaces", "Data Objects",
            "IT Components", "Providers", "Technical Stacks"]
    responses = [query_leanix(q, "authentication.json") for q in queries]  # Her laves en liste af responses.
    values = [v for v in map(response_to_count, responses)]  # Ud fra den ovenstående liste laves en liste af ints.
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
    """
    Denne renser et dataframe således at kolonnen "System Owner" indeholder en mail-adresse hvis en mail adresse kan
    findes i beskrivelse af bruger gruppen i fakta arket. Hvis der ikke kan findes en mail adresse, så er feltet tomt.
    :param df: Et dataframe med kolonnerne node.displayName og node.relApplicationToUserGroup.
    :return: et dataframe med kolonnerne Name og System Owner.
    """
    regex = r'(\w+\@\w+\.\w+\.\w+)'  # E-mail Regex som matcher mail-adresser på AAU.
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
            df["System Owner"].iloc[i] = ""  # Vi gør dette for at håndtere cases hvor at user_grp er tom.
    return df


def make_tag_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Denne funktion bruges til at pakke dictionaries ud i tags kolonnen og lave disse dictionaries om til
    to-dimensionelle lister, hvor index 0 er navnet på tagget og index 1 er antal af fakta ark der har dette tag.
    Denne funktion anvendes når man kun er interesseret i en enkel gruppe af tags og bruges sammen med filter_tag_group.

    :param df: et dataframe som indeholder alle tag groups.
    :return: et dataframe med kolonnen tags, som er en liste af lister med key value.
    """
    df.columns = ["name", "fact_sheet_types", "tags"]
    for row in df.iterrows():
        inner_dicts = list(map(lambda x: x.pop("node"), row[1][2]))  # Her laves en liste med dicts.
        kvs = list(map(lambda x: x.values(), inner_dicts))  # Her hentes værdierne fra dicts ned i en liste.
        df.tags[row[0]] = list(map(list, kvs))
        df.fact_sheet_types[row[0]] = row[1][1][0] if len(row[1][1]) != 0 else None
    return df


def filter_tag_group(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    """
    Denne funktion laver et nyt dataframe som består af en bestemt tag gruppe og de tags, som er indeholdt i tag gruppen.
    Dette resulterer i et dataframe med kolonnerne: navn, fact_sheet_type, tag_name og fact_sheets.

    :param df: et dataframe med kolonnen tags, som er en liste af lister.
    :param tag: den tag group man ønsker at filtrere efter
    :return: et dataframe med tag gruppe navnet, hvilke fakta ark det tagget må anvendes på,
    tags i gruppen og antallet af fakta ark tagget er anvendt på.
    """
    value = tag  # for at man må anvende variablen i den nedenstående linje skal den eksistere i det lokale scope.
    selected_data = df.query('name == @value')
    values = [{"tag_name": v[0], "fact_sheets": v[1]} for v in selected_data.tags.values[0]]
    not_tagged = get_factsheet_count(selected_data.fact_sheet_types.iloc[0]) - sum([v["fact_sheets"] for v in values])
    values.append({"tag_name": "Not tagged", "fact_sheets": not_tagged})
    tag_group_data = pd.DataFrame.from_records(values)

    return selected_data.append(tag_group_data).reset_index()


def get_factsheet_count(fact_sheet_type: str = None, auth=None) -> int:
    """
    Denne funktion returnerer antallet af fakta ark af en bestemt type, hvis den kaldes med en type som parameter.
    Hvis typen ikke angives, returnerer funktionen antallet af alle fakta ark.

    :param fact_sheet_type: det type fakta ark man ønsker at kende antallet af.
    :param auth: en sti til authentication filen, hvis funktionen kaldes udenfor core mappen. Fix dette.
    :return: Antallet af fakta ark med den angivne type eller antallet af alle fakta ark.
    """
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
            return response_to_count(query_leanix(ALL_SHEETS, auth=auth))


def get_completion_percentages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Denne funktion omdøber kolonnerne på det dataframe der gives som parameter
    og returnerer et dataframe med navnene på applikationerne og deres completion percentages som heltal.
    Denne funktion anvendes i get_avg_completion til at få gennemsnittet af completion rates.

    :param df: et dataframe returneret fra response_to_df kaldt med QUERY1.
    :return: et dataframe med to kolonner: navn og applikationens completion percentage.
    """
    df = df[["node.name", "node.completion.percentage"]]
    return df.rename(columns={"node.name": "Name", "node.completion.percentage": "Completion"})


def get_avg_completion(df: pd.DataFrame) -> float:
    return round(df["Completion"].mean(), ROUNDING_PRECISION)


def get_percent_system_owners(df: pd.DataFrame) -> tuple:
    """
    Denne funktion returner en tuple bestående af to floats.
    Den første float er procentdelen af applikations fakta ark som har en systemejer angivet.
    Den anden float er procentdelen af applikations fakta ark som ikke har en systemejer angivet.

    :param df: et dataframe med kolonnen System Owner returneret fra get_system_owners
    :return: en tuple bestående af to floats.
    """
    total = len(df)
    has_system_owners = len(df[df["System Owner"] != ""]) / total
    no_system_owners = 1 - has_system_owners
    return round(has_system_owners, ROUNDING_PRECISION), round(no_system_owners, ROUNDING_PRECISION)


############################
# Diverse hjælpefunktioner #
############################


def insert_into_csv(fp: str, data):
    """
    Denne funktion tilføjer en række med dagens dato og data til en CSV fil, angivet med paramteret fp.
    Hvis data ikke er en samling som kan itereres omdannes data til en liste.
    Hvis data er en dict, så er det kun værdierne som tilføjes til CSV filen.

    :param fp: en streng som angiver stien til den CSV fil der skal skrives til.
    :param data: Det data der ønskes skrevet til CSV filen.
    :return: None
    """
    if not isinstance(data, Iterable):
        data = [data]
    if isinstance(data, dict):
        row = [f"{datetime.date.today()}"] + [f"{i}" for i in data.values()]
    else:
        row = [f"{datetime.date.today()}"] + [f"{i}" for i in data]

    with open(fp, 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(row)


def get_synth_dates(length, as_strings=True):
    """
    Af og til kan det være rart at have noget dummy-dato'er som man kan teste dashboards med,
    hvilket er det præcise formål med denne funktion. Parameteret styrer hvor mange dage der ønskes.
    Funktionen giver en liste med datetime objekter tilbage, hvis funktionen kaldes med as_strings parameteret som falsk
    Ellers returnerer funktionen liste med datoer i strengformat.
    :param length: Længden på listen af datoer, angivet som heltal.
    :param as_strings: En bool som styrer hvorvidt man ønsker strenge eller datetime objekter. Pr automatik er den sand.
    :return: En liste af strenge eller datetime objekter.
    """
    week = 21
    start_date = time.asctime(time.strptime('2021 %d 1' % week, '%Y %W %w'))
    start_date = datetime.datetime.strptime(start_date, '%a %b %d %H:%M:%S %Y').date()
    dates = [start_date]
    for i in range(1, length):
        dates.append(start_date + datetime.timedelta(days=i))
    if as_strings:
        dates = map(str, dates)
    return [*dates]


def generate_synth_data(length, data, variance=3, fp='./datasets/synth_counts.csv'):
    dates = get_synth_dates(length)
    with open(fp, 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        for d in dates:
            row = [d] + [f"{random.randrange(i - variance, i + variance)}" for i in data.values()]
            csv_writer.writerow(row)


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


def log_percent_system_owners() -> None:
    df = response_to_df(query_leanix(QUERY1, "authentication.json"))
    df = get_system_owners(df)
    insert_into_csv("systemOwners.csv", get_percent_system_owners(df))


def log_fact_sheet_counts() -> None:
    data = get_fact_sheet_counts(COUNT_QUERY)
    insert_into_csv("./datasets/counts.csv", data)


def log_average_completion() -> None:
    df = response_to_df(query_leanix(QUERY2, "authentication.json"))
    df = get_completion_percentages(df)
    insert_into_csv("./datasets/completions.csv", get_avg_completion(df))


def log_all() -> None:
    log_fact_sheet_counts()
    log_average_completion()
    log_percent_system_owners()