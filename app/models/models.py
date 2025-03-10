import uuid
from datetime import datetime
from app import db

class Aggregator(db.Model):
    __tablename__ = 'aggregators'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_active = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship with metrics
    metrics = db.relationship('Metric', backref='aggregator', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }

class Metric(db.Model):
    __tablename__ = 'metrics'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Foreign key to aggregator
    aggregator_uuid = db.Column(db.String(36), db.ForeignKey('aggregators.uuid'), nullable=False)
    
    # Relationship with snapshots
    snapshots = db.relationship('Snapshot', backref='metric', lazy=True, cascade='all, delete-orphan')
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('aggregator_uuid', 'name', name='uq_metric_aggregator_name'),
    )
    
    def __init__(self, aggregator_uuid, name, unit):
        self.uuid = str(uuid.uuid4())
        self.aggregator_uuid = aggregator_uuid
        self.name = name
        self.unit = unit
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'unit': self.unit,
            'aggregator_name': self.aggregator.name,
            'created_at': self.created_at.isoformat()
        }

class Snapshot(db.Model):
    __tablename__ = 'snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    offset = db.Column(db.Integer, nullable=False)  # Client timezone offset in minutes
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Foreign key to metric
    metric_uuid = db.Column(db.String(36), db.ForeignKey('metrics.uuid'), nullable=False)
    
    def __init__(self, metric_uuid, value, timestamp, offset):
        self.metric_uuid = metric_uuid
        self.value = value
        self.timestamp = timestamp
        self.offset = offset
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'offset': self.offset
        }
    
    def to_dict_with_metric(self):
        return {
            'metric_uuid': self.metric_uuid,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'offset': self.offset
        } 