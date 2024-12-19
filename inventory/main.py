# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from redis_om import HashModel, get_redis_connection
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel, get_redis_connection
from typing import Optional
from uuid import UUID

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Redis connection
redis = get_redis_connection(
    host='redis-18296.c334.asia-southeast2-1.gce.redns.redis-cloud.com',
    port=18296,
    username="default",
    password="ZtBHVAVQ7lNrAT0PNlUXi0X7oSrewc7n",
    decode_responses=True,
)

# Define Product model for Redis OM
# class Product(HashModel):
#     # name: str
#     product_id:uuid
#     price: float
#     quantity: int

#     class Meta:
#         database = redis

# Define Product model for Redis OM
class Product(HashModel):
    product_id: UUID  # UUID field for product_id
    name: str =None
    product_attribute_id: Optional[UUID] = None  # Nullable UUID field
    qty: Optional[int] = None  # Nullable integer
    low_stock_threshold: Optional[int] = None  # Nullable integer
    
    # price: float
    # quantity: int

    class Meta:
        database = redis

        
    def save(self, *args, **kwargs):
        # Set pk to be equal to product_id
        self.pk = str(self.product_id)
        super().save(*args, **kwargs)

# Define Pydantic schema for input validation
class ProductSchema(BaseModel):
    # name: str
    # product_id:UUID
    # price: float
    # quantity: int

    product_id: UUID
    name:str =None
    product_attribute_id: Optional[UUID] = None
    qty: Optional[int] = None
    low_stock_threshold: Optional[int] = None

@app.get('/products')
def all():
    # Retrieve all primary keys and return full product details
    return [Product.get(pk).dict() for pk in Product.all_pks()]

# @app.post('/products')
# def create(product: ProductSchema):
#     # Use the schema to create a Product instance
#     new_product = Product(**product.dict())
#     new_product.save()
#     return new_product

@app.post('/products')
def create_product(product: ProductSchema):
    try:
        # Simpan produk ke Redis
        new_product = Product(**product.dict())
        new_product.save()
        return new_product.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello wahyu"}

# @app.get('/products/{pk}')
# def get_product(pk: str):
#     try:
#         # Fetch the product from Redis by primary key
#         product = Product.get(pk)
#         return product.dict()  # Convert Redis OM model to dictionary
#     except KeyError:
#         # Handle case when the product is not found
#         return {"error": f"Product with id {pk} not found"}, 404
#     except Exception as e:
#         # Handle unexpected errors
#         return {"error": str(e)}, 500
    

@app.get('/products/{pk}')
def get_product(pk: str):
    try:
        product = Product.get(pk)
        return product.dict()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Product with id {pk} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/products/{pk}')
def delete_product(pk: str):
    try:
        # Attempt to delete the product
        deleted_count = Product.delete(pk)
        if deleted_count == 0:
            return {"error": f"Product with id {pk} not found"}, 404
        return {"message": f"Product with id {pk} has been deleted successfully"}
    except Exception as e:
        # Handle unexpected errors
        return {"error": str(e)}, 500

@app.put('/products/{pk}')
def update_product(pk: str, updated_data: ProductSchema):
    try:
        # Ambil produk dari Redis
        product = Product.get(pk)
        
        # Perbarui hanya atribut yang diberikan
        update_dict = updated_data.dict(exclude_unset=True)  # Hanya atribut yang dikirim
        for key, value in update_dict.items():
            setattr(product, key, value)
        
        # Simpan perubahan ke Redis
        product.save()
        return product.dict()
    except KeyError:
        # Tangani kasus ketika produk tidak ditemukan
        raise HTTPException(status_code=404, detail=f"Product with id {pk} not found")
    except Exception as e:
        # Tangani error lainnya
        raise HTTPException(status_code=500, detail=str(e))


# @app.post('/products/validate_stock')
# def validate_stock(product_id: UUID, qty: int):
#     try:
#         product = Product.find(Product.product_id == product_id).first()
#         if not product:
#             raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
#         if product.qty is None or product.qty < qty:
#             raise HTTPException(status_code=400, detail="Insufficient stock")
#         return {"message": "Stock is sufficient", "product_id": product_id, "available_qty": product.qty}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# @app.post('/products/validate_stock')
# def validate_stock(product_id: UUID, qty: int):
#     try:
#         # Cari produk berdasarkan product_id
#         product = Product.find(Product.product_id == product_id).first()
#         if not product:
#             # Produk tidak ditemukan
#             raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

#         if product.qty is None or product.qty < qty:
#             # Stok tidak mencukupi
#             raise HTTPException(status_code=400, detail="Stok produk tidak mencukupi")

#         # Stok mencukupi
#         return {"message": "Stok mencukupi", "product_id": product_id, "available_qty": product.qty}
#     except Exception as e:
#         # Tangani error lainnya
#         raise HTTPException(status_code=500, detail=str(e))

