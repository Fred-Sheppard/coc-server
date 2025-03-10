from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging
from app import db
from app.models.models import Aggregator, Metric, Snapshot
from app.routes.sse import send_shutdown_event

# Get logger for this module
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/register_aggregator', methods=['POST'])
def register_aggregator():
    data = request.get_json()
    logger.debug(f"/register_aggregator request body: {data}")
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    name = data['name']
    
    try:
        aggregator = Aggregator(name=name)
        db.session.add(aggregator)
        db.session.commit()
        return jsonify({'uuid': aggregator.uuid}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': f'Aggregator with name "{name}" already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/register_metric', methods=['POST'])
def register_metric():
    data = request.get_json()
    logger.debug(f"/register_metric request body: {data}")
    
    if not data or 'aggregator_uuid' not in data or 'name' not in data or 'unit' not in data:
        return jsonify({'error': 'Aggregator UUID, metric name, and unit are required'}), 400
    
    aggregator_uuid = data['aggregator_uuid']
    name = data['name']
    unit = data['unit']
    
    # Check if aggregator exists
    aggregator = Aggregator.query.get(aggregator_uuid)
    if not aggregator:
        return jsonify({'error': f'Aggregator with UUID "{aggregator_uuid}" not found'}), 404
    
    try:
        metric = Metric(aggregator_uuid=aggregator_uuid, name=name, unit=unit)
        db.session.add(metric)
        db.session.commit()
        logger.debug(f"Metric registered with UUID: {metric.uuid}")
        return jsonify({'uuid': metric.uuid}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': f'Metric with name "{name}" already exists for this aggregator'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/snapshot', methods=['POST'])
def submit_snapshot():
    data = request.get_json()
    
    if not data or 'metric_uuid' not in data or 'value' not in data or 'timestamp' not in data or 'offset' not in data:
        return jsonify({'error': 'Metric UUID, value, timestamp, and offset are required'}), 400
    
    metric_uuid = data['metric_uuid']
    value = data['value']
    timestamp_str = data['timestamp']
    offset = data['offset']
    
    # Check if metric exists
    metric = Metric.query.get(metric_uuid)
    if not metric:
        return jsonify({'error': f'Metric with UUID "{metric_uuid}" not found'}), 404
    
    try:
        # Parse timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Create snapshot
        snapshot = Snapshot(metric_uuid=metric_uuid, value=value, timestamp=timestamp, offset=offset)
        db.session.add(snapshot)
        
        # Update aggregator's last_active timestamp
        metric.aggregator.last_active = datetime.utcnow()
        
        db.session.commit()
        return '', 201
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Use ISO8601 UTC format.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = Metric.query.all()
    return jsonify([metric.to_dict() for metric in metrics])

@api_bp.route('/snapshots', methods=['GET'])
def get_snapshots():
    metric_uuid = request.args.get('metric_uuid')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    
    if not metric_uuid:
        return jsonify({'error': 'Metric UUID is required'}), 400
    
    # Check if metric exists
    metric = Metric.query.get(metric_uuid)
    if not metric:
        return jsonify({'error': f'Metric with UUID "{metric_uuid}" not found'}), 404
    
    query = Snapshot.query.filter_by(metric_uuid=metric_uuid)
    
    # Apply time filters if provided
    if start_time:
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(Snapshot.timestamp >= start_datetime)
        except ValueError:
            return jsonify({'error': 'Invalid start time format. Use ISO8601 UTC format.'}), 400
    
    if end_time:
        try:
            end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(Snapshot.timestamp <= end_datetime)
        except ValueError:
            return jsonify({'error': 'Invalid end time format. Use ISO8601 UTC format.'}), 400
    
    # Order by timestamp
    snapshots = query.order_by(Snapshot.timestamp).all()
    
    return jsonify([snapshot.to_dict() for snapshot in snapshots])

@api_bp.route('/latest_snapshots', methods=['GET'])
def get_latest_snapshots():
    # Subquery to get the latest snapshot for each metric
    latest_snapshots = []
    
    for metric in Metric.query.all():
        snapshot = Snapshot.query.filter_by(metric_uuid=metric.uuid).order_by(Snapshot.timestamp.desc()).first()
        if snapshot:
            latest_snapshots.append(snapshot.to_dict_with_metric())
    
    return jsonify(latest_snapshots)

@api_bp.route('/aggregators', methods=['GET'])
def get_aggregators():
    aggregators = Aggregator.query.all()
    return jsonify([aggregator.to_dict() for aggregator in aggregators])

@api_bp.route('/shutdown_aggregator', methods=['POST'])
def shutdown_aggregator():
    data = request.get_json()
    
    if not data or 'aggregator_uuid' not in data:
        return jsonify({'error': 'Aggregator UUID is required'}), 400
    
    aggregator_uuid = data['aggregator_uuid']
    
    # Check if aggregator exists
    aggregator = Aggregator.query.get(aggregator_uuid)
    if not aggregator:
        return jsonify({'error': f'Aggregator with UUID "{aggregator_uuid}" not found'}), 404
    
    # Send shutdown event
    send_shutdown_event(aggregator_uuid)
    
    return '', 200 