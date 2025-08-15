"""End-to-end integration tests for the complete affordance system"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
import re
from unittest.mock import patch, Mock

import pytest
from pydantic import ValidationError

from dashboard import load_evaluation_from_file
from evaluation import create_evaluation, rerun_evaluation
from utils import generate_evaluation_output_path, serialize_data_model


class TestEndToEndWorkflow:
    """Test complete system workflows from start to finish"""

    def _sanitize_api_keys(self, text: str) -> str:
        """Remove potential API keys from text before logging"""
        if not isinstance(text, str):
            return str(text)

        # Pattern for OpenAI API keys (sk-...)
        text = re.sub(r"sk-[a-zA-Z0-9]{48}", "sk-***REDACTED***", text)
        # Pattern for other potential keys
        text = re.sub(r"\b[A-Za-z0-9]{32,}\b", "***REDACTED***", text)
        return text

    def _validate_code_content(self, content: str) -> None:
        """Basic validation that content looks like safe code"""
        if not isinstance(content, str):
            return

        # Check for obviously malicious patterns
        dangerous_patterns = [
            r"import\s+os",
            r"import\s+subprocess",
            r"import\s+sys",
            r"__import__\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r'open\s*\([^)]*["\'][rwa]',  # File operations
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous code detected: {pattern}")

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="No OpenAI API key for real end-to-end test",
    )
    def test_complete_real_evaluation_workflow(self):
        """Test the complete workflow with REAL API calls and code execution"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Run actual evaluation pipeline (no mocking!)
            evaluation = create_evaluation(config_dir)

            # Step 2: Verify structure
            assert evaluation.taskset.size == 2
            assert evaluation.resultset.size == 2

            # Step 3: Verify real API responses were generated
            answers = evaluation.answerset.answers
            assert len(answers) == 2

            for answer in answers:
                assert isinstance(answer.content, str)
                assert len(answer.content.strip()) > 0
                # Sanitize API response before logging
                sanitized_content = self._sanitize_api_keys(answer.content)
                print(f"Generated answer for {answer.task.name}: {sanitized_content}")
                # Validate that content looks like code (basic security check)
                self._validate_code_content(answer.content)

            # Step 4: Verify code was actually executed and tested
            results = evaluation.resultset.results
            for result in results:
                print(f"Task: {result.answer.task.name}")
                sanitized_code = self._sanitize_api_keys(result.answer.content)
                print(f"Generated code: {sanitized_code}")
                print(f"Test: {result.test.content}")
                print(f"Passed: {result.passed}")
                print("---")
                # Validate code content for security
                self._validate_code_content(result.answer.content)

                # Verify result has boolean value (code was executed)
                assert isinstance(result.passed, bool)

            # Step 5: Generate output path and serialize
            output_path = generate_evaluation_output_path(
                evaluation.name, evaluation.model.name, temp_dir
            )
            serialize_data_model(output_path, evaluation)

            # Verify file was created with correct naming
            assert os.path.exists(output_path)
            assert output_path.endswith(".json")
            assert "TestLib" in output_path
            assert evaluation.model.name in output_path

            # Step 6: Load evaluation for dashboard (test serialization integrity)
            loaded_evaluation = load_evaluation_from_file(output_path)

            assert loaded_evaluation is not None
            assert loaded_evaluation.name == evaluation.name
            assert loaded_evaluation.resultset.size == evaluation.resultset.size
            assert (
                loaded_evaluation.resultset.number_passed
                == evaluation.resultset.number_passed
            )

            # Verify all data survived serialization/deserialization
            for orig, loaded in zip(
                evaluation.resultset.results,
                loaded_evaluation.resultset.results,
            ):
                assert orig.answer.content == loaded.answer.content
                assert orig.test.content == loaded.test.content
                assert orig.passed == loaded.passed
                assert orig.answer.task.name == loaded.answer.task.name

            print(
                f"Final results: {loaded_evaluation.resultset.number_passed}/{loaded_evaluation.resultset.size} passed ({loaded_evaluation.resultset.percentage_passed}%)"
            )

    def test_evaluation_via_command_line_interface(self):
        """Test the complete workflow via the command-line interface"""
        config_dir = "tests/configs/test_configs"

        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key for command-line test")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use subprocess with proper working directory handling
            original_cwd = os.getcwd()

            try:
                # Create evals directory in temp_dir
                evals_dir = Path(temp_dir) / "evals"
                evals_dir.mkdir(exist_ok=True)

                # Run evaluation via command line with clear working directory
                result = subprocess.run(
                    [
                        sys.executable,
                        os.path.join(original_cwd, "evaluation.py"),
                        "--create",
                        os.path.join(original_cwd, config_dir),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,  # Run subprocess in temp_dir
                    env={
                        **os.environ,
                        "PYTHONPATH": original_cwd,
                    },  # Ensure imports work
                )

                # Sanitize output to avoid leaking API keys
                sanitized_stdout = self._sanitize_api_keys(result.stdout)
                sanitized_stderr = self._sanitize_api_keys(result.stderr)
                print(f"Command output: {sanitized_stdout}")
                print(f"Command errors: {sanitized_stderr}")

                # Verify command succeeded
                assert result.returncode == 0, f"Command failed: {result.stderr}"

                # Check that evaluation file was created in temp_dir
                evals_dir = Path(temp_dir) / "evals"
                eval_files = (
                    list(evals_dir.glob("Evaluation_for_TestLib_*.json"))
                    if evals_dir.exists()
                    else []
                )

                assert len(eval_files) > 0, (
                    f"No evaluation files found. Checked: {temp_dir}/evals and {original_cwd}/evals"
                )

                # Load and verify the generated evaluation
                eval_file = eval_files[0]
                loaded_evaluation = load_evaluation_from_file(str(eval_file))

                assert loaded_evaluation is not None
                assert loaded_evaluation.taskset.size == 2
                assert loaded_evaluation.resultset.size == 2

                # Verify it contains real generated answers
                for answer in loaded_evaluation.answerset.answers:
                    assert len(answer.content.strip()) > 0

                print(
                    f"Command-line evaluation completed: {loaded_evaluation.resultset.number_passed}/{loaded_evaluation.resultset.size} passed"
                )

                # Note: File cleanup handled by temp directory context manager

            finally:
                # No need to restore directory since we didn't change it
                pass

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="No OpenAI API key for rerun test",
    )
    def test_real_evaluation_rerun_workflow(self):
        """Test the rerun functionality with real API calls"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create initial evaluation
            original_evaluation = create_evaluation(config_dir)

            # Save it
            eval_path = os.path.join(temp_dir, "rerun_test.json")
            serialize_data_model(eval_path, original_evaluation)

            print("Original evaluation results:")
            for result in original_evaluation.resultset.results:
                print(
                    f"  {result.answer.task.name}: {result.passed} ({result.answer.content})"
                )

            # Step 2: Rerun the evaluation (this will generate new API responses)
            rerun_evaluation_result = rerun_evaluation(eval_path)

            print("Rerun evaluation results:")
            for result in rerun_evaluation_result.resultset.results:
                print(
                    f"  {result.answer.task.name}: {result.passed} ({result.answer.content})"
                )

            # Step 3: Verify rerun worked
            assert rerun_evaluation_result.name == original_evaluation.name
            assert (
                rerun_evaluation_result.taskset.size == original_evaluation.taskset.size
            )
            assert (
                rerun_evaluation_result.resultset.size
                == original_evaluation.resultset.size
            )

            # Answers might be different due to new API calls
            original_answers = [
                a.content for a in original_evaluation.answerset.answers
            ]
            rerun_answers = [
                a.content for a in rerun_evaluation_result.answerset.answers
            ]

            print(f"Original answers: {original_answers}")
            print(f"Rerun answers: {rerun_answers}")

            # Results might be different, but structure should be same
            assert len(rerun_evaluation_result.resultset.results) == len(
                original_evaluation.resultset.results
            )

            for result in rerun_evaluation_result.resultset.results:
                assert isinstance(result.passed, bool)
                assert len(result.answer.content.strip()) > 0

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="No OpenAI API key for numpy test",
    )
    def test_evaluation_with_numpy_configs_if_available(self):
        """Test end-to-end workflow with numpy demo configs if they exist (REAL API calls)"""
        config_dir = "eval_configs/numpy_demo_configs"

        if not os.path.exists(config_dir):
            pytest.skip("NumPy demo configs not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Run real evaluation with numpy configs
                evaluation = create_evaluation(config_dir)

                print(f"NumPy evaluation created with {evaluation.taskset.size} tasks")

                # Verify structure
                assert evaluation.taskset.size > 0
                assert evaluation.resultset.size == evaluation.taskset.size
                # More specific assertion for numpy library
                assert (
                    evaluation.library.name == "NumPy"
                    or evaluation.library.name == "numpy"
                )

                # Print results for inspection
                print("NumPy evaluation results:")
                for result in evaluation.resultset.results:
                    print(f"Task: {result.answer.task.name}")
                    print(f"Generated: {result.answer.content[:100]}...")
                    print(f"Passed: {result.passed}")
                    print("---")

                # Serialize and load
                output_path = os.path.join(temp_dir, "numpy_evaluation.json")
                serialize_data_model(output_path, evaluation)

                loaded = load_evaluation_from_file(output_path)
                assert loaded is not None
                assert loaded.taskset.size == evaluation.taskset.size
                assert (
                    loaded.resultset.number_passed == evaluation.resultset.number_passed
                )

                print(
                    f"NumPy evaluation: {loaded.resultset.number_passed}/{loaded.resultset.size} tasks passed ({loaded.resultset.percentage_passed:.1f}%)"
                )

            except FileNotFoundError:
                pytest.skip("Required numpy config files not found")

    def test_evaluation_serialization_and_dashboard_loading(self):
        """Test that evaluations can be properly serialized and loaded by dashboard"""
        config_dir = "tests/configs/test_configs"

        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key for serialization test")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create evaluation
            evaluation = create_evaluation(config_dir)

            # Test multiple serialization formats and locations
            paths = [
                os.path.join(temp_dir, "test1.json"),
                os.path.join(temp_dir, "Test_Evaluation_with_spaces.json"),
                generate_evaluation_output_path(
                    "Custom Eval", evaluation.model.name, temp_dir
                ),
            ]

            for path in paths:
                # Serialize
                serialize_data_model(path, evaluation)
                assert os.path.exists(path)

                # Load via dashboard function
                loaded = load_evaluation_from_file(path)
                assert loaded is not None

                # Verify complete data integrity
                assert loaded.name == evaluation.name
                assert loaded.taskset.size == evaluation.taskset.size
                assert (
                    loaded.resultset.number_passed == evaluation.resultset.number_passed
                )
                assert (
                    loaded.resultset.percentage_passed
                    == evaluation.resultset.percentage_passed
                )

                # Verify detailed structure for dashboard rendering
                assert len(loaded.answerset.answers) == len(
                    evaluation.answerset.answers
                )
                assert len(loaded.resultset.results) == len(
                    evaluation.resultset.results
                )

                for orig_result, loaded_result in zip(
                    evaluation.resultset.results, loaded.resultset.results
                ):
                    assert orig_result.passed == loaded_result.passed
                    assert orig_result.answer.content == loaded_result.answer.content
                    assert (
                        orig_result.answer.task.name == loaded_result.answer.task.name
                    )


class TestEndToEndErrorScenarios:
    """Test end-to-end workflows with various error conditions"""

    def test_api_error_scenarios(self):
        """Test handling of various API error conditions"""
        config_dir = "tests/configs/test_configs"

        # Test with invalid API key format
        with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid-key-format"}):
            with pytest.raises(Exception):  # Should fail with invalid key
                create_evaluation(config_dir)

        # Test with empty API key
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with pytest.raises(Exception):  # Should fail with empty key
                create_evaluation(config_dir)

    def test_network_failure_scenarios(self):
        """Test handling of network-related failures"""
        config_dir = "tests/configs/test_configs"

        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key for network failure test")

        # Mock network failure
        with patch("openai.OpenAI") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Simulate connection error on the correct API endpoint
            from requests.exceptions import ConnectionError

            mock_client.responses.create.side_effect = ConnectionError(
                "Network unreachable"
            )

            with pytest.raises(ConnectionError):
                create_evaluation(config_dir)

    def test_malformed_api_response_handling(self):
        """Test handling of malformed API responses"""
        config_dir = "tests/configs/test_configs"

        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key for malformed response test")

        # Mock malformed response
        with patch("llm.generate_openai_answer") as mock_generate:
            # Return non-code content
            mock_generate.return_value = (
                "I cannot help with that request. Please try again."
            )

            evaluation = create_evaluation(config_dir)

            # Verify it handles non-code responses gracefully
            for answer in evaluation.answerset.answers:
                # Should not contain executable code patterns
                assert "import" not in answer.content.lower()
                assert "def " not in answer.content.lower()

    def test_config_injection_security(self):
        """Test that config files cannot inject malicious content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with potential injection
            malicious_config = os.path.join(temp_dir, "language_malicious.json")
            with open(malicious_config, "w") as f:
                f.write(
                    '{\n    "name": "Python",\n    "version": "3.13",\n    "description": "Python; import os; os.system(\'rm -rf /\');"\n}'
                )

            # Should handle malicious content safely
            with pytest.raises((ValidationError, KeyError, TypeError)):
                create_evaluation(temp_dir)

    def test_subprocess_path_validation(self):
        """Test that subprocess calls validate paths properly"""
        # Test with malicious path injection
        malicious_config = "../../../etc/passwd; rm -rf /; #"

        with pytest.raises((FileNotFoundError, OSError, ValueError)):
            # Should not execute injected commands
            create_evaluation(malicious_config)

    def test_workflow_with_missing_config_files(self):
        """Test error handling when config files are missing"""
        with tempfile.TemporaryDirectory() as empty_dir:
            with pytest.raises(
                FileNotFoundError, match="No config file matching pattern"
            ):
                create_evaluation(empty_dir)

    def test_workflow_with_invalid_config_structure(self):
        """Test error handling for malformed config files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid language config
            config_path = os.path.join(temp_dir, "language_invalid.json")
            with open(config_path, "w") as f:
                f.write('{"invalid": "structure"}')  # Missing required fields

            with pytest.raises((ValidationError, KeyError, TypeError)):
                create_evaluation(temp_dir)

    def test_workflow_with_serialization_failures(self):
        """Test workflow when serialization fails due to invalid paths"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key for serialization failure test")

        config_dir = "tests/configs/test_configs"
        evaluation = create_evaluation(config_dir)

        # Try to serialize to invalid path
        invalid_path = "/nonexistent_directory/evaluation.json"

        with pytest.raises(FileNotFoundError):
            serialize_data_model(invalid_path, evaluation)

    def test_workflow_with_corrupted_output_file(self):
        """Test dashboard loading with corrupted evaluation file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            corrupted_path = os.path.join(temp_dir, "corrupted.json")

            # Create corrupted JSON file
            with open(corrupted_path, "w") as f:
                f.write('{"incomplete": "json", "missing')  # Invalid JSON

            # Dashboard should handle this gracefully
            result = load_evaluation_from_file(corrupted_path)
            assert result is None
