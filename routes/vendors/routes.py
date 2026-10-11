from flask import Blueprint, jsonify, request
from extensions import db
from models import Vendor, StockItem

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")

# ---------- Vendors ----------
@vendors_bp.route("", methods=["POST"])
def create_vendor():
    data = request.get_json()

    if not data or "name" not in data or "phone" not in data:
        return jsonify({"error": "name and phone are required"}), 400

    if Vendor.query.filter_by(phone=data["phone"]).first():
        return jsonify({
            "error": "a vendor with this phone already exists"
        }), 400

    vendor = Vendor(
        name=data["name"],
        phone=data["phone"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        languages_known=data.get("languages_known")
    )

    db.session.add(vendor)
    db.session.commit()
    return jsonify(
        vendor.to_dict()
    ), 201


@vendors_bp.route("", methods=["GET"])
def list_vendors():
    vendors = Vendor.query.all()
    return jsonify(
        [vendors.to_dict() for vendor in vendors]
    ), 200

# ---------- Stock (belongs to a vendor) ----------
@vendors_bp.route("/<int:vendor_id>/stock", methods=["POST"])
def add_stock(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id) # auto returns 404 if vendor not found with the id
    data = request.get_json()

    if not data or "name" not in data or "price" not in data:
        return jsonify({"error": "name and price are required"}), 400
    
    item = StockItem(name=data["name"], price=data["price"], vendor=vendor)

    db.session.add(item)
    db.session.commit()

    return jsonify(
        item.to_dict()
    ), 201

@vendors_bp.route("/<int:vendor_id>/stock", methods=["GET"])
def get_stock(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id)
    return jsonify(
        [item.to_dict() for item in vendor.stock_items]
    ), 200

