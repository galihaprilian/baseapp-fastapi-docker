import asyncio
import logging

from app.db.init_db import init_db
from app.db import database, engine, metadata

metadata.create_all(engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> None:
    await database.connect()
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
