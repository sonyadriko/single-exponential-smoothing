from datetime import datetime
from sqlalchemy.orm import Session
import models
from services.auth_service import get_password_hash


# Seed data constants - single source of truth
PRODUCTS = [
    "Soto Ayam",
    "Nasi Goreng Jawa",
    "Nasi Bebek Biasa",
    "Nasi Ayam",
    "Nasi Lele",
    "Nasi 3T",
    "Es Teh",
    "Es Jeruk"
]

MAY_DATA_RAW = [
    ["01-May-25", 21, 9, 23, 14, 17, 19, 21, 12],
    ["02-May-25", 20, 4, 19, 17, 20, 20, 16, 20],
    ["03-May-25", 18, 12, 21, 20, 28, 19, 17, 23],
    ["04-May-25", 20, 8, 16, 24, 24, 24, 8, 16],
    ["05-May-25", 22, 6, 20, 14, 18, 21, 15, 8],
    ["06-May-25", 19, 7, 24, 12, 25, 15, 19, 10],
    ["07-May-25", 14, 6, 10, 13, 15, 12, 17, 11],
    ["08-May-25", 18, 3, 16, 15, 15, 18, 20, 7],
    ["09-May-25", 20, 5, 20, 14, 11, 24, 21, 9],
    ["10-May-25", 21, 15, 14, 20, 17, 19, 19, 16],
    ["11-May-25", 19, 6, 12, 16, 21, 14, 21, 15],
    ["12-May-25", 20, 11, 16, 9, 17, 17, 15, 10],
    ["13-May-25", 16, 18, 15, 12, 15, 19, 18, 9],
    ["14-May-25", 18, 9, 12, 11, 16, 16, 16, 14],
    ["15-May-25", 14, 9, 10, 13, 12, 13, 11, 10],
    ["16-May-25", 16, 16, 14, 17, 18, 15, 22, 18],
    ["17-May-25", 18, 10, 9, 10, 17, 11, 20, 13],
    ["18-May-25", 12, 8, 11, 8, 19, 17, 16, 15],
    ["19-May-25", 14, 11, 15, 11, 17, 12, 10, 11],
    ["20-May-25", 16, 15, 12, 13, 14, 11, 19, 10],
    ["21-May-25", 12, 13, 10, 14, 18, 8, 15, 12],
    ["22-May-25", 11, 8, 9, 9, 16, 11, 18, 11],
    ["23-May-25", 16, 9, 8, 10, 13, 14, 23, 10],
    ["24-May-25", 13, 4, 11, 11, 16, 10, 21, 9],
    ["25-May-25", 11, 5, 12, 14, 14, 9, 19, 11],
    ["26-May-25", 15, 7, 14, 9, 13, 8, 16, 7],
    ["27-May-25", 12, 3, 9, 7, 11, 16, 18, 9],
    ["28-May-25", 10, 12, 8, 12, 15, 20, 15, 6],
    ["29-May-25", 8, 7, 10, 6, 11, 10, 18, 10],
    ["30-May-25", 11, 6, 7, 9, 12, 12, 17, 15],
    ["31-May-25", 9, 9, 11, 10, 15, 16, 14, 11],
]


class SeedService:
    """Service for seeding initial data into the database."""

    def __init__(self, db: Session):
        self.db = db

    def create_default_users(self):
        """Create default admin and owner users if they don't exist."""
        if not self.db.query(models.User).filter(models.User.username == "admin").first():
            admin = models.User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            self.db.add(admin)

        if not self.db.query(models.User).filter(models.User.username == "owner").first():
            owner = models.User(
                username="owner",
                hashed_password=get_password_hash("owner123"),
                role="owner"
            )
            self.db.add(owner)
        self.db.commit()

    def create_default_products(self):
        """Create default products if they don't exist."""
        if self.db.query(models.Product).count() == 0:
            for product_name in PRODUCTS:
                product = models.Product(name=product_name, created_at=datetime.utcnow())
                self.db.add(product)
            self.db.commit()

    def seed_may_data(self):
        """Seed May 2025 sales data if no sales exist."""
        if self.db.query(models.Sale).count() == 0:
            for row in MAY_DATA_RAW:
                date = row[0]
                for i, product in enumerate(PRODUCTS):
                    qty = row[i + 1]
                    sale = models.Sale(date=date, product_name=product, qty=qty)
                    self.db.add(sale)
            self.db.commit()

    def seed_all(self):
        """Seed all initial data (users, products, sales)."""
        self.create_default_users()
        self.create_default_products()
        self.seed_may_data()


# Convenience function for use in startup event
def seed_database(db: Session) -> SeedService:
    """Create a SeedService instance and seed all data."""
    service = SeedService(db)
    service.seed_all()
    return service
