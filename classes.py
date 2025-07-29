from dataclasses import dataclass


@dataclass
class Language:
    name: str
    version: str


@dataclass
class Library:
    language: Language
    name: str
    version: str
    description: str | None = None


@dataclass
class Task:
    name: str
    version: str
    content: str
    description: str | None = None


@dataclass
class Taskset:
    library: Library
    name: str
    version: str
    tasks: list[Task] | None = None
    description: str | None = None


@dataclass
class Test:
    task: Task
    name: str
    version: str
    content: str
    description: str | None = None


@dataclass
class Testset:
    taskset: Taskset
    tests: list[Test] | None = None


@dataclass
class Model:
    name: str
    provider: str
    version: str
    description: str | None = None


@dataclass
class Agent:
    model: Model
    name: str
    version: str
    configuration: str | None = None
    scaffolding: str | None = None
    description: str | None = None
