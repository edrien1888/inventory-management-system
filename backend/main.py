from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models
from auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from database import Base, SessionLocal, engine
from schemas import (
    CategoryCreate,
    CategoryResponse,
    MovementCreate,
    MovementResponse,
    ProductCreate,
    ProductResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)


app = FastAPI()
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://inventory-management-frontend-three-rose.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    user = db.query(
        models.User
    ).filter(
        models.User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return user

@app.get("/")
def home():
    return {
        "message": "Backend funcionando correctamente"
    }


@app.get("/test-db")
def test_database():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "message": "PostgreSQL conectado correctamente"
    }

@app.post("/auth/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/auth/login", response_model=TokenResponse)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(
        models.User
    ).filter(
        models.User.email == credentials.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not verify_password(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@app.post(
    "/categories",
    response_model=CategoryResponse
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_category = db.query(
        models.Category
    ).filter(
        models.Category.name == category.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="La categoría ya existe"
        )

    new_category = models.Category(
        name=category.name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@app.get(
    "/categories",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(
        models.Category
    ).all()


@app.put(
    "/categories/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_category = db.query(
        models.Category
    ).filter(
        models.Category.id == category_id
    ).first()

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Categoría no encontrada"
        )

    duplicate_category = db.query(
        models.Category
    ).filter(
        models.Category.name == category.name,
        models.Category.id != category_id
    ).first()

    if duplicate_category:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una categoría con ese nombre"
        )

    existing_category.name = category.name

    db.commit()
    db.refresh(existing_category)

    return existing_category


@app.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = db.query(
        models.Category
    ).filter(
        models.Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Categoría no encontrada"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Categoría eliminada correctamente"
    }

@app.post(
    "/products",
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = db.query(
        models.Category
    ).filter(
        models.Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="La categoría no existe"
        )

    if product.price < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio no puede ser negativo"
        )

    if product.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="El stock no puede ser negativo"
        )

    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(
        models.Product
    ).all()


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing_product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    category = db.query(
        models.Category
    ).filter(
        models.Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="La categoría no existe"
        )

    if product.price < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio no puede ser negativo"
        )

    if product.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="El stock no puede ser negativo"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.stock = product.stock
    existing_product.category_id = product.category_id

    db.commit()
    db.refresh(existing_product)

    return existing_product


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Producto eliminado correctamente"
    }

@app.post(
    "/movements",
    response_model=MovementResponse
)
def create_movement(
    movement: MovementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == movement.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    if movement.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor que cero"
        )

    movement_type = movement.movement_type.lower().strip()

    if movement_type == "entrada":
        product.stock += movement.quantity

    elif movement_type == "salida":
        if product.stock < movement.quantity:
            raise HTTPException(
                status_code=400,
                detail="Stock insuficiente"
            )

        product.stock -= movement.quantity

    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo de movimiento inválido. Use 'entrada' o 'salida'"
        )

    new_movement = models.Movement(
        movement_type=movement_type,
        quantity=movement.quantity,
        product_id=movement.product_id,
        user_id=current_user.id
    )

    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)

    return new_movement


@app.get(
    "/movements",
    response_model=list[MovementResponse]
)
def get_movements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(
        models.Movement
    ).all()