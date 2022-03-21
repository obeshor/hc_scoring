import pandas as pd
from flask import current_app as app

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
