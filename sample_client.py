import requests
import json
import time
import random
from datetime import datetime, timezone, timedelta
import threading
import signal
import sys
import os
from dotenv import load_dotenv
from app.utils import get_server_url

# Load environment variables
load_dotenv()

# Base URL for the API
BASE_URL = get_server_url()

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

def register_metric(aggregator_uuid, name, unit):
    """Register a new metric."""
    response = requests.post(
        f"{BASE_URL}/register_metric",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "aggregator_uuid": aggregator_uuid,
            "name": name,
            "unit": unit
        })
    )
    
    if response.status_code == 201:
        return response.json()["uuid"]
    else:
        print(f"Error registering metric: {response.text}")
        return None

def submit_snapshot(metric_uuid, value, offset_minutes):
    """Submit a metric snapshot."""
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    
    response = requests.post(
        f"{BASE_URL}/snapshot",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "metric_uuid": metric_uuid,
            "value": value,
            "timestamp": now.isoformat(),
            "offset": offset_minutes
        })
    )
    
    return response.status_code == 201

def listen_for_shutdown(aggregator_uuid):
    """Poll for shutdown status."""
    global shutdown_requested
    
    url = f"{BASE_URL}/poll_shutdown_status/{aggregator_uuid}"
    
    while not shutdown_requested:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('should_shutdown', False):
                    print("Received shutdown command. Shutting down...")
                    shutdown_requested = True
                    break
            else:
                print(f"Error polling shutdown status: {response.text}")
        except Exception as e:
            print(f"Error in polling connection: {e}")
        
        # Wait before polling again
        time.sleep(5)  # Poll every 5 seconds

def generate_metrics(aggregator_uuid, metric_uuids, interval=5):
    """Generate random metrics at regular intervals."""
    global shutdown_requested
    
    # Define different timezone offsets for each metric (in minutes)
    offsets = {
        metric_uuids[0]: -480,  # UTC-8 (e.g., Pacific Time)
        metric_uuids[1]: 60,    # UTC+1 (e.g., Central European Time)
        metric_uuids[2]: 330,   # UTC+5:30 (e.g., India)
    }
    
    while not shutdown_requested:
        for metric_uuid in metric_uuids:
            # Generate a random value
            value = random.uniform(0, 100)
            
            # Get the offset for this metric
            offset = offsets.get(metric_uuid, 0)
            
            # Submit the snapshot with the offset
            success = submit_snapshot(metric_uuid, value, offset)
            if success:
                print(f"Submitted snapshot for metric {metric_uuid}: {value} (UTC{'+' if offset >= 0 else ''}{offset//60:02d}:{abs(offset%60):02d})")
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
    
    # Register metrics with location context
    metrics = [
        {"name": "temperature_sf", "unit": "°C"},    # San Francisco
        {"name": "temperature_paris", "unit": "°C"},  # Paris
        {"name": "temperature_mumbai", "unit": "°C"}, # Mumbai
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