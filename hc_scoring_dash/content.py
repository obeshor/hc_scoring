from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

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
                                        {'label': 'Risque de défaut de paiement', 'value': '1'},
                                        {'label': 'Pas de risque de défaut de paiement', 'value': '0'},
                                    ], value='2',
                            id='filter-risk', style={'margin-right': '0', 'margin-bottom': '4px', 'margin-left': 'auto', 'width': '300px', 'display': 'block'}),
                    html.Div(children=[
                        dbc.Spinner([html.Div(children=[
                            html.Div(children=[
                                                html.Label("Moyenne", style=CELL_TITLE_STYLE),
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Montant du prêt", style=CELL_TITLE_STYLE),
                                                html.Div(id='credit-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Label("Echéance", style=CELL_TITLE_STYLE),
                                                html.Div(id='annuity-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
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
                        ], style={"margin-bottom":"4px"})], color="primary", type="border"),
                        dbc.Spinner([html.Div(children=[
                            html.Div(children=[
                                                html.Label("Client", style=CELL_TITLE_STYLE),
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-credit-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
                            html.Div(children=[
                                                html.Div(id='cust-annuity-amount', style=CELL_STYLE)
                                              ], style=GRID_STYLE),
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
                        ])], color="primary", type="border"),
                    ], style={"width":"100%"}),
                ], style=CONTENT_STYLE)
