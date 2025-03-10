import requests
import json
import time
import random
from datetime import datetime, timezone
import threading
import signal
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for the API
BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5001')

# Global flag for shutdown
shutdown_requested = False

def register_aggregator(name):
    """Register a new aggregator."""
    response = requests.post(
        f"{BASE_URL}/register_aggregator",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": name})
    )
    
    if response.status_code == 201:
        return response.json()["uuid"]
    else:
        print(f"Error registering aggregator: {response.text}")
        return None

def register_metric(aggregator_uuid, metric_name, unit):
    """Register a new metric under an aggregator."""
    response = requests.post(
        f"{BASE_URL}/register_metric",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "aggregator_uuid": aggregator_uuid,
            "metric_name": metric_name,
            "unit": unit
        })
    )
    
    if response.status_code == 201:
        return response.json()["metric_uuid"]
    else:
        print(f"Error registering metric: {response.text}")
        return None

def submit_snapshot(metric_uuid, value):
    """Submit a metric snapshot."""
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    # Get local timezone offset in minutes
    offset = int(time.timezone / 60)
    
    response = requests.post(
        f"{BASE_URL}/snapshot",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "metric_uuid": metric_uuid,
            "value": value,
            "timestamp": now.isoformat(),
            "offset": offset
        })
    )
    
    return response.status_code == 201

def listen_for_shutdown(aggregator_uuid):
    """Listen for shutdown events."""
    global shutdown_requested
    
    url = f"{BASE_URL}/shutdown_events/{aggregator_uuid}"
    headers = {"Accept": "text/event-stream"}
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data:'):
                    data_str = line_str[5:].strip()
                    data = json.loads(data_str)
                    
                    if "action" in data and data["action"] == "shutdown":
                        print("Received shutdown command. Shutting down...")
                        shutdown_requested = True
                        break
    except Exception as e:
        print(f"Error in SSE connection: {e}")
        # In a real client, you would reconnect after a delay

def generate_metrics(aggregator_uuid, metric_uuids, interval=5):
    """Generate random metrics at regular intervals."""
    global shutdown_requested
    
    while not shutdown_requested:
        for metric_uuid in metric_uuids:
            # Generate a random value
            value = random.uniform(0, 100)
            
            # Submit the snapshot
            success = submit_snapshot(metric_uuid, value)
            if success:
                print(f"Submitted snapshot for metric {metric_uuid}: {value}")
            else:
                print(f"Failed to submit snapshot for metric {metric_uuid}")
        
        # Wait for the next interval
        time.sleep(interval)

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shut down."""
    global shutdown_requested
    print("Ctrl+C received. Shutting down...")
    shutdown_requested = True
    sys.exit(0)

def main():
    """Main function."""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Register an aggregator
    aggregator_name = f"sample-aggregator-{int(time.time())}"
    print(f"Registering aggregator: {aggregator_name}")
    aggregator_uuid = register_aggregator(aggregator_name)
    
    if not aggregator_uuid:
        print("Failed to register aggregator. Exiting.")
        return
    
    print(f"Aggregator registered with UUID: {aggregator_uuid}")
    
    # Register some metrics
    metrics = [
        {"name": "temperature", "unit": "°C"},
        {"name": "humidity", "unit": "%"},
        {"name": "pressure", "unit": "hPa"}
    ]
    
    metric_uuids = []
    for metric in metrics:
        print(f"Registering metric: {metric['name']}")
        metric_uuid = register_metric(aggregator_uuid, metric["name"], metric["unit"])
        if metric_uuid:
            print(f"Metric registered with UUID: {metric_uuid}")
            metric_uuids.append(metric_uuid)
        else:
            print(f"Failed to register metric: {metric['name']}")
    
    if not metric_uuids:
        print("No metrics registered. Exiting.")
        return
    
    # Start a thread to listen for shutdown events
    shutdown_thread = threading.Thread(target=listen_for_shutdown, args=(aggregator_uuid,))
    shutdown_thread.daemon = True
    shutdown_thread.start()
    
    # Generate metrics
    print("Starting to generate metrics...")
    generate_metrics(aggregator_uuid, metric_uuids)

if __name__ == "__main__":
    main() 