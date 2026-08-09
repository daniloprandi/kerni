from flask import Flask
from common.routes.health import health_bp

app = Flask(__name__)

app.register_blueprint(health_bp)