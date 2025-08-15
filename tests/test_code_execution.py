"""Smoke tests for code execution safety in tester.py"""

import pytest
from data_models import Answer, Test, Agent, Task, Model, Library, Language
from tester import generate_result, safe_import


class TestCodeExecutionSafety:
    """Test code execution safety and security measures"""

    def create_minimal_objects(self):
        """Helper to create minimal objects for testing"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="TestLib", version="1.0.0", description="Test", language=language
        )
        model = Model(
            name="test", version="1.0.0", description="Test", provider="openai"
        )
        agent = Agent(
            name="test",
            version="1.0.0",
            description="Test",
            model=model,
            prompt="test",
            configuration="test",
            scaffolding="test",
        )
        task = Task(
            name="test",
            version="1.0.0",
            description="Test",
            library=library,
            content="test",
        )
        return agent, task

    def test_safe_code_execution_passes(self):
        """Test that safe, correct code executes and passes"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="result = 5 + 3",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 8",
        )

        result = generate_result(answer, test)
        assert result is True

    def test_failing_assertion_returns_false(self):
        """Test that code with failing assertions returns False (not exception)"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="result = 5 + 2",  # Wrong answer: 7
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 8",  # Expects 8
        )

        result = generate_result(answer, test)
        assert result is False

    def test_multiple_assertions(self):
        """Test code with multiple assertions"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="x = 10\ny = 20\nsum_result = x + y\nproduct = x * y",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert x == 10\nassert y == 20\nassert sum_result == 30\nassert product == 200",
        )

        result = generate_result(answer, test)
        assert result is True

    def test_multiple_assertions_one_fails(self):
        """Test that if any assertion fails, the whole test fails"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="x = 10\ny = 20\nsum_result = 25",  # Wrong sum
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert x == 10\nassert y == 20\nassert sum_result == 30",  # This will fail
        )

        result = generate_result(answer, test)
        assert result is False

    def test_blocked_os_import(self):
        """Test that 'os' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import os\nresult = 8",  # Dangerous import
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 8",
        )

        with pytest.raises(ImportError, match="Import of 'os' is blocked"):
            generate_result(answer, test)

    def test_blocked_sys_import(self):
        """Test that 'sys' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import sys\nresult = sys.version",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert 'Python' in result",
        )

        with pytest.raises(ImportError, match="Import of 'sys' is blocked"):
            generate_result(answer, test)

    def test_blocked_subprocess_import(self):
        """Test that 'subprocess' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import subprocess\nresult = 'test'",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 'test'",
        )

        with pytest.raises(ImportError, match="Import of 'subprocess' is blocked"):
            generate_result(answer, test)

    def test_blocked_socket_import(self):
        """Test that 'socket' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import socket\nresult = 'network'",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 'network'",
        )

        with pytest.raises(ImportError, match="Import of 'socket' is blocked"):
            generate_result(answer, test)

    def test_blocked_urllib_import(self):
        """Test that 'urllib' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import urllib\nresult = 'web'",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 'web'",
        )

        with pytest.raises(ImportError, match="Import of 'urllib' is blocked"):
            generate_result(answer, test)

    def test_blocked_requests_import(self):
        """Test that 'requests' module import is blocked"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import requests\nresult = 'http'",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 'http'",
        )

        with pytest.raises(ImportError, match="Import of 'requests' is blocked"):
            generate_result(answer, test)

    def test_safe_import_function_directly(self):
        """Test the safe_import function directly"""
        # Test that safe modules can be imported
        math_module = safe_import("math")
        assert hasattr(math_module, "pi")

        # Test that blocked modules raise ImportError
        with pytest.raises(ImportError, match="Import of 'os' is blocked"):
            safe_import("os")

        with pytest.raises(ImportError, match="Import of 'sys' is blocked"):
            safe_import("sys")

    def test_allowed_safe_imports(self):
        """Test that safe modules can still be imported and used"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="import math\nresult = math.sqrt(16)",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 4.0",
        )

        result = generate_result(answer, test)
        assert result is True

    def test_python_builtins_still_work(self):
        """Test that Python builtins are still available"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="numbers = [1, 2, 3, 4, 5]\nresult = sum(numbers)\nlength = len(numbers)",
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 15\nassert length == 5",
        )

        result = generate_result(answer, test)
        assert result is True

    def test_syntax_error_handling(self):
        """Test handling of syntax errors in code"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="result = 5 +",  # Syntax error
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 5",
        )

        # Should raise SyntaxError, not return False
        with pytest.raises(SyntaxError):
            generate_result(answer, test)

    def test_runtime_error_handling(self):
        """Test handling of runtime errors in code"""
        agent, task = self.create_minimal_objects()

        answer = Answer(
            name="Test Answer",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="result = 1 / 0",  # Runtime error
        )

        test = Test(
            name="Test",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert result == 8",
        )

        # Should raise ZeroDivisionError, not return False
        with pytest.raises(ZeroDivisionError):
            generate_result(answer, test)

    def test_variable_isolation_between_tests(self):
        """Test that variables don't leak between test executions"""
        agent, task = self.create_minimal_objects()

        # First test sets a variable
        answer1 = Answer(
            name="Test Answer 1",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="secret_var = 42",
        )

        test1 = Test(
            name="Test 1",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert secret_var == 42",
        )

        result1 = generate_result(answer1, test1)
        assert result1 is True

        # Second test should not have access to secret_var from first test
        answer2 = Answer(
            name="Test Answer 2",
            version="1.0.0",
            description="Test answer",
            agent=agent,
            task=task,
            content="result = 10",  # Don't set secret_var
        )

        test2 = Test(
            name="Test 2",
            version="1.0.0",
            description="Test",
            task=task,
            content="assert 'secret_var' not in globals()",
        )

        # This should pass because each test runs in its own namespace
        result2 = generate_result(answer2, test2)
        assert result2 is True
