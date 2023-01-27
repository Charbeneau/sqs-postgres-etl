import os
import psycopg2
from loguru import logger
from models import UserLogin
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


def create_postgres_url():
    """Creates an SQLAlchemy URL
    used to connect to the DB.

    Args:
        None

    Returns:
        An instance of sqlalchemy.engine.URL.
    """
    POSTGRES_URL = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE")
    )
    return POSTGRES_URL

POSTGRES_URL = create_postgres_url()
ENGINE = create_engine(POSTGRES_URL)
SESSION = sessionmaker(ENGINE)


def add_user_login_to_db(user_login) -> None:
    """Inserts an instance of the UserLogin to Postgres.

    Args:
        user_login: An instance of the UserLogin model.

    Returns:
        Nothing.
    """

    with SESSION() as session:
        logger.info("Adding UserLogin instance to the DB.")
        session.add(user_login)
        session.commit()
        logger.info("Done.")