from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger


class BaseCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, name: str):
        self.name = name
        self.last_collection: Optional[datetime] = None
        self.logger = logger.getChild(name)

    @abstractmethod
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect data from the source. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def validate(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate collected data. Must be implemented by subclasses."""
        pass

    async def run(self, **kwargs) -> List[Dict[str, Any]]:
        """Execute collection pipeline: collect -> validate -> return."""
        self.logger.info(f"Starting data collection: {self.name}")
        try:
            raw_data = await self.collect(**kwargs)
            validated = await self.validate(raw_data)
            self.last_collection = datetime.utcnow()
            self.logger.info(f"Collected {len(validated)} items from {self.name}")
            return validated
        except Exception as e:
            self.logger.error(f"Collection failed for {self.name}: {e}")
            raise
