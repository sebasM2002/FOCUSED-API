from sqlalchemy import Column, Integer, String
from database.database import Base

class Professional(Base):
    __tablename__ = "professional"

    
    id = Column(Integer, primary_key=True, index=True)
    id_office = Column(Integer)
    name = Column(String)
    lastname = Column(String)
    email = Column(String)
    birthdate = Column(String)
    phone =  Column(String)
    document_type =  Column(String)
    document =  Column(String)
    password =  Column(String)
    exequatur = Column(bool)
    role = Column(Integer)
