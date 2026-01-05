from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base

class Counter(Base):
    __tablename__ = "GLIDE_INCREMENTAL_NUMBERS"

    CLIENT_KEY = Column(String(383), primary_key=True)
    COUNTER_NAME = Column(String(383), primary_key=True,)
    COUNTER_VALUE = Column(Integer, unique=True, nullable=False)
    LAST_MODIFIED_ON = Column(DateTime)
