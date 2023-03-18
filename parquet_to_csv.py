import pandas as pd


def change_file(file_name, file_type, var_year):
    df = pd.read_parquet(f"raw_data/{file_name}{var_year}{file_type}")
    df.to_csv(f"raw_data_csv/{file_name}{var_year}.csv", index=True)
    return


def main():
    # hyper_parameter
    start_year = 2023
    end_year = 2023

    # static_parameter
    file_name = "blue_alliance_"
    file_type = ".parquet.gzip"

    for var_year in range(start_year, end_year + 1):
        try:
            change_file(file_name, file_type, var_year)
        except Exception as E:
            print(E)
    return


if __name__ == "__main__":
    main()
