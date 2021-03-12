import json
import requests

def get_auth(config_file : str) -> tuple:
    with open(config_file) as f:
        data = json.load(f)
        return (data["api_token"], data["auth_url"], data["request_url"])


secrets = get_auth('authentification.json')

def query_leanix(query: str, auth: str):
    authentication = get_auth(auth)
    response = requests.post(authentication[1],
                             auth=('apitoken', authentication[0]),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']

    data = {"query": query}
    json_data = json.dumps(data)
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}

    return requests.post(url=authentication[2], headers=header, data=json_data)