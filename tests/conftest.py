import os

import pytest
from fastapi.testclient import TestClient
from loguru import logger
from sqlmodel import SQLModel, create_engine

from app.core.config import configs
from app.core.container import Container
from app.main import AppCreator

os.environ["ENV"] = "test"


def reset_db():
    engine = create_engine(configs.DATABASE_URI)
    logger.info(engine)
    with engine.begin() as conn:
        # if "test" in configs.TEST_DATABASE_URI:
        SQLModel.metadata.drop_all(conn)
        SQLModel.metadata.create_all(conn)
    # else:
    # raise Exception("Not in test environment")
    return engine


@pytest.fixture
def client():
    reset_db()
    app_creator = AppCreator()
    app = app_creator.app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def container():
    return Container()


@pytest.fixture
def test_name(request):
    return request.node.name
