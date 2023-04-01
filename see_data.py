import pandas as pd


def main():
    df = pd.read_parquet("raw_data/blue_alliance_2022.parquet.gzip")
    print(df.shape)
    print(df.head())
    return


if __name__ == "__main__":
    main()