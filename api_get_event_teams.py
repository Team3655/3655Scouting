import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry


def create_session(headers):
    session = requests.Session()
    session.headers.update(headers)
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session


def get_teams_at_event(base_url, event_key, headers):
    print("\tGetting teams...")
    session = create_session(headers)
    events_response = session.get(
        base_url + f"/event/{event_key}/teams"
    )
    teams = []
    for var_dict in events_response.json():
        teams.append(var_dict["key"])
    return teams


def main():
    #gmail: scoutingTractor3655
    #password: d4Ta4Sc0ut1ng


    # https://www.thebluealliance.com/apidocs
    # https://www.thebluealliance.com/apidocs/v3

    # hyper parameters
    event_key = "2023micmp"
    verbose = True

    # static parameters
    base_url = "https://www.thebluealliance.com/api/v3"
    headers = {
        'User-Agent': "3655scouting",
        'From': "scoutingTractor3655@gmail.com",
        'X-TBA-Auth-Key': "QQEfWdunQpMgnapxMGoWwY3a76vTtU4n2NCq3hFLxYak95HkR0yGq5Xh2iWSERnq"
    }

    print("Getting Blue Alliance Data...")
    teams = get_teams_at_event(base_url, event_key, headers, verbose)
    print("Run Complete.")
    return


if __name__ == "__main__":
    main()
