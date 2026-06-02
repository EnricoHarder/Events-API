from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from models import db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.rsvps import rsvps_bp
from routes.polls import polls_bp
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(rsvps_bp)
    app.register_blueprint(polls_bp)

    # Swagger UI configuration
    SWAGGER_URL = '/apidocs'
    API_URL = '/api/openapi.yaml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, 
        config={'app_name': "Evently API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/api/openapi.yaml')
    def serve_openapi():
        return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'})

    # Define a CLI command to create the database tables
    @app.cli.command("init-db")
    def init_db_command():
        """Creates the database tables."""
        db.create_all()
        print("Initialized the database.")

    return app

if __name__ == '__main__':
    app = create_app()
    # The db.create_all() is now handled by the 'flask init-db' command
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)