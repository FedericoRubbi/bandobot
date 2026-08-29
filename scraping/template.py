from abc import ABC, abstractmethod
import logging
import pickle
from pathlib import Path
import hashlib

from bs4 import BeautifulSoup

from paths import base_dir


logger = logging.getLogger(__name__)


class Scraper(ABC):
    def __init__(self) -> None:
        self.name = self.__module__.split(".")[-1].lower()
        self._history = set()
        self._history_path = base_dir() / "data" / "history" / f"{self.name}.pkl"
        if self._history_path.is_file():
            self._load_history()
        else:
            self._create_history()
        self.results = []

    def _create_history(self) -> None:
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        self._history_path.touch()
        self._save_history()

    def _save_history(self) -> None:
        with open(self._history_path, "wb") as file:
            pickle.dump(self._history, file)
        logger.info("Saved %d entries to %s.", len(self._history), self._history_path)

    def _load_history(self) -> None:
        with open(self._history_path, "rb") as file:
            self._history = pickle.load(file)
        logger.info("Loaded %d entries from %s.", len(self._history), self._history_path)

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def update(self) -> None:
        keys = {self._key(r) for r in self.results}
        keys -= self._history
        self._history |= keys
        self.results = [r for r in self.results if self._key(r) in keys]
        self._save_history()

    @staticmethod
    @abstractmethod
    def scrape() -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def format(results: list[str]) -> str:
        pass

    def run(self) -> str | None:
        self.results = self.scrape()
        self.update()
        return None if not self.results else self.format(self.results)
