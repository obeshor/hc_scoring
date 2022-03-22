from flask import Flask, abort, render_template, jsonify, request
import shap
import joblib
import pandas as pd
import hc_scoring_api.data_operations as do

app = Flask(__name__)
app.config.from_object("config.Config")
app.config.from_json("../conf.json")

df = pd.read_csv(app.config.get("TEST_DATA"))
model = joblib.load(app.config.get("SERIALIZED_MODEL"))
columns = joblib.load("model/columns.joblib")
df = do.drop_columns(df, ['SK_ID_CURR'] + columns)
y = do.classification(df, model, app.config.get("THRESHOLD"))
df_transformed = model[:-3].transform(df.drop('SK_ID_CURR', axis=1))
fi = pd.read_csv('data/feature_importance.csv', usecols=['FEATURE_NAME', 'IMPORTANCE'])
explainer = shap.TreeExplainer(model["model"])

@app.route("/")
def home():
    return str(do.average_value(df, y, "EXT_SOURCE_3", 1))

@app.route("/average/<string:feature_name>/<int:target>")
def average(feature_name: str, target: int):
    return jsonify({"aggregation" : "average", "feature" : feature_name, "target" : target, "value" : do.average_value(df, y, feature_name, target)})
    
@app.route("/value/<string:feature_name>/<int:client_id>")
def client_value(feature_name: str, client_id: int):
    return jsonify({"aggregation" : "exact_value", "feature" : feature_name, "value" : do.exact_value(df, feature_name, client_id)})
    
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        client_id = request.form['client_id']
    model = joblib.load(app.config.get("SERIALIZED_MODEL"))
    df = pd.read_csv(app.config.get("TEST_DATA"))
    X = df[df.SK_ID_CURR == int(client_id)]
    X = model[:-3].transform(X.drop('SK_ID_CURR', axis=1))
    prob = model["model"].predict_proba(X)[:, 1]
    return jsonify({"client_id" : client_id, "score" : prob[0]})

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

@app.route('/verification/<string:client_id>')
def verification(client_id: str):
    model = joblib.load(app.config.get("SERIALIZED_MODEL"))
    df = pd.read_csv("data/data_500.csv")
    X = df[df.SK_ID_CURR == int(client_id)]
    target = X.TARGET.values[0]
    X = model[:-3].transform(X.drop(['SK_ID_CURR', 'TARGET'], axis=1))
    prob = model["model"].predict_proba(X)[:, 1]
    return jsonify({"client_id" : client_id, "score" : prob[0], "target" : str(target)})

@app.route("/explain/<string:client_id>")
def explain(client_id: str):
    d = dict()
    ind = df[df.SK_ID_CURR == int(client_id)].index[0]
    values = do.shap_values(explainer, df_transformed, ind, 1)
    for index, row in fi.sort_values('IMPORTANCE', ascending=False)[:10].iterrows():
        d[row.FEATURE_NAME] = values[index]
    return jsonify(d)
    
@app.route("/explain/<string:client_id>/<string:feature_name>")
def explain_feature(client_id: str, feature_name: str):
    ind = df[df.SK_ID_CURR == int(client_id)].index[0]
    values = do.shap_values(explainer, df_transformed, ind, 1)
    return jsonify({"client_id" : client_id, "feature" : feature_name, "shap_value" : values[fi[fi.FEATURE_NAME == feature_name].index[0]]})