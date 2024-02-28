from flask import Flask
from routes import bp as routes_bp
import logging

app = Flask(__name__)

app.register_blueprint(routes_bp)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

if __name__ == '__main__':
    app.run(debug=True)
