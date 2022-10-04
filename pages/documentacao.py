import dash
from dash import html, dcc

dash.register_page(__name__, path='/', name='documentacao')

layout = html.Div(children=[
    html.H1(children='Documentação'),

    html.Div(children='''
        Conteúdo da aba de documentação.
    '''),
])