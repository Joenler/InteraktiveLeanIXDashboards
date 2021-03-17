import pandas as pd
from helpers import *
from queries import QUERY2, QUERY1
from datetime import datetime

now = datetime.now()

df = response_to_df(query_leanix(QUERY1, "authentification.json"))
df = get_system_owners(df)







after = datetime.now()

print(f"Runtime: {after-now}")
# below25 = df[df["node.completion.percentage"] < 25]
# below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
# above50 = df[df["node.completion.percentage"] > 50]
#

# df["node.relApplicationToUserGroup.edges"][0][1]["node"]["usageType"]
# df["node.relApplicationToUserGroup.edges"][2][0]["node"]["description"]

# regex: (Systemejer:) (\w+) (\w+|\w\.) (\w+|\w\.|) (\<)(\w+\@\w+\.\w+\.\w+)( |\>)+