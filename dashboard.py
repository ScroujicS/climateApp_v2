# dashboard.py
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
from db_utils import load_climate_data

def create_dashboard(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/dash/', suppress_callback_exceptions=True)
    
    df = load_climate_data()
    cities = df['city'].unique()

    app.layout = html.Div([
        html.H2("Климатический дашборд"),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in cities],
            value=cities[0],
            clearable=False
        ),
        dcc.Graph(id='temperature-graph')
    ])

    @app.callback(
        Output('temperature-graph', 'figure'),
        Input('city-dropdown', 'value')
    )
    def update_graph(selected_city):
        filtered = df[df['city'] == selected_city]
        fig = px.line(filtered, x='timestamp', y='temperature', title=f"Температура в {selected_city}")
        return fig

    return app