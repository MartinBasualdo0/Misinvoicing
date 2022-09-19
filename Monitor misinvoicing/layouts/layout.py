from dash import html, dcc

def layout():
    return (html.Div([
        html.Header([
            html.H1('MONITOR: Intercambio comercial Argentino')
        ])
]),
            html.Main([
                html.Div([
                    html.Label([
            'Seleccione NCM',
            dcc.Dropdown(value=27101921 ,multi= False, id='dropdown-ncm', persistence=True) #Seleccion de las NCM dentro de la lista
            ])
                ])
            ])
    )
    