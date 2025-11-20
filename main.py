import asyncio
from app import main

from config import settings

if __name__ == "__main__":
    asyncio.run(main(settings))
    
