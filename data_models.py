from pydantic import BaseModel, ConfigDict, computed_field


class BaseEntity(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    version: str
    description: str


class Language(BaseEntity):
    pass


class Library(BaseEntity):
    language: Language


class Task(BaseEntity):
    library: Library
    content: str


class Taskset(BaseEntity):
    library: Library
    tasks: list[Task] | None = None

    @computed_field
    @property
    def size(self) -> int | None:
        return len(self.tasks) if self.tasks else None


class Test(BaseEntity):
    task: Task
    content: str


class Testset(BaseEntity):
    taskset: Taskset
    tests: list[Test] | None = None

    @computed_field
    @property
    def size(self) -> int | None:
        return len(self.tests) if self.tests else None


class Model(BaseEntity):
    provider: str


class Agent(BaseEntity):
    model: Model
    configuration: str | None = None
    scaffolding: str | None = None


class Answer(BaseEntity):
    agent: Agent
    task: Task
    content: str


class Answerset(BaseEntity):
    agent: Agent
    taskset: Taskset
    answers: list[Answer] | None = None

    @computed_field
    @property
    def size(self) -> int | None:
        return len(self.answers) if self.answers else None


class Result(BaseEntity):
    answer: Answer
    test: Test
    passed: bool = False


class Resultset(BaseEntity):
    taskset: Taskset
    testset: Testset
    answerset: Answerset
    results: list[Result] | None = None

    @computed_field
    @property
    def size(self) -> int | None:
        return len(self.results) if self.results else None

    @computed_field
    @property
    def number_passed(self) -> int | None:
        if not self.results:
            return None
        return sum(1 for result in self.results if result.passed)

    @computed_field
    @property
    def percentage_passed(self) -> float | None:
        if not self.results:
            return None
        return (
            (float(self.number_passed) / float(self.size)) * 100.0
            if self.size
            else None
        )


class Benchmark(BaseEntity):
    library: Library
    resultsets: list[Resultset] | None = None

    @computed_field
    @property
    def size(self) -> int | None:
        return len(self.resultsets) if self.resultsets else None

    @computed_field
    @property
    def total_size(self) -> int | None:
        return (
            sum(resultset.size for resultset in self.resultsets)
            if self.resultsets
            else None
        )

    @computed_field
    @property
    def number_passed(self) -> int | None:
        if not self.resultsets:
            return None
        return sum(resultset.number_passed for resultset in self.resultsets)

    @computed_field
    @property
    def percentage_passed(self) -> float | None:
        if not self.resultsets:
            return None
        return (
            (float(self.number_passed) / float(self.total_size)) * 100.0
            if self.total_size
            else None
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
    benchmark: Benchmark
