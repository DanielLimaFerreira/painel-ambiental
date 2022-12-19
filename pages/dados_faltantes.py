import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
from dash.dash_table import FormatTemplate
from dash import dash_table as dt
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/dados-faltantes', name='dados-faltantes')

snis = pd.read_csv('data/snis-2010-2019.csv')

estados = snis['Estado'].unique().tolist()
anos = snis['Ano de Referência'].unique().tolist()


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

layout = html.Div(children=[
    dbc.Row([
        dbc.Col(
            html.Div(
            children=[
                html.H2('Filtros'),
                html.Br(),
                html.P('Selecione o Estado:',style={'font-weight': 'bold'}),
                dcc.Dropdown(id='estados',
                            options=[{'label':estado,'value':estado} for estado in estados],
                            style={'width':'200px', 'margin-bottom':'20px'}),
                html.P('Selecione o ano:',style={'font-weight': 'bold'}),
                dcc.Dropdown(id='ano-qualidade',
                            options=[{'label':ano,'value':ano} for ano in anos],
                            style={'width':'200px', 'margin':'0 auto'},
                            value=2019),            
            ], style={'width':'250px', 'height':'360px', 'display':'inline-block', 'vertical-align':'top', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)', 'text-align': 'center'}
            ),xs = 12, sm=12, md=2, lg=2
        ),
        dbc.Col(html.Div(),xs = 0, sm=0, md=1, lg=1),

        dbc.Col(
            html.Div(
                children=[
                    html.P('Verificação da porcentagem de valores nulos e de zeros para cada variável selecionada do SNIS, sendo possível aplicar filtros por Estado e ano.'),
                    html.Br(),
                    dt.DataTable(id='data-table',
                                columns = d_columns,
                                data = quality_data.to_dict('records'),
                                cell_selectable = False,
                                sort_action = 'native',
                                style_as_list_view=True,
                                style_cell={'padding': '5px',
                                            'height': 'auto',
                                            'minWidth': '90px',
                                            'width': '110px', 
                                            'maxWidth': '130px',
                                            'whiteSpace': 'normal'},
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
                ], style={'display':'inline-block', 'padding':'20px', 'margin':'20px','background-color': 'rgb(255,255,255)'},
            ),xs = 12, sm=12, md=8, lg=8
        )
    ])
])

@callback(
    Output('data-table','data'),
    Input('estados','value'),
    Input('ano-qualidade','value')
)
def update_rows(selected_estado, ano):
    snis_copy = snis.copy()

    colunas = ['IN013 - Índice de perdas faturamento',
            'IN016 - Índice de tratamento de esgoto',
            'IN022 - Consumo médio percapita de água',
            'IN049 - Índice de perdas na distribuição',
            'IN052 - Índice de consumo de água',
            'PORC1 - Porcentagem da população total atendida com abastecimento de água',
            'PORC2 - Porcentagem da população total atendida com esgotamento sanitário',
            'POP_TOT - População total do município do ano de referência (Fonte: IBGE):']

    if selected_estado:
        snis_copy = snis_copy[snis_copy['Estado'] == selected_estado]

    if ano:
        snis_copy = snis_copy[snis_copy['Ano de Referência'] == ano]
    
    return percentage_nulls_zeros_columns(snis_copy[colunas]).to_dict('records')