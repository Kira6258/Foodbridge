from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import Config
from models.db import mysql, User
import firebase_admin
from firebase_admin import credentials, auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Firebase Admin
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(app.config['FIREBASE_SERVICE_ACCOUNT_KEY'])
            firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"WARNING: Firebase Admin SDK initialization failed: {e}")
        print("Make sure you have placed 'firebase-adminsdk.json' in the project root.")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.donor import donor_bp
    from routes.shelter import shelter_bp
    from routes.volunteer import volunteer_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp, url_prefix='/donor')
    app.register_blueprint(shelter_bp, url_prefix='/shelter')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
