import pandas as pd
from typing import Union
from pandas.api.types import CategoricalDtype

############################
# Funktioner til Excel ark #
############################


"""
Denne samling af hjælpefunktioner har at gøre med manipulation af data fra et Excel ark. 
De har ikke længere relevans for projektet, men er med i tilfælde af at der skulle blive brug for dem. 

"""

def create_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Denne funktion hjælper med at lave kolonnenavne til et dataframe ud fra et Excel ark.
    Dette er nødvendigt at gøre, da Excel arket har inddelt Økonomiklasse, Manpower, Eksterne Ydelser, Interne Ydelser
    og Afdelingskontakt i forskellige zoner i Excel arket, og hedder derfor det samme, men i Pandas må man ikke have
    kolonner med samme navn.

    :param df: Et dataframe returneret af parse_excel_sheet.
    :return: Et dataframe med kolonner der har passende navne.
    """
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
    """
    Denne funktion tager en sti til et Excel ark og laver det om til et dataframe.

    :param fp: En streng som indeholder en filsti som peger på hvor Excel arket er placeret.
    :return: et dataframe hvor kommentarer, andet og kolonnen nan er udeladt.
    """
    df = create_column_names(pd.read_excel(fp)).drop(0)  # Den første row udelades da dette blot er kolonnenavne fra ark
    return df.drop(columns=["kommentarer", "Andet", "nan"])


def system_owner_count_from_excel(df: pd.DataFrame) -> int:
    """
    Denne funktion returnerer antallet af ikke tomme felter i kolonnen systemejer.

    :param df: En dataframe returneret af parse_excel_sheet
    :return: antallet af rækker hvor kolonnen systemejer ikke er tom.
    """
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
        df["Økonomiklasse"].iloc[i] = df[cols].iloc[i].max()  # Det her må man ikke. Find en anden måde.

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
