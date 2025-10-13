from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class SQLRepositoryBase:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, echo=False, future=True)
        self.session_maker = sessionmaker(bind=self.engine, future=True)
        Base.metadata.create_all(self.engine)