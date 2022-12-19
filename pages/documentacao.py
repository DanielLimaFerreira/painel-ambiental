import dash
from dash import html, dcc, Input, Output, callback

dash.register_page(__name__, path='/', name='documentacao')

layout = html.Div(children=[
    html.H1(children='Documentação'),
    
    html.P('''Esse painel tem como objetivo permitir a comparação das condições obstétricas com condições
    de saneamento básico dos municípios brasileiros.'''),

    html.P('''Sua construção se baseou na necessidade de visualização do relacionamento entre variáveis socioambientais e as obstétricas.
    Para sua construção, foram utilizadas as variáveis socioeconômicas e a classificação dos municípios em cinco grupos encontrados em Siqueira et al. (2021).
    Dessa maneira, é possível visualizar, de forma sistêmica, quais municípios pertencem a um mesmo grupo e quais municípios enquadram-se em condições socioeconômicas diferenciadas e comparar com as variáveis de saneamento e de saúde obstétrica.
    '''),
    html.P(children=['Para visualização das condições de saneamento básico, foram utilizados dados desagregados do Sistema Nacional de Informações sobre Saneamento ',
           html.A(children='SNIS',href='https://www.gov.br/mdr/pt-br/assuntos/saneamento/snis',target="_blank"),
           ', adotando indicadores com poder explicativo na diferenciação dos grupos definidos através das variáveis socioeconômicas.']),
    html.P('O painel disponibiliza também uma aba para verificação da disponibilidade e qualidade dos dados do SNIS.'),
    
    html.P('O glossário das variáveis utilizadas pode ser baixado pelo botão abaixo:'),
    html.Button("Download Glossário", id="btn-download-txt"),

    dcc.Download(id="download-text"),
    html.Br(),
    html.Br(),
    html.H4('Referências'),
    html.P('SIQUEIRA, Thayane Santos et al. Spatial clusters, social determinants of health and risk of maternal mortality by COVID-19 in Brazil: a national population-based ecological study. The Lancet Regional Health-Americas, v. 3, p. 100076, 2021.'),
    html.Br(),
])

@callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(
        "assets/Variáveis utilizadas e glossários.pdf"
    )
