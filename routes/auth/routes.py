import re
import secrets
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from extensions import db
from models import Vendor, OtpCode

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

PHONE_RE = re.compile(r"^[6-9]\d{9}$")   # 10-digit Indian mobile number
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 30

@auth_bp.route("/request-otp", methods=["POST"])
def request_otp():
    data = request.get_json() or {}
    phone = str(data.get("phone", "")).strip()

    if not PHONE_RE.match(phone):
        return jsonify({
            "error": "enter a valid 10-digit mobile number"
        }), 400

    existing = OtpCode.query.filter_by(phone=phone).first()

    if existing and existing.seconds_since_created < RESEND_COOLDOWN_SECONDS:
        return (
            {
                "error": "please wait before requesting another OTP"
            }
        ), 429
    
    # one active OTP per phone: remove the old one
    OtpCode.query.filter_by(phone=phone).delete()

    # generating new code
    code = f"{secrets.randbelow(1_000_000):06d}"
    otp = OtpCode(phone=phone)
    otp.set_code(code)
    db.session.add(otp)
    db.session.commit()

    print(f"[DEV ONLY] OTP for {phone}: {code}")

    return jsonify(
        {
            "message": "OTP sent"
        }
    ), 200


@auth_bp.route("/verify-otp",methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    phone = str(data.get("phone","")).strip()
    code = str(data.get("otp", "")).strip()

    otp = OtpCode.query.filter_by(phone=phone).first()

    if not otp:
        return jsonify(
            {
                "error": "request an OTP first"
            }
        ), 400
    
    if otp.is_expired:
        db.session.delete(otp)
        db.session.commit()
        return jsonify(
            {
                "error": "OTP expired, request a new one"
            }
        ), 400

    if otp.attempts >= MAX_ATTEMPTS:
        return jsonify(
            {
                "error": "too many attempts, request a new OTP"
            }
        ), 429

    if not otp.check_code(code):
        otp.attempts += 1
        db.session.commit()
        return jsonify(
            {
                "error": "incorrect OTP"
            }
        ), 400

    # OTP is correct and single use so delete it
    db.session.delete(otp)

    vendor = Vendor.query.filter_by(phone=phone).first()
    if not vendor:
        # first login = signup, and a name is needed for new vendors
        name = str(data.get("name", "")).strip()
        if not name:
            db.session.rollback()   # keeps the OTP, so the vendor can retry with a name
            return jsonify(
                {
                    "error": "name is required for new vendors"
                }
            ), 400
        
        vendor = Vendor(
            name=name,
            phone=phone,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            languages_known=data.get("languages_known")
        )
        db.session.add(vendor)

    db.session.commit()

    token = create_access_token(identity=str(vendor.id))
    return jsonify(
        {
            "access_token": token, 
            "vendor": vendor.to_dict()
        }
    ), 200


