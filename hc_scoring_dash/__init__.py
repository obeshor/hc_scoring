import dash
from dash import dcc, html, Input, Output
from dash.dash_table import DataTable, FormatTemplate
import pandas as pd
import requests
import locale
from babel import numbers
from .sidebar import sidebar
from .content import content

threshhold = 0.3771

df_total = pd.read_csv("data/data_test.csv")
main_columns = ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'PAYMENT_RATE', 'DAYS_BIRTH', 'IS_FEMALE', 'AMT_ANNUITY',
                'APPROVED_CNT_PAYMENT_MEAN', 'DAYS_ID_PUBLISH', 'AMT_CREDIT', 'INSTAL_AMT_PAYMENT_SUM']
df = df_total.loc[:, main_columns]



locale.setlocale(locale.LC_NUMERIC, "fr_FR")
external_scripts = ["https://cdn.plot.ly/plotly-locale-fr-latest.js"]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)



app.layout = html.Div(children=[sidebar,
                                content,
                                ])



@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_score_div(input_value):
    response = requests.request("GET", "http://localhost:5000/prediction/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    score = json_response['score']
    return score

@app.callback(
    Output('green-tank', 'value'), 
    Output('red-tank', 'value'), 
    Input('my-output', 'children'))
def update_tank(value):
    return (value * 100, value * 100)
    
@app.callback(
    Output('green-tank', 'style'),
    Input('my-output', 'children'))
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
    Input('my-output', 'children'))
def red_tank_visibility(value):
    try:
        if value < threshhold:
            return {'margin-left': '10rem', 'display': 'none'}
        else:
            return {'margin-left': '10rem', 'display': 'block'}
    except Exception:
        return {'margin-left': '10rem', 'display': 'none'}

@app.callback(
    Output(component_id='credit-amount', component_property='children'),
    Input(component_id='filter-risk', component_property='value')
)
def update_credit_amount_div(input_value):
    response = requests.request("GET", "http://localhost:5000/average/AMT_CREDIT/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/average/AMT_ANNUITY/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/average/EXT_SOURCE_3/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/average/EXT_SOURCE_2/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/average/PAYMENT_RATE/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/average/DAYS_BIRTH/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()
    val = numbers.format_decimal(json_response['value'] / -365.25, locale='fr_FR') + " ans"
    return val
    
@app.callback(
    Output(component_id='cust-credit-amount', component_property='children'),
    Input(component_id='client-id', component_property='value')
)
def update_cust_credit_amount_div(input_value):
    response = requests.request("GET", "http://localhost:5000/value/AMT_CREDIT/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/value/AMT_ANNUITY/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/value/EXT_SOURCE_3/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/value/EXT_SOURCE_2/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/value/PAYMENT_RATE/"+str(input_value))
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
    response = requests.request("GET", "http://localhost:5000/value/DAYS_BIRTH/"+str(input_value))
    if response.status_code == 404:
        return "Not found"
    json_response = response.json()    
    val = numbers.format_decimal(json_response['value'] / -365.25, locale='fr_FR') + " ans"
    return val