from pydantic import BaseModel, computed_field


class BaseEntity(BaseModel, frozen=True, strict=True, extra="forbid"):
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
    provider: str


class Agent(BaseEntity):
    model: Model
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


class Benchmark(BaseEntity):
    library: Library
    resultsets: tuple[Resultset, ...]

    @computed_field
    @property
    def size(self) -> int:
        return len(self.resultsets)

    @computed_field
    @property
    def total_size(self) -> int:
        return sum(resultset.size for resultset in self.resultsets)

    @computed_field
    @property
    def number_passed(self) -> int:
        return sum(resultset.number_passed for resultset in self.resultsets)

    @computed_field
    @property
    def percentage_passed(self) -> float:
        return (
            (float(self.number_passed) / float(self.total_size)) * 100.0
            if self.total_size > 0
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
    benchmark: Benchmark
