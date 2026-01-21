from fastapi import FastAPI, Query, Path, Depends
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
import aio_pika
import json

class MusicEntry(BaseModel):
    title : str = Field(description="a title for the search", min_length=1, max_length=50)
    artist: str = Field(description="the artist of the music", min_length=1, max_length=50)
    duration : int = Field(gt=0)
    genre : Literal["Rock", "Pop", "Jazz", "Techno"]
    created_at : datetime = Field(default_factory=datetime.now, description="date of creation")

class MusicSearch(BaseModel):
    title : str | None = Field(default=None, description="the search query", min_length=1, max_length=50)
    filter : Literal["Rock", "Pop", "Jazz", "Techno"] | None = None
    sorted_by : Literal["title", "created_at", "duration", "Playlists"] | None = None
    limit : int = Field(5, gt=0, le=10, description="limit of result")
    offset : int = Field(0, ge=0, description="the offset where to search")
    direction : Literal["asc", "desc"] = "desc"
    duration : int = Field(0, ge=0, description="minimum duration in seconds")

# Client Elasticsearch global
es: AsyncElasticsearch | None = None

async def save_music_es(message: aio_pika.IncomingMessage):
    async with message.process():
        body = message.body.decode()
        data = json.loads(body)
        print(f"Received message: {data}")
        
        # Convertir en MusicEntry pour validation
        music = MusicEntry(**data)
        document = music.model_dump()
        
        response = await es.index(index="music", document=document)
        print(f"Indexed in ES: {response['_id']}")
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: créer la connexion
    try:
        global es
        es = AsyncElasticsearch(hosts=["http://localhost:9200"])
        
        # Créer l'index "music" s'il n'existe pas
        if not await es.indices.exists(index="music"):
            await es.indices.create(
                index="music",
                mappings={
                    "properties": {
                        "title": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "artist": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "duration": {"type": "integer"},
                        "genre": {"type": "keyword"},
                        "created_at": {"type": "date"}
                    }
                }
            )
            print("Index 'music' créé avec succès")
        else:
            print("Index 'music' existe déjà")
        
        # Connexion RabbitMQ asynchrone
        connection = await aio_pika.connect_robust(
            "amqp://admin:admin@localhost:5672/"
        )
        channel = await connection.channel()
        queue = await channel.declare_queue("music_data", durable=False)
        
        # Consommer les messages
        await queue.consume(save_music_es)
        print("RabbitMQ consumer started")
    except Exception as e:
        print(f"Error during startup: {e}")
    
    yield
    
    # Shutdown: fermer les connexions
    try:
        await connection.close()
    except:
        pass
    if es:
        await es.close()
    print("Connections closed")

app = FastAPI(lifespan=lifespan)

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
            # Utiliser .keyword pour les champs text
            sort_field = params.sorted_by
            if params.sorted_by == "title":
                sort_field = "title.keyword"
            query["sort"].append({
                sort_field: {
                    "order": params.direction
                }
            })
    
    response = await es.search(index="music", body=query)
    return response["hits"]["hits"]

    

@app.get("/search/")
async def search(params: Annotated[MusicSearch, Depends()]):
    results = await search_music_es(params)
    return results

# Example of expected payload for track.created event
#{
#  "event": "track.created",
#  "data": {
#    "id": "123",
#    "title": "Bohemian Rhapsody",
#    "artist": "Queen",
#    "duration": 354,
#    "genre": "Rock"
#  }
#}
