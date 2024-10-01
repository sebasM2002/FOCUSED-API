from sqlalchemy import Column, Integer, String
from database.database import Base

class Patient(Base):
    __tablename__ = "patient"

    
    id = Column(Integer, primary_key=True, index=True)
    id_psychiatrist = Column(Integer)
    id_psychologist = Column(Integer)
    name = Column(String)
    lastname = Column(String)
    email = Column(String)
    phone =  Column(String)
    document_type =  Column(String)
    document =  Column(String)
    password =  Column(String)
    verified = Column(bool)
    allergies = Column(String)
    condition = Column(String)
    city = Column(String)
    sector = Column(String)
    address = Column(String)
