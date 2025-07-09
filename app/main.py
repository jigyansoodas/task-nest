from urllib.request import Request

from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from fastapi import FastAPI
from app.database import SessionLocal
from app.resolvers import query, mutation

app = FastAPI()

async def get_context_value(request: Request):
    db = SessionLocal()
    return {
        "request": request,
        "db": db
    }

type_defs = load_schema_from_path("app/schema.graphql")
schema = make_executable_schema(type_defs, [query, mutation])
graphql_app = GraphQL(
    schema,
    context_value=get_context_value
)

app.mount("/graphql", graphql_app)