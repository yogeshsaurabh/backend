import logging

from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings

from .mongodb import db


async def connect_to_mongo():
    logging.info("db-open: connecting to mongodb...")
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
    )
    logging.info("db-open: mongodb connected")


async def close_mongo_connection():
    logging.info("db-close: disconnecting from mongodb...")
    db.client.close()
    logging.info("db-close: mongodb disconnected")
