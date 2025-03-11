import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask

def init_dashboard(server: Flask):
    """Initialize the Dash application and register it with the Flask server."""
    # Create a Dash app
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dashboard/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    # Set the browser tab title
    app.title = "Dashboard"
    
    # Import pages
    from app.dashboard.about import register_about_callbacks
    from app.dashboard.live import register_live_callbacks
    from app.dashboard.history import register_history_callbacks
    from app.dashboard.control import register_control_callbacks
    
    # Define the layout
    app.layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("About", href="/dashboard/")),
                dbc.NavItem(dbc.NavLink("Live", href="/dashboard/live")),
                dbc.NavItem(dbc.NavLink("History", href="/dashboard/history")),
                dbc.NavItem(dbc.NavLink("Control", href="/dashboard/control")),
            ],
            brand="Metric Aggregator Dashboard",
            brand_href="/dashboard/",
            color="primary",
            dark=True,
        ),
        dbc.Container(id="page-content", className="mt-4", fluid=True),
        dbc.Alert(
            id="error-alert",
            is_open=False,
            dismissable=True,
            color="danger",
            className="mt-3"
        ),
        # Store components for page routing
        dash.dcc.Location(id="url", refresh=False),
        dash.dcc.Store(id="page-store"),
    ])
    
    # Register callbacks
    register_about_callbacks(app)
    register_live_callbacks(app)
    register_history_callbacks(app)
    register_control_callbacks(app)
    
    # Page routing callback
    @app.callback(
        dash.Output("page-content", "children"),
        dash.Input("url", "pathname")
    )
    def display_page(pathname):
        if pathname == "/dashboard/" or pathname == "/dashboard":
            from app.dashboard.about import layout
            return layout
        elif pathname == "/dashboard/live":
            from app.dashboard.live import layout
            return layout
        elif pathname == "/dashboard/history":
            from app.dashboard.history import layout
            return layout
        elif pathname == "/dashboard/control":
            from app.dashboard.control import layout
            return layout
        else:
            return dbc.Jumbotron(
                [
                    html.H1("404: Not found", className="text-danger"),
                    html.Hr(),
                    html.P(f"The pathname {pathname} was not recognized..."),
                ]
            )
    
    return app 