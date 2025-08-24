# importa los modelos para que create_all los registre
from app.db.models.brand import Brand  # noqa: F401
from app.db.models.product import Product
from app.db.models.sale import Sale, SaleItem
from app.db.models.user import User 