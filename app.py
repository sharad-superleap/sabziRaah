from flask import Flask, jsonify
from extensions import db
from routes.vendors.routes import vendors_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sabziraah.db"

db.init_app(app)
app.register_blueprint(vendors_bp)    # like app.use("/vendors", router)

with app.app_context():
    import models               # makes sure the table gets registered
    db.create_all()

@app.route("/")
def home():
    return jsonify({"message":"Hello from SabziRaah"})