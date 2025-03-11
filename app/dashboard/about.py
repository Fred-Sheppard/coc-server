from dash import html, dcc
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Define the layout for the About page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Metric Aggregator Server", className="display-4"),
            html.Hr(),
            html.P(
                "This application collects and aggregates metrics from various sources, "
                "providing a dashboard for visualization and control.",
                className="lead"
            ),
            html.H2("TODO"),
            dcc.Markdown(
                """
                - Fix code TODOs
                - Study and understand code
                - Make powerpoint
                - Upload to cloud
                - Update ReadMe
                - Update About
                - pip install, add plugins outside sdk
                """
            ),
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
                    curl -X POST {SERVER_URL}/register_aggregator \\
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
                    
                    # Load environment variables
                    load_dotenv()
                    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
                    
                    response = requests.post(
                        f"{SERVER_URL}/register_aggregator",
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
                    curl -X POST {SERVER_URL}/register_metric \\
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
                    
                    # Load environment variables
                    load_dotenv()
                    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
                    
                    response = requests.post(
                        f"{SERVER_URL}/register_metric",
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
                    curl -X POST {SERVER_URL}/snapshot \\
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
                    
                    # Load environment variables
                    load_dotenv()
                    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
                    
                    # Function to submit a snapshot
                    def submit_snapshot(metric_uuid, value):
                        # Get current time in UTC
                        now = datetime.now(timezone.utc)
                        # Get local timezone offset in minutes
                        offset = int(time.timezone / 60)
                        
                        response = requests.post(
                            f"{SERVER_URL}/snapshot",
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
            
            html.H4("4. Listen for Shutdown Events", className="mt-3"),
            html.P("Aggregators should listen for shutdown events:"),
            dbc.Card([
                dbc.CardHeader("SSE Endpoint: GET /shutdown_events/<aggregator_uuid>"),
                dbc.CardBody([
                    html.P("Example (Python):"),
                    dcc.Markdown("""
                    ```python
                    import requests
                    import json
                    import sseclient
                    import signal
                    import sys
                    import os
                    from dotenv import load_dotenv
                    
                    # Load environment variables
                    load_dotenv()
                    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
                    
                    # Function to handle shutdown
                    def handle_shutdown():
                        print("Received shutdown command. Shutting down...")
                        # Perform cleanup here
                        sys.exit(0)
                    
                    # Function to listen for shutdown events
                    def listen_for_shutdown(aggregator_uuid):
                        url = f"{SERVER_URL}/shutdown_events/{aggregator_uuid}"
                        headers = {"Accept": "text/event-stream"}
                        
                        try:
                            response = requests.get(url, headers=headers, stream=True)
                            client = sseclient.SSEClient(response)
                            
                            for event in client.events():
                                data = json.loads(event.data)
                                if "action" in data and data["action"] == "shutdown":
                                    handle_shutdown()
                        except Exception as e:
                            print(f"Error in SSE connection: {e}")
                            # Reconnect after a delay
                            time.sleep(5)
                            listen_for_shutdown(aggregator_uuid)
                    
                    # Start listening for shutdown events
                    listen_for_shutdown(aggregator_uuid)
                    ```
                    """)
                ])
            ], className="mb-4"),
        ])
    ])
], fluid=True)

def register_about_callbacks(_app):
    """Register callbacks for the About page."""
    # No callbacks needed for the About page
    pass 