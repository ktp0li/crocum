import os
import base64
import binascii
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError
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


# fastapi models
class ConfigRespPost(BaseModel):
    lab_id: int
    config_file_name: str
    config_file: str


class LabRespPost(BaseModel):
    lab_name: str


class LabRespGet(BaseModel):
    lab_id: int
    lab_name: str
    configs: List[str]


# db models
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
    config_id = Column(Integer, primary_key=True)
    config_file_name = Column(String, nullable=False)
    config_file = Column(String, nullable=False)
    lab_id = Column(ForeignKey("labs.lab_id"))


class LabInstances(Base):
    __tablename__ = "lab_instances"
    instance_id = Column(Integer, primary_key=True)
    lab_id = Column(ForeignKey("labs.lab_id"))
    user_id = Column(ForeignKey("users.user_id"))
    resources = Column(String)
    state = Column(String)


@app.get("/labs/")
async def get_labs() -> List[LabRespGet]:
    labs = session.query(Labs).all()
    configs = session.query(Configs)
    return [
        LabRespGet(
            lab_id=i.lab_id,
            lab_name=i.lab_name,
            configs=[
                j.config_file_name for j in configs.filter_by(lab_id=i.lab_id).all()
            ],
        )
        for i in labs
    ]


@app.post("/labs/")
async def post_lab(lab: LabRespPost) -> LabRespPost:
    entry = Labs(lab_name=lab.lab_name)
    session.add(entry)
    session.commit()
    return lab


@app.post("labs/configs/")
async def post_config(config: ConfigRespPost) -> ConfigRespPost:
    # base64 validation for config_file
    try:
        base64.b64decode(config.config_file.encode())
    except binascii.Error as exc:
        raise RequestValidationError(
            [
                ErrorWrapper(
                    ValueError("config_file must be base64 string"),
                    ("body", "config_file"),
                )
            ]
        ) from exc

    # add entry to db
    entry = Configs(
        config_file_name=config.config_file_name,
        config_file=config.config_file,
        lab_id=config.lab_id,
    )

    try:
        session.add(entry)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(404, f"Lab with id {config.lab_id} not found") from exc
    return config


if __name__ == "__main__":
    Base.metadata.create_all(engine)
