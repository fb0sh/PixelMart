from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    app.config['SECRET_KEY'] = 'pixelmart-super-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pixelmart.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.products import products_bp
    from app.api.admin import admin_bp
    from app.api.challenges import challenges_bp
    from app.api.cart import cart_bp
    from app.api.ssrf import ssrf_bp
    from app.api.feedback import feedback_bp
    from app.api.logs import logs_bp
    from app.api.profile import profile_bp
    from app.api.config import config_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(challenges_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api')
    app.register_blueprint(ssrf_bp, url_prefix='/api')
    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(logs_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(config_bp)

    # Internal flag endpoint (for SSRF)
    @app.route('/internal/flag')
    def internal_flag():
        return {'flag': 'FloatCTF{ssrf_caught_the_internal_flag}'}

    # Serve frontend static files in production
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    if os.path.exists(static_dir):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path.startswith('api/') or path.startswith('internal/'):
                from flask import jsonify
                return jsonify({'error': 'Not found'}), 404
            file_path = os.path.join(static_dir, path) if path else os.path.join(static_dir, 'index.html')
            if os.path.isfile(file_path):
                return send_from_directory(static_dir, path if path else 'index.html')
            return send_from_directory(static_dir, 'index.html')

    with app.app_context():
        from app import models
        models.init_db()

    return app
