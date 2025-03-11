import os
from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import requests
from dash import html, dcc, Input, Output, dash_table
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Define the layout for the History page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Metric History", className="display-4"),
            html.Hr(),
            html.P(
                "This page allows you to explore historical metric data. "
                "Select a metric, time range, and timezone to view the data.",
                className="lead"
            ),
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Metric"),
                            dcc.Dropdown(
                                id="metric-dropdown",
                                placeholder="Select a metric",
                            ),
                        ], md=6),
                        dbc.Col([
                            html.Label("Timezone"),
                            dcc.Dropdown(
                                id="timezone-dropdown",
                                options=[
                                    {"label": "UTC", "value": "utc"},
                                    {"label": "Server Time", "value": "server"},
                                    {"label": "Client Time", "value": "client"},
                                ],
                                value="utc",
                                clearable=False,
                            ),
                        ], md=6),
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Start Date/Time"),
                            html.Div([
                                dcc.DatePickerSingle(
                                    id="start-date",
                                    display_format="YYYY-MM-DD",
                                    date=datetime.now().date() - timedelta(days=1),
                                ),
                                dcc.Input(
                                    id="start-time",
                                    type="time",
                                    value="00:00",
                                    style={
                                        "font-family": "'Open Sans', sans-serif",
                                        "font-size": "18px",
                                        "height": "46px",
                                        "width": "65px",
                                        "margin-left": "10px",
                                        "margin-right": "10px",
                                    },
                                ),
                            ], style={"display": "flex", "align-items": "center"}),
                        ], md=6),
                        dbc.Col([
                            html.Label("End Date/Time"),
                            html.Div([
                                dcc.DatePickerSingle(
                                    id="end-date",
                                    display_format="YYYY-MM-DD",
                                    date=datetime.now().date(),
                                ),
                                dcc.Input(
                                    id="end-time",
                                    type="time",
                                    value="23:59",
                                    style={
                                        "font-family": "'Open Sans', sans-serif",
                                        "font-size": "18px",
                                        "height": "46px",
                                        "width": "65px",
                                        "margin-left": "10px",
                                        "margin-right": "10px",
                                    },
                                ),
                            ], style={"display": "flex", "align-items": "center"}),
                        ], md=6),
                    ], className="mt-3"),
                    
                    # Apply Filters button removed
                ]),
            ], className="mb-4"),
        ]),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Metric History Graph"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-graph",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="history-graph",
                                figure={
                                    "layout": {
                                        "title": "Select a metric to view its history",
                                        "xaxis": {"title": "Time"},
                                        "yaxis": {"title": "Value"},
                                    }
                                },
                                style={"height": "500px"},
                            ),
                        ],
                    ),
                ]),
            ]),
        ]),
    ]),
    
    # Add Data Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Metric History Data"),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-table",
                        type="default",
                        children=[
                            dash_table.DataTable(
                                id="history-table",
                                columns=[
                                    {"name": "Timestamp", "id": "timestamp"},
                                    {"name": "Value", "id": "value", "type": "numeric"},
                                    {"name": "Formatted Value", "id": "formatted_value"}
                                ],
                                page_size=10,
                                page_current=0,
                                page_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                filter_action="native",
                                tooltip_data=[],
                                tooltip_duration=None,
                                style_table={"overflowX": "auto"},
                                style_cell={
                                    "textAlign": "left",
                                    "padding": "10px",
                                    "fontFamily": "'Open Sans', sans-serif"
                                },
                                style_header={
                                    "backgroundColor": "#f8f9fa",
                                    "fontWeight": "bold",
                                    "borderBottom": "1px solid #dee2e6"
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "#f8f9fa"
                                    }
                                ]
                            ),
                        ],
                    ),
                ]),
            ], className="mt-4 mb-4"),
        ]),
    ]),
    
    # Store for metrics data
    dcc.Store(id="metrics-list-store"),
    dcc.Store(id="selected-metric-store"),
    dcc.Store(id="snapshots-store"),
], fluid=True)

def register_history_callbacks(app):
    """Register callbacks for the History page."""
    
    @app.callback(
        Output("metrics-list-store", "data"),
        Input("metric-dropdown", "id"),  # Just to trigger on page load
        prevent_initial_call=False
    )
    def fetch_metrics_list(_):
        """Fetch the list of available metrics."""
        try:
            response = requests.get(f"{SERVER_URL}/metrics")
            metrics = response.json()
            return metrics
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return []
    
    @app.callback(
        Output("metric-dropdown", "options"),
        Input("metrics-list-store", "data"),
        prevent_initial_call=True
    )
    def update_metric_dropdown(metrics):
        """Update the metric dropdown with available metrics."""
        if not metrics:
            return []
        
        options = []
        for metric in metrics:
            options.append({
                "label": f"{metric['name']} ({metric['unit']}) - {metric['aggregator_name']}",
                "value": metric["uuid"]
            })
        
        return options
    
    @app.callback(
        Output("selected-metric-store", "data"),
        [Input("metric-dropdown", "value"),
         Input("metrics-list-store", "data")],
        prevent_initial_call=True
    )
    def store_selected_metric(metric_uuid, metrics):
        """Store the selected metric details."""
        if not metric_uuid or not metrics:
            return None
        
        selected_metric = next((m for m in metrics if m["uuid"] == metric_uuid), None)
        return selected_metric
    
    @app.callback(
        Output("snapshots-store", "data"),
        [Input("metric-dropdown", "value"),
         Input("start-date", "date"),
         Input("start-time", "value"),
         Input("end-date", "date"),
         Input("end-time", "value")],
        prevent_initial_call=True
    )
    def fetch_snapshots(metric_uuid, start_date, start_time, end_date, end_time):
        """Fetch snapshots for the selected metric and time range."""
        if not metric_uuid:
            return []
        
        try:
            # Construct ISO8601 datetime strings
            start_datetime = f"{start_date}T{start_time}:00Z"
            end_datetime = f"{end_date}T{end_time}:59Z"
            
            # Fetch snapshots
            response = requests.get(
                f"{SERVER_URL}/snapshots",
                params={
                    "metric_uuid": metric_uuid,
                    "start": start_datetime,
                    "end": end_datetime
                }
            )
            
            snapshots = response.json()
            return snapshots
        except Exception as e:
            print(f"Error fetching snapshots: {e}")
            return []
    
    @app.callback(
        Output("history-graph", "figure"),
        [Input("snapshots-store", "data"),
         Input("selected-metric-store", "data"),
         Input("timezone-dropdown", "value")],
        prevent_initial_call=True
    )
    def update_history_graph(snapshots, selected_metric, timezone):
        """Update the history graph with the fetched snapshots."""
        if not snapshots or not selected_metric:
            return {
                "layout": {
                    "title": "No data available",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Value"},
                }
            }
        
        # Extract data for plotting
        timestamps = []
        values = []
        
        for snapshot in snapshots:
            # Parse timestamp based on selected timezone
            timestamp = datetime.fromisoformat(snapshot["timestamp"].replace('Z', '+00:00'))
            
            # Apply timezone conversion if needed
            if timezone == "client":
                # Client-side conversion will be handled by JavaScript
                pass
            elif timezone == "server":
                # In a real app, convert to server timezone
                pass
            # For UTC, no conversion needed
            
            timestamps.append(timestamp)
            values.append(snapshot["value"])
        
        # Create the figure
        figure = {
            "data": [
                {
                    "x": timestamps,
                    "y": values,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": selected_metric["name"],
                    "line": {"color": "#007bff"},
                }
            ],
            "layout": {
                "title": f"{selected_metric['name']} ({selected_metric['unit']}) - {selected_metric['aggregator_name']}",
                "xaxis": {
                    "title": f"Time ({timezone.upper()})",
                    "gridcolor": "#eee",
                },
                "yaxis": {
                    "title": f"Value ({selected_metric['unit']})",
                    "gridcolor": "#eee",
                },
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
            }
        }
        
        return figure
    
    # Add JavaScript for client-side timezone conversion
    app.clientside_callback(
        """
        function(snapshots, timezone) {
            if (!snapshots || timezone !== 'client') return window.dash_clientside.no_update;
            
            // Convert timestamps to client local time for display
            const graph = document.getElementById('history-graph');
            if (graph && graph.layout && graph.layout.xaxis) {
                graph.layout.xaxis.title.text = 'Time (Client Local)';
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("snapshots-store", "data", allow_duplicate=True),
        [Input("snapshots-store", "data"),
         Input("timezone-dropdown", "value")],
        prevent_initial_call=True
    ) 
    
    @app.callback(
        Output("history-table", "data"),
        [Input("snapshots-store", "data"),
         Input("selected-metric-store", "data"),
         Input("timezone-dropdown", "value")],
        prevent_initial_call=True
    )
    def update_history_table(snapshots, selected_metric, timezone):
        """Update the history table with the fetched snapshots."""
        if not snapshots or not selected_metric:
            return []
        
        # Prepare table data
        table_data = []
        
        for snapshot in snapshots:
            # Parse timestamp based on selected timezone
            timestamp = datetime.fromisoformat(snapshot["timestamp"].replace('Z', '+00:00'))
            
            # Format timestamp for display
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if timezone == "utc":
                formatted_timestamp += " UTC"
            elif timezone == "server":
                formatted_timestamp += " (Server Time)"
            elif timezone == "client":
                formatted_timestamp += " (Local Time)"
            
            # Format value based on metric type
            value = snapshot["value"]
            
            # Format the value based on the type
            formatted_value = value
            if isinstance(value, (int, float)):
                if selected_metric.get("unit") in ["percent", "%"]:
                    formatted_value = f"{value:.2f}%"
                elif selected_metric.get("unit") in ["bytes", "B"]:
                    # Format bytes to appropriate unit (KB, MB, GB)
                    if value >= 1024**3:
                        formatted_value = f"{value/1024**3:.2f} GB"
                    elif value >= 1024**2:
                        formatted_value = f"{value/1024**2:.2f} MB"
                    elif value >= 1024:
                        formatted_value = f"{value/1024:.2f} KB"
                    else:
                        formatted_value = f"{value} B"
                else:
                    # For other numeric values, format with 2 decimal places
                    formatted_value = f"{value:.2f} {selected_metric.get('unit', '')}"
            
            # Add row to table data
            table_data.append({
                "timestamp": formatted_timestamp,
                "value": value,
                "formatted_value": formatted_value
            })
        
        return table_data
    
    @app.callback(
        Output("history-table", "columns"),
        [Input("selected-metric-store", "data")],
        prevent_initial_call=True
    )
    def update_table_columns(selected_metric):
        """Update table columns based on selected metric."""
        if not selected_metric:
            return [
                {"name": "Timestamp", "id": "timestamp"},
                {"name": "Value", "id": "value"},
                {"name": "Formatted Value", "id": "formatted_value"}
            ]
        
        # Create columns with appropriate headers
        return [
            {"name": "Timestamp", "id": "timestamp"},
            {"name": f"Raw Value", "id": "value", "type": "numeric"},
            {"name": f"Formatted Value", "id": "formatted_value"},
        ] 
    
    @app.callback(
        Output("history-table", "tooltip_data"),
        [Input("history-table", "data"),
         Input("selected-metric-store", "data")],
        prevent_initial_call=True
    )
    def update_tooltip_data(table_data, selected_metric):
        """Update tooltip data for the table rows."""
        if not table_data or not selected_metric:
            return []
        
        tooltip_data = []
        for row in table_data:
            tooltip_data.append({
                "timestamp": {"value": f"Recorded at {row['timestamp']}"},
                "value": {"value": f"Raw value: {row['value']} {selected_metric.get('unit', '')}"},
                "formatted_value": {"value": f"Metric: {selected_metric.get('name', '')}\nAggregator: {selected_metric.get('aggregator_name', '')}\nValue: {row['formatted_value']}"}
            })
        
        return tooltip_data