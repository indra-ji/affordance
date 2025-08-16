import asyncio
import sys

from data_models import (
    Agent,
    Answer,
    Answerset,
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
from llm import generate_answer
from tester import generate_result
from utils import (
    deserialize_data_model,
    deserialize_dict,
    find_config_file,
    generate_evaluation_output_path,
    serialize_data_model,
)


def create_language(configs_dir: str) -> Language:
    language = deserialize_data_model(configs_dir, Language)
    return language


def create_library(configs_dir: str, language: Language) -> Library:
    library_dict = deserialize_dict(configs_dir)

    library = Library(
        name=library_dict["name"],
        version=library_dict["version"],
        description=library_dict["description"],
        language=language,
    )

    return library


def create_taskset(configs_dir: str, library: Library) -> Taskset:
    taskset_dict = deserialize_dict(configs_dir)

    tasks = tuple(
        Task(
            name=task_dict["name"],
            version=task_dict["version"],
            description=task_dict["description"],
            library=library,
            content=task_dict["content"],
        )
        for task_dict in taskset_dict["tasks"]
    )

    taskset = Taskset(
        name=taskset_dict["name"],
        version=taskset_dict["version"],
        description=taskset_dict["description"],
        library=library,
        tasks=tasks,
    )
    return taskset


def create_testset(configs_dir: str, taskset: Taskset) -> Testset:
    testset_dict = deserialize_dict(configs_dir)
    tasks = taskset.tasks

    tests = tuple(
        Test(
            name=test_dict["name"],
            version=test_dict["version"],
            description=test_dict["description"],
            task=task,
            content=test_dict["content"],
        )
        for test_dict, task in zip(testset_dict["tests"], tasks)
    )

    testset = Testset(
        name=testset_dict["name"],
        version=testset_dict["version"],
        description=testset_dict["description"],
        taskset=taskset,
        tests=tests,
    )

    return testset


def create_model(configs_dir: str) -> Model:
    model = deserialize_data_model(configs_dir, Model)

    return model


def create_agent(configs_dir: str, model: Model) -> Agent:
    agent_dict = deserialize_dict(configs_dir)

    agent = Agent(
        name=agent_dict["name"],
        version=agent_dict["version"],
        description=agent_dict["description"],
        model=model,
        prompt=agent_dict["prompt"],
        configuration=agent_dict["configuration"],
        scaffolding=agent_dict["scaffolding"],
    )

    return agent


async def create_answerset(agent: Agent, taskset: Taskset) -> Answerset:
    tasks = taskset.tasks

    # Run all API calls concurrently, preserving order
    contents = await asyncio.gather(*[generate_answer(agent, task) for task in tasks])

    # Build answers with results in same order as tasks
    answers = tuple(
        Answer(
            name=f"Answer for {task.name}",
            version="1.0.0",
            description=f"Answer generated for {task.name} using {agent.name} and {agent.model.name}",
            agent=agent,
            task=task,
            content=content,
        )
        for task, content in zip(tasks, contents)
    )

    answerset = Answerset(
        name=f"Answerset for {taskset.name}",
        version="1.0.0",
        description=f"Answerset for {taskset.name} using {agent.name} and {agent.model.name}",
        agent=agent,
        taskset=taskset,
        answers=answers,
    )

    return answerset


def create_resultset(
    taskset: Taskset, testset: Testset, answerset: Answerset
) -> Resultset:
    tasks = taskset.tasks
    tests = testset.tests
    answers = answerset.answers

    results = tuple(
        Result(
            name=f"Result for {task.name}",
            version="1.0.0",
            description=f"Result for {task.name} using {test.name} and {answer.name}",
            answer=answer,
            test=test,
            passed=generate_result(answer, test),
        )
        for task, answer, test in zip(tasks, answers, tests)
    )

    resultset = Resultset(
        name=f"Resultset for {answerset.name}",
        version="1.0.0",
        description=f"Resultset for {answerset.name} using {taskset.name} and {testset.name}",
        taskset=taskset,
        testset=testset,
        answerset=answerset,
        results=results,
    )

    return resultset


def create_evaluation(configs_dir: str) -> Evaluation:
    language = create_language(
        configs_dir=find_config_file(configs_dir, "language_*.json")
    )
    library = create_library(
        configs_dir=find_config_file(configs_dir, "library_*.json"),
        language=language,
    )
    taskset = create_taskset(
        configs_dir=find_config_file(configs_dir, "taskset_*.json"),
        library=library,
    )
    testset = create_testset(
        configs_dir=find_config_file(configs_dir, "testset_*.json"),
        taskset=taskset,
    )
    model = create_model(configs_dir=find_config_file(configs_dir, "model_*.json"))
    agent = create_agent(
        configs_dir=find_config_file(configs_dir, "agent_*.json"), model=model
    )
    answerset = asyncio.run(create_answerset(agent, taskset))
    resultset = create_resultset(taskset, testset, answerset)

    evaluation = Evaluation(
        name=f"Evaluation for {library.name}",
        version="1.0.0",
        description=f"Evaluation for {library.name} using {taskset.name} and {testset.name}",
        language=language,
        library=library,
        taskset=taskset,
        testset=testset,
        model=model,
        agent=agent,
        answerset=answerset,
        resultset=resultset,
    )
    return evaluation


def rerun_evaluation(eval_path: str) -> Evaluation:
    evaluation = deserialize_data_model(eval_path, Evaluation)

    name = evaluation.name
    version = evaluation.version
    description = evaluation.description
    language = evaluation.language
    library = evaluation.library
    taskset = evaluation.taskset
    testset = evaluation.testset
    model = evaluation.model
    agent = evaluation.agent

    answerset = asyncio.run(create_answerset(agent, taskset))
    resultset = create_resultset(taskset, testset, answerset)

    evaluation = Evaluation(
        name=name,
        version=version,
        description=description,
        language=language,
        library=library,
        taskset=taskset,
        testset=testset,
        model=model,
        agent=agent,
        answerset=answerset,
        resultset=resultset,
    )

    return evaluation


def load_evaluation(eval_path: str) -> Evaluation:
    evaluation = deserialize_data_model(eval_path, Evaluation)

    return evaluation


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["--create", configs_dir]:
            evaluation = create_evaluation(configs_dir)
            output_path = generate_evaluation_output_path(
                evaluation.name, evaluation.model.name
            )
            serialize_data_model(output_path, evaluation)
        case ["--rerun", eval_path]:
            evaluation = rerun_evaluation(eval_path)
            output_path = generate_evaluation_output_path(
                evaluation.name, evaluation.model.name
            )
            serialize_data_model(output_path, evaluation)
        case ["--load", eval_path]:
            evaluation = load_evaluation(eval_path)
            output_path = generate_evaluation_output_path(
                evaluation.name, evaluation.model.name
            )
        case _:
            raise Exception(
                "Usage: python evaluation.py --create <configs_dir> OR python evaluation.py --rerun <eval_path> OR python evaluation.py --load <eval_path>"
            )
