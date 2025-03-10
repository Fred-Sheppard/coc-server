# Metric Aggregator Server with Dashboard

A Flask-based application that collects and aggregates metrics from various sources, with a Plotly Dash dashboard for visualization.

## Features

- Register aggregators and metrics
- Submit metric snapshots
- View real-time metrics on a dashboard
- Explore historical metric data
- Control aggregators (shutdown functionality)
- Server-Sent Events (SSE) for aggregator control

## Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/metric_aggregator
   FLASK_APP=app
   FLASK_ENV=development
   ```

4. Initialize the database:
   ```
   flask db-init
   ```

5. Run the application:
   ```
   flask run
   ```

## API Endpoints

- `POST /register_aggregator`: Register a new aggregator
- `POST /register_metric`: Register a metric under an aggregator
- `POST /snapshot`: Submit a metric snapshot
- `GET /metrics`: Fetch all registered metrics
- `GET /snapshots`: Fetch historical snapshots for a metric
- `GET /latest_snapshots`: Fetch the most recent snapshot for all metrics
- `POST /shutdown_aggregator`: Initiate shutdown for a specific aggregator
- `GET /shutdown_events/<aggregator_uuid>`: SSE endpoint for shutdown events

## Dashboard

The dashboard consists of four pages:
- **About**: Project description and usage guide
- **Live**: Real-time metrics display
- **History**: Historical metric data visualization
- **Control**: Aggregator management

Access the dashboard at `http://localhost:5000/dashboard/` 