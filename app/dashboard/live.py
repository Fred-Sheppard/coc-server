from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import requests
from dash import html, dcc, Input, Output

from app.utils import get_server_url

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
            dbc.Row([
                dbc.Col([
                    html.Label("Timezone Display"),
                    dcc.Dropdown(
                        id="timezone-dropdown",
                        options=[
                            {"label": "UTC", "value": "utc"},
                            {"label": "Server Time", "value": "server"},
                            {"label": "Local Time", "value": "client"},
                            {"label": "Aggregator Time", "value": "aggregator"}
                        ],
                        value="utc",
                        clearable=False,
                        className="mb-3"
                    ),
                ], md=4),
            ]),
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

def create_metric_card(metric_uuid, metric_name, unit, value, timestamp, offset, timezone="utc"):
    """Create a card for a metric."""
    # Convert timestamp to different timezones
    utc_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    # Format time based on selected timezone
    if timezone == "utc":
        display_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
        timezone_label = "UTC"
    elif timezone == "server":
        # Convert to server's local time
        server_time = datetime.now().astimezone().tzinfo
        display_time = utc_time.astimezone(server_time).strftime("%Y-%m-%d %H:%M:%S")
        timezone_label = "Server Time"
    elif timezone == "aggregator":
        # Convert to aggregator's timezone using the offset
        aggregator_time = utc_time + timedelta(minutes=offset)
        display_time = aggregator_time.strftime("%Y-%m-%d %H:%M:%S")
        timezone_label = f"Aggregator Time (UTC{'+' if offset >= 0 else ''}{offset//60:02d}:{abs(offset%60):02d})"
    else:  # client/local time
        display_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
        timezone_label = "Local Time"
    
    return dbc.Card([
        dbc.CardHeader(html.H4(metric_name, className="card-title")),
        dbc.CardBody([
            html.H2(f"{value:.2f} {unit}", className="card-text text-center"),
            html.Hr(),
            html.P([
                html.Span(display_time, className="metric-time"),
                " ",
                html.Span(timezone_label, className="timezone-label")
            ])
        ]),
    ], className="mb-4")

def register_live_callbacks(app):
    """Register callbacks for the Live page."""
    
    @app.callback(
        Output("metrics-data-store", "data"),
        Input("interval-component", "n_intervals"),
        prevent_initial_call=False
    )
    def update_metrics_data(n_intervals):
        """Fetch the latest metrics data."""
        try:
            # Fetch metrics data
            metrics_response = requests.get(f"{get_server_url()}/metrics")
            metrics = metrics_response.json()
            
            # Fetch latest snapshots
            snapshots_response = requests.get(f"{get_server_url()}/latest_snapshots")
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
            print(f"Error fetching metrics data: {e}")
            return []
    
    @app.callback(
        [Output("metrics-grid", "children"),
         Output("last-update-time", "children")],
        [Input("metrics-data-store", "data"),
         Input("timezone-dropdown", "value")],
        prevent_initial_call=False
    )
    def update_metrics_grid(metrics_data, timezone):
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
                metric["offset"],
                timezone
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
        function(metrics_data, timezone) {
            if (!metrics_data) return window.dash_clientside.no_update;
            
            // Convert timestamps to client local time only when local time is selected
            if (timezone === 'client') {
                setTimeout(function() {
                    const timeElements = document.querySelectorAll('.metric-time');
                    timeElements.forEach(elem => {
                        const timeStr = elem.textContent;
                        const utcTime = new Date(timeStr + ' UTC');
                        elem.textContent = utcTime.toLocaleString();
                    });
                }, 100);
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("metrics-data-store", "data", allow_duplicate=True),
        [Input("metrics-data-store", "data"),
         Input("timezone-dropdown", "value")],
        prevent_initial_call=True
    )