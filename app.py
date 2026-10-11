import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from extensions import db, jwt
from routes.vendors.routes import vendors_bp
from routes.auth.routes import auth_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sabziraah.db"
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

db.init_app(app)
jwt.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(vendors_bp)    # like app.use("/vendors", router)

with app.app_context():
    import models               # makes sure the table gets registered
    db.create_all()

@app.route("/")
def home():
    return jsonify({"message":"Hello from SabziRaah"})