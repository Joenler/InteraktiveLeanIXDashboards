from helpers import *
from entities.constants import *

import os.path


def run():
    if not os.path.isfile('authentication.json'):
        generate_auth_config()
    df1: pd.DataFrame = response_to_df(query_leanix(QUERY1, "authentication.json"))
    df1 = get_system_owners(df1)
    # df2: pd.DataFrame = response_to_df(query_leanix(QUERY2, "authentication.json"))
    # df2 = get_completion_percentages(df2)

    # insert_into_csv("completions.csv", get_avg_completion(df2))
    # insert_into_csv("systemOwners.csv", get_percent_system_owners(df1))


if __name__ == '__main__':
    log_fact_sheet_counts()