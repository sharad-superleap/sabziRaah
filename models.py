
from datetime import datetime, timezone
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
