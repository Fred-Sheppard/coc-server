from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    # This file is used for migration commands only
    pass 