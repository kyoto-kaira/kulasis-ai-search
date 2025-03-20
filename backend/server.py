import json
import traceback
from typing import List, Optional

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.pipeline import Pipelines

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Course(BaseModel):
    id: str
    code: str
    title: str
    department: str
    instructor: str
    semester: str
    enrollment_count: int
    rating: float
    difficulty_rating: float
    content_rating: float
    reviews: int


class SearchParams(BaseModel):
    year: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    semester: Optional[str] = None
    days: Optional[List[str]] = None
    periods: Optional[List[str]] = None
    course_name: Optional[str] = None
    instructor: Optional[str] = None
    query: Optional[str] = None


@app.get("/ping")
def ping() -> Response:
    response = Response(
        content="ping",
        status_code=status.HTTP_200_OK,
        media_type="text/plain",
    )
    return response


@app.post("/invocations")
def search_courses(params: SearchParams) -> Response:
    try:
        config = {
            "data": {"input_dir": "data/raw"},
            "summary": {
                "summary_dir": "data/summary",
                "summary_name": "summary_data.json",
            },
            "index": {
                "index_dir": "data/index_selected",
                "embedding_name": "faiss_index.bin",
                "processed_data_name": "processed_data.json",
            },
            "preprocessing": {
                "method": "simple_selected",
                "chunk_size": 512,
                "normalization": True,
            },
            "embedding": {
                "method": "e5",
                "model": "intfloat/multilingual-e5-small",
                "batch_size": 32,
            },
            "search": {
                "method": "simple",
                "top_k": 10,
                "metadata_filter": {},
            },
            "reranking": {"method": "bge", "model": "BAAI/bge-reranker-large"},
            "queries": [params.query if params.query else ""],
        }

        if params.department:
            config["search"]["metadata_filter"] = {"department": params.department}

        pipelines = Pipelines(config)
        cources = pipelines()
        response = Response(
            content=json.dumps(cources, default=str, ensure_ascii=False, indent=4),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )

    except Exception:
        exc = traceback.format_exc()
        contents = {"error": exc}
        print(exc)
        contents_json = json.dumps(contents, default=str, ensure_ascii=False, indent=4)
        response = Response(
            content=contents_json,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/json",
        )

    return response


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
