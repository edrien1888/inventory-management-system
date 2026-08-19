from datetime import datetime

from sqlalchemy import (
                Column,
                DateTime,
                Float,
                ForeignKey,
                Integer,
                String,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
                __tablename__ = "users"

                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(100), nullable=False)
                email = Column(String(150), unique=True, index=True, nullable=False)
                password_hash = Column(String(255), nullable=False)

                movements = relationship("Movement", back_populates="user")


class Category(Base):
                __tablename__ = "categories"

                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(100), unique=True, nullable=False)

                products = relationship("Product", back_populates="category")


class Product(Base):
                __tablename__ = "products"

                id = Column(Integer, primary_key=True, index=True)
                name = Column(String(150), nullable=False)
                description = Column(String(300), nullable=True)
                price = Column(Float, nullable=False)
                stock = Column(Integer, nullable=False, default=0)

                category_id = Column(
                Integer,
                ForeignKey("categories.id"),
                nullable=False,
                )

                category = relationship("Category", back_populates="products")
                movements = relationship("Movement", back_populates="product")


class Movement(Base):
                __tablename__ = "movements"

                id = Column(Integer, primary_key=True, index=True)
                movement_type = Column(String(20), nullable=False)
                quantity = Column(Integer, nullable=False)

                product_id = Column(
                Integer,
                ForeignKey("products.id"),
                nullable=False,
                )

                user_id = Column(
                Integer,
                ForeignKey("users.id"),
                nullable=False,
                )

                created_at = Column(
                DateTime,
                default=datetime.utcnow,
                nullable=False,
                )

                product = relationship("Product", back_populates="movements")
                user = relationship("User", back_populates="movements")