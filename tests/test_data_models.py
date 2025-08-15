"""Smoke tests for affordance evaluation framework"""

# Import the actual application modules
import pytest

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
from evaluation import (
    create_agent,
    create_language,
    create_library,
    create_model,
    create_taskset,
    create_testset,
)
from utils import find_config_file


class TestDataModels:
    """Smoke tests for all data models - test creation and all properties"""

    def test_language_creation_and_properties(self):
        """Test Language creation and all properties"""
        language = Language(
            name="Python",
            version="3.13",
            description="Python programming language",
        )
        assert language.name == "Python"
        assert language.version == "3.13"
        assert language.description == "Python programming language"

    def test_library_creation_and_properties(self):
        """Test Library creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="Numerical computing library",
            language=language,
        )
        assert library.name == "NumPy"
        assert library.version == "2.0.0"
        assert library.description == "Numerical computing library"
        assert library.language == language
        assert library.language.name == "Python"

    def test_model_creation_and_properties(self):
        """Test Model creation and all properties"""
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="OpenAI GPT-4 model",
            provider="openai",
        )
        assert model.name == "gpt-4"
        assert model.version == "1.0.0"
        assert model.description == "OpenAI GPT-4 model"
        assert model.provider == "openai"

    def test_agent_creation_and_properties(self):
        """Test Agent creation and all properties"""
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="CodingAgent",
            version="2.0.0",
            description="AI coding assistant",
            model=model,
            prompt="You are a helpful coding assistant",
            configuration="temperature=0.1, max_tokens=1000",
            scaffolding="basic python environment",
        )
        assert agent.name == "CodingAgent"
        assert agent.version == "2.0.0"
        assert agent.description == "AI coding assistant"
        assert agent.model == model
        assert agent.prompt == "You are a helpful coding assistant"
        assert agent.configuration == "temperature=0.1, max_tokens=1000"
        assert agent.scaffolding == "basic python environment"

    def test_task_creation_and_properties(self):
        """Test Task creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        task = Task(
            name="Array Sum",
            version="1.5.0",
            description="Calculate sum of array elements",
            library=library,
            content="Create an array [1, 2, 3, 4, 5] and store its sum in variable 'total'",
        )
        assert task.name == "Array Sum"
        assert task.version == "1.5.0"
        assert task.description == "Calculate sum of array elements"
        assert task.library == library
        assert (
            task.content
            == "Create an array [1, 2, 3, 4, 5] and store its sum in variable 'total'"
        )

    def test_taskset_creation_and_properties(self):
        """Test Taskset creation and all properties including computed fields"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )

        task1 = Task(
            name="Task1",
            version="1.0.0",
            description="First",
            library=library,
            content="x = 1",
        )
        task2 = Task(
            name="Task2",
            version="1.0.0",
            description="Second",
            library=library,
            content="y = 2",
        )
        task3 = Task(
            name="Task3",
            version="1.0.0",
            description="Third",
            library=library,
            content="z = 3",
        )

        taskset = Taskset(
            name="NumPy Basics",
            version="3.0.0",
            description="Basic NumPy operations",
            library=library,
            tasks=(task1, task2, task3),
        )
        assert taskset.name == "NumPy Basics"
        assert taskset.version == "3.0.0"
        assert taskset.description == "Basic NumPy operations"
        assert taskset.library == library
        assert taskset.tasks == (task1, task2, task3)
        assert taskset.size == 3  # Test computed field

    def test_test_creation_and_properties(self):
        """Test Test creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        task = Task(
            name="Task1",
            version="1.0.0",
            description="Task",
            library=library,
            content="x = 5",
        )

        test = Test(
            name="Validate Result",
            version="1.2.0",
            description="Check if result is correct",
            task=task,
            content="assert x == 5",
        )
        assert test.name == "Validate Result"
        assert test.version == "1.2.0"
        assert test.description == "Check if result is correct"
        assert test.task == task
        assert test.content == "assert x == 5"

    def test_testset_creation_and_properties(self):
        """Test Testset creation and all properties including computed fields"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )

        task1 = Task(
            name="Task1",
            version="1.0.0",
            description="First",
            library=library,
            content="x = 1",
        )
        task2 = Task(
            name="Task2",
            version="1.0.0",
            description="Second",
            library=library,
            content="y = 2",
        )

        taskset = Taskset(
            name="TestTaskset",
            version="1.0.0",
            description="Test",
            library=library,
            tasks=(task1, task2),
        )

        test1 = Test(
            name="Test1",
            version="1.0.0",
            description="First test",
            task=task1,
            content="assert x == 1",
        )
        test2 = Test(
            name="Test2",
            version="1.0.0",
            description="Second test",
            task=task2,
            content="assert y == 2",
        )

        testset = Testset(
            name="Validation Suite",
            version="2.1.0",
            description="Complete test validation",
            taskset=taskset,
            tests=(test1, test2),
        )
        assert testset.name == "Validation Suite"
        assert testset.version == "2.1.0"
        assert testset.description == "Complete test validation"
        assert testset.taskset == taskset
        assert testset.tests == (test1, test2)
        assert testset.size == 2  # Test computed field

    def test_answer_creation_and_properties(self):
        """Test Answer creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="Agent",
            version="1.0.0",
            description="Agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )
        task = Task(
            name="Task1",
            version="1.0.0",
            description="Task",
            library=library,
            content="x = 5",
        )

        answer = Answer(
            name="Solution Code",
            version="1.1.0",
            description="Generated solution for the task",
            agent=agent,
            task=task,
            content="x = 5\nprint('Task completed')",
        )
        assert answer.name == "Solution Code"
        assert answer.version == "1.1.0"
        assert answer.description == "Generated solution for the task"
        assert answer.agent == agent
        assert answer.task == task
        assert answer.content == "x = 5\nprint('Task completed')"

    def test_answerset_creation_and_properties(self):
        """Test Answerset creation and all properties including computed fields"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="Agent",
            version="1.0.0",
            description="Agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )

        task1 = Task(
            name="Task1",
            version="1.0.0",
            description="First",
            library=library,
            content="x = 1",
        )
        task2 = Task(
            name="Task2",
            version="1.0.0",
            description="Second",
            library=library,
            content="y = 2",
        )
        taskset = Taskset(
            name="TestTaskset",
            version="1.0.0",
            description="Test",
            library=library,
            tasks=(task1, task2),
        )

        answer1 = Answer(
            name="Answer1",
            version="1.0.0",
            description="First answer",
            agent=agent,
            task=task1,
            content="x = 1",
        )
        answer2 = Answer(
            name="Answer2",
            version="1.0.0",
            description="Second answer",
            agent=agent,
            task=task2,
            content="y = 2",
        )

        answerset = Answerset(
            name="Complete Solutions",
            version="1.3.0",
            description="All generated solutions",
            agent=agent,
            taskset=taskset,
            answers=(answer1, answer2),
        )
        assert answerset.name == "Complete Solutions"
        assert answerset.version == "1.3.0"
        assert answerset.description == "All generated solutions"
        assert answerset.agent == agent
        assert answerset.taskset == taskset
        assert answerset.answers == (answer1, answer2)
        assert answerset.size == 2  # Test computed field

    def test_result_creation_and_properties(self):
        """Test Result creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="Agent",
            version="1.0.0",
            description="Agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )
        task = Task(
            name="Task1",
            version="1.0.0",
            description="Task",
            library=library,
            content="x = 5",
        )
        answer = Answer(
            name="Answer",
            version="1.0.0",
            description="Answer",
            agent=agent,
            task=task,
            content="x = 5",
        )
        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert x == 5",
        )

        result = Result(
            name="Test Result",
            version="1.4.0",
            description="Result of running test on answer",
            answer=answer,
            test=test,
            passed=True,
        )
        assert result.name == "Test Result"
        assert result.version == "1.4.0"
        assert result.description == "Result of running test on answer"
        assert result.answer == answer
        assert result.test == test
        assert result.passed is True

    def test_resultset_creation_and_properties(self):
        """Test Resultset creation and all properties including computed fields"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="Agent",
            version="1.0.0",
            description="Agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )

        task1 = Task(
            name="Task1",
            version="1.0.0",
            description="First",
            library=library,
            content="x = 1",
        )
        task2 = Task(
            name="Task2",
            version="1.0.0",
            description="Second",
            library=library,
            content="y = 2",
        )
        task3 = Task(
            name="Task3",
            version="1.0.0",
            description="Third",
            library=library,
            content="z = 3",
        )
        taskset = Taskset(
            name="TestTaskset",
            version="1.0.0",
            description="Test",
            library=library,
            tasks=(task1, task2, task3),
        )

        test1 = Test(
            name="Test1",
            version="1.0.0",
            description="First test",
            task=task1,
            content="assert x == 1",
        )
        test2 = Test(
            name="Test2",
            version="1.0.0",
            description="Second test",
            task=task2,
            content="assert y == 2",
        )
        test3 = Test(
            name="Test3",
            version="1.0.0",
            description="Third test",
            task=task3,
            content="assert z == 3",
        )
        testset = Testset(
            name="TestTestset",
            version="1.0.0",
            description="Test",
            taskset=taskset,
            tests=(test1, test2, test3),
        )

        answer1 = Answer(
            name="Answer1",
            version="1.0.0",
            description="First answer",
            agent=agent,
            task=task1,
            content="x = 1",
        )
        answer2 = Answer(
            name="Answer2",
            version="1.0.0",
            description="Second answer",
            agent=agent,
            task=task2,
            content="y = 2",
        )
        answer3 = Answer(
            name="Answer3",
            version="1.0.0",
            description="Third answer",
            agent=agent,
            task=task3,
            content="z = 3",
        )
        answerset = Answerset(
            name="TestAnswerset",
            version="1.0.0",
            description="Test",
            agent=agent,
            taskset=taskset,
            answers=(answer1, answer2, answer3),
        )

        result1 = Result(
            name="Result1",
            version="1.0.0",
            description="First result",
            answer=answer1,
            test=test1,
            passed=True,
        )
        result2 = Result(
            name="Result2",
            version="1.0.0",
            description="Second result",
            answer=answer2,
            test=test2,
            passed=False,
        )
        result3 = Result(
            name="Result3",
            version="1.0.0",
            description="Third result",
            answer=answer3,
            test=test3,
            passed=True,
        )

        resultset = Resultset(
            name="Test Results",
            version="1.5.0",
            description="Complete test results",
            taskset=taskset,
            testset=testset,
            answerset=answerset,
            results=(result1, result2, result3),
        )
        assert resultset.name == "Test Results"
        assert resultset.version == "1.5.0"
        assert resultset.description == "Complete test results"
        assert resultset.taskset == taskset
        assert resultset.testset == testset
        assert resultset.answerset == answerset
        assert resultset.results == (result1, result2, result3)
        assert resultset.size == 3  # Test computed field
        assert resultset.number_passed == 2  # Test computed field (2 out of 3 passed)
        assert resultset.percentage_passed == pytest.approx(
            66.66666666666667
        )  # Test computed field

    def test_evaluation_creation_and_properties(self):
        """Test Evaluation creation and all properties"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="NumPy",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="Agent",
            version="1.0.0",
            description="Agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )

        task = Task(
            name="Task1",
            version="1.0.0",
            description="Task",
            library=library,
            content="x = 1",
        )
        taskset = Taskset(
            name="TestTaskset",
            version="1.0.0",
            description="Test",
            library=library,
            tasks=(task,),
        )

        test = Test(
            name="Test1",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert x == 1",
        )
        testset = Testset(
            name="TestTestset",
            version="1.0.0",
            description="Test",
            taskset=taskset,
            tests=(test,),
        )

        answer = Answer(
            name="Answer1",
            version="1.0.0",
            description="Answer",
            agent=agent,
            task=task,
            content="x = 1",
        )
        answerset = Answerset(
            name="TestAnswerset",
            version="1.0.0",
            description="Test",
            agent=agent,
            taskset=taskset,
            answers=(answer,),
        )

        result = Result(
            name="Result1",
            version="1.0.0",
            description="Result",
            answer=answer,
            test=test,
            passed=True,
        )
        resultset = Resultset(
            name="TestResultset",
            version="1.0.0",
            description="Test",
            taskset=taskset,
            testset=testset,
            answerset=answerset,
            results=(result,),
        )

        evaluation = Evaluation(
            name="Complete Evaluation",
            version="2.0.0",
            description="Full evaluation of AI agent performance",
            language=language,
            library=library,
            taskset=taskset,
            testset=testset,
            model=model,
            agent=agent,
            answerset=answerset,
            resultset=resultset,
        )
        assert evaluation.name == "Complete Evaluation"
        assert evaluation.version == "2.0.0"
        assert evaluation.description == "Full evaluation of AI agent performance"
        assert evaluation.language == language
        assert evaluation.library == library
        assert evaluation.taskset == taskset
        assert evaluation.testset == testset
        assert evaluation.model == model
        assert evaluation.agent == agent
        assert evaluation.answerset == answerset
        assert evaluation.resultset == resultset


class TestConfigLoading:
    """Test loading all data models from config files"""

    def test_load_language_from_config(self):
        """Test loading Language from config and all properties"""
        config_dir = "tests/configs/test_configs"
        language_config = find_config_file(config_dir, "language_*.json")
        language = create_language(language_config)
        assert language.name == "Python"
        assert language.version == "3.13"
        assert language.description == "Python programming language for testing"

    def test_load_library_from_config(self):
        """Test loading Library from config and all properties"""
        config_dir = "tests/configs/test_configs"
        language_config = find_config_file(config_dir, "language_*.json")
        language = create_language(language_config)
        library_config = find_config_file(config_dir, "library_*.json")
        library = create_library(library_config, language)
        assert library.name == "TestLib"
        assert library.version == "1.0.0"
        assert library.description == "Mock library for testing evaluation framework"
        assert library.language == language
        assert library.language.name == "Python"

    def test_load_model_from_config(self):
        """Test loading Model from config and all properties"""
        config_dir = "tests/configs/test_configs"
        model_config = find_config_file(config_dir, "model_*.json")
        model = create_model(model_config)
        assert model.name == "test-model"
        assert model.version == "1.0.0"
        assert model.description == "Mock model for testing"
        assert model.provider == "openai"

    def test_load_agent_from_config(self):
        """Test loading Agent from config and all properties"""
        config_dir = "tests/configs/test_configs"
        model_config = find_config_file(config_dir, "model_*.json")
        model = create_model(model_config)
        agent_config = find_config_file(config_dir, "agent_*.json")
        agent = create_agent(agent_config, model)
        assert agent.name == "TestAgent"
        assert agent.version == "1.0.0"
        assert agent.description == "Mock agent for testing"
        assert agent.model == model
        assert (
            agent.prompt
            == "You are a helpful coding assistant. Solve the task in the specified language and library. Return ONLY the code, no other text."
        )
        assert agent.configuration == "temperature=0.1"
        assert agent.scaffolding == "basic"

    def test_load_taskset_from_config(self):
        """Test loading Taskset from config and all properties"""
        config_dir = "tests/configs/test_configs"
        language_config = find_config_file(config_dir, "language_*.json")
        language = create_language(language_config)
        library_config = find_config_file(config_dir, "library_*.json")
        library = create_library(library_config, language)
        taskset_config = find_config_file(config_dir, "taskset_*.json")
        taskset = create_taskset(taskset_config, library)
        assert taskset.name == "TestTaskset"
        assert taskset.version == "1.0.0"
        assert taskset.description == "Mock taskset for testing"
        assert taskset.library == library
        assert taskset.size == 2
        assert len(taskset.tasks) == 2

        # Test first task
        task1 = taskset.tasks[0]
        assert task1.name == "Simple Addition"
        assert task1.version == "1.0.0"
        assert task1.description == "Add two numbers"
        assert task1.library == library
        assert "result" in task1.content

        # Test second task
        task2 = taskset.tasks[1]
        assert task2.name == "String Reversal"
        assert task2.version == "1.0.0"
        assert task2.description == "Reverse a string"
        assert task2.library == library
        assert "reversed_str" in task2.content

    def test_load_testset_from_config(self):
        """Test loading Testset from config and all properties"""
        config_dir = "tests/configs/test_configs"
        language_config = find_config_file(config_dir, "language_*.json")
        language = create_language(language_config)
        library_config = find_config_file(config_dir, "library_*.json")
        library = create_library(library_config, language)
        taskset_config = find_config_file(config_dir, "taskset_*.json")
        taskset = create_taskset(taskset_config, library)
        testset_config = find_config_file(config_dir, "testset_*.json")
        testset = create_testset(testset_config, taskset)
        assert testset.name == "TestTestset"
        assert testset.version == "1.0.0"
        assert testset.description == "Mock testset for testing"
        assert testset.taskset == taskset
        assert testset.size == 2
        assert len(testset.tests) == 2

        # Test first test
        test1 = testset.tests[0]
        assert test1.name == "Test Addition"
        assert test1.version == "1.0.0"
        assert test1.description == "Test that result equals 8"
        assert test1.task == taskset.tasks[0]
        assert test1.content == "assert result == 8"

        # Test second test
        test2 = testset.tests[1]
        assert test2.name == "Test String Reversal"
        assert test2.version == "1.0.0"
        assert test2.description == "Test that reversed string equals 'olleh'"
        assert test2.task == taskset.tasks[1]
        assert test2.content == "assert reversed_str == 'olleh'"
