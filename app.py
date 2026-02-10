from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from auth_blueprint import authentication_blueprint
from appointments_blueprint import appointments_blueprint

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

app.register_blueprint(authentication_blueprint)
app.register_blueprint(appointments_blueprint)

@app.route("/")
def index():
    return "Pregnancy Planner API"

app.run(debug=True, port=5000)
