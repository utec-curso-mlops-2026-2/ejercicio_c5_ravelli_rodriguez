import fire
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import os
import pickle


class TrainEvaluateModels:
    _output_path_train = ""
    _output_path_preprocess = ""

    def _create_output_path_train(self):
        if not(os.path.exists(self._output_path_train)):
            os.mkdir(self._output_path_train)
        if not(os.path.exists(f'{self._output_path_train}/models')):
            os.mkdir(f'{self._output_path_train}/models')
        if not(os.path.exists(f'{self._output_path_train}/metrics')):
            os.mkdir(f'{self._output_path_train}/metrics')

    def _get_preprocess_x_columns(self):
        x_cols = pd.read_csv(f'{self._output_path_preprocess}/final_variables.csv')['variable'].to_list()
        return x_cols

    def _get_preprocess_y_column(self):
        y_col = pd.read_csv(f'{self._output_path_preprocess}/y_col_name.csv')['y_col'].to_list()
        return y_col


    def __init__(self, output_path_train, output_path_preprocess):
        self._output_path_train = output_path_train
        self._output_path_preprocess = output_path_preprocess
        self._create_output_path_train()

    def train_evaluate_models(self, df_data_train, model_parameters_grid):
        rf = RandomForestClassifier()
        x_cols = self._get_preprocess_x_columns()
        y_col = self._get_preprocess_y_column()
        grid_search = GridSearchCV(estimator=rf, param_grid=model_parameters_grid, scoring='roc_auc')
        grid_search.fit(df_data_train[x_cols], df_data_train[y_col].values.ravel())

        df_model_results = pd.DataFrame({'model_parameters': grid_search.cv_results_['params'],
                                         'model_rank': grid_search.cv_results_['rank_test_score'],
                                         'auc_score_mean': grid_search.cv_results_['mean_test_score'],
                                         'auc_score_std': grid_search.cv_results_['std_test_score']})
        df_model_results['auc_score_cv'] = df_model_results['auc_score_std'] / df_model_results['auc_score_mean']
        df_model_results.to_csv(f'{self._output_path_train}/metrics/train_cv_model_results.csv', index=False)

        df_model_results_best_model = df_model_results[df_model_results['model_rank']==1]
        df_model_results_best_model.to_csv(f'{self._output_path_train}/metrics/train_cv_model_results_best_model.csv', index=False)

        df_feature_importance = pd.DataFrame({'variable': grid_search.feature_names_in_, 'importance': grid_search.best_estimator_.feature_importances_})
        df_feature_importance.to_csv(f'{self._output_path_train}/feature_importance.csv', index=False)

        with open(f'{self._output_path_train}/models/grid_search_model.pickle', 'wb') as handle:
            pickle.dump(grid_search, handle, protocol=pickle.HIGHEST_PROTOCOL)


def process_train_evaluate_models(model_parameters_grid):
    if (os.getcwd().endswith("src")):
        os.chdir("..")
    df_data_train = pd.read_csv("data/out/application_data_train_prepared.csv")
    train_validate_models_instance = TrainEvaluateModels(output_path_train="outputs/train", output_path_preprocess="outputs/preprocess")
    train_validate_models_instance.train_evaluate_models(df_data_train, model_parameters_grid)


def main():
    #model_parameters_grid =  {'n_estimators':[50,100,500], 'max_depth':[2,4,6,8], 'min_samples_leaf':[50,100,250,500], 'min_impurity_decrease':[0, 0.001, 0.005]}
    model_parameters_grid = {'n_estimators': [50, 100], 'max_depth': [4, 6],
                             'min_samples_leaf': [100], 'min_impurity_decrease': [0]}
    process_train_evaluate_models(model_parameters_grid)

if __name__ == "__main__":
    fire.Fire(main)

