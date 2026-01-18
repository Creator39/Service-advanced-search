from fastapi import FastAPI, Query, Path
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
    filter : Literal["Rock", "Pop", "Jazz", "Techno"] | None = None
    trie : Literal["title", "created_at"] | None = None
    limit : int = Field(5, gt=0, le=10, description="limit of result")
    offset : int = Field(0, ge=0, description="the offset where to search")
    direction : Literal["asc", "desc"] = "desc"

app = FastAPI()

@app.get("/search/")
async def search(params: Annotated[MusicSearch, Query()]):
    return params    