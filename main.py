from fastapi import FastAPI, Query, Path, Depends
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from datetime import datetime

class MusicEntry(BaseModel):
    title : str = Field(description="a title for the search", min_length=1, max_length=50)
    artist: str = Field(description="the artist of the music", min_length=1, max_length=50)
    duration : int = Field(gt=0)
    genre : Literal["Rock", "Pop", "Jazz", "Techno"]
    created_at : datetime = Field(default_factory=datetime.now, description="date of creation")

class MusicSearch(BaseModel):
    title : str | None = Field(default=None, description="the search query", min_length=1, max_length=50)
    filter : Literal["Rock", "Pop", "Jazz", "Techno"] | None = None
    sorted_by : Literal["title", "created_at", "duration"] | None = None
    limit : int = Field(5, gt=0, le=10, description="limit of result")
    offset : int = Field(0, ge=0, description="the offset where to search")
    direction : Literal["asc", "desc"] = "desc"
    duration : int = Field(0, ge=0, description="minimum duration in seconds")

app = FastAPI()

async def search_music_es(params: MusicSearch):
    query = {
        "query": {
            "bool": {
            "must": [],
            "filter": []
            },
        },
        "from": params.offset,
        "size": params.limit,
        "sort": []
    }
    if params.title:
            query["query"]["bool"]["must"].append({
                "match": {
                    "title": params.title
                }
            })
    else:
            query["query"]["bool"]["must"].append({
                "match_all": {}
            })
    if params.filter:
            query["query"]["bool"]["filter"].append({
                "term": {
                    "genre": params.filter
                }
            })
    if params.duration > 0:
            query["query"]["bool"]["filter"].append({
                "range": {
                    "duration": {
                        "gte": params.duration
                    }
                }
            })
    if params.sorted_by:
            query["sort"].append({
                params.sorted_by: {
                    "order": params.direction
                }
            })
    return query # In a real implementation, this would execute the query against Elasticsearch
    

@app.get("/search/")
async def search(params: Annotated[MusicSearch, Depends()]):
    results = await search_music_es(params)
    return results