import time


from fastapi import FastAPI,HTTPException
from app.database_connector.connections import  get_db_pipeline
from app.fastapitypes.sql_connection import Db_Connection_Args

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/get_schema")
async def get_schema(db_info:Db_Connection_Args,return_normalize_schema:bool=False):
    start_time = time.time()
    db_pipeline = await get_db_pipeline(db_info)

    return {"database_schema": db_pipeline.return_db_prompt(False),
            "extraction_time": time.time() - start_time,
            "normalized_schema": db_pipeline.return_db_prompt(True) if return_normalize_schema else None }

@app.post("/execute_query")
async def execute_query(db_info:Db_Connection_Args,
                        query:str,
                        normalized_query:bool,
                        max_rows:int,
                        autocommit:bool=False,
                        unormalized_schema:bool=False,):
    if normalized_query and unormalized_schema is None:
        # technically we could also ju
        raise HTTPException(status_code=400, detail=("If a normalized query is provided, a unormalized "
                                                     "schema must be provided to transform the query to "
                                                     "its unormalized form."))




    start_time = time.time()