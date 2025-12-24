import logging
from flask import Flask
from config import Config
from models import db
from utils import init_db_data
from routes import main

# --- LOGGING CONFIG ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logging.basicConfig(
    filename='system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        init_db_data()
    app.run(debug=True)