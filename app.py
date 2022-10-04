import dash_bootstrap_components as dbc
import dash_labs as dl
from dash import Input, Output, State, html, dcc, Dash
import dash

app = Dash(__name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        use_pages=True
    )

pages = ['documentacao','dados-faltantes','caracterizacao-dos-grupos','mapas']

icon = html.I(className="bi bi-list", style={'color':'white'})

navbar = dbc.Navbar(
    html.Div([
        html.Div([html.H4("Painel Ambiental")],style={'display':'inline-block','margin':'15px'},),
        html.Div([dbc.Button(children=icon, outline=True, size='lg',id="btn_sidebar")],style={'display':'inline-block'})
    ],className='head-banner'),
    dark=True
    )

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("Documentação", href=dash.page_registry['pages.documentacao']['path'], id="documentacao"),
                dbc.NavLink("Dados Faltantes", href=dash.page_registry['pages.dados_faltantes']['path'], id="dados-faltantes"),
                dbc.NavLink("Caracterização dos Grupos", href=dash.page_registry['pages.caracterizacao_grupos']['path'], id="caracterizacao-dos-grupos"),
                dbc.NavLink("Mapas", href=dash.page_registry['pages.mapas']['path'], id="mapas"),
            ],
            vertical=True,
            pills=True
        ),
    ],
    id="sidebar",
    className='sidebar-style'
) 

content = html.Div([dash.page_container],
    id="page-content",
    className='content_style')

app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)

@app.callback(
    [
        Output("sidebar", "className"),
        Output("page-content", "className"),
        Output("side_click", "data"),
    ],
    [Input("btn_sidebar", "n_clicks")],
    [State("side_click", "data")]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = 'sidebar_hiden'
            content_style = 'content_style_1'
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = 'sidebar-style'
            content_style = 'content_style'
            cur_nclick = "SHOW"
    else:
        sidebar_style = 'sidebar-style'
        content_style = 'content_style'
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick

@app.callback(
    [Output(f"{page}", "active") for page in pages],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        return True, False, False, False
    return [pathname == f"/{page}" for page in pages]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    return dash.page_container  

if __name__ == "__main__":
    app.run_server(debug=True)