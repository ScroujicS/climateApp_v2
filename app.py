import pandas as pd
from flask import Flask, render_template, request, jsonify
import dash
from dash import dcc, html, Input, Output, ctx
import plotly.express as px
import plotly.io as pio
from dash.dependencies import State
import json
import dash_bootstrap_components as dbc
# Читаем данные из CSV
df = pd.read_csv("mock_climate_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')

GRAPH_TYPES = {
    "temperature": "Температура (°C)",
    "humidity": "Влажность (%)",
    "pressure": "Давление (гПа)",
    "wind_speed": "Скорость ветра (м/с)",
    "feels_like": "Ощущается как (°C)"
}

app.layout = html.Div(className="gradient-bg", children=[
    html.Div(className="container py-5", children=[
        html.H1("🌦 Климатический дашборд", className="text-center mb-4 text-gray-800", style={
            "fontWeight": "bold",
            "textShadow": "2px 2px 4px rgba(0,0,0,0.1)"
        }),

        dbc.Row([
            dbc.Col([
                html.Label("Выберите город:", className="mb-2 text-gray-700 font-medium"),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=[{"label": city, "value": city} for city in df["city"].unique()],
                    value=df["city"].unique()[0],
                    className="mb-4",
                    style={"width": "100%"}
                ),
            ], md=4),

            dbc.Col([
                html.Label("Типы графиков:", className="mb-2 text-gray-700 font-medium"),
                dcc.Checklist(
                    id="graph-types-checklist",
                    options=[{"label": v, "value": k} for k, v in GRAPH_TYPES.items()],
                    value=["temperature", "humidity"],
                    className="dash-card",
                    inline=True
                ),
            ], md=8)
        ]),

        html.Div(className="dash-card my-4", children=[
            html.Label("Диапазон дат:", className="mb-2 text-gray-700 font-medium"),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=df['timestamp'].min(),
                max_date_allowed=df['timestamp'].max(),
                start_date=df['timestamp'].min(),
                end_date=df['timestamp'].max(),
                className="w-100"
            ),
        ]),

        html.Button("Выгрузить CSV",
                    id="btn-download-csv",
                    className="btn btn-primary px-4 py-2 shadow-sm"
                    ),
        dcc.Download(id="download-dataframe-csv"),
        html.Div(id="graphs-container", className="mt-4"),
    ])
], style={"minHeight": "100vh"})

@app.callback(
    Output('graphs-container', 'children'),
    [Input('city-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('graph-types-checklist', 'value')]
)

def update_graphs(selected_city, start_date, end_date, selected_graphs):
    # Фильтрация данных по выбранным параметрам
    filtered_df = df[
        (df['city'] == selected_city) &
        (df['timestamp'] >= start_date) &
        (df['timestamp'] <= end_date)
        ]

    graphs = []
    for graph_type in selected_graphs:
        fig = px.line(
            filtered_df,
            x='timestamp',
            y=graph_type,
            title=GRAPH_TYPES[graph_type]
        )
        graphs.append(
            dcc.Graph(
                figure=fig,
                className="dash-card mt-4",
                config={'displayModeBar': True}
            )
        )

    return graphs


@app.callback(
    Output("download-graph", "data"),
    Input({'type': 'export-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State("city-dropdown", "value"),
    State("graph-types-checklist", "value"),
    State("date-picker", "start_date"),
    State("date-picker", "end_date"),
    prevent_initial_call=True
)
def export_graph(n_clicks_list, city, graph_types, start_date, end_date):
    ctx_trigger = dash.callback_context.triggered
    if not ctx_trigger:
        return dash.no_update

    button_id = ctx_trigger[0]['prop_id'].split('.')[0]
    if button_id == "":
        return dash.no_update

    btn_obj = json.loads(button_id)
    idx = btn_obj['index']

    gtype = graph_types[idx]

    filtered = df[(df["city"] == city) &
                  (df["timestamp"] >= pd.to_datetime(start_date)) &
                  (df["timestamp"] <= pd.to_datetime(end_date))]

    fig = px.line(
        filtered,
        x="timestamp",
        y=gtype,
        title=GRAPH_TYPES[gtype],
        labels={"timestamp": "Дата и время", gtype: GRAPH_TYPES[gtype]},
        markers=True,
        line_shape="spline"
    )

    img_bytes = pio.to_image(fig, format='png')

    return dcc.send_bytes(img_bytes, filename=f"{city}_{gtype}.png")


@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("btn-download-csv", "n_clicks")],
    [Input('city-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')],
    prevent_initial_call=True
)
def download_csv(n_clicks, selected_city, start_date, end_date):
    # Фильтрация данных по выбранным параметрам
    filtered_df = df[
        (df['city'] == selected_city) &
        (df['timestamp'] >= start_date) &
        (df['timestamp'] <= end_date)
        ]

    # Создание CSV в памяти
    csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
    return dict(content=csv_string, filename=f"{selected_city}_data.csv")


@server.route("/")
def index():
    return render_template("index.html")
@server.route("/dash/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    server.run(debug=True)