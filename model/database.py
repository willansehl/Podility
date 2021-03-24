from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://wwzjnlvhkgolub:8e540e9fca7275963888eabb845acd91163bf9dabc2c2e9d87de6ab339141455@ec2-18-211-97-89.compute-1.amazonaws.com/d1m287o6b0hig7"
engine = create_engine( SQLALCHEMY_DATABASE_URL )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()