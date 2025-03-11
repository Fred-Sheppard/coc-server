import dash_bootstrap_components as dbc
from dash import html, dcc

from app.utils import get_server_url


# Define the layout for the About page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Metric Aggregator Server with Dashboard", className="display-4"),
            html.Hr(),
            html.P(
                "A Flask-based application that collects and aggregates metrics from various sources, "
                "with a Plotly Dash dashboard for visualization.",
                className="lead"
            ),
            
            html.H2("Features", className="mt-4"),
            html.Ul([
                html.Li("Register aggregators and metrics"),
                html.Li("Submit metric snapshots"),
                html.Li("View real-time metrics on a dashboard"),
                html.Li("Explore historical metric data"),
                html.Li("Control aggregators (shutdown functionality)")
            ]),
        ])
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("Getting Started", className="mt-4"),
            html.P("Follow these steps to start using the Metric Aggregator:"),

            html.H4("1. Register an Aggregator", className="mt-3"),
            html.P("First, register a new aggregator with a unique name:"),
            dbc.Card([
                dbc.CardHeader("API Endpoint: POST /register_aggregator"),
                dbc.CardBody([
                    html.P("Request:"),
                    dcc.Markdown("""
                    ```json
                    {
                        "name": "my-aggregator"
                    }
                    ```
                    """),
                    html.P("Response:"),
                    dcc.Markdown("""
                    ```json
                    {
                        "uuid": "12345678-1234-5678-1234-567812345678"
                    }
                    ```
                    """),
                    html.P("Example (curl):"),
                    dcc.Markdown(f"""
                    ```bash
                    curl -X POST {get_server_url()}/register_aggregator \\
                         -H "Content-Type: application/json" \\
                         -d '{{"name": "my-aggregator"}}'
                    ```
                    """),
                    html.P("Example (Python):"),
                    dcc.Markdown("""
                    ```python
                    import requests
                    import json
                    import os
                    from dotenv import load_dotenv
                    from app.utils import get_server_url
                    
                    # Load environment variables
                    load_dotenv()
                    
                    response = requests.post(
                        f"{get_server_url()}/register_aggregator",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({"name": "my-aggregator"})
                    )
                    
                    aggregator_uuid = response.json()["uuid"]
                    print(f"Aggregator UUID: {aggregator_uuid}")
                    ```
                    """)
                ])
            ], className="mb-4"),

            html.H4("2. Register Metrics", className="mt-3"),
            html.P("Next, register metrics under your aggregator:"),
            dbc.Card([
                dbc.CardHeader("API Endpoint: POST /register_metric"),
                dbc.CardBody([
                    html.P("Request:"),
                    dcc.Markdown("""
                    ```json
                    {
                        "aggregator_uuid": "12345678-1234-5678-1234-567812345678",
                        "metric_name": "temperature",
                        "unit": "°C"
                    }
                    ```
                    """),
                    html.P("Response:"),
                    dcc.Markdown("""
                    ```json
                    {
                        "metric_uuid": "87654321-8765-4321-8765-432187654321"
                    }
                    ```
                    """),
                    html.P("Example (curl):"),
                    dcc.Markdown(f"""
                    ```bash
                    curl -X POST {get_server_url()}/register_metric \\
                         -H "Content-Type: application/json" \\
                         -d '{{
                             "aggregator_uuid": "12345678-1234-5678-1234-567812345678",
                             "metric_name": "temperature",
                             "unit": "°C"
                         }}'
                    ```
                    """),
                    html.P("Example (Python):"),
                    dcc.Markdown("""
                    ```python
                    import requests
                    import json
                    import os
                    from dotenv import load_dotenv
                    from app.utils import get_server_url
                    
                    # Load environment variables
                    load_dotenv()
                    
                    response = requests.post(
                        f"{get_server_url()}/register_metric",
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({
                            "aggregator_uuid": aggregator_uuid,
                            "metric_name": "temperature",
                            "unit": "°C"
                        })
                    )
                    
                    metric_uuid = response.json()["metric_uuid"]
                    print(f"Metric UUID: {metric_uuid}")
                    ```
                    """)
                ])
            ], className="mb-4"),

            html.H4("3. Submit Metric Snapshots", className="mt-3"),
            html.P("Finally, submit metric snapshots:"),
            dbc.Card([
                dbc.CardHeader("API Endpoint: POST /snapshot"),
                dbc.CardBody([
                    html.P("Request:"),
                    dcc.Markdown("""
                    ```json
                    {
                        "metric_uuid": "87654321-8765-4321-8765-432187654321",
                        "value": 25.5,
                        "timestamp": "2023-01-01T12:00:00Z",
                        "offset": -240
                    }
                    ```
                    """),
                    html.P("Example (curl):"),
                    dcc.Markdown(f"""
                    ```bash
                    curl -X POST {get_server_url()}/snapshot \\
                         -H "Content-Type: application/json" \\
                         -d '{{
                             "metric_uuid": "87654321-8765-4321-8765-432187654321",
                             "value": 25.5,
                             "timestamp": "2023-01-01T12:00:00Z",
                             "offset": -240
                         }}'
                    ```
                    """),
                    html.P("Example (Python):"),
                    dcc.Markdown("""
                    ```python
                    import requests
                    import json
                    from datetime import datetime, timezone
                    import time
                    import os
                    from dotenv import load_dotenv
                    from app.utils import get_server_url
                    
                    # Load environment variables
                    load_dotenv()
                    
                    # Function to submit a snapshot
                    def submit_snapshot(metric_uuid, value):
                        # Get current time in UTC
                        now = datetime.now(timezone.utc)
                        # Get local timezone offset in minutes
                        offset = int(time.timezone / 60)
                        
                        response = requests.post(
                            f"{get_server_url()}/snapshot",
                            headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "metric_uuid": metric_uuid,
                                "value": value,
                                "timestamp": now.isoformat(),
                                "offset": offset
                            })
                        )
                        
                        return response.status_code == 201
                    
                    # Example usage
                    submit_snapshot(metric_uuid, 25.5)
                    ```
                    """)
                ])
            ], className="mb-4"),

            html.H4("4. Poll for Shutdown Status", className="mt-3"),
            html.P("Aggregators should periodically poll for shutdown status:"),
            dbc.Card([
                dbc.CardHeader("API Endpoint: GET /poll_shutdown_status/<aggregator_uuid>"),
                dbc.CardBody([
                    html.P("Example (Python):"),
                    dcc.Markdown("""
                    ```python
                    import requests
                    import json
                    import time
                    import sys
                    import os
                    from dotenv import load_dotenv
                    from app.utils import get_server_url
                    
                    # Load environment variables
                    load_dotenv()
                    
                    # Function to handle shutdown
                    def handle_shutdown():
                        print("Received shutdown command. Shutting down...")
                        # Perform cleanup here
                        sys.exit(0)
                    
                    # Function to poll for shutdown status
                    def poll_shutdown_status(aggregator_uuid, interval=5):
                        url = f"{get_server_url()}/poll_shutdown_status/{aggregator_uuid}"
                        
                        while True:
                            try:
                                response = requests.get(url)
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get("should_shutdown", False):
                                        handle_shutdown()
                                
                                # Wait before polling again
                                time.sleep(interval)
                            except Exception as e:
                                print(f"Error polling shutdown status: {e}")
                                # Wait before retrying
                                time.sleep(interval)
                    
                    # Start polling for shutdown status
                    poll_shutdown_status(aggregator_uuid)
                    ```
                    """)
                ])
            ], className="mb-4"),
            
            html.H2("API Endpoints", className="mt-4"),
            html.Ul([
                html.Li(html.Code("POST /register_aggregator"), ": Register a new aggregator"),
                html.Li(html.Code("POST /register_metric"), ": Register a metric under an aggregator"),
                html.Li(html.Code("POST /snapshot"), ": Submit a metric snapshot"),
                html.Li(html.Code("GET /metrics"), ": Fetch all registered metrics"),
                html.Li(html.Code("GET /snapshots"), ": Fetch historical snapshots for a metric"),
                html.Li(html.Code("GET /latest_snapshots"), ": Fetch the most recent snapshot for all metrics"),
                html.Li(html.Code("POST /shutdown_aggregator"), ": Initiate shutdown for a specific aggregator"),
                html.Li(html.Code("GET /poll_shutdown_status/<aggregator_uuid>"), ": Poll to check if an aggregator should shut down")
            ]),
        ])
    ])
], fluid=True)


def register_about_callbacks(_app):
    """Register callbacks for the About page."""
    # No callbacks needed for the About page
    pass
