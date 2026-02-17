from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from auth_blueprint import authentication_blueprint
from appointments_blueprint import appointments_blueprint
from pregnancy_profile_blueprint import pregnancy_profile_blueprint

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

app.register_blueprint(authentication_blueprint)
app.register_blueprint(appointments_blueprint)
app.register_blueprint(pregnancy_profile_blueprint)

@app.route("/")
def index():
    return "Pregnancy Planner"

if __name__ == "__main__":
    app.run()
