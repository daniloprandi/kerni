import sys
from flask import Flask
from threading import Thread
from backend.node_discovery_api.routes.health import health_bp
from common.linux.tcp_ip.internet_layer.ping import listen_for_ping

sys.path.insert(0, "/var/www/kerni")

app = Flask(__name__)

app.register_blueprint(health_bp)


if __name__ == "__main__":
  Thread(target=listen_for_ping, daemon=True).start()

  app.run(host="0.0.0.0", port=5001)