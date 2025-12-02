"""
Video Publisher Web Application - Flask app with Web UI and REST API
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """Create and configure Flask application."""
    
    app = Flask(__name__,
                template_folder='api/templates',
                static_folder='api/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024  # 4GB max file size
    app.config['UPLOAD_FOLDER'] = Path('uploads')
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    
    # Trust proxy headers for proper URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Import and register blueprints inside app context to avoid circular imports
    from api.web_routes import web_bp
    from api.api_routes import api_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('base.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return "Internal Server Error", 500
    
    return app

app = create_app()

if __name__ == '__main__':
    print("\n🚀 Starting UploadVerse Web Application...")
    print("📱 Open your browser and navigate to: http://localhost:5000")
    print("📖 API Documentation: http://localhost:5000/api")
    print("\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
