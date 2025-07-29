from dataclasses import dataclass


@dataclass()
class BaseEntity:
    name: str
    version: str
    description: str


@dataclass()
class Language(BaseEntity):
    pass


@dataclass()
class Library(BaseEntity):
    language: Language


@dataclass()
class Task(BaseEntity):
    library: Library
    content: str


@dataclass()
class Taskset(BaseEntity):
    library: Library
    tasks: list[Task] | None = None

    @property
    def size(self) -> int | None:
        return len(self.tasks) if self.tasks else None


@dataclass()
class Test(BaseEntity):
    task: Task


@dataclass()
class Testset(BaseEntity):
    taskset: Taskset
    tests: list[Test] | None = None

    @property
    def size(self) -> int | None:
        return len(self.tests) if self.tests else None


@dataclass()
class Model(BaseEntity):
    provider: str


@dataclass()
class Agent(BaseEntity):
    model: Model
    configuration: str | None = None
    scaffolding: str | None = None


@dataclass()
class Answer(BaseEntity):
    agent: Agent
    task: Task


@dataclass()
class Answerset(BaseEntity):
    agent: Agent
    taskset: Taskset
    answers: list[Answer] | None = None

    @property
    def size(self) -> int | None:
        return len(self.answers) if self.answers else None


@dataclass()
class Result(BaseEntity):
    answer: Answer
    test: Test


@dataclass()
class Evaluation(BaseEntity):
    taskset: Taskset
    testset: Testset
    answerset: Answerset
    results: list[Result] | None = None


@dataclass()
class Benchmark(BaseEntity):
    library: Library
    evaluations: list[Evaluation] | None = None
