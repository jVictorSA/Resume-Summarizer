import asyncio
import logging
from beanie import init_beanie
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import env_config
from models.logs import CVsAnalysisLogs

logger = logging.getLogger(__name__)

class MongoDBManager:
    
    _instance = None
    _lock = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._client: Optional[AsyncIOMotorClient] = None
            self._db: Optional[AsyncIOMotorDatabase] = None
            self._document_models = [CVsAnalysisLogs]
            self._initialized = True
            logger.debug("MongoDBManager initialized")
    
    async def connect(self) -> None:
        if self._lock:
            logger.warning("Connection attempt during initialization")
            return
            
        if self.is_connected:
            logger.info("Database connection already established")
            return
        
        self._lock = True
        try:
            logger.info("Connecting to MongoDB...")
            self._client = AsyncIOMotorClient(
                env_config.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            await self._client.admin.command('ping')
            logger.info("MongoDB connection established")
            
            self._db = self._client[env_config.MONGODB_DB_NAME]

            await init_beanie(
                database=self._db,
                document_models=self._document_models
            )
            
        except Exception as e:
            logger.critical(f"Failed to connect to MongoDB: {str(e)}")
            self._lock = False
            raise
        finally:
            self._lock = False
    
    async def disconnect(self) -> None:
        if not self.is_connected:
            logger.warning("No MongoDB connection to close")
            return
        
        try:
            logger.info("Closing MongoDB connection...")
            self._client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
        finally:
            self._client = None
            self._db = None
    
    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._db is not None
    
    @asynccontextmanager
    async def db_session(self) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
        if not self.is_connected:
            await self.connect()
        
        try:
            yield self._db
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise
    
    def get_db(self) -> AsyncIOMotorDatabase:
        if not self.is_connected:
            raise RuntimeError(
                "Database not initialized. Call connect() during startup."
            )
        return self._db
    
    @classmethod
    def get_db_instance(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls()
        return cls._instance

    @staticmethod
    def initialize_db():
        try:
            db_manager = MongoDBManager.get_db_instance()
            
            if not db_manager.is_connected:
                logger.info("Initializing database connection...")
            
                loop = asyncio.get_event_loop()
                loop.run_until_complete(db_manager.connect())
                logger.info("Database connection established")
            
            return db_manager
        except Exception as e:
            logger.critical(f"Failed to initialize database: {str(e)}")
            raise

    @staticmethod
    def close_db():
        try:
            db_manager = MongoDBManager.get_db_instance()
            if db_manager.is_connected:
            
                loop = asyncio.get_event_loop()
                loop.run_until_complete(db_manager.disconnect())
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")