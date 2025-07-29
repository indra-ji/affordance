from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Language:
    name: str
    version: str


@dataclass
class Library:
    language: Language
    name: str
    version: str
    description: Optional[str] = None


@dataclass
class Task:
    name: str
    version: str
    content: str
    description: Optional[str] = None


@dataclass
class Dataset:
    library: Library
    name: str
    version: str
    tasks: Optional[List[Task]] = None
    description: Optional[str] = None


@dataclass
class Test:
    task: Task
    name: str
    version: str
    content: str
    description: Optional[str] = None


@dataclass
class Testset:
    dataset: Dataset
    tests: Optional[List[Test]] = None
