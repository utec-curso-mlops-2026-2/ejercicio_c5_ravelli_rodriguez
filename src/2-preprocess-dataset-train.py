import fire
import pandas as pd
import sklearn.metrics as metrics
import os


class PreprocessData:
    _output_path = ""
    _correlation_cutoff = 0.70
    _auc_bivariate_cutoff = 0.51

    def __init__(self, output_path):
        self._output_path = output_path
        self._create_output_path()

    def _create_output_path(self):
        if not(os.path.exists(self._output_path)):
            os.makedirs(self._output_path)

    def _save_y_col_name(self, y_col):
        df_y_col_name = pd.DataFrame({'y_col':[y_col]})
        df_y_col_name.to_csv(f'{self._output_path}/y_col_name.csv', index=False)

    def preprocess_descriptive_statistics_x(self, df_data, x_cols):
        df_descriptive_statistics_x = df_data[x_cols].describe().transpose()
        df_descriptive_statistics_x = df_descriptive_statistics_x.reset_index().rename({'index': 'variable'}, axis='columns')
        df_descriptive_statistics_x.to_csv(f"{self._output_path}/descriptive_statistics_x.csv", index=False)
        return df_descriptive_statistics_x

    def preprocess_descriptive_statistics_y(self, df_data, y_col):
        df_descriptive_statistics_y = df_data.groupby(y_col).agg({y_col: 'count'})
        df_descriptive_statistics_y = df_descriptive_statistics_y.rename({y_col: 'count'}, axis='columns')
        df_descriptive_statistics_y = df_descriptive_statistics_y.reset_index()
        df_descriptive_statistics_y.to_csv(f"{self._output_path}/descriptive_statistics_y.csv", index=False)
        return df_descriptive_statistics_y

    def preprocess_descriptive_statistics(self, df_data, x_cols, y_col):
        df_descriptive_statistics_x = self.preprocess_descriptive_statistics_x(df_data, x_cols)
        df_descriptive_statistics_y = self.preprocess_descriptive_statistics_y(df_data, y_col)
        return df_descriptive_statistics_x, df_descriptive_statistics_y

    def preprocess_impute_missing(self, df_data, x_cols):
        df_data_imputed = df_data.copy()
        df_impute_parameters = pd.DataFrame()
        for col in x_cols:
            col_mean = df_data[col].mean()
            df_data_imputed[col] = df_data[col].fillna(col_mean)
            df_impute_parameters_col = pd.DataFrame({"variable": [col], "impute_value": [col_mean]})
            df_impute_parameters = pd.concat([df_impute_parameters, df_impute_parameters_col])
        df_impute_parameters.to_csv(f"{self._output_path}/impute_missing_parameters.csv", index=False)
        return df_data_imputed

    def preprocess_compute_bivariate_analysis(self, df_data, x_cols, y_col):
        pd_bivariate_analysis = pd.DataFrame()
        for col in x_cols:
            auc_col = metrics.roc_auc_score(df_data[y_col], df_data[col])
            if (auc_col < 0.5): auc_col = (1 - auc_col)
            pd_bivariate_analysis_col = pd.DataFrame({"variable": [col], "bivariate_auc": [auc_col]})
            pd_bivariate_analysis = pd.concat([pd_bivariate_analysis, pd_bivariate_analysis_col])
        pd_bivariate_analysis.to_csv(f"{self._output_path}/bivariate_analysis.csv", index=False)
        return pd_bivariate_analysis

    def preprocess_compute_correlation_pairs(self, df_data, x_cols):
        corr_matrix = df_data[x_cols].corr()
        corr_matrix_abs = corr_matrix.abs()
        so = corr_matrix_abs.unstack()
        df_corr_pairs_abs = pd.DataFrame(so).reset_index()
        df_corr_pairs_abs.columns = ["variable_1", "variable_2", "corr"]
        df_corr_pairs_abs = df_corr_pairs_abs[df_corr_pairs_abs["corr"] < 1]
        df_corr_pairs_abs_cutoff = df_corr_pairs_abs[df_corr_pairs_abs["corr"] >= self._correlation_cutoff]
        return df_corr_pairs_abs_cutoff

    def _find_variable_bivariate_auc(self, df_bivariate_analysis, variable_name):
        return df_bivariate_analysis[df_bivariate_analysis["variable"] == variable_name]["bivariate_auc"].iloc[0]

    def _find_bivariate_auc_high_correlation_pairs(self, df_bivariate_analysis, df_corr_pairs_abs_cutoff):
        df_corr_pairs_abs_cutoff_bivariate = df_corr_pairs_abs_cutoff.copy()
        auc_1_list, auc_2_list = [], []
        for index, row in df_corr_pairs_abs_cutoff.iterrows():
            auc_1_list.append(self._find_variable_bivariate_auc(df_bivariate_analysis, row["variable_1"]))
            auc_2_list.append(self._find_variable_bivariate_auc(df_bivariate_analysis, row["variable_2"]))
        df_corr_pairs_abs_cutoff_bivariate["bivariate_auc_1"] = auc_1_list
        df_corr_pairs_abs_cutoff_bivariate["bivariate_auc_2"] = auc_2_list
        return df_corr_pairs_abs_cutoff_bivariate

    def _filter_high_correlation_pairs(self, df_corr_pairs_abs_cutoff_bivariate):
        vars_selected = []
        for index, row in df_corr_pairs_abs_cutoff_bivariate.iterrows():
            var_selected = row["variable_1"]
            if (row["bivariate_auc_2"] > row["bivariate_auc_1"]):
                var_selected = row["variable_2"]
            vars_selected.append(var_selected)
        return list(set(vars_selected))

    def preprocess_clean_correlations(self, df_data, x_cols, y_col, df_corr_pairs_abs_cutoff, df_bivariate_analysis):
        df_corr_pairs_abs_cutoff_bivariate = self._find_bivariate_auc_high_correlation_pairs(df_bivariate_analysis, df_corr_pairs_abs_cutoff)
        x_cols_high_correlation = list(set(df_corr_pairs_abs_cutoff_bivariate["variable_1"] + df_corr_pairs_abs_cutoff_bivariate["variable_2"]))
        x_cols_low_correlation = [x for x in x_cols if x not in x_cols_high_correlation]

        x_cols_final = list(set(self._filter_high_correlation_pairs(df_corr_pairs_abs_cutoff_bivariate) + x_cols_low_correlation))
        df_vars_final = pd.DataFrame({"variable": x_cols_final}).to_csv(f"{self._output_path}/prefinal_variables.csv", index=False)
        return df_data[x_cols_final + [y_col]]

    def preprocess_clean_low_bivariate_auc(self, df_data_preprocessed, y_col):
        x_prefinal_variables = pd.read_csv(f"{self._output_path}/prefinal_variables.csv")['variable'].to_list()
        df_bivariate_analysis = pd.read_csv(f"{self._output_path}/bivariate_analysis.csv")
        df_bivariate_analysis_prefinal = df_bivariate_analysis[df_bivariate_analysis['variable'].isin(x_prefinal_variables)]
        df_bivariate_analysis_clean = df_bivariate_analysis_prefinal[df_bivariate_analysis_prefinal['bivariate_auc'] >= self._auc_bivariate_cutoff]
        x_cols_clean = df_bivariate_analysis_clean['variable'].to_list()
        df_bivariate_analysis_clean['variable'].to_csv(f"{self._output_path}/final_variables.csv", index=False)

        df_data_preprocessed_clean = df_data_preprocessed[x_cols_clean + [y_col]]
        return df_data_preprocessed_clean

    def preprocess_dataset(self, df_data, x_cols, y_col):
        self._save_y_col_name(y_col)
        _df_descriptive_statistics = self.preprocess_descriptive_statistics(df_data, x_cols, y_col)
        df_data_preprocessed = df_data[x_cols + [y_col]]
        df_data_preprocessed = self.preprocess_impute_missing(df_data_preprocessed, x_cols)
        df_bivariate_analysis = self.preprocess_compute_bivariate_analysis(df_data_preprocessed, x_cols, y_col)
        df_corr_pairs_abs_cutoff = self.preprocess_compute_correlation_pairs(df_data_preprocessed, x_cols)
        df_data_preprocessed_clean = self.preprocess_clean_correlations(df_data_preprocessed, x_cols, y_col, df_corr_pairs_abs_cutoff, df_bivariate_analysis)
        df_data_preprocessed_clean = self.preprocess_clean_low_bivariate_auc(df_data_preprocessed_clean, y_col)

        return df_data_preprocessed_clean

def process_preprocess_dataset(x_cols, y_col):
    if (os.getcwd().endswith('src')):
        os.chdir("..")
    df_data_train = pd.read_csv("data/out/application_data_train.csv")
    preprocess_data_instance = PreprocessData("outputs/preprocess")
    df_data_train_prepared = preprocess_data_instance.preprocess_dataset(df_data_train, x_cols, y_col)
    df_data_train_prepared.to_csv("data/out/application_data_train_prepared.csv", index=False)

def main():
    x_cols = ['CNT_CHILDREN', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE', 'REGION_POPULATION_RELATIVE', 'DAYS_BIRTH', 'DAYS_EMPLOYED', 'DAYS_REGISTRATION', 'DAYS_ID_PUBLISH', 'OWN_CAR_AGE', 'FLAG_MOBIL', 'FLAG_EMP_PHONE', 'FLAG_WORK_PHONE', 'FLAG_CONT_MOBILE', 'FLAG_PHONE', 'FLAG_EMAIL', 'CNT_FAM_MEMBERS', 'REGION_RATING_CLIENT', 'REGION_RATING_CLIENT_W_CITY', 'HOUR_APPR_PROCESS_START', 'REG_REGION_NOT_LIVE_REGION', 'REG_REGION_NOT_WORK_REGION', 'LIVE_REGION_NOT_WORK_REGION', 'REG_CITY_NOT_LIVE_CITY', 'REG_CITY_NOT_WORK_CITY', 'LIVE_CITY_NOT_WORK_CITY', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'APARTMENTS_AVG', 'BASEMENTAREA_AVG', 'YEARS_BEGINEXPLUATATION_AVG', 'YEARS_BUILD_AVG', 'COMMONAREA_AVG', 'ELEVATORS_AVG', 'ENTRANCES_AVG', 'FLOORSMAX_AVG', 'FLOORSMIN_AVG', 'LANDAREA_AVG', 'LIVINGAPARTMENTS_AVG', 'LIVINGAREA_AVG', 'NONLIVINGAPARTMENTS_AVG', 'NONLIVINGAREA_AVG', 'APARTMENTS_MODE', 'BASEMENTAREA_MODE', 'YEARS_BEGINEXPLUATATION_MODE', 'YEARS_BUILD_MODE', 'COMMONAREA_MODE', 'ELEVATORS_MODE', 'ENTRANCES_MODE', 'FLOORSMAX_MODE', 'FLOORSMIN_MODE', 'LANDAREA_MODE', 'LIVINGAPARTMENTS_MODE', 'LIVINGAREA_MODE', 'NONLIVINGAPARTMENTS_MODE', 'NONLIVINGAREA_MODE', 'APARTMENTS_MEDI', 'BASEMENTAREA_MEDI', 'YEARS_BEGINEXPLUATATION_MEDI', 'YEARS_BUILD_MEDI', 'COMMONAREA_MEDI', 'ELEVATORS_MEDI', 'ENTRANCES_MEDI', 'FLOORSMAX_MEDI', 'FLOORSMIN_MEDI', 'LANDAREA_MEDI', 'LIVINGAPARTMENTS_MEDI', 'LIVINGAREA_MEDI', 'NONLIVINGAPARTMENTS_MEDI', 'NONLIVINGAREA_MEDI', 'TOTALAREA_MODE', 'OBS_30_CNT_SOCIAL_CIRCLE', 'DEF_30_CNT_SOCIAL_CIRCLE', 'OBS_60_CNT_SOCIAL_CIRCLE', 'DEF_60_CNT_SOCIAL_CIRCLE', 'DAYS_LAST_PHONE_CHANGE', 'FLAG_DOCUMENT_2', 'FLAG_DOCUMENT_3', 'FLAG_DOCUMENT_4', 'FLAG_DOCUMENT_5', 'FLAG_DOCUMENT_6', 'FLAG_DOCUMENT_7', 'FLAG_DOCUMENT_8', 'FLAG_DOCUMENT_9', 'FLAG_DOCUMENT_10', 'FLAG_DOCUMENT_11', 'FLAG_DOCUMENT_12', 'FLAG_DOCUMENT_13', 'FLAG_DOCUMENT_14', 'FLAG_DOCUMENT_15', 'FLAG_DOCUMENT_16', 'FLAG_DOCUMENT_17', 'FLAG_DOCUMENT_18', 'FLAG_DOCUMENT_19', 'FLAG_DOCUMENT_20', 'FLAG_DOCUMENT_21', 'AMT_REQ_CREDIT_BUREAU_HOUR', 'AMT_REQ_CREDIT_BUREAU_DAY', 'AMT_REQ_CREDIT_BUREAU_WEEK', 'AMT_REQ_CREDIT_BUREAU_MON', 'AMT_REQ_CREDIT_BUREAU_QRT', 'AMT_REQ_CREDIT_BUREAU_YEAR']
    y_col = "TARGET"
    process_preprocess_dataset(x_cols, y_col)

if __name__ == "__main__":
    fire.Fire(main)
