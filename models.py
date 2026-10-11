
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from sqlalchemy import JSON

# vendor model
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    latitude = db.Column(db.Float)    # plain floats for now; PostGIS comes later
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    languages_known = db.Column(JSON, nullable=False, default=list)

    # the 'one side : vendor.stock_items gives a list of this vendor's items
    stock_items = db.relationship(
        "StockItem", back_populates="vendor", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "languages_known": self.languages_known,
        }

# stockItem model
class StockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(50), nullable=False)

    # the many side : the foreign key column that stores the link
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=False)
    vendor = db.relationship("Vendor", back_populates="stock_items")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "vendor_id": self.vendor_id,
        }

# Otp Code for logging in
class OtpCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False,index=True)
    code_hash = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def _as_utc(dt):
        # SQLite returns naive datetimes, so we re-attach UTC before comparing
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    
    def set_code(self,code):
        self.code_hash = generate_password_hash(code)
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    def check_code(self, code):
        return check_password_hash(self.code_hash, code)
    
    @property
    def is_expired(self):
        return datetime.now(timezone.utc) > self._as_utc(self.expires_at)

    @property
    def seconds_since_created(self):
        return (datetime.now(timezone.utc) - self._as_utc(self.created_at)).total_seconds()
    