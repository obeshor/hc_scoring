import pandas as pd
from flask import current_app as app
import shap

def drop_columns(df, columns):
    new_df = pd.DataFrame()
    for col in columns:
        if col in df.columns:
            new_df[col] = df[col]
        else:
            new_df[col] = 0
    return new_df

def classification(df, model, threshold):
    X = model[:-3].transform(df.drop('SK_ID_CURR', axis=1))
    y_pred_proba = model["model"].predict_proba(X)[:, 1]
    y_pred_final = (y_pred_proba > threshold).astype('int')
    return y_pred_final

def average_value(df, y, feature, target):
    if target in [0, 1]:
        val = df[y == target][feature].mean()
    else:
        val = df[feature].mean()
    return val
    
def exact_value(df, feature, client_id):
    mask = df.SK_ID_CURR == client_id
    if df[mask].size == 0:
        return 0
    else:
        return list(df[mask][feature])[0]

def shap_values(explainer, df, ind, target):
    shap_values = explainer.shap_values(df[ind].reshape(1,-1))
    return shap_values[target].flatten()