from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from tinydb import TinyDB

from src.database import DbClient
from src.services.graphql import GraphQLService

description = """
This API helps you to see Recent Activity of users by ronin address. 🚀

*Example of ronin address: ronin:325f6d8ff8f1bc000b28a006ab3656ad5562f552*
"""
app = FastAPI(
    title="Axie Activity Api",
    description=description,
    version="0.0.1",
    contact={
        "name": "Stefan Kecskes",
        "email": "mr.kecskes@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }, )

items_sold_db = "items_sold.json"


@app.get("/", response_class=HTMLResponse)
async def home():
    return "<html>Visit <a href=\"http://127.0.0.1:8000/docs\">swagger documentation</a></html>"


@app.get("/refresh")
async def refresh_db():
    db = TinyDB(items_sold_db)
    gql_service = GraphQLService(db)
    gql_service.save_recently_items_sold()
    return {"message": "Done"}


@app.get("/activity/{ronin_address}")
async def get_activity(ronin_address: str):
    db = TinyDB(items_sold_db)
    gql_service = GraphQLService(db)
    activities = gql_service.get_activity_of_user(ronin_address)
    return activities


@app.get("/events/{ronin_address}")
async def get_events(ronin_address: str):
    db = DbClient()
    transfers = db.get_transfers(ronin_address)
    return transfers
