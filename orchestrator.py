from pprint import pprint

from classes import (
    Agent,
    Language,
    Library,
    Model,
    Task,
    Taskset,
    Test,
    Testset,
)


def create_library() -> Library:
    language = Language(
        name="Python", version="3.13", description="Latest version of Python"
    )

    library = Library(
        name="Numpy",
        version="3.2.3",
        description="Numpy is a library for numerical computing.",
        language=language,
    )

    return library


def create_taskset(library: Library) -> Taskset:
    taskset = Taskset(
        name="Test_Dataset",
        version="1.0.0",
        description="Test dataset with basic operations",
        library=library,
    )

    number_tasks = 10

    tasks = [
        Task(
            name=f"Task_{i}",
            version="1.0.0",
            description=f"Placeholder description for task {i}",
            library=library,
            content="Placeholder content for task {i}",
        )
        for i in range(number_tasks)
    ]

    taskset.tasks = tasks

    return taskset


def create_testset(taskset: Taskset) -> Testset:
    testset = Testset(
        name="Test_Testset",
        version="1.0.0",
        description="Testset with placeholder tests",
        taskset=taskset,
    )

    tasks = taskset.tasks

    tests = [
        Test(
            name=f"Test_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for test {task.name}",
            task=task,
            content="Placeholder content for test {task.name}",
        )
        for task in tasks
    ]

    testset.tests = tests

    return testset


def create_agent() -> Agent:
    model = Model(
        name="GPT-4o",
        version="1.0.0",
        description="Daily use model",
        provider="OpenAI",
    )

    agent = Agent(
        name="vanilla-agent",
        version="1.0.0",
        description="Vanilla agent that calls the model.",
        model=model,
    )

    return agent


def run():
    library = create_library()
    taskset = create_taskset(library)
    testset = create_testset(taskset)
    agent = create_agent()

    return library, taskset, testset, agent


if __name__ == "__main__":
    library, taskset, testset, agent = run()

    pprint(library)
    pprint(taskset)
    print(f"Taskset size: {taskset.size}")
    pprint(testset)
    print(f"Testset size: {testset.size}")
    pprint(agent)
