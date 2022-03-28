from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

CONTENT_STYLE = {
    "margin-left": "34rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "width": "80%",
}

GRID_STYLE = {
    "display": "inline-block", 
    "background-color": "SlateGrey",
    "color": "white",
    "margin-left": "4px", 
    "width" : "13%"
}

GRID_ROW_STYLE = {
    "display": "inline-block", 
    "background-color": "SlateGrey",
    "color": "white",
    "margin-left": "4px", 
    "width" : "8%"
}

GRID_HIDDEN_STYLE = {
    'display': 'none', 
    "background-color": "SlateGrey",
    "color": "white",
    "margin-left": "4px", 
    "width" : "13%"
}
    
CELL_TITLE_STYLE = {
    'padding' : '4px', 
    'font-size': '16px', 
    'font-weight': 'bold'
}
CELL_STYLE = {
    'padding' : '4px', 
    'text-align' : 'right'
}

content = html.Div(children=[
                    dcc.Dropdown(
                            options=[
                                        {'label': 'Tous', 'value': '2'},
                                        {'label': 'Refusés', 'value': '1'},
                                        {'label': 'Acceptés', 'value': '0'},
                                    ], value='2',
                            id='filter-risk', style={'margin-right': '0', 'margin-bottom': '4px', 'margin-left': 'auto', 'width': '300px', 'display': 'block'}),
                    html.Div(children=[
                        dbc.Spinner([html.Div(children=[
                            html.Div(children=[
                                                html.Div(id='outcome-value', style=CELL_TITLE_STYLE)
                                              ], style=GRID_ROW_STYLE),
                            html.Div(children=[
                                                html.Label("Montant du prêt", style=GRID_HIDDEN_STYLE),
                                                html.Div(id='credit-amount', style=GRID_HIDDEN_STYLE)
                                              ], style=GRID_HIDDEN_STYLE),
                            html.Div(children=[
                                                html.Label("Score source 3", style=CELL_TITLE_STYLE),
                                                html.Div(id='extsource3-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Score source 2", style=CELL_TITLE_STYLE),
                                                html.Div(id='extsource2-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Durée", style=CELL_TITLE_STYLE),
                                                html.Div(id='payment-rate-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Age", style=CELL_TITLE_STYLE),
                                                html.Div(id='days-birth-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Echéances", style=CELL_TITLE_STYLE),
                                                html.Div(id='annuity-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Hommes|Femmes", style=CELL_TITLE_STYLE),
                                                html.Div(id='sex-category', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                        ], style={"margin-bottom":"4px"})], color="primary", type="border"),
                        dbc.Spinner([html.Div(children=[
                            html.Div(children=[
                                                html.Label("Client", style=CELL_TITLE_STYLE),
                                              ], style=GRID_ROW_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-credit-amount', style=GRID_HIDDEN_STYLE)
                                              ], style=GRID_HIDDEN_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-extsource3-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-extsource2-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-payment-rate-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-days-birth-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-annuity-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-sex-value', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                        ])], color="primary", type="border"),
                    ], style={"width":"80%", "display": "inline-block"}),
                    html.Br(),
                    dbc.Spinner([
                        dcc.Graph(id='scatter-plot',
                                figure={
                                        "data": [],
                                        "layout": {
                                        },
                                    },),
                        html.Div(children=[
                            html.Div(children=[
                                    html.Label("Axe 1", style={"text-align": "center", "background-color": "SlateGrey", "color": "white", "width": "300px", "margin-left": "4px", "margin-right": "4px"}),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'Score source 3', 'value': 'EXT_SOURCE_3'},
                                            {'label': 'Score source 2', 'value': 'EXT_SOURCE_2'},
                                            {'label': 'Durée', 'value': 'PAYMENT_RATE'},
                                            {'label': 'Age', 'value': 'DAYS_BIRTH'},
                                            {'label': 'Echéances', 'value': 'AMT_ANNUITY'},
                                            {'label': 'Montant du prêt', 'value': 'AMT_CREDIT'},
                                        ], value='EXT_SOURCE_3',
                                        id='filter-axis1', style={"display": "inline-block", "width": "300px"})
                                    ], style={"display": "inline-block"}),
                            html.Div(children=[
                                    html.Label("Axe 2", style={"text-align": "center", "background-color": "SlateGrey", "color": "white", "width": "300px", "margin-left": "4px", "margin-right": "4px"}),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'Score source 3', 'value': 'EXT_SOURCE_3'},
                                            {'label': 'Score source 2', 'value': 'EXT_SOURCE_2'},
                                            {'label': 'Durée', 'value': 'PAYMENT_RATE'},
                                            {'label': 'Age', 'value': 'DAYS_BIRTH'},
                                            {'label': 'Echéances', 'value': 'AMT_ANNUITY'},
                                            {'label': 'Montant du prêt', 'value': 'AMT_CREDIT'},
                                        ], value='EXT_SOURCE_2',
                                        id='filter-axis2', style={"display": "inline-block", "width": "300px"})
                                    ], style={"display": "inline-block"})
                                ], style={"text-align": "center"}
                            ),
                        ], color="primary", type="border")
                ], style=CONTENT_STYLE)
                
                
def scale_color_shap_value(val):
    if val > 0.7:
        style = {'padding' : '4px', 'text-align' : 'right', 'background-color': 'Crimson'}
    elif val > 0.1:
        style = {'padding' : '4px', 'text-align' : 'right', 'background-color': 'Tomato'}
    elif val < -0.7:
        style = {'padding' : '4px', 'text-align' : 'right', 'background-color': 'LimeGreen'}
    elif val < -0.1:
        style = {'padding' : '4px', 'text-align' : 'right', 'background-color': 'Lime'}
    else:
        style = {'padding' : '4px', 'text-align' : 'right'}
    return style