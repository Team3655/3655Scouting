import json
import pandas as pd


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


def get_df(df):
    # TODO: pd.json_normalize(df['score_breakdown']) failed because some values are null????
    fix_json_column(df, 'score_breakdown')
    fix_json_column(df, 'alliances')
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
            'red_teams',
            'red.autoCommunity.B', 'red.autoCommunity.M', 'red.autoCommunity.T',
            'red.teleopCommunity.B', 'red.teleopCommunity.M','red.teleopCommunity.T',
            'blue.linkPoints', 'blue.teleopPoints', 'blue.links',
            'red.linkPoints', 'red.teleopPoints', 'red.links'
        ]
    )
    return score_df


def get_score_locations(file_name, verbose):
    df = get_df(file_name)
    # TODO: Aggregate score location by team
    # TODO: Figure out how to format data into a viewable format (HTML???)
    return


def main():
    # hyper parameters
    year = 2023
    verbose = True

    # static parameters
    file_name = f"raw_data_csv/blue_alliance_{year}.csv"

    print("generating team score locations...")
    get_score_locations(file_name, verbose)
    print("Run Complete.")
    return


if __name__ == "__main__":
    main()
