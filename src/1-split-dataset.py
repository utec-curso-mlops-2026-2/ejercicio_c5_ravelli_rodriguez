import pandas as pd
import fire
import os


def split_data(df_data, perc_data_train):
    df_data_train = df_data.sample(frac=perc_data_train)
    df_data_test = df_data.drop(df_data_train.index)
    return df_data_train, df_data_test

def process_split_data():
    if (os.getcwd().endswith('src')):
        os.chdir("..")
    df_data = pd.read_csv("data/in/application_data.csv")
    df_data_train, df_data_test = split_data(df_data, 0.7)

    if (not (os.path.exists("data/out"))):
        os.mkdir("data/out")
    df_data_train.to_csv("data/out/application_data_train.csv", index=False)
    df_data_test.to_csv("data/out/application_data_test.csv", index=False)

def main():
    process_split_data()

if __name__ == "__main__":
    fire.Fire(main)
