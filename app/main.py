from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import os
from dotenv import load_dotenv
import time
from sqlalchemy.exc import OperationalError


# Налаштування бази даних
load_dotenv()  # Додайте, якщо використовуєте локальне тестування з .env

# Формування DATABASE_URL
DATABASE_URL = (
    f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
)

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

def wait_for_database_connection(retries=5, delay=5):
    for attempt in range(retries):
        try:
            # Спроба підключитися до бази
            with engine.connect() as connection:
                print("Database connection successful!")
                return True
        except OperationalError as e:
            print(f"Attempt {attempt + 1} - Database not ready, retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed to connect to the database after multiple attempts.")
    return False

# Перевірка підключення при запуску застосунку
if not wait_for_database_connection():
    raise Exception("Database connection could not be established. Exiting...")

app = FastAPI()

@app.on_event("startup")
async def startup():
    if not wait_for_database_connection():
        raise Exception("Database connection could not be established. Exiting...")
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Оголошення моделі
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Створення таблиць
Base.metadata.create_all(bind=engine)

# Ініціалізація FastAPI
app = FastAPI()

# Модель даних для входу
class ItemCreate(BaseModel):
    name: str
    description: str

class ItemUpdate(BaseModel):
    name: str
    description: str

# 1. Виведення простої інформації
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

# 2. Виведення об'єктів з бази даних
@app.get("/items/", response_model=List[ItemCreate])
def read_items(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    items = db.query(Item).offset(skip).limit(limit).all()
    db.close()
    return items

# 3. Внесення об'єкта в базу даних
@app.post("/items/", response_model=ItemCreate)
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

# 4. Оновлення об'єкта в базі даних
@app.put("/items/{item_id}", response_model=ItemCreate)
def update_item(item_id: int, item: ItemUpdate):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

# 5. Видалення об'єкта з бази даних
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    db.close()
    return {"detail": "Item deleted"}

# 6. Виведення інформації про об'єкт з бази даних
@app.get("/items/{item_id}", response_model=ItemCreate)
def read_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

