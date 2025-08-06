import datetime
import sys

from data_models import (
    Agent,
    Answer,
    Answerset,
    Benchmark,
    Evaluation,
    Language,
    Library,
    Model,
    Result,
    Resultset,
    Task,
    Taskset,
    Test,
    Testset,
)
from json_utils import deserialize_data_model, serialize_data_model


def create_language() -> Language:
    language = Language(
        name="Python",
        version="3.13",
        description="Latest version of Python",
    )

    return language


def load_language(evaluation: Evaluation) -> Language:
    language = evaluation.language

    return language


def create_library(language: Language) -> Library:
    library = Library(
        name="Numpy",
        version="3.2.3",
        description="Numpy is a library for numerical computing.",
        language=language,
    )

    return library


def load_library(evaluation: Evaluation) -> Library:
    library = evaluation.library

    return library


def create_taskset(library: Library) -> Taskset:
    NUMBER_TASKS = 10

    tasks = tuple(
        Task(
            name=f"Task_{i}",
            version="1.0.0",
            description=f"Placeholder description for task {i}",
            library=library,
            content=f"Placeholder content for task {i}",
        )
        for i in range(1, NUMBER_TASKS + 1)
    )

    taskset = Taskset(
        name="demo_taskset",
        version="1.0.0",
        description="Test dataset with basic operations",
        library=library,
        tasks=tasks,
    )

    return taskset


def load_taskset(evaluation: Evaluation) -> Taskset:
    taskset = evaluation.taskset

    return taskset


def create_testset(taskset: Taskset) -> Testset:
    tasks = taskset.tasks

    tests = tuple(
        Test(
            name=f"Test_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for test {task.name}",
            task=task,
            content=f"Placeholder content for test {task.name}",
        )
        for task in tasks
    )

    testset = Testset(
        name="demo_testset",
        version="1.0.0",
        description="Testset with placeholder tests",
        taskset=taskset,
        tests=tests,
    )

    return testset


def load_testset(evaluation: Evaluation) -> Testset:
    testset = evaluation.testset

    return testset


def create_model() -> Model:
    model = Model(
        name="GPT-4o",
        version="1.0.0",
        description="Daily use model",
        provider="OpenAI",
    )

    return model


def load_model(evaluation: Evaluation) -> Model:
    model = evaluation.model

    return model


def create_agent(model: Model) -> Agent:
    agent = Agent(
        name="vanilla-agent",
        version="1.0.0",
        description="Vanilla agent that calls the model.",
        model=model,
        configuration="Default configuration",
        scaffolding="No scaffolding",
    )

    return agent


def load_agent(evaluation: Evaluation) -> Agent:
    agent = evaluation.agent

    return agent


def create_answerset(agent: Agent, taskset: Taskset) -> Answerset:
    tasks = taskset.tasks

    answers = tuple(
        Answer(
            name=f"Answer_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for answer {task.name}",
            agent=agent,
            task=task,
            content=f"Placeholder content for answer {task.name}",
        )
        for task in tasks
    )

    answerset = Answerset(
        name="demo_answerset",
        version="1.0.0",
        description="Answerset with placeholder answers",
        agent=agent,
        taskset=taskset,
        answers=answers,
    )

    return answerset


def load_answerset(evaluation: Evaluation) -> Answerset:
    answerset = evaluation.answerset

    return answerset


def create_resultset(
    taskset: Taskset, testset: Testset, answerset: Answerset
) -> Resultset:
    tasks = taskset.tasks
    tests = testset.tests
    answers = answerset.answers

    results = tuple(
        Result(
            name=f"Result_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for result {task.name}",
            answer=answer,
            test=test,
            passed=False,
        )
        for task, answer, test in zip(tasks, answers, tests)
    )

    resultset = Resultset(
        name="demo_resultset",
        version="1.0.0",
        description="Resultset with placeholder results",
        taskset=taskset,
        testset=testset,
        answerset=answerset,
        results=results,
    )

    return resultset


def load_resultset(evaluation: Evaluation) -> Resultset:
    resultset = evaluation.resultset

    return resultset


def create_benchmark(library: Library, resultsets: tuple[Resultset, ...]) -> Benchmark:
    benchmark = Benchmark(
        name="demo_benchmark",
        version="1.0.0",
        description="Benchmark with placeholder resultsets",
        library=library,
        resultsets=resultsets,
    )

    return benchmark


def load_benchmark(evaluation: Evaluation) -> Benchmark:
    benchmark = evaluation.benchmark

    return benchmark


def create_evaluation() -> Evaluation:
    language = create_language()
    library = create_library(language)
    taskset = create_taskset(library)
    testset = create_testset(taskset)
    model = create_model()
    agent = create_agent(model)
    answerset = create_answerset(agent, taskset)
    resultset = create_resultset(taskset, testset, answerset)
    benchmark = create_benchmark(library, (resultset,))

    evaluation = Evaluation(
        name="demo_evaluation",
        version="1.0.0",
        description="Test benchmark evaluation with all components",
        language=language,
        library=library,
        taskset=taskset,
        testset=testset,
        model=model,
        agent=agent,
        answerset=answerset,
        resultset=resultset,
        benchmark=benchmark,
    )
    return evaluation


def load_evaluation(input_path: str) -> Evaluation:
    evaluation = deserialize_data_model(input_path, Evaluation)

    language = load_language(evaluation)
    library = load_library(evaluation)
    taskset = load_taskset(evaluation)
    testset = load_testset(evaluation)
    model = load_model(evaluation)
    agent = load_agent(evaluation)
    answerset = load_answerset(evaluation)
    resultset = load_resultset(evaluation)
    benchmark = load_benchmark(evaluation)

    evaluation = Evaluation(
        name=evaluation.name,
        version=evaluation.version,
        description=evaluation.description,
        language=language,
        library=library,
        taskset=taskset,
        testset=testset,
        model=model,
        agent=agent,
        answerset=answerset,
        resultset=resultset,
        benchmark=benchmark,
    )
    return evaluation


def rerun_evaluation(input_path: str) -> Evaluation:
    evaluation = deserialize_data_model(input_path, Evaluation)

    language = load_language(evaluation)
    library = load_library(evaluation)
    taskset = load_taskset(evaluation)
    testset = load_testset(evaluation)
    model = load_model(evaluation)
    agent = load_agent(evaluation)
    answerset = create_answerset(agent, taskset)
    resultset = create_resultset(taskset, testset, answerset)
    benchmark = create_benchmark(library, (resultset,))

    evaluation = Evaluation(
        name=evaluation.name,
        version=evaluation.version,
        description=evaluation.description,
        language=language,
        library=library,
        taskset=taskset,
        testset=testset,
        model=model,
        agent=agent,
        answerset=answerset,
        resultset=resultset,
        benchmark=benchmark,
    )
    return evaluation


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["--create"]:
            evaluation = create_evaluation()
        case ["--load", input_path]:
            evaluation = load_evaluation(input_path)
        case ["--rerun", input_path]:
            evaluation = rerun_evaluation(input_path)
        case _:
            raise Exception(
                "Usage: python evaluation.py --create OR python evaluation.py --load <input_path> OR python evaluation.py --rerun <input_path>"
            )

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{evaluation.name}_{timestamp}.json"
    serialize_data_model(evaluation, output_path)
