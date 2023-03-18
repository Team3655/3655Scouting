import ast
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers


def get_team_to_offense_score(year):
    offense_df = pd.read_csv(f'pre_processed_data_csv/{year}_offense.csv')
    team_to_offense_score = {}
    for index, row in offense_df.iterrows():
        team_to_offense_score[row['team']] = row['offense_score']
    return team_to_offense_score


def get_data(year):
    match_df = pd.read_csv(f'pre_processed_data_csv/{year}_match.csv')
    match_df = match_df[['key', 'actual_time', 'blue.team_keys', 'blue.score', 'red.team_keys', 'red.score']]
    full_match_list = []
    for index, row in match_df.iterrows():
        var_key = row['key']
        var_time = row['actual_time']
        var_blue_key = row['blue.team_keys']
        var_blue_score = row['blue.score']
        var_red_key = row['red.team_keys']
        var_red_score = row['red.score']
        full_match_list.append([var_key, var_time, var_blue_key, var_red_key, var_blue_score])
        full_match_list.append([var_key, var_time, var_red_key, var_blue_key, var_red_score])
    full_match_df = pd.DataFrame(
        full_match_list, columns=[
            'key', 'actual_time', 'offense_teams', 'defense_teams', 'points'
        ]
    )
    full_match_df['actual_time'] = full_match_df['actual_time'] - full_match_df['actual_time'].min()
    full_match_df['actual_time'] = full_match_df['actual_time'].div(604800)
    team_to_offense_score = get_team_to_offense_score(year)
    data = []
    for index, row in full_match_df.iterrows():
        var_key = row['key']
        var_time = row['actual_time']
        var_teams = ast.literal_eval(row['offense_teams'].replace("' '", "', '"))
        var_defense = ast.literal_eval(row['defense_teams'].replace("' '", "', '"))
        var_offense_scores = []
        for var_team in var_teams:
            var_offense_scores.append(team_to_offense_score[var_team])
        var_teams = [x for _, x in sorted(zip(var_offense_scores, var_teams))]
        var_offense_scores = sorted(var_offense_scores)
        var_points = row['points']
        data.append(
            [
                var_key, var_time,
                var_teams[0], var_offense_scores[0],
                var_teams[1], var_offense_scores[1],
                var_teams[2], var_offense_scores[2],
                var_defense[0], var_defense[1],
                var_defense[2], var_points
            ]
        )
    data_df = pd.DataFrame(
        data, columns=[
            'key', 'actual_time',
            'team1', 'team1_offense',
            'team2', 'team2_offense',
            'team3', 'team3_offense',
            'defense1', 'defense2',
            'defense3', 'points'
        ]
    )
    return data_df


def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Error [MPG]')
    plt.legend()
    plt.grid(True)
    plt.show()
    return


def residual_histogram(y, y_pred):
    # TODO: fix function not happy
    # https://www.tensorflow.org/tutorials/keras/regression
    error = y_pred - y
    plt.hist(error, bins=25)
    plt.xlabel('Prediction Error points')
    _ = plt.ylabel('Count')
    plt.show()
    return


def train_nn(df, dropout=0.05, learning_rate=0.001, show_graphs=False):
    model = keras.Sequential([
        layers.Dense(64, activation='relu'),
        layers.Dropout(dropout),
        layers.Dense(64, activation='relu'),
        layers.Dropout(dropout),
        layers.Dense(64, activation='relu'),
        layers.Dense(1)
    ])

    model.compile(loss='mean_absolute_error',
                  optimizer=tf.keras.optimizers.Adam(learning_rate))
    X = df[["actual_time", "team1_offense", "team2_offense", "team3_offense"]]
    y = df['points']
    history = model.fit(
        X,
        y,
        validation_split=0.2,
        verbose=0, epochs=100)
    plot_loss(history)
    y_pred = model.predict(X)
    if show_graphs:
        residual_histogram(y, y_pred)
    return y_pred


def main():
    # hyper_parameter
    dropout = 0.00
    learning_rate = 0.001
    show_graphs = False

    # static_parameter
    year = 2022

    df = get_data(year)
    print(df)
    predicted_scores = train_nn(df, dropout, learning_rate, show_graphs)
    print(predicted_scores)
    # TODO: Convert residual into defense scores
    # TODO: Add all code and resources to Github
    return


if __name__ == "__main__":
    main()