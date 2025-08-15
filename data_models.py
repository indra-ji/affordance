from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator


class BaseEntity(BaseModel, frozen=True, strict=True, extra="ignore"):
    name: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")  # Validate semantic versioning
    description: str

    @field_validator("version", mode="before")
    @classmethod
    def normalize_version(cls, text: str) -> str:
        if isinstance(text, str):
            return text.strip()
        return text


class Language(BaseEntity):
    name: Literal["python"]

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, text: str) -> str:
        if isinstance(text, str):
            return text.lower().strip()
        return text


class Library(BaseEntity):
    language: Language

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, text: str) -> str:
        if isinstance(text, str):
            return text.lower().strip()
        return text


class Task(BaseEntity):
    library: Library
    content: str


class Taskset(BaseEntity):
    library: Library
    tasks: tuple[Task, ...]

    @computed_field
    @property
    def size(self) -> int:
        return len(self.tasks)


class Test(BaseEntity):
    task: Task
    content: str


class Testset(BaseEntity):
    taskset: Taskset
    tests: tuple[Test, ...]

    @computed_field
    @property
    def size(self) -> int:
        return len(self.tests)


class Model(BaseEntity):
    provider: Literal["openai"]

    @field_validator("provider", mode="before")
    @classmethod
    def normalize_provider(cls, text: str) -> str:
        if isinstance(text, str):
            return text.lower().strip()
        return text


class Agent(BaseEntity):
    model: Model
    prompt: str
    configuration: str
    scaffolding: str


class Answer(BaseEntity):
    agent: Agent
    task: Task
    content: str


class Answerset(BaseEntity):
    agent: Agent
    taskset: Taskset
    answers: tuple[Answer, ...]

    @computed_field
    @property
    def size(self) -> int:
        return len(self.answers)


class Result(BaseEntity):
    answer: Answer
    test: Test
    passed: bool


class Resultset(BaseEntity):
    taskset: Taskset
    testset: Testset
    answerset: Answerset
    results: tuple[Result, ...]

    @computed_field
    @property
    def size(self) -> int:
        return len(self.results)

    @computed_field
    @property
    def number_passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @computed_field
    @property
    def percentage_passed(self) -> float:
        return (
            (float(self.number_passed) / float(self.size)) * 100.0
            if self.size > 0
            else 0.0
        )


class Evaluation(BaseEntity):
    language: Language
    library: Library
    taskset: Taskset
    testset: Testset
    model: Model
    agent: Agent
    answerset: Answerset
    resultset: Resultset
