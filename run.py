from helpers import *
from constants import QUERY2, QUERY1
from datetime import datetime


def run():
    df1 = response_to_df(query_leanix(QUERY1, "authentification.json"))
    df1 = get_system_owners(df1)
    df2 = response_to_df(query_leanix(QUERY2, "authentification.json"))
    df2 = get_completion_percentages(df2)

    insert_into_csv("completions.csv", get_avg_completion(df2))
    insert_into_csv("systemOwners.csv", get_percent_system_owners(df1))

if __name__ == '__main__':
    run()


