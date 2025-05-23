import time
import os
from pathlib import Path
from typing import List
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database_connector.connections import get_db_pipeline
from app.fastapitypes.sql_connection import Db_Connection_Args, SupportedDb
from app.fastapitypes.request_types import ExecuteQueryRequest
# Constants
BIGQUERY_KEYS_DIR = Path("app/files/bqkeys")
SQLITE_FILES_DIR = Path("app/files/sqlite")

app = FastAPI(
    title="Turbular Database API",
    description="A Multi-Cloud Platform (MCP) server that can connect to various database types and execute queries.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
BIGQUERY_KEYS_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_FILES_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}

@app.get("/supported-databases", response_model=List[str])
async def get_supported_databases():
    """
    Returns a list of all supported database types.
    """
    return [db.value for db in SupportedDb]

@app.post("/get_schema")
async def get_schema(db_info: Db_Connection_Args, return_normalize_schema: bool = False):
    """
    Get the schema of a database. If return_normalize_schema is True, the schema will be returned in its normalized form.
    Normalized form refers to the schema of the database in a format that is easier to work with for an LLM. Aka all names 
    are in lowercase and separated by underscores.
    """
    start_time = time.time()
    db_pipeline = await get_db_pipeline(db_info)

    return {"database_schema": db_pipeline.return_db_prompt(False),
            "extraction_time": time.time() - start_time,
            "normalized_schema": db_pipeline.return_db_prompt(True) if return_normalize_schema else None}


@app.post("/execute_query")
async def execute_query(req: ExecuteQueryRequest):
    """
    Execute a query on a database. If normalized_query is True, the query will be transformed from its normalized form 
    to its unormalized form.
    """
    
    if req.normalized_query and req.unormalized_schema is None:
        # technically we could also save a schema and reuse it here
        raise HTTPException(status_code=400, detail=("If a normalized query is provided, a unormalized "
                                                     "schema must be provided to transform the query to "
                                                     "its unormalized form."))

    start_time = time.time()
    if req.normalized_query:
        db_pipeline = await get_db_pipeline(req.db_info, cached_schema=req.unormalized_schema)
        query = db_pipeline.normalize_query(req.query)
    else:
        db_pipeline = await get_db_pipeline(req.db_info)

    query_res = db_pipeline.execute_sql_statement(sql_command=req.query, number_rows=req.max_rows, autocommit=req.autocommit)

    return {
        "execution_time": time.time() - start_time,
        "query_result": query_res,
        "executed_query": req.query,
    }

@app.post("/upload-bigquery-key")
async def upload_bigquery_key(
    project_id: str,
    key_file: UploadFile = File(...),
):
    """
    Upload a BigQuery service account key file for a specific project.
    The file will be stored securely and used for BigQuery connections.
    """
    if not key_file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON key files are accepted")
    
    file_path = BIGQUERY_KEYS_DIR / f"{project_id}.json"
    
    try:
        contents = await key_file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save key file: {str(e)}")
    
    return JSONResponse(
        content={"message": f"Successfully uploaded BigQuery key for project {project_id}"},
        status_code=201
    )

@app.get("/bigquery-projects")
async def list_bigquery_projects():
    """
    List all available BigQuery projects (based on uploaded key files).
    """
    try:
        projects = [f.stem for f in BIGQUERY_KEYS_DIR.glob("*.json")]
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")

@app.post("/upload-sqlite-file")
async def upload_sqlite_file(
    database_name: str,
    db_file: UploadFile = File(...),
):
    """
    Upload a SQLite database file.
    The file will be stored and can be used for SQLite connections.
    """
    if not db_file.filename.endswith('.db') and not db_file.filename.endswith('.sqlite'):
        raise HTTPException(status_code=400, detail="Only .db or .sqlite files are accepted")
    
    file_path = SQLITE_FILES_DIR / f"{database_name}.db"
    
    try:
        with file_path.open("wb") as f:
            shutil.copyfileobj(db_file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save database file: {str(e)}")
    
    return JSONResponse(
        content={"message": f"Successfully uploaded SQLite database {database_name}"},
        status_code=201
    )

@app.get("/sqlite-databases")
async def list_sqlite_databases():
    """
    List all available SQLite databases.
    """
    try:
        databases = [f.stem for f in SQLITE_FILES_DIR.glob("*.db")]
        return {"databases": databases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")
