from dash import Dash, Input, Output, dcc
from layouts import layout

app = Dash(__name__)

app.layout= layout()

app.run_server(debug=True)
