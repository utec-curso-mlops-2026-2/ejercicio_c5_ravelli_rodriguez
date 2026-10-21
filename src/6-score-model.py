import fire
import pandas as pd
import os
import pickle


class ScoreModel:
    _output_path_train = ""
    _output_path_preprocess = ""

    def __init__(self, output_path_train, output_path_preprocess):
        self._output_path_train = output_path_train
        self._output_path_preprocess = output_path_preprocess

    def prepare_impute_missing(self, df_data_score, x_cols):
        df_data_imputed = df_data_score.copy()
        df_impute_parameters = pd.read_csv(f"{self._output_path_preprocess}/impute_missing_parameters.csv")
        for col in x_cols:
            impute_value = df_impute_parameters[df_impute_parameters["variable"]==col]["impute_value"].values[0]
            df_data_imputed[col] = df_data_imputed[col].fillna(impute_value)
        return df_data_imputed

    def prepare_dataset(self, df_data):
        x_cols = pd.read_csv(f"{self._output_path_preprocess}/final_variables.csv")["variable"].values.tolist()
        df_data_prepared = df_data[x_cols]
        df_data_prepared = self.prepare_impute_missing(df_data_prepared, x_cols)

        return df_data_prepared

    def score_model(self, df_data_score):
        with open(f'{self._output_path_train}/models/best_model.pickle', 'rb') as handle:
            best_model = pickle.load(handle)

        features = pd.read_csv(f'{self._output_path_train}/feature_importance.csv')['variable'].to_list()

        y_pred = best_model.predict_proba(df_data_score[features])
        df_data_score['y_pred'] = y_pred[:,1]
        return df_data_score

    def score_preprocess_model(self, df_data_score):
        df_data_score_prepared = self.prepare_dataset(df_data_score)
        df_data_score_prepared_y_pred = self.score_model(df_data_score_prepared)
        return df_data_score_prepared_y_pred, df_data_score_prepared_y_pred['y_pred']


def process_score_model():
    if (os.getcwd().endswith("src")):
        os.chdir("..")
    df_data_score = pd.read_csv("data/out/application_data_test_prepared.csv")
    score_model_instance = ScoreModel(output_path_train="outputs/train", output_path_preprocess="outputs/preprocess")
    df_data_score_pred, y_pred = score_model_instance.score_preprocess_model(df_data_score)

    if (not (os.path.exists("data/score"))):
        os.mkdir("data/score")
    df_data_score_pred.to_csv("data/score/df_data_score_pred.csv")
    y_pred.to_csv("data/score/y_pred_score.csv")
    return y_pred


def main():
    process_score_model()

if __name__ == "__main__":
    fire.Fire(main)
