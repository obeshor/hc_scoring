import dash
from dash import dcc, html, Input, Output
import pandas as pd
import requests
import locale
from babel import numbers
from .sidebar import sidebar
from .content import content, scale_color_shap_value
import plotly.express as px

threshhold = 0.3771
API_ADDRESS = "https://hc-scoring-api.herokuapp.com/"

#locale.setlocale(locale.LC_NUMERIC, "fr_FR")
#external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div(children=[sidebar,
                                content,
                                ])


@app.callback(
    [Output(component_id='score-output', component_property='children'),
    Output(component_id='result-output', component_property='children'),],
    Input(component_id='client-id', component_property='value')
)
def update_score_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/prediction/"+str(input_value))
    if response.status_code == 404:
        return ("Not found", "Not found")
    json_response = response.json()    
    score = json_response['score']
    if score > threshhold:
        result = "prêt refusé"
    else:
        result = "prêt accepté"
    return (score, result)

@app.callback(
    Output('green-tank', 'value'), 
    Output('red-tank', 'value'), 
    Input('score-output', 'children'))
def update_tank(value):
    return (value * 100, value * 100)
    
@app.callback(
    Output('green-tank', 'style'),
    Input('score-output', 'children'))
def green_tank_visibility(value):
    try:
        if value >= threshhold:
            return {'margin-left': '10rem', 'display': 'none'}
        else:
            return {'margin-left': '10rem', 'display': 'block'}
    except Exception:
        return {'margin-left': '10rem', 'display': 'block'}

@app.callback(
    Output('red-tank', 'style'),
    Input('score-output', 'children'))
def red_tank_visibility(value):
    try:
        if value < threshhold:
            return {'margin-left': '10rem', 'display': 'none'}
        else:
            return {'margin-left': '10rem', 'display': 'block'}
    except Exception:
        return {'margin-left': '10rem', 'display': 'none'}


@app.callback(
    Output(component_id='outcome-value', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_outcome_div(input_value):
    if int(input_value) == 0:
        return "Acceptés"
    elif int(input_value) == 1:
        return "Refusés"
    else:
        return "Tous"

@app.callback(
    Output(component_id='credit-amount', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_credit_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/AMT_CREDIT/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    #'${:,.2f}'.format(
    val = numbers.format_currency(json_response['value'], 'USD', locale='fr_FR')
    return val
    
@app.callback(
    Output(component_id='annuity-amount', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_annuity_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/AMT_ANNUITY/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_currency(json_response['value'], 'USD', locale='fr_FR')
    return val
    
@app.callback(
    Output(component_id='extsource3-value', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_extsource3_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/EXT_SOURCE_3/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_percent(json_response['value'], locale='fr_FR')
    return val

@app.callback(
    Output(component_id='extsource2-value', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_extsource2_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/EXT_SOURCE_2/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_percent(json_response['value'], locale='fr_FR')
    return val
    
@app.callback(
    Output(component_id='payment-rate-value', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_payment_rate_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/PAYMENT_RATE/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_decimal(1 / json_response['value'], locale='fr_FR') + " ans"
    return val
    
@app.callback(
    Output(component_id='days-birth-value', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_days_birth_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/average/DAYS_BIRTH/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    val = numbers.format_decimal(json_response['value'] / -365.25, locale='fr_FR') + " ans"
    return val

@app.callback(
    [Output(component_id='sex-category', component_property='children'),
    Output(component_id='sex-category', component_property='style'),],
    Input(component_id='filter-risk', component_property='value')
)
def update_sex_category_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/feature/IS_FEMALE/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    perc_list = list(json_response.values())
    return (numbers.format_percent(perc_list[0], locale='fr_FR') + " _____|_____ " + numbers.format_percent(perc_list[1], locale='fr_FR'),
            {"background-image": "linear-gradient(to right, royalblue 45%, palevioletred 20%)", "padding" : "4px", "text-align" : "right"})


@app.callback(
    Output(component_id='cust-credit-amount', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_credit_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/AMT_CREDIT")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}

@app.callback(
    Output(component_id='cust-annuity-amount', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_annuity_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/AMT_ANNUITY")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}

@app.callback(
    Output(component_id='cust-extsource2-value', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_extsource2_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/EXT_SOURCE_2")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}
        
@app.callback(
    Output(component_id='cust-extsource3-value', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_extsource3_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/EXT_SOURCE_3")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}

@app.callback(
    Output(component_id='cust-payment-rate-value', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_payment_rate_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/PAYMENT_RATE")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}

@app.callback(
    Output(component_id='cust-days-birth-value', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_days_birth_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/DAYS_BIRTH")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}

@app.callback(
    Output(component_id='cust-sex-value', component_property='style'),
    Input(component_id='client-id', component_property='value')
)
def color_cust_sex_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/explain/"+str(input_value)+"/IS_FEMALE")
    if response.status_code == 404:
        return {'padding' : '4px', 'text-align' : 'right'}
    json_response = response.json()
    shap_value = json_response['shap_value']
    try:
        return scale_color_shap_value(shap_value)
    except Exception:
        return {'padding' : '4px', 'text-align' : 'right'}





@app.callback(
    Output(component_id='cust-credit-amount', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_credit_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/AMT_CREDIT/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    val = numbers.format_currency(json_response['value'], 'USD', locale='fr_FR')
    return val

@app.callback(
    Output(component_id='cust-annuity-amount', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_annuity_amount_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/AMT_ANNUITY/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_currency(json_response['value'], 'USD', locale='fr_FR')
    return val
    
@app.callback(
    Output(component_id='cust-extsource3-value', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_extsource3_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/EXT_SOURCE_3/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_percent(json_response['value'], locale='fr_FR')
    return val

@app.callback(
    Output(component_id='cust-extsource2-value', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_extsource2_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/EXT_SOURCE_2/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_percent(json_response['value'], locale='fr_FR')
    return val
    
@app.callback(
    Output(component_id='cust-payment-rate-value', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_payment_rate_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/PAYMENT_RATE/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    if json_response['value'] == 0:
        val = "0"
    else:
        val = numbers.format_decimal(1 / json_response['value'], locale='fr_FR') + " ans"
    return val
    
@app.callback(
    Output(component_id='cust-days-birth-value', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_days_birth_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/DAYS_BIRTH/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_decimal(json_response['value'] / -365.25, locale='fr_FR') + " ans"
    return val

@app.callback(
    Output(component_id='cust-sex-value', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_sex_value_div(input_value):
    response = requests.request("GET", API_ADDRESS+"/value/IS_FEMALE/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    if json_response['value'] == 1:
        val = "Femme"
    else:
        val = "Homme"
    return val


@app.callback(
    Output(component_id='scatter-plot', component_property='figure'),
    Input(component_id='filter-axis1', component_property='value'),
    Input(component_id='filter-axis2', component_property='value'),
    Input(component_id='client-id', component_property='value')
)
def update_graph_axes(axis1, axis2, client_id):
    response = requests.request("GET", API_ADDRESS+"/axis/"+str(axis1)+"/"+str(axis2))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json() 
    df = pd.DataFrame(json_response)
    if axis1 == "PAYMENT_RATE":
        df["DUREE"] = [1/val if val != 0 else 0 for val in df[axis1]]
        axis1 = "DUREE"
    if axis1 == "DAYS_BIRTH":
        df["AGE"] = [val/-365 for val in df[axis1]]
        axis1 = "AGE"
    if axis2 == "PAYMENT_RATE":
        df["DUREE"] = [1/val if val != 0 else 0 for val in df[axis2]]
        axis2 = "DUREE"
    if axis2 == "DAYS_BIRTH":
        df["AGE"] = [val/-365 for val in df[axis2]]
        axis2 = "AGE"
    fig = px.scatter(df, x=axis1, y=axis2, color="Résultat")
    if response.status_code != 404:
        fig.add_traces(px.scatter(df[df.SK_ID_CURR == int(client_id)], x=axis1, y=axis2).update_traces(marker_size=20, marker_color="yellow").data)
    fig.update_layout(title_text="Répartition des clients", title_x=0.5, legend=dict(bgcolor="#F1F5FF"))
    return fig
