from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Define the layout for the Live page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Live Metrics", className="display-4"),
            html.Hr(),
            html.P(
                "This page displays the latest metrics in real-time. "
                "The data is automatically refreshed every 5 seconds.",
                className="lead"
            ),
            dbc.Button(
                "Refresh Now", 
                id="refresh-button", 
                color="primary", 
                className="mb-3"
            ),
            html.Div(id="last-update-time"),
        ])
    ]),
    
    dbc.Row(id="metrics-grid"),
    
    # Hidden interval component for automatic updates
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds (5 seconds)
        n_intervals=0
    ),
    
    # Store for the latest metrics data
    dcc.Store(id="metrics-data-store"),
], fluid=True)

def create_metric_card(metric_uuid, metric_name, unit, value, timestamp, offset):
    """Create a card for a metric."""
    # Convert timestamp to different timezones
    utc_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    server_time = utc_time  # In a real app, convert to server timezone
    client_time = utc_time  # In a real app, convert to client timezone
    
    return dbc.Card([
        dbc.CardHeader(html.H4(metric_name, className="card-title")),
        dbc.CardBody([
            html.H2(f"{value} {unit}", className="card-text text-center"),
            html.Hr(),
            html.P([
                html.Strong("UTC: "), 
                html.Span(utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            ]),
            html.P([
                html.Strong("Server Time: "), 
                html.Span(server_time.strftime("%Y-%m-%d %H:%M:%S"))
            ]),
            html.P([
                html.Strong("Client Time: "), 
                html.Span(client_time.strftime("%Y-%m-%d %H:%M:%S")),
                html.Small(f" (Offset: {offset} min)", className="text-muted ml-2")
            ]),
        ]),
    ], className="mb-4")

def register_live_callbacks(app):
    """Register callbacks for the Live page."""
    
    @app.callback(
        Output("metrics-data-store", "data"),
        [Input("interval-component", "n_intervals"),
         Input("refresh-button", "n_clicks")],
        prevent_initial_call=True
    )
    def update_metrics_data(n_intervals, n_clicks):
        """Fetch the latest metrics data."""
        try:
            # Fetch metrics data
            metrics_response = requests.get(f"{SERVER_URL}/metrics")
            metrics = metrics_response.json()
            
            # Fetch latest snapshots
            snapshots_response = requests.get(f"{SERVER_URL}/latest_snapshots")
            snapshots = snapshots_response.json()
            
            # Combine metrics and snapshots
            metrics_data = []
            for snapshot in snapshots:
                metric_uuid = snapshot["metric_uuid"]
                metric = next((m for m in metrics if m["uuid"] == metric_uuid), None)
                if metric:
                    metrics_data.append({
                        "metric_uuid": metric_uuid,
                        "name": metric["name"],
                        "unit": metric["unit"],
                        "value": snapshot["value"],
                        "timestamp": snapshot["timestamp"],
                        "offset": snapshot["offset"],
                        "aggregator_name": metric["aggregator_name"]
                    })
            
            return metrics_data
        except Exception as e:
            # In a real app, handle errors properly
            print(f"Error fetching metrics data: {e}")
            return []
    
    @app.callback(
        [Output("metrics-grid", "children"),
         Output("last-update-time", "children")],
        Input("metrics-data-store", "data"),
        prevent_initial_call=True
    )
    def update_metrics_grid(metrics_data):
        """Update the metrics grid with the latest data."""
        if not metrics_data:
            return html.Div("No metrics data available."), ""
        
        # Create a grid of metric cards (3 per row)
        cards = []
        rows = []
        
        for i, metric in enumerate(metrics_data):
            card = create_metric_card(
                metric["metric_uuid"],
                metric["name"],
                metric["unit"],
                metric["value"],
                metric["timestamp"],
                metric["offset"]
            )
            cards.append(dbc.Col(card, md=4))
            
            # Create a new row after every 3 cards
            if (i + 1) % 3 == 0 or i == len(metrics_data) - 1:
                rows.append(dbc.Row(cards, className="mb-4"))
                cards = []
        
        # Update the last update time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_update = html.P(f"Last updated: {now}", className="text-muted")
        
        return rows, last_update
    
    # Add JavaScript for client-side timezone conversion
    app.clientside_callback(
        """
        function(metrics_data) {
            if (!metrics_data) return;
            
            // Convert timestamps to client local time
            setTimeout(function() {
                const cards = document.querySelectorAll('.card');
                cards.forEach(card => {
                    const clientTimeElem = card.querySelector('p:nth-child(5) span');
                    if (clientTimeElem) {
                        const utcTimeStr = card.querySelector('p:nth-child(3) span').textContent;
                        const utcTime = new Date(utcTimeStr + ' UTC');
                        clientTimeElem.textContent = utcTime.toLocaleString();
                    }
                });
            }, 100);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("metrics-data-store", "data", allow_duplicate=True),
        Input("metrics-data-store", "data"),
        prevent_initial_call=True
    ) 