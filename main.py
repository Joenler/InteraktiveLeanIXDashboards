import pandas as pd
from helpers import *
from queries import QUERY2, QUERY1
from datetime import datetime

now = datetime.now()

df1 = response_to_df(query_leanix(QUERY1, "authentification.json"))
df1 = get_system_owners(df1)
df2 = response_to_df(query_leanix(QUERY2, "authentification.json"))
df2 = get_completion_percentages(df2)
has_sys_owner, no_sys_owner = get_percent_system_owners(df1)
has_sys_owner = round(has_sys_owner, 3)
no_sys_owner = round(no_sys_owner, 3)
avg_cmpl = round(get_avg_completion(df2), 3)




after = datetime.now()

print(f"Runtime: {after-now}")
# below25 = df[df["node.completion.percentage"] < 25]
# below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
# above50 = df[df["node.completion.percentage"] > 50]
#

# df["node.relApplicationToUserGroup.edges"][0][1]["node"]["usageType"]
# df["node.relApplicationToUserGroup.edges"][2][0]["node"]["description"]

# regex: (Systemejer:) (\w+) (\w+|\w\.) (\w+|\w\.|) (\<)(\w+\@\w+\.\w+\.\w+)( |\>)+