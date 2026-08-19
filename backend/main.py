from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
from auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from database import Base, SessionLocal, engine
from schemas import (
    CategoryCreate,
    CategoryResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


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
    existing_user = db.query(models.User).filter(
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
    user = db.query(models.User).filter(
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
                