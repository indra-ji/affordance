from classes import Dataset, Language, Library, Task, Test, Testset


def set_library():
    """Set the library to be used"""

    # Set language as python
    language = Language(name="Python", version="3.13")

    # Set library as numpy
    library = Library(language=language, name="Numpy", version="3.2.3")

    return library


def create_dataset(library: Library) -> Dataset:
    """Create the evaluation dataset"""

    # Set dataset
    dataset = Dataset(library=library, name="Test_Dataset", version="1.0.0")

    # Create 10 placeholder tasks
    tasks = [Task(name=f"Task {i}", version="1.0.0", content="") for i in range(10)]
    dataset.tasks = tasks

    return dataset


def create_tests(dataset: Dataset) -> Testset:
    """Create the tests for the dataset"""

    # Extract tasks from dataset
    tasks = dataset.tasks

    # Create testset
    testset = Testset(dataset=dataset)

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


def benchmark():
    """Run benchmark for a given library"""

    library = set_library()
    dataset = create_dataset(library)
    testset = create_tests(dataset)

    return testset


if __name__ == "__main__":
    print(benchmark())
