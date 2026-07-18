from core.database import Base
from core.database import engine

# import all models
import models # pylint: disable=unused-import


def init_db():
    Base.metadata.create_all(bind=engine)
