from flask import Blueprint, Response, stream_with_context
import json
import time
from threading import Lock
from collections import defaultdict

sse_bp = Blueprint('sse', __name__)

# Dictionary to store clients for each aggregator
clients = defaultdict(list)
clients_lock = Lock()

def send_shutdown_event(aggregator_uuid):
    """Send a shutdown event to all clients of a specific aggregator."""
    with clients_lock:
        for queue in clients.get(aggregator_uuid, []):
            queue.append(json.dumps({"action": "shutdown"}))

@sse_bp.route('/shutdown_events/<aggregator_uuid>')
def shutdown_events(aggregator_uuid):
    """SSE endpoint for shutdown events."""
    def generate():
        # Create a message queue for this client
        queue = []
        
        # Register this client
        with clients_lock:
            clients[aggregator_uuid].append(queue)
        
        try:
            # Send initial message
            yield 'data: {"connected": true}\n\n'
            
            while True:
                # Check for messages
                if queue:
                    msg = queue.pop(0)
                    yield f'data: {msg}\n\n'
                
                # Keep-alive
                time.sleep(1)
        finally:
            # Unregister this client when the connection is closed
            with clients_lock:
                if queue in clients[aggregator_uuid]:
                    clients[aggregator_uuid].remove(queue)
                if not clients[aggregator_uuid]:
                    del clients[aggregator_uuid]
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    ) 