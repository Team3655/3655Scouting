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


def build_dataset(base_url, end_year, headers, start_year, verbose):
    print("\tBuilding Dataset...")
    session = create_session(headers)
    df_dict = {}
    years = []
    for var_year in range(start_year, end_year):
        years.append(var_year)
    for var_year in years:
        print(f"\t\tCalling all matches in {var_year}...")
        events_response = session.get(
            base_url + f"/events/{var_year}"
        )
        count = 0
        match_list = []
        for var_event in events_response.json():
            match_response = session.get(
                base_url + f"/event/{var_event['key']}/matches"
            )
            match_list.extend(match_response.json())
            count += 1
            if verbose:
                if count % 50 == 0:
                    print(f"\t\t\tApi call count = {count}.")
        event_df = pd.DataFrame.from_records(match_list)
        df_dict[var_year] = event_df
    return df_dict


def save_data(data, verbose):
    print("\tSaving data...")
    for var_year in data:
        var_df = data[var_year]
        if not var_df.empty:
            try:
                var_df.to_parquet(f"raw_data/blue_alliance_{var_year}.parquet.gzip", compression='gzip')
            except Exception as e:
                print(f"\t\t{var_year} failed to save: {e}")
            if verbose:
                print(f"\t\tSaved blue_alliance_{var_year}.parquet.gzip.")
    return


def getting_data(base_url, end_year, headers, start_year, verbose):
    data = build_dataset(base_url, end_year, headers, start_year, verbose)
    save_data(data, verbose)
    return


def main():
    #gmail: scoutingTractor3655
    #password: d4Ta4Sc0ut1ng


    # https://www.thebluealliance.com/apidocs

    # hyper parameters
    start_year = 2023
    end_year = 2024
    verbose = True

    # static parameters
    base_url = "https://www.thebluealliance.com/api/v3"
    headers = {
        'User-Agent': "3655scouting",
        'From': "scoutingTractor3655@gmail.com",
        'X-TBA-Auth-Key': "QQEfWdunQpMgnapxMGoWwY3a76vTtU4n2NCq3hFLxYak95HkR0yGq5Xh2iWSERnq"
    }

    print("Getting Blue Alliance Data...")
    getting_data(base_url, end_year, headers, start_year, verbose)
    print("Run Complete.")
    return


if __name__ == "__main__":
    main()
