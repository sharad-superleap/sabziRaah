from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Vendor, StockItem

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")

# ---------- Public (anyone can read) ----------
@vendors_bp.route("", methods=["GET"])
def list_vendors():
    vendors = Vendor.query.all()
    return jsonify(
        [vendor.to_dict() for vendor in vendors]
    ), 200

@vendors_bp.route("/<int:vendor_id>/stock", methods=["GET"])
def get_stock(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id)
    return jsonify(
        [item.to_dict() for item in vendor.stock_items]
    ), 200


# ---------- Protected (vendor must be logged in) ----------
@vendors_bp.route("/me/stock", methods=["POST"])
@jwt_required()
def add_my_stock():
    vendor = db.get_or_404(Vendor, int(get_jwt_identity()))
    data = request.get_json()

    if not data or "name" not in data or "price" not in data:
        return jsonify(
            {
                "error": "name and price are required"
            }
        ), 400

    item = StockItem(name=data["name"],price=data["price"], vendor=vendor)
    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201

@vendors_bp.route("/me/stock/<int:item_id>", methods=['DELETE'])
@jwt_required()
def delete_my_stock(item_id):
    vendor_id = int(get_jwt_identity())
    item = db.get_or_404(StockItem, item_id)

    if item.vendor_id != vendor_id:
        return jsonify(
            {
                "error": "not your item"
            }
        ), 400

    db.session.delete(item)
    db.session.commit()

    return "", 204


