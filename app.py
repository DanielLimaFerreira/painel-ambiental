import json
import requests
from dash import Dash, html, dcc, dash_table
import plotly.express as px
from dash.dash_table import DataTable, FormatTemplate
from dash import dash_table as dt
import pandas as pd
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

snis = pd.read_csv('data/snis-2010-2019.csv')
snis_cleaned = pd.read_csv('data\snis-2010-2019-cleaned-cod.csv')
cluster = pd.read_csv('data\cluster.csv')
cluster = cluster.astype({"Cluster": 'int'})
cluster = cluster.astype({"Cluster": 'str'})

estados = snis['Estado'].unique().tolist()
anos = snis['Ano de Referência'].unique().tolist()
colunas = ['IN013 - Índice de perdas faturamento',
            'IN016 - Índice de tratamento de esgoto',
            'IN022 - Consumo médio percapita de água',
            'IN049 - Índice de perdas na distribuição',
            'IN052 - Índice de consumo de água',
            'PORC1 - Porcentagem da população total atendida com abastecimento de água',
            'PORC2 - Porcentagem da população total atendida com esgotamento sanitário']

oobr = pd.read_csv('data/Indicadores_Obstetricos_muni.csv')
oobr_columns = [{'label':i,'value':i} for i in oobr.columns if i not in ['UF','Ano','Município','cod_municipio']]

socioeconomico = pd.read_csv('data\socioeconomico_2010.csv')
socioeconomico_columns =  [{'label':i,'value':i} for i in socioeconomico.columns if i not in ['ANO', 'UF', 'cod_municipio','Município']]

mun_info = pd.read_csv('data/mun_info.csv')

def percentage_nulls_zeros_columns(dataset):
  pct_nulls_zeros = pd.DataFrame(columns=['Coluna', 'Porcentagem de Valores Nulos','Porcentagem de Zeros'])

  for i in dataset.columns:
    pct_n = dataset[i].isna().sum()/dataset.shape[0]
    pct_z = (dataset[i] == 0).sum()/dataset.shape[0]

    values = pd.DataFrame({'Coluna':i,
                           'Porcentagem de Valores Nulos':pct_n,
                           'Porcentagem de Zeros':pct_z},index=[0])

    pct_nulls_zeros = pd.concat([values,pct_nulls_zeros],ignore_index=True)

  return pct_nulls_zeros

quality_data = percentage_nulls_zeros_columns(snis)

percentage = FormatTemplate.percentage(2)


d_columns = [{'name': i, 'id': i} for i in quality_data.columns if i == 'Coluna']
d_columns += [{'name': i, 'id': i, 'type':'numeric', 'format': percentage} for i in quality_data.columns if i != 'Coluna']


app = Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            className="head-banner",
            children=[
                html.H2(children="Painel Ambiental"),
            ],
        ),

        html.Div(
        children=[
            html.H2('Filtros'),
            html.Br(),
            html.H4('Selecione o Estado:'),
            dcc.Dropdown(id='estados',
                        options=[{'label':estado,'value':estado} for estado in estados],
                        style={'width':'200px', 'margin':'0 auto'}),
            html.H4('Selecione o ano:'),
            dcc.Dropdown(id='ano-qualidade',
                        options=[{'label':ano,'value':ano} for ano in anos],
                        style={'width':'200px', 'margin':'0 auto'},
                        value=2019),            
        ], style={'width':'200px', 'height':'360px', 'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'center'}
        ),
        html.Div(
            children=[
                dt.DataTable(id='data-table',
                            columns = d_columns,
                            data = quality_data.to_dict('records'),
                            cell_selectable = False,
                            sort_action = 'native',
                            style_as_list_view=True,
                            style_cell={'padding': '5px'},
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': c},
                                    'textAlign': 'left'
                                } for c in ['Date', 'Region']
                            ]),  
            ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}
        ),



        html.Div(
            children=[
                html.H2('Filtros'),
                html.Br(),
                html.H4('Selecione o ano:'),
                dcc.Dropdown(id='ano',
                        options=[{'label':ano,'value':ano} for ano in anos],
                        style={'width':'200px', 'margin':'0 auto'},
                        value=2019),
                html.H4('Selecione o Estado:'),
                dcc.Dropdown(id='uf',
                        options=[{'label':estado,'value':estado} for estado in estados],
                        style={'width':'200px', 'margin':'0 auto'},
                        value='SP'),
                html.H4('Selecione a coluna do snis:'),
                dcc.Dropdown(id='column',
                        options=[{'label':'IN013','value':'IN013 - Índice de perdas faturamento'},
                                 {'label':'IN016','value':'IN016 - Índice de tratamento de esgoto'},
                                 {'label':'IN022','value':'IN022 - Consumo médio percapita de água'},
                                 {'label':'IN049','value':'IN049 - Índice de perdas na distribuição'},
                                 {'label':'IN052','value':'IN052 - Índice de consumo de água'},
                                 {'label':'PORC1','value':'PORC1 - Porcentagem da população total atendida com abastecimento de água'},
                                 {'label':'PORC2','value':'PORC2 - Porcentagem da população total atendida com esgotamento sanitário'}
                                 ],
                        style={'width':'200px', 'margin':'0 auto'},
                        value='PORC1 - Porcentagem da população total atendida com abastecimento de água'),
                html.H4('Selecione a coluna socioeconômica:'),
                dcc.Dropdown(id='column_socioeconomico_map',
                        options=socioeconomico_columns,
                        style={'width':'200px', 'margin':'0 auto'},
                        value='T_ANALF18M'),

                html.H4('Selecione a coluna obstétrica:'),
                dcc.Dropdown(id='column_oobr_map',
                        options=oobr_columns,
                        style={'width':'200px', 'margin':'0 auto'},
                        value='Porc_anomalias'),
                
            ], style={'width':'200px', 'height':'600px', 'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'center'}
        ),

        html.Div(children=[
                    html.P(id='title-map', style={'text-align':'center'}),
                    dcc.Graph(id='map_graph',style={'width':'700px', 'height':'700px'})
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

        html.Div(children=[
                    html.P(id='title-map-socioeconomico', style={'text-align':'center'}),
                    dcc.Graph(id='map-graph-economico',style={'width':'700px', 'height':'700px'})
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

         html.Div(children=[
                    html.P(id='title-map-oobr', style={'text-align':'center'}),
                    dcc.Graph(id='map-graph-oobr',style={'width':'700px', 'height':'700px'})
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

        html.Div(children=[
            dt.DataTable(id='cluster-table',
                            columns = [{'name': i, 'id': i} for i in cluster.columns],
                            data = cluster.to_dict('records'),
                            cell_selectable = False,
                            #sort_action = 'native',
                            style_as_list_view=True,
                            filter_action='custom',
                            filter_query='',

                            page_action='custom',
                            page_current= 0,
                            page_size= 10,

                            sort_action='custom',
                            sort_mode='multi',
                            sort_by=[],

                            style_cell={'padding': '5px'},
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            )
        ],style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),

         html.Div(
            children=[
                html.H2('Filtros'),
                html.Br(),
                html.H4('Selecione o ano:'),
                dcc.Dropdown(id='ano_cluster',
                        options=[{'label':ano,'value':ano} for ano in anos],
                        style={'width':'200px', 'margin':'0 auto'},
                        value=2019),
                html.H4('Selecione a variável ambiental:'),
                dcc.Dropdown(id='snis_column',
                        options=[{'label':'IN013','value':'IN013 - Índice de perdas faturamento'},
                                 {'label':'IN016','value':'IN016 - Índice de tratamento de esgoto'},
                                 {'label':'IN022','value':'IN022 - Consumo médio percapita de água'},
                                 {'label':'IN049','value':'IN049 - Índice de perdas na distribuição'},
                                 {'label':'IN052','value':'IN052 - Índice de consumo de água'},
                                 {'label':'PORC1','value':'PORC1 - Porcentagem da população total atendida com abastecimento de água'},
                                 {'label':'PORC2','value':'PORC2 - Porcentagem da população total atendida com esgotamento sanitário'}
                                 ],
                        style={'width':'200px', 'margin':'0 auto'},
                        value='PORC1 - Porcentagem da população total atendida com abastecimento de água'),
                html.H4('Selecione a variável obstétrica:'),
                dcc.Dropdown(id='oobr_column',
                        options=oobr_columns,
                        style={'width':'200px', 'margin':'0 auto'},
                        value='Porc_anomalias'),
                
                html.H4('Selecione a variável socioeconômica:'),
                dcc.Dropdown(id='column_socioeconomico_bar',
                        options=socioeconomico_columns,
                        style={'width':'200px', 'margin':'0 auto'},
                        value='T_ANALF18M'),

            ], style={'width':'200px', 'height':'600px', 'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'center'}
        ),

        html.Div(
            id='cluster-plot' 
        ),
        html.Div(
            id='cluster-plot-oobr' 
        ),
         html.Div(
            id='cluster-plot-socioeconomico' 
        )    
    ]
)

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

@app.callback(
    Output('cluster-table', 'data'),
    Input('cluster-table', "page_current"),
    Input('cluster-table', "page_size"),
    Input('cluster-table', "sort_by"),
    Input('cluster-table', "filter_query")
    )
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = cluster.copy()

    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
      
        if type(filter_value) == float:
            filter_value = str(int(filter_value))

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[
        page_current*page_size: (page_current + 1)*page_size
    ].to_dict('records')


@app.callback(
    Output('data-table','data'),
    Input('estados','value'),
    Input('ano-qualidade','value')
)
def update_rows(selected_estado, ano):
    snis_copy = snis.copy()

    if selected_estado:
        snis_copy = snis_copy[snis_copy['Estado'] == selected_estado]

    if ano:
        snis_copy = snis_copy[snis_copy['Ano de Referência'] == ano]
    
    return percentage_nulls_zeros_columns(snis_copy).to_dict('records')

@app.callback(
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

    #data = load_json(uf)
    selected_mun_snis = snis_cleaned.loc[(snis_cleaned['Estado'] == uf) & (snis_cleaned['Ano de Referência'] == ano)]['Município'].values

    geodata_mun = []

    for feature in data['features']:
        #feature['id'] = feature['properties']['name']

        cod_mun = feature['properties']['codarea']

        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun

        geodata_mun.append(feature['id'])

    if ano:
        snis_copy = snis_copy[snis_copy['Ano de Referência'] == ano]
    if uf:
        snis_copy = snis_copy[snis_copy['Estado'] == uf]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun_snis))}

    snis_copy = snis_copy.append(pd.DataFrame(diff))
    snis_copy.fillna(-1, inplace=True)

    fig = px.choropleth(
        snis_copy, 
        locations = 'Município', #define the limits on the map/geography
        geojson = data, #shape information
        color = str(column), #defining the color of the scale through the database
        hover_name = 'Município', #the information in the box
        #hover_data =["Produção","Longitude","Latitude"],
        labels={str(column):''}
    )
    fig.update_geos(fitbounds = "geojson", visible = False)

    return fig

@app.callback(
    Output('title-map', 'children'),
    Input('column', 'value')
)
def update_title(column):
    return  str(column)


@app.callback(
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
        #feature['id'] = feature['properties']['name']

        cod_mun = feature['properties']['codarea']

        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun

        geodata_mun.append(feature['id'])

    if uf:
        socioeconomico_copy = socioeconomico_copy[socioeconomico_copy['UF'] == cod_estado]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun))}

    socioeconomico_copy = socioeconomico_copy.append(pd.DataFrame(diff))
    socioeconomico_copy.fillna(-1, inplace=True)

    fig = px.choropleth(
        socioeconomico_copy, 
        locations = 'Município', #define the limits on the map/geography
        geojson = data, #shape information
        color = str(column), #defining the color of the scale through the database
        hover_name = 'Município', #the information in the box
        #hover_data =["Produção","Longitude","Latitude"],
        labels={str(column):''}
    )
    fig.update_geos(fitbounds = "geojson", visible = False)

    return fig

@app.callback(
    Output('title-map-socioeconomico', 'children'),
    Input('column_socioeconomico_map', 'value')
)
def update_title(column):
    return  str(column)







############################### MAPA OOBR ########################

@app.callback(
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
        #feature['id'] = feature['properties']['name']

        cod_mun = feature['properties']['codarea']

        nome_mun = mun_info[mun_info['cod_municipio']==int(cod_mun)]['municipio'].values[0]
        feature['id'] = nome_mun

        geodata_mun.append(feature['id'])

    if uf:
        oobr_copy = oobr_copy[oobr_copy['UF'] == uf]

    if ano:
        oobr_copy = oobr_copy[oobr_copy['Ano'] == ano]

    diff = {'Município': list(set(geodata_mun) - set(selected_mun))}

    oobr_copy = oobr_copy.append(pd.DataFrame(diff))
    oobr_copy.fillna(-1, inplace=True)

    fig = px.choropleth(
        oobr_copy, 
        locations = 'Município', #define the limits on the map/geography
        geojson = data, #shape information
        color = str(column), #defining the color of the scale through the database
        hover_name = 'Município', #the information in the box
        #hover_data =["Produção","Longitude","Latitude"],
        labels={str(column):''}
    )
    fig.update_geos(fitbounds = "geojson", visible = False)

    return fig

@app.callback(
    Output('title-map-oobr', 'children'),
    Input('column_oobr_map', 'value')
)
def update_title(column):
    return  str(column)


################################################################






@app.callback(
    Output('cluster-plot', "children"),
    Input('cluster-table', "data"),
    Input('ano_cluster','value'),
    Input('snis_column', 'value'))
def update_graph_snis(rows, ano, snis_column):
    dff = pd.DataFrame(rows)

    snis_plot = pd.DataFrame({'Município':[],snis_column:[],'Cluster':[]})

    for i,row in dff.iterrows():
        snis_values = snis_cleaned.loc[(snis_cleaned['cod_municipio'] == row['cod_mun'] ) & (snis_cleaned['Ano de Referência'] == ano),[snis_column,'Município']]
        snis_values['Cluster'] = row['Cluster']
        
        snis_plot = pd.concat([snis_plot, snis_values], ignore_index=True)

    fig = px.bar(snis_plot, x='Município',y=snis_column,color='Cluster')

    return html.Div(
        [
            dcc.Graph(
                id=snis_column,
                figure={
                    "data": [
                        {
                            "x": snis_plot["Município"],
                            "y": snis_plot[snis_column],
                            "type": "bar",
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 300,
                        "title": snis_column,
                        "color": "Cluster"

                    },
                },
            )
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}
    )

@app.callback(
    Output('cluster-plot-oobr', "children"),
    Input('cluster-table', "data"),
    Input('ano_cluster','value'),
    Input('oobr_column', 'value'))
def update_graph_oobr(rows, ano, oobr_column):
    dff = pd.DataFrame(rows)

    oobr_plot = pd.DataFrame({'Município':[],oobr_column:[],'Cluster':[]})

    for i,row in dff.iterrows():
        oobr_values = oobr.loc[(oobr['cod_municipio'] == row['cod_mun'] ) & (oobr['Ano'] == ano),[oobr_column,'Município']]
        oobr_values['Cluster'] = row['Cluster']
        
        oobr_plot = pd.concat([oobr_plot, oobr_values], ignore_index=True)

    fig = px.bar(oobr_plot, x='Município',y=oobr_column,color='Cluster')

    print(oobr_plot)
    return html.Div(
        [
            dcc.Graph(
                id=oobr_column,
                figure={
                    "data": [
                        {
                            "x": oobr_plot["Município"],
                            "y": oobr_plot[oobr_column],
                            "type": "bar",
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 300,
                        "title": oobr_column,
                        "color": "Cluster"

                    },
                },
            )
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}
    )


@app.callback(
    Output('cluster-plot-socioeconomico', "children"),
    Input('cluster-table', "data"),
    Input('ano_cluster','value'),
    Input('column_socioeconomico_bar', 'value'))
def update_graph_socioeconomico(rows, ano, socioeconomico_column):
    dff = pd.DataFrame(rows)

    socioeconomico_plot = pd.DataFrame({'Município':[],socioeconomico_column:[],'Cluster':[]})

    for i,row in dff.iterrows():
        socioeconomico_values = socioeconomico.loc[(socioeconomico['cod_municipio'] == row['cod_mun'] ),[socioeconomico_column,'Município']]
        socioeconomico_values['Cluster'] = row['Cluster']
        
        socioeconomico_plot = pd.concat([socioeconomico_plot, socioeconomico_values], ignore_index=True)

    #fig = px.bar(socioeconomico_plot, x='Município',y=socioeconomico_column,color='Cluster')

    print(socioeconomico_plot)
    return html.Div(
        [
            dcc.Graph(
                id=socioeconomico_column,
                figure={
                    "data": [
                        {
                            "x": socioeconomico_plot["Município"],
                            "y": socioeconomico_plot[socioeconomico_column],
                            "type": "bar",
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 300,
                        "title": socioeconomico_column,
                        "color": "Cluster"

                    },
                },
            )
        ], style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}
    )


if __name__ == '__main__':
    app.run_server(debug=True)