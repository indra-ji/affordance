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
    content: str


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
    content: str


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
    passed: bool = False


@dataclass()
class Evaluation(BaseEntity):
    taskset: Taskset
    testset: Testset
    answerset: Answerset
    results: list[Result] | None = None

    @property
    def size(self) -> int | None:
        return len(self.results) if self.results else None

    @property
    def number_passed(self) -> int | None:
        if not self.results:
            return None
        return sum(1 for result in self.results if result.passed)

    @property
    def percentage_passed(self) -> float | None:
        if not self.results:
            return None
        return (self.number_passed / self.size) * 100 if self.size else None


@dataclass()
class Benchmark(BaseEntity):
    library: Library
    evaluations: list[Evaluation] | None = None

    @property
    def size(self) -> int | None:
        return len(self.evaluations) if self.evaluations else None

    @property
    def total_size(self) -> int | None:
        return (
            sum(evaluation.size for evaluation in self.evaluations)
            if self.evaluations
            else None
        )

    @property
    def number_passed(self) -> int | None:
        if not self.evaluations:
            return None
        return sum(evaluation.number_passed for evaluation in self.evaluations)

    @property
    def percentage_passed(self) -> float | None:
        if not self.evaluations:
            return None
        return (self.number_passed / self.total_size) * 100 if self.total_size else None
