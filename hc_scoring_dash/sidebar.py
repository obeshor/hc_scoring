from dash import dcc, html, Input, Output
import dash_daq as daq

threshhold = 0.3771

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "32rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

LABEL_STYLE = {
    'display':'inline-block', 'padding-right':'20px'
}

sidebar = html.Div(
    [
        html.H3(children='Home Credit Default Risk'),
        html.H4(children='Scoring crédit'),
        html.Hr(),
        html.Div([
            html.Label("ID client", style=LABEL_STYLE),
            dcc.Input(id='client-id', value='100001', type='text', debounce=True)
            ]),
        html.Br(),
        html.Label("Seuil retenu : " + str(threshhold)),
        html.Div([html.Label("Score : ", style=LABEL_STYLE), html.Div(id='score-output', style={'display':'inline-block'})]),
        html.Br(),
        daq.Tank(
            id='green-tank',
            value=0,
            min=0,
            max=100,
            color="LimeGreen",
            style={'margin-left': '10rem'}
            ),
        daq.Tank(
            id='red-tank',
            value=0,
            min=0,
            max=100,
            color="Crimson",
            style={'margin-left': '10rem', 'display': 'none'}
            ),
        html.Br(),
        html.Div([html.Label("Résultat : ", style=LABEL_STYLE), html.Div(id='result-output', style={'display':'inline-block'})]),
    ],
    style=SIDEBAR_STYLE,
)


