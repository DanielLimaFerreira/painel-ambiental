import dash
from dash import html, dcc
import pandas as pd
from dash import dash_table as dt
from dash import html, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/caracterizacao-dos-grupos', name='caracterizacao-dos-grupos')

snis_cleaned = pd.read_csv('data\snis-2010-2019-cleaned-cod.csv')
cluster = pd.read_csv('data\cluster.csv')
cluster = cluster.astype({"Cluster": 'int'})
cluster = cluster.astype({"Cluster": 'str'})

anos = snis_cleaned['Ano de Referência'].unique().tolist()

oobr = pd.read_csv('data/Indicadores_Obstetricos_muni.csv')
oobr_columns = [{'label':i,'value':i} for i in oobr.columns if i not in ['UF','Ano','Município','cod_municipio']]

socioeconomico = pd.read_csv('data\socioeconomico_2010.csv')
socioeconomico_columns =  [{'label':i,'value':i} for i in socioeconomico.columns if i not in ['ANO', 'UF', 'cod_municipio','Município']]

mun_info = pd.read_csv('data/mun_info.csv')

layout = html.Div(children=[
    dbc.Row([
        dbc.Col(
            html.Div(
                children=[
                    html.H2('Filtros'),
                    html.Br(),
                    html.P('Selecione o ano:',style={'font-weight': 'bold','margin':'8px'}),
                    dcc.Dropdown(id='ano_cluster',
                            options=[{'label':ano,'value':ano} for ano in anos],
                            style={'width':'300px',  'margin-bottom':'20px'},
                            value=2019),
                    html.P('Selecione a variável ambiental:', style={'font-weight': 'bold','margin':'8px'}),
                    dcc.Dropdown(id='snis_column',
                            options=[{'label':'IN013','value':'IN013 - Índice de perdas faturamento'},
                                    {'label':'IN016','value':'IN016 - Índice de tratamento de esgoto'},
                                    {'label':'IN022','value':'IN022 - Consumo médio percapita de água'},
                                    {'label':'IN049','value':'IN049 - Índice de perdas na distribuição'},
                                    {'label':'IN052','value':'IN052 - Índice de consumo de água'},
                                    {'label':'PORC1','value':'PORC1 - Porcentagem da população total atendida com abastecimento de água'},
                                    {'label':'PORC2','value':'PORC2 - Porcentagem da população total atendida com esgotamento sanitário'}
                                    ],
                            style={'width':'300px',  'margin-bottom':'20px'},
                            value='PORC1 - Porcentagem da população total atendida com abastecimento de água'),
                    html.P('Selecione a variável obstétrica:', style={'font-weight': 'bold','margin':'8px'}),
                    dcc.Dropdown(id='oobr_column',
                            options=oobr_columns,
                            style={'width':'300px', 'margin-bottom':'20px'},
                            value='Porc_anomalias'),
                    
                    html.P('Selecione a variável socioeconômica:', style={'font-weight': 'bold','margin':'8px'}),
                    dcc.Dropdown(id='column_socioeconomico_bar',
                            options=socioeconomico_columns,
                            style={'width':'300px',  'margin-bottom':'20px'},
                            value='T_ANALF18M'),

                ], style={'width':'350px', 'height':'500px', 'display':'inline-block', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'left'}
            ),xs = 12, sm=12, md=4, lg=4
        ),
        dbc.Col(html.Div(),xs = 0, sm=0, md=1, lg=1),
        dbc.Col(
        html.Div(children=[
            html.P('Análise exploratória nas variáveis ambientais de saneamento, juntamente com as variáveis obstétricas e socioeconômicas. Possibilitando comparar seus valores para cada grupo de municípios.'),
            html.Br(),
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
                            virtualization=True,

                            fixed_rows={ 'headers': True, 'data': 0 },
                            style_cell={ 'whiteSpace': 'normal'},
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_data_conditional=[
                                {'if': {'column_id': 'UF'},
                                'width': '20px'},
                                {'if': {'column_id': 'cod_mun'},
                                'width': '20px'},
                                {'if': {'column_id': 'Município'},
                                'width': '20px'},
                                {'if': {'column_id': 'Cluster'},
                                'width': '40px'}
                            ]
                
                            ,
                        )
        ],style={'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'}),xs = 12, sm=12, md=6, lg=6
        )
    ]),

        html.Div(
            id='cluster-plot' 
        ),
        html.Div(
            id='cluster-plot-oobr' 
        ),
         html.Div(
            id='cluster-plot-socioeconomico' 
        )
])

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

@callback(
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


@callback(
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

@callback(
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


@callback(
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