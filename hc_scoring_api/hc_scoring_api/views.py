from flask import Flask, abort, render_template, jsonify, request
import shap
import joblib
import pandas as pd
from imblearn.pipeline import Pipeline, make_pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import hc_scoring_api.data_operations as do

app = Flask(__name__)
app.config.from_object("config.Config")
app.config.from_json("../conf.json")

df_test = pd.read_csv(app.config.get("TEST_DATA"))
#model = joblib.load(app.config.get("SERIALIZED_MODEL"))
#columns = joblib.load(app.config.get("COLUMNS_MODEL"))
#df = do.drop_columns(df_test, ['SK_ID_CURR'] + columns)
#y = do.classification(df, model, app.config.get("THRESHOLD"))
#df_transformed = model[:-3].transform(df.drop('SK_ID_CURR', axis=1))
#fi = pd.read_csv('data/feature_importance.csv', usecols=['FEATURE_NAME', 'IMPORTANCE'])
#explainer = shap.TreeExplainer(model["model"])

@app.route("/")
def home():
    return str("Home page")

@app.route("/axis/<string:ax1>/<string:ax2>")
def subset(ax1: str, ax2: str):
    df_sub = pd.concat([df[["SK_ID_CURR", ax1, ax2]], pd.Series(y, name="Résultat").map({0: 'Prêt accepté', 1: 'Prêt refusé'})], axis=1)
    return jsonify(df_sub.to_dict())
    
@app.route("/feature/<string:feat>/<int:target>")
def count_feature(feat: str, target: int):
    df_sub = do.all_values(df, y, feat, target).value_counts(normalize=True)
    return jsonify(df_sub.to_dict())

@app.route("/average/<string:feature_name>/<int:target>")
def average(feature_name: str, target: int):
    return jsonify({"aggregation" : "average", "feature" : feature_name, "target" : target, "value" : do.average_value(df, y, feature_name, target)})
    
@app.route("/value/<string:feature_name>/<int:client_id>")
def client_value(feature_name: str, client_id: int):
    return jsonify({"aggregation" : "exact_value", "feature" : feature_name, "value" : do.exact_value(df, feature_name, client_id)})
    
@app.route('/prediction/<string:client_id>')
def prediction(client_id: str):
    try:
        model = joblib.load(app.config.get("SERIALIZED_MODEL"))
    except Exception as e:
        print ("Error while loading model", "error", e)
        exit()
    
    try:
        df = pd.read_csv(app.config.get("TEST_DATA"))
    except Exception as e:
        print ("Error while loading test data", "error", e)
        exit()
        
    X = df[df.SK_ID_CURR == int(client_id)]
    if len(X) == 0:
        abort(404)
        
    X = model[:-3].transform(X.drop('SK_ID_CURR', axis=1))
    prob = model["model"].predict_proba(X)[:, 1]
    
    return jsonify({"client_id" : client_id, "score" : prob[0]})

@app.route("/explain/<string:client_id>")
def explain(client_id: str):
    if int(client_id) in df.SK_ID_CURR.values:
        d = dict()
        ind = df[df.SK_ID_CURR == int(client_id)].index[0]
        values = do.shap_values(explainer, df_transformed, ind, 1)
        for index, row in fi.sort_values('IMPORTANCE', ascending=False)[:10].iterrows():
            d[row.FEATURE_NAME] = values[index]
        return jsonify(d)
    else:
        abort(404)
    
@app.route("/explain/<string:client_id>/<string:feature_name>")
def explain_feature(client_id: str, feature_name: str):
    if int(client_id) in df.SK_ID_CURR.values:
        ind = df[df.SK_ID_CURR == int(client_id)].index[0]
        values = do.shap_values(explainer, df_transformed, ind, 1)
        return jsonify({"client_id" : client_id, "feature" : feature_name, "shap_value" : values[fi[fi.FEATURE_NAME == feature_name].index[0]]})
    else:
        abort(404)