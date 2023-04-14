import os
import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
from api_get_event_teams import get_teams_at_event


def create_session(headers):
    session = requests.Session()
    session.headers.update(headers)
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session


def image_file_count(path):
    count = 0
    for root_dir, cur_dir, files in os.walk(path):
        count += len(files)
    return count


def url2id(url):
    source = url.split(".com/")[1]
    file_type = "jpg"
    file_types = ["jpg", "png"]
    stops = [".", "/", "\\", "jpg", "png"]
    for var_stop in stops:
        if var_stop in source:
            source = source.replace(var_stop, "")
            if var_stop in file_types:
                file_type = var_stop
    return source, file_type


def get_all_images(analyze_teams, base_url, session):
    print("\t\tDownloading Team Images...")
    downloaded_count = 0
    image_directory = os.path.dirname(os.path.realpath(__file__)) + "/robot_images"
    image_count = image_file_count(image_directory)
    for var_team in analyze_teams:
        if not os.path.exists(image_directory + f"/{var_team}"):
            os.makedirs(image_directory + f"/{var_team}")
        response = session.get(
            base_url + f"/team/{var_team}/media/2023" # TODO: parameterize year
        )
        for var_media in response.json():
            if var_media["direct_url"]:
                id, file_type = url2id(var_media["direct_url"])
                if not os.path.exists(image_directory + f"/{var_team}" + f"/{id}.{file_type}"):
                    var_img_data = requests.get(var_media["direct_url"]).content
                    with open(image_directory + f"/{var_team}" + f"/{id}.{file_type}", 'wb') as handler:
                        handler.write(var_img_data)
                    downloaded_count +=1
                    image_count += 1
            if downloaded_count % 50:
                print(f"\t\t\tdownloaded {downloaded_count} files")
            if image_count >= 3000: # ~3GB worth of images
                assert False, "Careful! Images are taking up a lot memory"
    return


def get_team_data(analyze_teams, base_url, headers, verbose):
    print("\tGetting Team Information...")
    session = create_session(headers)
    #get_all_images(analyze_teams, base_url, session)
    team_dict = {}
    for var_team in analyze_teams:
        response = session.get(
            base_url + f"/team/{var_team}"
        )
        var_team_str = str(response.json()["team_number"]) + " | " + str(response.json()["nickname"])
        var_loc = str(response.json()["city"]) + ", " + str(response.json()["state_prov"]) + " - " + str(response.json()["country"])
        var_web = str(response.json()["website"])
        var_start = str(response.json()["rookie_year"])

        var_awards = []
        awards_response = session.get(
            base_url + f"/team/{var_team}/awards"
        )
        for var_award in awards_response.json():
            if var_award["award_type"] == 1 and var_award["year"] == 2023: # TODO: parameterize year
                var_award_name = var_award["name"]
                var_event_key = var_award["event_key"]
                event_response = session.get(
                    base_url + f"/event/{var_event_key}"
                )
                var_event_name = event_response.json()["name"]
                var_awards.append(f"{var_award_name} - {var_event_name}")
        team_dict[var_team] = {
            "team": var_team_str, 
            "location": var_loc, 
            "website": var_web, 
            "first_year": var_start,
            "awards": var_awards
        }
    return team_dict


def create_html_reports(team_dict):
    for var_team in team_dict:
        var_html = f"""
<head><title>3655 Scouting Report</title></head>
<style>
    body {{
        padding: 0 0 0 0;
        margin: 0 0 0 0;
        background: #ffffff;
    }}
    ol {{
        list-style:none;
        list-style-type: none;
        padding: 0 0 0 0;
        margin: 0 0 0 0;
    }}
    ul {{
        list-style:none;
        list-style-type: none;
        padding: 0 0 0 0;
        margin: 0 0 0 0;
    }}
    #content {{
        display: flex;
        flex-direction: row;
    }}
    #dual {{
        display: flex;
        flex-direction: column;
        align-self: center;
    }}
    dual_b {{
        width: 50vw;
    }}
    #robot_img {{
        width: 50vw;
        height: auto;
    }}
    #score_locations {{
        width: 80vw;
        height: auto;
        align-self: center;
    }}
</style>
<body>
    <div id=content>
        <div>
            <ul id=dual>
                <!-- TODO: parameterize image reference -->
                <li id=dual_a><img id=robot_img src="../robot_images/frc3655/LdDL18wh.jpg"></li>
                <li id=dual_b>
                    <ol>
                        <li><p>Team: {team_dict[var_team]["team"]}</p></li>
                        <li><p>Location: {team_dict[var_team]["location"]}</p></li>
                        <li><p>Website: {team_dict[var_team]["website"]}</p></li>
                        <li><p>Founded: {team_dict[var_team]["first_year"]}</p></li>
                        <li><p>Awards: {str(team_dict[var_team]["awards"]).replace("[", "").replace("'", "").replace("]", "")}</p></li>
                    </ol>
                </li>
            </ul>
        </div>
    </div>
    <!-- TODO: parameterize image reference -->
    <img id=score_locations src="../score_images/frc3655.png">
</body>
        """
        with open(os.path.dirname(os.path.realpath(__file__)) + f"/html_reports/{var_team}.html", "w") as handler:
            handler.write(var_html)
        assert False
    return


def main():
    #gmail: scoutingTractor3655
    #password: d4Ta4Sc0ut1ng


    # https://www.thebluealliance.com/apidocs

    # hyper parameters
    event_key = "2023cmptx"
    verbose = True

    # static parameters
    base_url = "https://www.thebluealliance.com/api/v3"
    headers = {
        'User-Agent': "3655scouting",
        'From': "scoutingTractor3655@gmail.com",
        'X-TBA-Auth-Key': "QQEfWdunQpMgnapxMGoWwY3a76vTtU4n2NCq3hFLxYak95HkR0yGq5Xh2iWSERnq"
    }
    analyze_teams = ["frc3655", "frc8424"]
    #analyze_teams = get_teams_at_event("https://www.thebluealliance.com/api/v3", event_key, headers, False)

    print("Generating Reports...")
    team_dict = get_team_data(analyze_teams, base_url, headers, verbose)
    create_html_reports(team_dict)
    print("Run Complete.")
    return


if __name__ == "__main__":
    main()
