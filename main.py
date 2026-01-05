from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models, json
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text, cast, DateTime
from datetime import datetime, timezone


app = FastAPI(title="Incremental Numbers API")
models.Base.metadata.create_all(bind=engine)

class CounterBase(BaseModel):
    CLIENT_KEY: str
    COUNTER_NAME: str
    COUNTER_VALUE: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/counters/", status_code=status.HTTP_201_CREATED)
async def create_counter(counter: CounterBase, db: db_dependency):
    db_counter = models.Counter(
        CLIENT_KEY=counter.CLIENT_KEY,
        COUNTER_NAME=counter.COUNTER_NAME,
        COUNTER_VALUE=counter.COUNTER_VALUE
    )
    db.add(db_counter)
    db.commit()
    db.refresh(db_counter)
    return db_counter


@app.post("/increment_counter/", status_code=status.HTTP_200_OK)
async def increment_counter(client_key: str, counter_name: str, db: db_dependency):

    if not client_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CLIENT_KEY is required")
    
    if not counter_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="COUNTER_NAME is required")
    
    query = text("""INSERT INTO GLIDE_INCREMENTAL_NUMBERS (CLIENT_KEY, COUNTER_NAME, COUNTER_VALUE)
		VALUES (:client_key, :counter_name, 1)
		ON DUPLICATE KEY
			UPDATE COUNTER_VALUE = COUNTER_VALUE + 1, LAST_MODIFIED_ON = CURRENT_TIMESTAMP
		RETURNING COUNTER_VALUE, LAST_MODIFIED_ON;""")
    result = db.execute(query, {"client_key": client_key, "counter_name": counter_name}).fetchone()

    print("Increment Result:")
    print(result)
    print(type(result))

    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An Error occurred in the backend while incrementing the counter")

    db.commit()

    resp = {
        "COUNTER_VALUE": result.COUNTER_VALUE,
        "LAST_MODIFIED_ON": str(result.LAST_MODIFIED_ON)
    }

    return resp