import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configure the SQLAlchemy database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register API routes
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    # Register Dash application
    from app.dashboard import init_dashboard
    init_dashboard(app)
    
    # Command to initialize the database
    @app.cli.command('db-init')
    def db_init():
        db.create_all()
        logging.info('Database initialized.')
    
    return app 