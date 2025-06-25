from flask import Flask
from config import config
from routes.api_routes import api_bp
import os


def create_app(config_name=None):
    """Application factory pattern for creating Flask app"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app


if __name__ == '__main__':
    # Create and run the app
    app = create_app()
    app.run(debug=app.config['DEBUG']) 