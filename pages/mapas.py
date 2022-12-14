from turtle import width
import dash
import requests
import numpy as np
from dash import html, dcc, callback
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


dash.register_page(__name__,path='/mapas', name='mapas')

snis_cleaned = pd.read_csv('data\snis-2010-2019-cleaned-cod.csv')

estados = snis_cleaned['Estado'].unique().tolist()
anos = snis_cleaned['Ano de Referência'].unique().tolist()


oobr = pd.read_csv('data/Indicadores_Obstetricos_muni.csv')
oobr_columns = [{'label':i,'value':i} for i in oobr.columns if i not in ['UF','Ano','Município','cod_municipio']]

socioeconomico = pd.read_csv('data\socioeconomico_2010.csv')
socioeconomico_columns =  [{'label':i,'value':i} for i in socioeconomico.columns if i not in ['ANO', 'UF', 'cod_municipio','Município']]

mun_info = pd.read_csv('data/mun_info.csv')

layout = html.Div(children=[
    
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                        children=[
                            html.H2('Filtros'),
                            html.Br(),
                            html.P('Visualize os valores das variáveis selecionadas para os municípios de cada Estado e ano.'),

                            html.P('Selecione o ano:',style={'font-weight': 'bold','margin':'8px'}),
                            dcc.Dropdown(id='ano',
                                    options=[{'label':ano,'value':ano} for ano in anos],
                                    style={'width':'300px', 'margin-bottom':'20px'},
                                    value=2019,
                                    clearable=False),
                            html.P('Selecione o Estado:',style={'font-weight': 'bold','margin':'8px'}),
                            dcc.Dropdown(id='uf',
                                    options=[{'label':estado,'value':estado} for estado in estados],
                                    style={'width':'300px', 'margin-bottom':'20px'},
                                    value='SP',
                                    clearable=False),
                            html.P('Selecione a coluna do snis:',style={'font-weight': 'bold','margin':'8px'}),
                            dcc.Dropdown(id='column',
                                    options=[{'label':'IN013','value':'IN013 - Índice de perdas faturamento'},
                                            {'label':'IN016','value':'IN016 - Índice de tratamento de esgoto'},
                                            {'label':'IN022','value':'IN022 - Consumo médio percapita de água'},
                                            {'label':'IN049','value':'IN049 - Índice de perdas na distribuição'},
                                            {'label':'IN052','value':'IN052 - Índice de consumo de água'},
                                            {'label':'PORC1','value':'PORC1 - Porcentagem da população total atendida com abastecimento de água'},
                                            {'label':'PORC2','value':'PORC2 - Porcentagem da população total atendida com esgotamento sanitário'}
                                            ],
                                    style={'width':'300px', 'margin-bottom':'20px'},
                                    value='PORC1 - Porcentagem da população total atendida com abastecimento de água',
                                    clearable=False),
                            html.P('Selecione a coluna socioeconômica:',style={'font-weight': 'bold','margin':'8px'}),
                            dcc.Dropdown(id='column_socioeconomico_map',
                                    options=socioeconomico_columns,
                                    style={'width':'300px', 'margin-bottom':'20px'},
                                    value='T_ANALF18M',
                                    clearable=False),

                            html.P('Selecione a coluna obstétrica:',style={'font-weight': 'bold','margin':'8px'}),
                            dcc.Dropdown(id='column_oobr_map',
                                    options=oobr_columns,
                                    style={'width':'300px',  'margin-bottom':'20px'},
                                    value='Porc_anomalias',
                                    clearable=False),
                            
                        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'left'}
                ),xs = 12, sm=12, md=6, lg=3
            ),
            dbc.Col(html.Div(),xs = 0, sm=0, md=1, lg=1),

            dbc.Col(
                html.Div(children=[
                        html.P(id='title-map', style={'text-align':'center'}),
                        dcc.Loading(dcc.Graph(id='map_graph',responsive=True),type='circle')
                ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}
                ),xs=12, sm=12, md=12, lg=8
            )
        ]
    ),

       

        html.Div(children=[
                    html.P(id='title-map-socioeconomico', style={'text-align':'center'}),
                    dcc.Loading(dcc.Graph(id='map-graph-economico',style={'width':'800px', 'height':'400px'}),type='circle')
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

         html.Div(children=[
                    html.P(id='title-map-oobr', style={'text-align':'center'}),
                    dcc.Loading(dcc.Graph(id='map-graph-oobr',style={'width':'800px', 'height':'400px'}),type='circle')
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

])


@callback(
    Output('map_graph','figure'),
    Input('ano','value'),
    Input('uf','value'),
    Input('column', 'value')
)
def update_map(ano, uf, column):
    snis_copy = snis_cleaned.copy()
    cod_estado = int(mun_info[mun_info['UF']==uf]['cod_UF'].values[0])
    response = requests.get(f'https://servicodados.ibge.gov.br/api/v2/malhas/{cod_estado}?resolucao=5&formato=application/vnd.geo+json')
    data = response.json()
    selected_mun_snis = snis_cleaned.loc[(snis_cleaned['Estado'] == uf) & (snis_cleaned['Ano de Referência'] == ano)]['Município'].values
    geodata_mun = []

    for feature in data['features']:
        cod_mun = feature['properties']['codarea']
        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun
        geodata_mun.append(feature['id'])

    if ano:
        snis_copy = snis_copy[snis_copy['Ano de Referência'] == ano]
    if uf:
        snis_copy = snis_copy[snis_copy['Estado'] == uf]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun_snis))}
    min_value = snis_copy[column].min()
    snis_copy = snis_copy.append(pd.DataFrame(diff))

    if snis_copy[column].isnull().sum() > 0:
        gray_scale_value = min_value - 1e-5
        snis_copy.fillna(gray_scale_value, inplace=True)

    else:
        gray_scale_value = np.nan

    return generate_map(data, snis_copy, column, gray_scale_value)

@callback(
    Output('title-map', 'children'),
    Input('column', 'value')
)
def update_title(column):
    return  str(column)


@callback(
    Output('map-graph-economico','figure'),
    Input('uf','value'),
    Input('column_socioeconomico_map', 'value')
)
def update_map_economico(uf, column):
    socioeconomico_copy = socioeconomico.copy()
    cod_estado = int(mun_info[mun_info['UF']==uf]['cod_UF'].values[0])
    response = requests.get(f'https://servicodados.ibge.gov.br/api/v2/malhas/{cod_estado}?resolucao=5&formato=application/vnd.geo+json')
    data = response.json()
    selected_mun = socioeconomico_copy.loc[(socioeconomico_copy['UF'] == cod_estado)]['Município'].values
    geodata_mun = []

    for feature in data['features']:
        cod_mun = feature['properties']['codarea']
        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun
        geodata_mun.append(feature['id'])

    if uf:
        socioeconomico_copy = socioeconomico_copy[socioeconomico_copy['UF'] == cod_estado]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun))}
    min_value = socioeconomico_copy[column].min()
    socioeconomico_copy = socioeconomico_copy.append(pd.DataFrame(diff))

    if socioeconomico_copy[column].isnull().sum() > 0:
        gray_scale_value = min_value - 1e-5
        socioeconomico_copy.fillna(gray_scale_value, inplace=True)

    else:
        gray_scale_value = np.nan

    return generate_map(data, socioeconomico_copy, column, gray_scale_value)

@callback(
    Output('title-map-socioeconomico', 'children'),
    Input('column_socioeconomico_map', 'value')
)
def update_title(column):
    return  str(column)


@callback(
    Output('map-graph-oobr','figure'),
    Input('ano','value'),
    Input('uf','value'),
    Input('column_oobr_map', 'value')
)
def update_map_oobr(ano, uf, column):
    oobr_copy = oobr.copy()
    cod_estado = int(mun_info[mun_info['UF']==uf]['cod_UF'].values[0])
    response = requests.get(f'https://servicodados.ibge.gov.br/api/v2/malhas/{cod_estado}?resolucao=5&formato=application/vnd.geo+json')
    data = response.json()
    selected_mun = oobr_copy.loc[(oobr_copy['UF'] == uf) & (oobr_copy['Ano'] == ano)]['Município'].values
    geodata_mun = []

    for feature in data['features']:
        cod_mun = feature['properties']['codarea']
        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun
        geodata_mun.append(feature['id'])

    if uf:
        oobr_copy = oobr_copy[oobr_copy['UF'] == uf]

    if ano:
        oobr_copy = oobr_copy[oobr_copy['Ano'] == ano]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun))}
    min_value = oobr_copy[column].min()
    oobr_copy = oobr_copy.append(pd.DataFrame(diff))

    if oobr_copy[column].isnull().sum() > 0:
        gray_scale_value = min_value - 1e-5
        oobr_copy.fillna(gray_scale_value, inplace=True)

    else:
        gray_scale_value = np.nan

    return generate_map(data, oobr_copy, column, gray_scale_value)

@callback(
    Output('title-map-oobr', 'children'),
    Input('column_oobr_map', 'value')
)
def update_title(column):
    return  str(column)


def generate_map(geojson, dataset, column, gray_scale_value):

    if not np.isnan(gray_scale_value):
        color_legend = [[0, "rgb(160, 160, 160)"],
                        [1e-10, "rgb(49,54,149)"],
                        [0.1111111111111111, "rgb(69,117,180)"],
                        [0.2222222222222222, "rgb(116,173,209)"],
                        [0.3333333333333333, "rgb(171,217,233)"],
                        [0.4444444444444444, "rgb(224,243,248)"],
                        [0.5555555555555555, "rgb(254,224,144)"],
                        [0.6666666666666666, "rgb(253,174,97)"],
                        [0.7777777777777777, "rgb(244,109,67)"],
                        [0.8888888888888888, "rgb(215,48,39)"],
                        [1, "rgb(165,0,38)"]]

    else:
        color_legend = [[0, "rgb(49,54,149)"],
                        [0.1111111111111111, "rgb(69,117,180)"],
                        [0.2222222222222222, "rgb(116,173,209)"],
                        [0.3333333333333333, "rgb(171,217,233)"],
                        [0.4444444444444444, "rgb(224,243,248)"],
                        [0.5555555555555555, "rgb(254,224,144)"],
                        [0.6666666666666666, "rgb(253,174,97)"],
                        [0.7777777777777777, "rgb(244,109,67)"],
                        [0.8888888888888888, "rgb(215,48,39)"],
                        [1, "rgb(165,0,38)"]]


    fig = go.Figure(data=go.Choropleth(
        geojson=geojson,
        locations=dataset['Município'],
        z=dataset[column],
        marker_line_color='white',
        marker_line_width=0.5,
        colorscale=color_legend,
        hovertemplate=np.select(
                [dataset[column] == gray_scale_value], ["%{location}<extra>--</extra>"], "%{location}<extra>%{z}</extra>"
        ),
    ))
    fig.update_geos(fitbounds = "locations", visible = False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
