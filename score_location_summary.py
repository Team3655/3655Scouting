import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def fix_json_column(df, column_name):
    df[column_name] = df[column_name] \
        .str.replace("'", "\"", regex=True) \
        .str.replace("False", "false", regex=True) \
        .str.replace("True", "true", regex=True) \
        .str.replace("array\(", "", regex=True) \
        .str.replace(", dtype=object\)", "", regex=True) \
        .str.replace(", dtype=int64\)", "", regex=True) \
        .str.replace("dtype=object\),", "", regex=True) \
        .str.replace("\n", "", regex=True) \
        .str.replace("  ", "", regex=True)
    return df


def get_teams(color, alliance_dict):
    should_play = set(alliance_dict[color]['team_keys'])
    dq = alliance_dict[color]['dq_team_keys']
    sub = alliance_dict[color]['surrogate_team_keys']
    will_play = should_play
    for var_dq in dq:
        if will_play is not None:
            if var_dq in will_play:
                will_play = will_play.remove(var_dq)
    for var_sub in sub:
        if var_sub in will_play:
            will_play = will_play.add(var_sub)
    if will_play is None:
        return []
    return list(will_play)


def get_df(file_name):
    df = pd.read_csv(file_name)
    # TODO: pd.json_normalize(df['score_breakdown']) failed because some values are null????
    df = fix_json_column(df, 'score_breakdown')
    df = fix_json_column(df, 'alliances')
    score_list = []
    for index, row in df.iterrows():
        var_row = [row['key']]
        if pd.notnull(row['score_breakdown']):
            var_score_dict = json.loads(row["score_breakdown"])
            var_alliance_dict = json.loads(row["alliances"])
            for var_color in ['blue', 'red']:
                var_row.append(get_teams(var_color, var_alliance_dict))
                for var_driver in ['autoCommunity', 'teleopCommunity']:
                    for var_height in ['B', 'M', 'T']:
                        var_row.append(var_score_dict[var_color][var_driver][var_height])
                var_row.append(var_score_dict[var_color]['linkPoints'])
                var_row.append(var_score_dict[var_color]['teleopPoints'])

                links_str = "["
                for var_link in var_score_dict[var_color]['links']:
                    links_str += str(var_link)
                links_str += "]"
                var_row.append(links_str)
            score_list.append(var_row)

    score_df = pd.DataFrame(
        score_list,
        columns=[
            'key',
            'blue_teams',
            'blue.autoCommunity.B', 'blue.autoCommunity.M', 'blue.autoCommunity.T',
            'blue.teleopCommunity.B', 'blue.teleopCommunity.M', 'blue.teleopCommunity.T',
            'blue.linkPoints', 'blue.teleopPoints', 'blue.links',
            'red_teams',
            'red.autoCommunity.B', 'red.autoCommunity.M', 'red.autoCommunity.T',
            'red.teleopCommunity.B', 'red.teleopCommunity.M','red.teleopCommunity.T',
            'red.linkPoints', 'red.teleopPoints', 'red.links'
        ]
    )
    return score_df


def get_team_data(df):
    team_to_data = {}
    for index, row in df.iterrows():
        for var_color in ["red", "blue"]:
            var_teams = row[f"{var_color}_teams"]
            for var_column in ['autoCommunity.B', 'autoCommunity.M', 'autoCommunity.T',
                               'teleopCommunity.B', 'teleopCommunity.M', 'teleopCommunity.T',
                               'linkPoints', 'teleopPoints', 'links']:
                for var_team in var_teams:
                    var_dict = {}
                    if var_team in team_to_data:
                        var_dict = team_to_data[var_team]
                    if var_column in var_dict:
                        var_arr = var_dict[var_column]
                        var_arr.append(row[f"{var_color}.{var_column}"])
                        var_dict[var_column] = var_arr
                    else:
                        var_dict[var_column] = [row[f"{var_color}.{var_column}"]]
                    team_to_data[var_team] = var_dict
    return team_to_data


def aggregate_scores_location(driver, element, team, team_to_data):
    score_location = []
    team_dict = team_to_data[team]
    for var_tier in ["T", "M", "B"]:
        var_match_score_locations = team_dict[f"{driver}.{var_tier}"]
        match_count = len(var_match_score_locations)
        var_score_tier = [0] * len(var_match_score_locations[0])
        for var_match_score_location in var_match_score_locations:
            for var_index in range(len(var_match_score_location)):
                if var_match_score_location[var_index] == element:
                    var_score_tier[var_index] = var_score_tier[var_index] + 1
        var_score_tier[:] = [round(x / match_count, 4) for x in var_score_tier]
        score_location.append(var_score_tier)
    return score_location


def get_team_score_prob(analyze_teams, df):
    team_to_data = get_team_data(df)
    team_score_prob = {}
    for var_team in analyze_teams:
        var_dict = {}
        for var_driver in ["autoCommunity", "teleopCommunity"]:
            for var_element in ["Cone", "Cube"]:
                var_dict[f"{var_driver}|{var_element}"] = aggregate_scores_location(var_driver, var_element,
                                                                                    var_team, team_to_data)
        team_score_prob[var_team] = var_dict
    return team_score_prob


def save_depict_team_scores(team_score_prob):
    for var_team in team_score_prob:
        var_team_data = team_score_prob[var_team]
        for var_perspective in var_team_data:
            var_driver = var_perspective.split("|")[0]
            var_element = var_perspective.split("|")[1]
            if var_element == "Cone":
                color_scheme = "light:#F9C70C"
            else:
                color_scheme = "light:#710193"
            var_heatmap_data = np.array((var_team_data[var_perspective]))
            fig, ax = plt.subplots(figsize=(15, 15))
            plt.title(f"{var_team} - {var_driver} {var_element} Heatmap")
            sns.heatmap(var_heatmap_data, square=True, ax=ax,
                        annot=True, linewidth=.5, vmin=0,
                        vmax=1, cmap=sns.color_palette(color_scheme, as_cmap=True))
            plt.yticks(rotation=0, fontsize=16)
            plt.xticks(fontsize=12)
            plt.tight_layout()
            plt.savefig(f"{var_team}_{var_driver}_{var_element}")
    return


def depict_team_scores(team_score_prob):
    driver_to_index = {"autoCommunity": 0, "teleopCommunity": 1}
    element_to_index = {"Cone": 0, "Cube": 1}
    for var_team in team_score_prob:
        fig, axs = plt.subplots(2, 2, figsize=(15, 15))
        var_team_data = team_score_prob[var_team]
        for var_perspective in var_team_data:
            var_driver = var_perspective.split("|")[0]
            var_element = var_perspective.split("|")[1]
            plt.sca(axs[element_to_index[var_element], driver_to_index[var_driver]])
            if var_element == "Cone":
                color_scheme = "light:#F9C70C"
            else:
                color_scheme = "light:#710193"
            var_heatmap_data = np.array((var_team_data[var_perspective]))
            plt.title(f"{var_team} - {var_driver} {var_element} Heatmap")
            sns.heatmap(var_heatmap_data, square=True,
                        ax=axs[element_to_index[var_element], driver_to_index[var_driver]],
                        annot=True, linewidth=.5, vmin=0,
                        vmax=1, cmap=sns.color_palette(color_scheme, as_cmap=True))
            plt.yticks(rotation=0, fontsize=12)
            plt.xticks(fontsize=12)
            plt.tight_layout()
        plt.savefig(f"./score_images/{var_team}")
    return


def get_score_locations(analyze_teams, file_name, verbose):
    df = get_df(file_name)
    team_score_prob = get_team_score_prob(analyze_teams, df)
    depict_team_scores(team_score_prob)
    return


def main():
    # hyper parameters
    analyze_teams = ["frc3655", "frc8424"]
    verbose = True
    year = 2023

    # static parameters
    file_name = f"raw_data_csv/blue_alliance_{year}.csv"

    print("generating team score locations...")
    get_score_locations(analyze_teams, file_name, verbose)
    print("Run Complete.")
    return


if __name__ == "__main__":
    main()
