from sqlalchemy import Column, Integer, String
from database.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    id_rol = Column(Integer)