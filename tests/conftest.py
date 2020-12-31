import os
import pytest
import json
import sqlalchemy as sa

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker

EMPTY_TRACKER = Tracker.from_dict(json.load(open("tests/data/empty_tracker.json")))
DATABASE_URL = os.environ.setdefault("DATABASE_URL", "postgresql:///postgres")


@pytest.fixture
def dispatcher():
    return CollectingDispatcher()


@pytest.fixture
def domain():
    return dict()


# @pytest.fixture
# def session():
#     engine = sa.create_engine(DATABASE_URL)
#     db_session = sessionmaker(bind=engine)()

#     try:
#         yield db_session
#     finally:
#         db_session.close()
#         Base.metadata.drop_all(engine)
