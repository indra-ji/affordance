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
    language = Language(name="Python", version="3.13")

    # Set library as numpy
    library = Library(language=language, name="Numpy", version="3.2.3")

    return library


def create_taskset(library: Library) -> Taskset:
    """Create the evaluation dataset"""

    # Set dataset
    taskset = Taskset(library=library, name="Test_Dataset", version="1.0.0")

    # Create 10 placeholder tasks
    tasks = [Task(name=f"Task_{i}", version="1.0.0", content="") for i in range(10)]
    taskset.tasks = tasks

    return taskset


def create_testset(taskset: Taskset) -> Testset:
    """Create the tests for the dataset"""

    # Extract tasks from dataset
    tasks = taskset.tasks

    # Create testset
    testset = Testset(taskset=taskset)

    # Create 10 placeholder tests
    tests = [
        Test(
            task=task,
            name=f"Test_{task.name}",
            version="1.0.0",
            content="",
        )
        for task in tasks
    ]

    testset.tests = tests

    return testset


def set_agent() -> Agent:
    """Set the agent to be used"""

    # Set model
    model = Model(name="GPT-4o", provider="OpenAI", version="1.0.0")

    # Set agent
    agent = Agent(model=model, name="GPT-4o-vanilla-agent", version="1.0.0")

    return agent


def benchmark():
    """Run benchmark for a given library"""

    library = set_library()
    taskset = create_taskset(library)
    testset = create_testset(taskset)
    agent = set_agent()

    return library, taskset, testset, agent


if __name__ == "__main__":
    pprint(benchmark())
