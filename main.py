import pandas as pd
from helpers import *
from queries import QUERY2, QUERY1
from datetime import datetime

now = datetime.now()

df = response_to_df(query_leanix(QUERY1, "authentification.json"))
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
after = datetime.now()

print(f"Runtime: {after-now}")
# below25 = df[df["node.completion.percentage"] < 25]
# below50above25 = df[(df["node.completion.percentage"] < 50) & (df["node.completion.percentage"] > 25)]
# above50 = df[df["node.completion.percentage"] > 50]
#

# df["node.relApplicationToUserGroup.edges"][0][1]["node"]["usageType"]
# df["node.relApplicationToUserGroup.edges"][2][0]["node"]["description"]

# regex: (Systemejer:) (\w+) (\w+|\w\.) (\w+|\w\.|) (\<)(\w+\@\w+\.\w+\.\w+)( |\>)+