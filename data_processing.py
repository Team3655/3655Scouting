import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import scipy


def read_data(year):
    df = pd.read_parquet(f"raw_data/blue_alliance_{year}.parquet.gzip")
    return df


def get_score_df(df):
    score_df = pd.json_normalize(df['score_breakdown'])
    score_columns = [
        'adjustPoints',
        'autoCargoPoints',
        'autoCargoTotal',
        'autoPoints',
        'cargoBonusRankingPoint',
        'endgamePoints',
        'endgameRobot1',
        'endgameRobot2',
        'endgameRobot3',
        'foulCount',
        'foulPoints',
        'hangarBonusRankingPoint',
        'matchCargoTotal',
        'quintetAchieved',
        'rp',
        'techFoulCount',
        'teleopCargoPoints',
        'teleopCargoTotal',
        'teleopPoints',
        'totalPoints'
    ]
    filter_columns = []
    for var_color in ["blue", "red"]:
        for var_column in score_columns:
            filter_columns.append(f"{var_color}.{var_column}")
    score_df = score_df[filter_columns]
    return score_df


def get_videos_df(df):
    videos_list = []
    for index, row in df.iterrows():
        var_raw = row['videos']
        var_list = []
        for var_dict in var_raw:
            if var_dict["type"] == "youtube":
                var_list.append(f"https://www.youtube.com/watch?v={var_dict['key']}")
        videos_list.append([var_list])
    videos_df = pd.DataFrame(videos_list, columns=["links"])
    return videos_df


def get_filter_df(df):
    filter_df = df.drop(
        columns=[
            'alliances',
            'score_breakdown',
            'videos',
            'match_number',
            'post_result_time',
            'predicted_time',
            'time'
        ]
    )
    return filter_df


def pre_processing(df, save, year):
    text_file = open("sample.txt", "w")
    n = text_file.write(str(df.iloc[0]['score_breakdown']))
    text_file.close()
    assert False
    alliances_df = pd.json_normalize(df['alliances'])
    score_df = get_score_df(df)
    videos_df = get_videos_df(df)
    filter_df = get_filter_df(df)
    clean_df = filter_df.join(videos_df)
    clean_df = clean_df.join(score_df)
    clean_df = clean_df.join(alliances_df)
    # Filter out all values after worlds 4/20-4/23
    clean_df = clean_df[clean_df['actual_time'] < 1650830400]
    if save:
        clean_df.to_csv(f"pre_processed_data_csv/{year}_match.csv", index=True)
    return clean_df


def normalize(arr):
    arr = np.log(arr)
    arr[np.where(arr == -np.Inf)] = 0
    arr = arr - np.mean(arr)
    arr = arr / np.std(arr)
    return arr


def point_histoogram(clean_df, show_graphs):
    blue_points = clean_df['blue.totalPoints'].to_numpy()
    red_points = clean_df['red.totalPoints'].to_numpy()
    total_points = np.concatenate([blue_points, red_points])
    log_total_points = normalize(total_points)
    if show_graphs:
        plt.hist(total_points)
        plt.show()
        plt.hist(log_total_points)
        plt.show()
    return

def get_all_team_keys(df):
    teamsList = df["team_keys"].values.tolist()
    teamSet = set()
    for var_teamList in teamsList:
        for var_team in var_teamList:
            if var_team not in teamSet:
                teamSet.add(var_team)
    return list(teamSet)


def points_over_time(clean_df, show_graphs):
    blue_filter_dataframe = clean_df[['blue.totalPoints', 'actual_time', 'event_key']]
    blue_filter_dataframe = blue_filter_dataframe.rename(columns={"blue.totalPoints": "totalPoints"}, errors="raise")

    red_filter_dataframe = clean_df[['red.totalPoints', 'actual_time', 'event_key']]
    red_filter_dataframe = red_filter_dataframe.rename(columns={"red.totalPoints": "totalPoints"}, errors="raise")

    df = pd.concat([blue_filter_dataframe, red_filter_dataframe])
    avg_points_df = df[['event_key', 'totalPoints']].groupby(by=['event_key']).mean()
    clean_df = clean_df.sort_values(by=['actual_time'])
    event_to_time_df = clean_df[['event_key', 'actual_time']].drop_duplicates(subset=['event_key'])
    avg_points_df = avg_points_df.merge(event_to_time_df, on='event_key', how='left')
    avg_points_df['actual_time'] = pd.to_datetime(avg_points_df['actual_time'], unit='s')
    if show_graphs:
        fig, ax = plt.subplots()
        ax.scatter(avg_points_df['actual_time'], avg_points_df['totalPoints'])
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.show()
    return


def get_time_series(clean_df):
    blue_filter_dataframe = clean_df[['blue.totalPoints', 'actual_time', 'blue.team_keys']]
    blue_filter_dataframe = blue_filter_dataframe.rename(
        columns={"blue.totalPoints": "totalPoints", 'blue.team_keys': 'team_keys'}, errors="raise"
    )

    red_filter_dataframe = clean_df[['red.totalPoints', 'actual_time', 'red.team_keys']]
    red_filter_dataframe = red_filter_dataframe.rename(
        columns={"red.totalPoints": "totalPoints", 'red.team_keys': 'team_keys'}, errors="raise"
    )

    df = pd.concat([blue_filter_dataframe, red_filter_dataframe])
    df = df.sort_values(by=['actual_time'])
    df['actual_time'] = df['actual_time'] - df['actual_time'].min()
    df['log_totalPoints'] = np.log(df['totalPoints'])
    df['log_totalPoints'] = df['log_totalPoints'].replace(-np.Inf, 0)
    return df


def get_log_scores(df, show_graphs):
    curve = np.polyfit(df['actual_time'], df['log_totalPoints'], 1)
    y = curve[0] * df['actual_time'] + curve[1]
    df['adjusted'] = df['actual_time'] * curve[0]
    df['adjusted_logPoints'] = df['log_totalPoints'] - df['adjusted']
    df['center_adjusted_points'] = df['adjusted_logPoints'] - df['adjusted_logPoints'].mean()
    df['normal_adjusted_points'] = df['center_adjusted_points'] / df['center_adjusted_points'].std()
    df['percent_rank'] = df['normal_adjusted_points'].rank(pct=True)
    if show_graphs:
        plt.hist(df['normal_adjusted_points'])
        plt.show()
    return df


def get_team_to_point_time(df):
    team_to_point_time = {}
    for index, row in df.iterrows():
        var_team_list = row['team_keys']
        var_actual_time = row['actual_time'] / 604800
        var_normal_adjusted_points = row['normal_adjusted_points']
        for var_team in var_team_list:
            if var_team in team_to_point_time:
                var_tuple_list = team_to_point_time[var_team].copy()
                var_tuple_list.append((var_normal_adjusted_points, var_actual_time))
                team_to_point_time[var_team] = var_tuple_list
            else:
                team_to_point_time[var_team] = [(var_normal_adjusted_points, var_actual_time)]
    return team_to_point_time


def calculate_weighted_scores(team_to_point_time):
    team_scores = {}
    for var_team in team_to_point_time:
        var_total_score = 0
        var_total_weight = 0
        for var_match in team_to_point_time[var_team]:
            var_total_score += var_match[0] * var_match[1]
            var_total_weight += var_match[1]
        team_scores[var_team] = var_total_score / var_total_weight
    scores_df = pd.DataFrame.from_dict(team_scores, orient='index')
    scores_df.reset_index(inplace=True)
    scores_df = scores_df.rename(columns={'index': 'team', 0: 'weighted_score'})
    return scores_df


def get_scores(df):
    hist = np.histogram(df['weighted_score'], bins=100)
    hist_dist = scipy.stats.rv_histogram(hist, density=False)
    offense = []
    for index, row in df.iterrows():
        offense.append(hist_dist.cdf(row["weighted_score"]))
    print(min(offense))
    print(max(offense))
    df['offense_score'] = offense
    df = df.drop(columns=['weighted_score'])
    return df


def build_offensive_scores(df, save, show_graphs, year):
    team_to_point_time = get_team_to_point_time(df)
    scores_df = calculate_weighted_scores(team_to_point_time)
    if show_graphs:
        plt.hist(scores_df['weighted_score'])
        plt.show()
    scores = get_scores(scores_df)
    if save:
        scores.to_csv(f"pre_processed_data_csv/{year}_offense.csv", index=True)
    return scores


def fitted_time_series(clean_df, save, show_graphs, year):
    df = get_time_series(clean_df)
    df = get_log_scores(df, show_graphs)
    scores_df = build_offensive_scores(df, save, show_graphs, year)
    print(scores_df)
    return


def visualize(clean_df, save, show_graphs, year):
    # TODO: uncomment
    point_histoogram(clean_df, show_graphs)
    points_over_time(clean_df, show_graphs)
    fitted_time_series(clean_df, save, show_graphs, year)
    return


def main():
    # hyper_parameter
    save = True
    show_graphs = False

    # static_parameter
    year = 2022

    df = read_data(year)
    clean_df = pre_processing(df, save, year)
    visualize(clean_df, save, show_graphs, year)
    return


if __name__ == "__main__":
    main()
