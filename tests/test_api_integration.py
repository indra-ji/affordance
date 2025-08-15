"""Integration tests for OpenAI API connectivity and response handling"""

import os
from unittest.mock import Mock, patch

import pytest

from data_models import Agent, Language, Library, Model, Task
from llm import generate_answer, generate_openai_answer
from utils import clean_code


class TestOpenAIAPIIntegration:
    """Test real OpenAI API integration"""

    def create_test_objects(self):
        """Helper to create test objects"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="TestLib",
            version="1.0.0",
            description="Test",
            language=language,
        )
        model = Model(
            name="gpt-4o-mini",
            version="1.0.0",
            description="GPT-4o Mini",
            provider="openai",
        )
        agent = Agent(
            name="TestAgent",
            version="1.0.0",
            description="Test agent",
            model=model,
            prompt="You are a helpful coding assistant. Write only code, no explanations.",
            configuration="temperature=0.1",
            scaffolding="basic",
        )
        task = Task(
            name="Simple Math",
            version="1.0.0",
            description="Simple addition task",
            library=library,
            content="Write code that calculates 2 + 3 and stores the result in a variable called 'answer'",
        )
        return agent, task

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="No OpenAI API key available"
    )
    def test_real_openai_api_call(self):
        """Test actual OpenAI API call with real key"""
        agent, task = self.create_test_objects()

        # This will make a real API call
        response = generate_openai_answer(agent, task)

        # Verify we got a response
        assert isinstance(response, str)
        assert len(response) > 0

        # Check that response contains expected elements for the task
        # (should contain code that calculates 2 + 3)
        response_lower = response.lower()
        assert any(
            keyword in response_lower for keyword in ["answer", "2", "3", "5", "="]
        )

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="No OpenAI API key available"
    )
    def test_real_api_with_different_task(self):
        """Test real API with a different, more complex task"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="TestLib",
            version="1.0.0",
            description="Test",
            language=language,
        )
        model = Model(
            name="gpt-4o-mini",
            version="1.0.0",
            description="GPT-4o Mini",
            provider="openai",
        )
        agent = Agent(
            name="TestAgent",
            version="1.0.0",
            description="Test agent",
            model=model,
            prompt="You are a helpful coding assistant. Write only code, no explanations.",
            configuration="temperature=0.1",
            scaffolding="basic",
        )
        task = Task(
            name="String Manipulation",
            version="1.0.0",
            description="String reversal task",
            library=library,
            content="Write code that reverses the string 'hello' and stores it in a variable called 'reversed_word'",
        )

        response = generate_openai_answer(agent, task)

        # Verify response
        assert isinstance(response, str)
        assert len(response) > 0

        # Should contain code for string reversal
        response_lower = response.lower()
        assert any(
            keyword in response_lower
            for keyword in ["reversed_word", "hello", "reverse", "[::-1]"]
        )

    def test_generate_answer_router_openai(self):
        """Test that generate_answer correctly routes to OpenAI"""
        agent, task = self.create_test_objects()

        with patch("llm.generate_openai_answer") as mock_openai:
            mock_openai.return_value = "answer = 2 + 3"

            result = generate_answer(agent, task)

            # Verify the router called OpenAI function
            mock_openai.assert_called_once_with(agent, task)
            assert result == "answer = 2 + 3"

    def test_generate_answer_unsupported_provider(self):
        """Test error handling for unsupported provider"""
        language = Language(name="Python", version="3.13", description="Python")
        library = Library(
            name="TestLib",
            version="1.0.0",
            description="Test",
            language=language,
        )
        model = Model(
            name="claude",
            version="1.0.0",
            description="Claude",
            provider="anthropic",
        )  # Unsupported
        agent = Agent(
            name="TestAgent",
            version="1.0.0",
            description="Test agent",
            model=model,
            prompt="prompt",
            configuration="config",
            scaffolding="scaffold",
        )
        task = Task(
            name="task",
            version="1.0.0",
            description="Test",
            library=library,
            content="test",
        )

        with pytest.raises(ValueError, match="Unsupported model provider: anthropic"):
            generate_answer(agent, task)


class TestResponseProcessing:
    """Test processing of API responses"""

    def test_clean_code_removes_markdown(self):
        """Test that clean_code properly removes markdown code blocks"""
        # Test typical AI response with code blocks
        raw_response = "Here's the solution:\n\n```python\nresult = 5 + 3\nprint(result)\n```\n\nThis code calculates the sum."
        cleaned = clean_code(raw_response)

        assert "```" not in cleaned
        assert "result = 5 + 3" in cleaned
        assert "print(result)" in cleaned

    def test_clean_code_multiple_blocks(self):
        """Test cleaning response with multiple code blocks"""
        raw_response = "First:\n```python\nx = 1\n```\nThen:\n```\ny = 2\n```\nDone."
        cleaned = clean_code(raw_response)

        assert "```" not in cleaned
        assert "x = 1" in cleaned
        assert "y = 2" in cleaned

    def test_clean_code_no_blocks(self):
        """Test that clean_code handles responses without code blocks"""
        raw_response = "x = 5\ny = 10\nresult = x + y"
        cleaned = clean_code(raw_response)

        # Should remain unchanged
        assert cleaned == raw_response

    def test_prompt_construction(self):
        """Test that prompts are constructed properly for API calls"""
        language = Language(
            name="Python",
            version="3.13",
            description="Python programming language",
        )
        library = Library(
            name="NumPy",
            version="2.0.0",
            description="Numerical computing",
            language=language,
        )
        model = Model(
            name="gpt-4",
            version="1.0.0",
            description="GPT-4",
            provider="openai",
        )
        agent = Agent(
            name="CodingAgent",
            version="1.0.0",
            description="Coding assistant",
            model=model,
            prompt="You are a helpful coding assistant. Write clean code.",
            configuration="temperature=0.1",
            scaffolding="python environment",
        )
        task = Task(
            name="Array Operations",
            version="1.0.0",
            description="Array sum calculation",
            library=library,
            content="Create a NumPy array [1, 2, 3] and calculate its sum, store in 'total'",
        )

        with patch("openai.OpenAI") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_response = Mock()
            mock_response.output_text = (
                "import numpy as np\narr = np.array([1, 2, 3])\ntotal = np.sum(arr)"
            )
            mock_client.responses.create.return_value = mock_response

            result = generate_openai_answer(agent, task)

            # Verify the API was called with correct parameters
            mock_client.responses.create.assert_called_once()
            call_kwargs = mock_client.responses.create.call_args[1]

            assert call_kwargs["model"] == "gpt-4"

            # Check that the prompt contains all necessary information
            prompt = call_kwargs["input"]
            assert "You are a helpful coding assistant. Write clean code." in prompt
            assert (
                "Create a NumPy array [1, 2, 3] and calculate its sum, store in 'total'"
                in prompt
            )
            assert "Library: NumPy 2.0.0" in prompt
            assert "Language: Python 3.13" in prompt

            assert (
                result
                == "import numpy as np\narr = np.array([1, 2, 3])\ntotal = np.sum(arr)"
            )


class TestAPIIntegrationWithRealEnvironment:
    """Tests that require environment setup but test real integration points"""

    def test_api_key_environment_loading(self):
        """Test that API key is properly loaded from environment"""
        # This tests the environment loading without making actual API calls
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            with patch("openai.OpenAI") as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_response = Mock()
                mock_response.output_text = "test_result = 42"
                mock_client.responses.create.return_value = mock_response

                language = Language(name="Python", version="3.13", description="Python")
                library = Library(
                    name="TestLib",
                    version="1.0.0",
                    description="Test",
                    language=language,
                )
                model = Model(
                    name="gpt-4o-mini",
                    version="1.0.0",
                    description="GPT-4o Mini",
                    provider="openai",
                )
                agent = Agent(
                    name="TestAgent",
                    version="1.0.0",
                    description="Test agent",
                    model=model,
                    prompt="prompt",
                    configuration="config",
                    scaffolding="scaffold",
                )
                task = Task(
                    name="task",
                    version="1.0.0",
                    description="Test",
                    library=library,
                    content="test",
                )

                result = generate_openai_answer(agent, task)

                # Verify OpenAI client was created (indicating env var was read)
                mock_client_class.assert_called_once_with(api_key="test-key-123")
                assert result == "test_result = 42"
