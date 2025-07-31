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


def create_library() -> [Language, Library]:
    language = Language(
        name="Python",
        version="3.13",
        description="Latest version of Python",
    )

    library = Library(
        name="Numpy",
        version="3.2.3",
        description="Numpy is a library for numerical computing.",
        language=language,
    )

    return language, library


def create_taskset(library: Library) -> Taskset:
    taskset = Taskset(
        name="Test_Dataset",
        version="1.0.0",
        description="Test dataset with basic operations",
        library=library,
    )

    NUMBER_TASKS = 10

    tasks = [
        Task(
            name=f"Task_{i}",
            version="1.0.0",
            description=f"Placeholder description for task {i}",
            library=library,
            content="Placeholder content for task {i}",
        )
        for i in range(NUMBER_TASKS)
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


def create_agent() -> [Model, Agent]:
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

    return model, agent


def create_answerset(agent: Agent, taskset: Taskset) -> Answerset:
    answerset = Answerset(
        name="Test_Answerset",
        version="1.0.0",
        description="Answerset with placeholder answers",
        agent=agent,
        taskset=taskset,
    )

    tasks = taskset.tasks

    answers = [
        Answer(
            name=f"Answer_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for answer {task.name}",
            agent=agent,
            task=task,
            content=f"Placeholder content for answer {task.name}",
        )
        for task in tasks
    ]

    answerset.answers = answers

    return answerset


def create_resultset(
    taskset: Taskset, testset: Testset, answerset: Answerset
) -> Resultset:
    resultset = Resultset(
        name="Test_Resultset",
        version="1.0.0",
        description="Resultset with placeholder results",
        taskset=taskset,
        testset=testset,
        answerset=answerset,
    )

    tasks = taskset.tasks
    tests = testset.tests
    answers = answerset.answers

    results = [
        Result(
            name=f"Result_{task.name}",
            version="1.0.0",
            description=f"Placeholder description for result {task.name}",
            answer=answer,
            test=test,
            passed=False,
        )
        for task, answer, test in zip(tasks, answers, tests)
    ]

    resultset.results = results

    return resultset


def create_benchmark(library: Library, resultsets: list[Resultset]) -> Benchmark:
    benchmark = Benchmark(
        name="Test_Benchmark",
        version="1.0.0",
        description="Benchmark with placeholder resultsets",
        library=library,
        resultsets=resultsets,
    )

    return benchmark


def create_evaluation() -> Evaluation:
    language, library = create_library()
    taskset = create_taskset(library)
    testset = create_testset(taskset)
    model, agent = create_agent()
    answerset = create_answerset(agent, taskset)
    resultset = create_resultset(taskset, testset, answerset)
    benchmark = create_benchmark(library, [resultset])

    evaluation = Evaluation(
        name="Test_Evaluation",
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


if __name__ == "__main__":
    evaluation = create_evaluation()
