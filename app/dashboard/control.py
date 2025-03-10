from dash import html, dcc, callback, Input, Output, State, MATCH, ALL, callback_context
import dash_bootstrap_components as dbc
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Define the layout for the Control page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Aggregator Control", className="display-4"),
            html.Hr(),
            html.P(
                "This page allows you to manage aggregators. "
                "You can view the status of all aggregators and send shutdown commands.",
                className="lead"
            ),
            dbc.Button(
                "Reload Aggregators", 
                id="reload-aggregators-button", 
                color="primary", 
                className="mb-3"
            ),
            html.Div(id="last-reload-time"),
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Aggregators"),
                dbc.CardBody([
                    html.Div(id="aggregators-table-container"),
                ]),
            ]),
        ]),
    ]),
    
    # Modal for shutdown confirmation
    dbc.Modal([
        dbc.ModalHeader("Confirm Shutdown"),
        dbc.ModalBody("Are you sure you want to shut down this aggregator?"),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cancel-shutdown-button", className="ml-auto"),
            dbc.Button("Shutdown", id="confirm-shutdown-button", color="danger"),
        ]),
    ], id="shutdown-confirmation-modal"),
    
    # Store for aggregators data
    dcc.Store(id="aggregators-store"),
    dcc.Store(id="selected-aggregator-store"),
], fluid=True)

def create_aggregators_table(aggregators):
    """Create a table of aggregators with shutdown buttons."""
    if not aggregators:
        return html.Div("No aggregators found.")
    
    # Sort aggregators by last_active (descending)
    sorted_aggregators = sorted(
        aggregators, 
        key=lambda x: datetime.fromisoformat(x["last_active"]), 
        reverse=True
    )
    
    # Create table header
    header = html.Thead(html.Tr([
        html.Th("Aggregator Name"),
        html.Th("Last Active"),
        html.Th("Action"),
    ]))
    
    # Create table rows
    rows = []
    for aggregator in sorted_aggregators:
        # Format last_active timestamp
        last_active = datetime.fromisoformat(aggregator["last_active"].replace('Z', '+00:00'))
        last_active_str = last_active.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Create row
        row = html.Tr([
            html.Td(aggregator["name"]),
            html.Td(last_active_str),
            html.Td(
                dbc.Button(
                    "Shutdown", 
                    id={"type": "shutdown-button", "index": aggregator["uuid"]},
                    color="danger", 
                    size="sm"
                )
            ),
        ])
        rows.append(row)
    
    # Create table body
    body = html.Tbody(rows)
    
    # Create table
    table = dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
    
    return table

def register_control_callbacks(app):
    """Register callbacks for the Control page."""
    
    @app.callback(
        Output("aggregators-store", "data"),
        [Input("reload-aggregators-button", "n_clicks")],
        prevent_initial_call=False
    )
    def fetch_aggregators(n_clicks):
        """Fetch the list of aggregators."""
        try:
            response = requests.get(f"{SERVER_URL}/aggregators")
            aggregators = response.json()
            return aggregators
        except Exception as e:
            print(f"Error fetching aggregators: {e}")
            return []
    
    @app.callback(
        [Output("aggregators-table-container", "children"),
         Output("last-reload-time", "children")],
        Input("aggregators-store", "data"),
        prevent_initial_call=True
    )
    def update_aggregators_table(aggregators):
        """Update the aggregators table with the fetched data."""
        table = create_aggregators_table(aggregators)
        
        # Update the last reload time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_reload = html.P(f"Last reloaded: {now}", className="text-muted")
        
        return table, last_reload
    
    @app.callback(
        [Output("shutdown-confirmation-modal", "is_open"),
         Output("selected-aggregator-store", "data")],
        [Input({"type": "shutdown-button", "index": ALL}, "n_clicks"),
         Input("cancel-shutdown-button", "n_clicks"),
         Input("confirm-shutdown-button", "n_clicks")],
        [State("shutdown-confirmation-modal", "is_open"),
         State("aggregators-store", "data")],
        prevent_initial_call=True
    )
    def toggle_shutdown_modal(shutdown_clicks, cancel_clicks, confirm_clicks, is_open, aggregators):
        """Toggle the shutdown confirmation modal."""
        ctx = callback_context
        
        if not ctx.triggered:
            return is_open, None
        
        # Get the ID of the component that triggered the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Check if a shutdown button was clicked
        if trigger_id.startswith("{"):
            # Parse the JSON from the trigger_id
            button_id = json.loads(trigger_id)
            if button_id.get("type") == "shutdown-button":
                aggregator_uuid = button_id["index"]
                
                # Find the aggregator in the list
                selected_aggregator = next((a for a in aggregators if a["uuid"] == aggregator_uuid), None)
                
                return True, selected_aggregator
        
        # Check if cancel or confirm button was clicked
        elif trigger_id == "cancel-shutdown-button" or trigger_id == "confirm-shutdown-button":
            # Cancel or confirm button was clicked
            return False, None
        
        return is_open, None
    
    @app.callback(
        Output("error-alert", "children"),
        [Input("confirm-shutdown-button", "n_clicks"),
         State("selected-aggregator-store", "data")],
        prevent_initial_call=True
    )
    def shutdown_aggregator(n_clicks, selected_aggregator):
        """Send a shutdown command to the selected aggregator."""
        if not n_clicks or not selected_aggregator:
            return ""
        
        try:
            # Send shutdown command
            response = requests.post(
                f"{SERVER_URL}/shutdown_aggregator",
                json={"aggregator_uuid": selected_aggregator["uuid"]}
            )
            
            if response.status_code == 200:
                return f"Shutdown command sent to aggregator '{selected_aggregator['name']}'."
            else:
                return f"Error sending shutdown command: {response.text}"
        except Exception as e:
            return f"Error sending shutdown command: {str(e)}"
    
    @app.callback(
        Output("error-alert", "is_open"),
        Input("error-alert", "children"),
        prevent_initial_call=True
    )
    def show_error_alert(children):
        """Show the error alert if there's an error message."""
        return bool(children) 