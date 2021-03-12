import json


def get_auth(config_file : str) -> tuple:
    with open(config_file) as f:
        data = json.load(f)
        return (data["api_token"], data["auth_url"], data["request_url"])


secrets = get_auth('authentification.json')

