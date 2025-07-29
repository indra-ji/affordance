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


def set_library() -> Library:
    """Set the library to be used"""

    # Set language as python
    language = Language(
        name="Python", version="3.13", description="Latest version of Python"
    )

    # Set library as numpy
    library = Library(
        name="Numpy",
        version="3.2.3",
        description="Numpy is a library for numerical computing with Python.",
        language=language,
    )

    return library


def create_taskset(library: Library) -> Taskset:
    """Create the evaluation dataset"""

    # Set dataset
    taskset = Taskset(
        name="Test_Dataset",
        version="1.0.0",
        description="Test dataset with basic operations",
        library=library,
    )

    number_tasks = 10

    # Create 10 placeholder tasks
    tasks = [
        Task(
            name=f"Task_{i}",
            version="1.0.0",
            description=f"Placeholder description for task {i}",
            content="Placeholder content for task {i}",
            library=library,
        )
        for i in range(number_tasks)
    ]

    taskset.tasks = tasks

    return taskset


def create_testset(taskset: Taskset) -> Testset:
    """Create the tests for the dataset"""

    # Extract tasks from dataset
    tasks = taskset.tasks

    # Create testset
    testset = Testset(
        name="Test_Testset",
        version="1.0.0",
        description="Testset with placeholder tests",
        taskset=taskset,
    )

    # Create placeholder tests
    tests = [
        Test(
            name=f"Test_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for test {task.name}",
            task=task,
        )
        for task in tasks
    ]

    testset.tests = tests

    return testset


def set_agent() -> Agent:
    """Set the agent to be used"""

    # Set model
    model = Model(
        name="GPT-4o",
        provider="OpenAI",
        version="1.0.0",
        description="GPT-4o is a large language model developed by OpenAI.",
    )

    # Set agent
    agent = Agent(
        model=model,
        name="GPT-4o-vanilla-agent",
        version="1.0.0",
        description="GPT-4o-vanilla-agent is a vanilla agent that uses GPT-4o as its model.",
    )

    return agent


def benchmark():
    """Run benchmark for a given library"""

    library = set_library()
    taskset = create_taskset(library)
    testset = create_testset(taskset)
    agent = set_agent()

    return library, taskset, testset, agent


if __name__ == "__main__":
    library, taskset, testset, agent = benchmark()

    pprint(library)
    pprint(taskset)
    print(f"Taskset size: {taskset.size}")
    pprint(testset)
    print(f"Testset size: {testset.size}")
    pprint(agent)
