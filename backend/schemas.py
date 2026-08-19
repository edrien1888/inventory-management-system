from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    category_id: int

    class Config:
        from_attributes = True
        
class MovementCreate(BaseModel):
    movement_type: str
    quantity: int
    product_id: int
    user_id: int


class MovementResponse(BaseModel):
    id: int
    movement_type: str
    quantity: int
    product_id: int
    user_id: int

    class Config:
        from_attributes = True