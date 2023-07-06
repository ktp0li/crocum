import os

from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

dbuser, dbpass, dbhost, dbport, dbname = (
    os.getenv("DB_USER"),
    os.getenv("DB_PASS"),
    os.getenv("DB_HOST"),
    os.getenv("DB_PORT"),
    os.getenv("DB_NAME"),
)
engine = create_engine(f"postgresql://{dbname}:{dbpass}@{dbhost}:{dbport}/{dbname}")
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = FastAPI()

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)


class Labs(Base):
    __tablename__ = "labs"
    lab_id = Column(Integer, primary_key=True)
    lab_name = Column(String, unique=True, nullable=False)


class Configs(Base):
    __tablename__ = "configs"
    config_file = Column(LargeBinary, nullable=False)
    lab = Column(ForeignKey("labs.lab_id"))


class LabInstances(Base):
    __tablename__ = "lab_instances"
    instance_id = Column(Integer, primary_key=True)
    lab = Column(ForeignKey("labs.lab_id"))
    user = Column(ForeignKey("users.user_id"))
    resources = Column(String)
    state = Column(String)
