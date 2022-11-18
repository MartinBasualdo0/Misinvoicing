from dash import Dash, dcc, html, Input, Output,dash_table
from plotly import graph_objects as go, express as px
import pandas as pd
import src.exportaciones as expo
import src.importaciones as impo

app = Dash(__name__)

app.layout = html.Div([
    html.Header([
        html.H1('Monotior de Outliers')
    ]),
    html.Main([
        html.Strong("Comercio"),
        dcc.RadioItems(
            id="que-comercio",
            options = {
                "expo":'Exportaciones',
                "impo":'Importaciones'},
            value="expo"
            ),
            
        html.Div([
        html.Label([
            'Seleccione NCM',
            dcc.Dropdown(value="12019000",multi= False, id='dropdown-ncm') #Seleccion de las NCM dentro de la lista de comercio...
            ], id='selector-ncm',className="selector"), #Titulo del dropdown
        
        html.Label([
            'Seleccione SIM (opcional)',
            dcc.Dropdown(value=None,multi= False, id='dropdown-sim') #Seleccion de las NCM dentro de la lista de comercio...
            ], id='selector-sim',className="selector"), #Titulo del dropdown
        ],className="grid-container"),
        
        html.Strong("Color"),
        dcc.RadioItems(
            id="que-color",
            options = {
                "empresa":'Empresas',
                "pais_descri":'Paises'},
            value="pais_descri"
            ),

        html.Div([
            'Top (empresa o país): ',
            dcc.Input(id='cuantos-top', value=None,type = "number"),
        
        
        # html.Label([
        #     'Seleccione país (opcional)',
        #     dcc.Dropdown(value=None,multi= False, id='dropdown-pais') #Seleccion de las NCM dentro de la lista de comercio...
        #     ], id='selector-pais'), #Titulo del dropdown
        
        html.Div([
            'Precio máximo (opcional): ',
            dcc.Input(id='precio-top', value=None,type = "number"),
        ]),
        ],className="grid-container"),

        html.Div([
            dcc.Graph(id='grafico0',className= 'grafico'),
        ], className='grid-container'),
        
    # html.Div([dash_table.DataTable(
    #                                style_cell={'textAlign':'left'},
    #                                style_data={
    #                                 'color': 'black',
    #                                 'backgroundColor': 'white'},
    #                                style_data_conditional=[
    #                                 {
    #                                     'if': {'row_index': 'odd'},
    #                                     'backgroundColor': 'rgb(220, 220, 220)',
    #                                 }],id="tabla-html"
    #                                ),]),
        html.Div([
            html.Button('Descargar mensuales', id='btn_xlsx'),
            dcc.Download(id='download-dataframe-xlsx'),
        ],className='btn-descarga'),
     
     ]),
        
    html.Footer([
        html.P('COMEX - INDEC')
    ])
])

@app.callback(
    Output('dropdown-ncm', 'options'),
    Input('que-comercio', 'value')
    )
def get_list_ncm(comercio):
    if comercio == "expo": return expo.ncm_lista
    if comercio == "impo": return impo.ncm_lista
    
@app.callback(
    Output('dropdown-sim', 'options'),
    Input('que-comercio', 'value'),
    Input('dropdown-ncm','value')
    )
def get_list_sim(comercio, ncm):
    if comercio == "expo": return expo.sim_unique(ncm)
    if comercio == "impo": return impo.sim_unique(ncm)
    
# @app.callback(
#     Output('dropdown-pais', 'options'),
#     Input('que-comercio', 'value'),
#     Input('dropdown-ncm','value')
#     )
# def get_list_sim(comercio, ncm):
#     if comercio == "expo": return expo.pais_unique(ncm)
#     if comercio == "impo": return impo.pais_unique(ncm)


@app.callback(
    Output('grafico0','figure'),
    Input("que-comercio","value"),
    Input("dropdown-ncm",'value'),
    Input("dropdown-sim",'value'),
    Input("que-color","value"),
    Input("cuantos-top","value"),
    # Input('dropdown-pais','value'),
    Input("precio-top","value")
    )
def plot(comercio, ncm_input, sim_input,color_input,top,
        #  pais_input,
         max_range_input):
    if comercio == "expo": 
        clasificacion = "fob"
        tipo = expo
    if comercio == "impo": 
        clasificacion = "cif"
        tipo = impo
    if color_input == "empresa":
        n_empresa_input = top
        n_pais_input = None
    if color_input == "pais_descri":
        n_empresa_input = None
        n_pais_input = top
    return tipo.plot_precio(df=tipo.df_producto, #Se aclara de donde se van a sacar los datos, ignorar
                y=f'{clasificacion}_unitario_ton', # Eje Y: 'fob_unitario_ton' o 'diferencia_ref'
                ncm=ncm_input, # La nomenclatura que se quiere ver
                sim=sim_input, # El código sim
                color=color_input, # 'empresa' o 'pais_descri' para cambiar la variable que determina los colores
                n_empresa=n_empresa_input, # Por si se quiere ver un "top" de empresas, están ordenadas por fob/cif
                n_paises=n_pais_input, # "top" países, igual que con las empresas
                # pais=pais_input, # Por si se quiere ver un país en particular, pierde el sentido el n_paises
                max_range=max_range_input  # Por si se quiere poner un máximo al eje Y, muy bueno para evitar ver los outliers
    )
        
# @app.callback(
#     Output("tabla-html",'data'),
#     Output("tabla-html","columns"),
#     Input("que-comercio","value"),
#     Input("dropdown-ncm",'value'),
#     Input("dropdown-sim",'value')
# )
# def html_table(comercio, ncm_input,sim_input):
#     if comercio == "expo": 
#         # clasificacion = "fob"
#         tipo = expo
#     if comercio == "impo": 
#         # clasificacion = "cif"
#         tipo = impo
#     df = tipo.sim_filtro(df=tipo.df_producto,ncm=ncm_input,sim = sim_input)
#     return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("que-comercio","value"),
    Input("dropdown-ncm",'value'),
    Input("dropdown-sim",'value'),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)

def descarga(comercio, ncm_input, sim_input,n_clicks):
    if n_clicks is not None:
        if comercio == "expo": 
            df = expo.sim_filtro(df=expo.df_producto,ncm=ncm_input,sim = sim_input)
            return dcc.send_data_frame(df.to_excel, f"{comercio}-{ncm_input}.xlsx")
            
        if comercio == "impo": 
            df = impo.sim_filtro(df=impo.df_producto,ncm=ncm_input,sim = sim_input)
            return dcc.send_data_frame(df.to_excel, f"{comercio}-{ncm_input}.xlsx")
    
    

app.run_server(debug=True, port=8053) #Para que no se tape con el otro monitor