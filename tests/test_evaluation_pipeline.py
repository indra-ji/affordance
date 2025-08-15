"""Integration tests for the evaluation pipeline"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from evaluation import (
    create_evaluation,
    create_answerset,
    create_resultset,
    rerun_evaluation,
    load_evaluation,
)
from data_models import Evaluation
from utils import serialize_data_model


class TestEvaluationPipeline:
    """Test the complete evaluation pipeline from config to results"""

    def test_create_evaluation_from_configs(self):
        """Test creating evaluation from test config files"""
        config_dir = "tests/configs/test_configs"

        with patch("llm.generate_answer") as mock_generate:
            # Mock the LLM response for both tasks
            mock_generate.side_effect = [
                "result = 5 + 3",  # First task (addition)
                "reversed_str = 'hello'[::-1]",  # Second task (string reversal)
            ]

            evaluation = create_evaluation(config_dir)

            # Verify evaluation structure
            assert isinstance(evaluation, Evaluation)
            assert evaluation.name == "Evaluation for TestLib"
            assert evaluation.language.name == "Python"
            assert evaluation.library.name == "TestLib"
            assert evaluation.model.provider == "openai"
            assert evaluation.agent.name == "TestAgent"

            # Verify taskset and testset
            assert evaluation.taskset.size == 2
            assert evaluation.testset.size == 2
            assert evaluation.answerset.size == 2
            assert evaluation.resultset.size == 2

            # Verify tasks were processed
            tasks = evaluation.taskset.tasks
            assert tasks[0].name == "Simple Addition"
            assert tasks[1].name == "String Reversal"

            # Verify answers were generated
            answers = evaluation.answerset.answers
            assert answers[0].content == "result = 5 + 3"
            assert answers[1].content == "reversed_str = 'hello'[::-1]"

            # Verify tests are linked correctly
            tests = evaluation.testset.tests
            assert tests[0].content == "assert result == 8"
            assert tests[1].content == "assert reversed_str == 'olleh'"

            # Verify results were computed
            results = evaluation.resultset.results
            assert len(results) == 2
            assert results[0].passed is True  # 5 + 3 = 8 ✓
            assert results[1].passed is True  # 'hello'[::-1] = 'olleh' ✓

            # Verify computed metrics
            assert evaluation.resultset.number_passed == 2
            assert evaluation.resultset.percentage_passed == 100.0

    def test_create_evaluation_with_failing_test(self):
        """Test evaluation pipeline when some tests fail"""
        config_dir = "tests/configs/test_configs"

        with patch("llm.generate_answer") as mock_generate:
            # Mock responses where one will fail the test
            mock_generate.side_effect = [
                "result = 5 + 2",  # Wrong! Should be 8, but this gives 7
                "reversed_str = 'hello'[::-1]",  # Correct
            ]

            evaluation = create_evaluation(config_dir)

            # Verify basic structure
            assert evaluation.taskset.size == 2
            assert evaluation.resultset.size == 2

            # Verify results
            results = evaluation.resultset.results
            assert results[0].passed is False  # 5 + 2 = 7, but test expects 8
            assert results[1].passed is True  # String reversal correct

            # Verify computed metrics
            assert evaluation.resultset.number_passed == 1
            assert evaluation.resultset.percentage_passed == 50.0

    def test_create_answerset_generation(self):
        """Test answerset creation in isolation"""
        config_dir = "tests/configs/test_configs"

        # Create the components manually
        from evaluation import (
            create_language,
            create_library,
            create_taskset,
            create_model,
            create_agent,
        )
        from utils import find_config_file

        language = create_language(find_config_file(config_dir, "language_*.json"))
        library = create_library(
            find_config_file(config_dir, "library_*.json"), language
        )
        taskset = create_taskset(
            find_config_file(config_dir, "taskset_*.json"), library
        )
        model = create_model(find_config_file(config_dir, "model_*.json"))
        agent = create_agent(find_config_file(config_dir, "agent_*.json"), model)

        with patch("llm.generate_answer") as mock_generate:
            mock_generate.side_effect = ["answer1_code", "answer2_code"]

            answerset = create_answerset(agent, taskset)

            # Verify answerset structure
            assert answerset.name == f"Answerset for {taskset.name}"
            assert answerset.agent == agent
            assert answerset.taskset == taskset
            assert answerset.size == 2

            # Verify answers were generated for each task
            answers = answerset.answers
            assert len(answers) == 2
            assert answers[0].content == "answer1_code"
            assert answers[1].content == "answer2_code"
            assert answers[0].task == taskset.tasks[0]
            assert answers[1].task == taskset.tasks[1]

            # Verify generate_answer was called for each task
            assert mock_generate.call_count == 2
            mock_generate.assert_any_call(agent, taskset.tasks[0])
            mock_generate.assert_any_call(agent, taskset.tasks[1])

    def test_create_resultset_computation(self):
        """Test resultset creation and result computation"""
        config_dir = "tests/configs/test_configs"

        # Create components
        from evaluation import (
            create_language,
            create_library,
            create_taskset,
            create_testset,
            create_model,
            create_agent,
        )
        from utils import find_config_file

        language = create_language(find_config_file(config_dir, "language_*.json"))
        library = create_library(
            find_config_file(config_dir, "library_*.json"), language
        )
        taskset = create_taskset(
            find_config_file(config_dir, "taskset_*.json"), library
        )
        testset = create_testset(
            find_config_file(config_dir, "testset_*.json"), taskset
        )
        model = create_model(find_config_file(config_dir, "model_*.json"))
        agent = create_agent(find_config_file(config_dir, "agent_*.json"), model)

        with patch("llm.generate_answer") as mock_generate:
            mock_generate.side_effect = [
                "result = 5 + 3",  # Correct answer
                "reversed_str = 'wrong'",  # Incorrect answer
            ]

            answerset = create_answerset(agent, taskset)
            resultset = create_resultset(taskset, testset, answerset)

            # Verify resultset structure
            assert resultset.taskset == taskset
            assert resultset.testset == testset
            assert resultset.answerset == answerset
            assert resultset.size == 2

            # Verify results
            results = resultset.results
            assert len(results) == 2

            # First result should pass (5 + 3 = 8)
            assert results[0].answer.content == "result = 5 + 3"
            assert results[0].test.content == "assert result == 8"
            assert results[0].passed is True

            # Second result should fail ('wrong' != 'olleh')
            assert results[1].answer.content == "reversed_str = 'wrong'"
            assert results[1].test.content == "assert reversed_str == 'olleh'"
            assert results[1].passed is False

            # Verify computed metrics
            assert resultset.number_passed == 1
            assert resultset.percentage_passed == 50.0

    def test_evaluation_serialization_and_loading(self):
        """Test that evaluations can be serialized and loaded"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_evaluation.json")

            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]

                # Create and serialize evaluation
                original_evaluation = create_evaluation(config_dir)
                serialize_data_model(output_path, original_evaluation)

                # Load evaluation back
                loaded_evaluation = load_evaluation(output_path)

                # Verify loaded evaluation matches original
                assert loaded_evaluation.name == original_evaluation.name
                assert (
                    loaded_evaluation.language.name == original_evaluation.language.name
                )
                assert (
                    loaded_evaluation.library.name == original_evaluation.library.name
                )
                assert (
                    loaded_evaluation.taskset.size == original_evaluation.taskset.size
                )
                assert (
                    loaded_evaluation.resultset.size
                    == original_evaluation.resultset.size
                )
                assert (
                    loaded_evaluation.resultset.number_passed
                    == original_evaluation.resultset.number_passed
                )

                # Verify detailed structure is preserved
                assert len(loaded_evaluation.answerset.answers) == 2
                assert (
                    loaded_evaluation.answerset.answers[0].content == "result = 5 + 3"
                )
                assert loaded_evaluation.resultset.results[0].passed is True

    def test_rerun_evaluation(self):
        """Test rerunning an existing evaluation with new answers"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = os.path.join(temp_dir, "test_evaluation.json")

            # Create initial evaluation
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]

                original_evaluation = create_evaluation(config_dir)
                serialize_data_model(eval_path, original_evaluation)

            # Rerun with different answers
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 4 + 4",
                    "reversed_str = 'world'[::-1]",
                ]

                rerun_evaluation_result = rerun_evaluation(eval_path)

                # Verify the evaluation was rerun with new answers
                assert (
                    rerun_evaluation_result.name == original_evaluation.name
                )  # Same metadata
                assert (
                    rerun_evaluation_result.library.name
                    == original_evaluation.library.name
                )

                # But different answers
                new_answers = rerun_evaluation_result.answerset.answers
                assert new_answers[0].content == "result = 4 + 4"
                assert new_answers[1].content == "reversed_str = 'world'[::-1]"

                # And different results
                new_results = rerun_evaluation_result.resultset.results
                assert new_results[0].passed is True  # 4 + 4 = 8 ✓
                assert (
                    new_results[1].passed is False
                )  # 'world'[::-1] = 'dlrow' ≠ 'olleh'

                assert rerun_evaluation_result.resultset.number_passed == 1
                assert rerun_evaluation_result.resultset.percentage_passed == 50.0


class TestEvaluationPipelineErrorHandling:
    """Test error handling in the evaluation pipeline"""

    def test_missing_config_files(self):
        """Test error when config files are missing"""
        with tempfile.TemporaryDirectory() as empty_dir:
            with pytest.raises(
                FileNotFoundError, match="No config file matching pattern"
            ):
                create_evaluation(empty_dir)

    def test_invalid_config_structure(self):
        """Test error handling for malformed config files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid language config
            invalid_config = Path(temp_dir) / "language_invalid.json"
            invalid_config.write_text('{"invalid": "structure"}')

            with pytest.raises(Exception):  # Should raise validation error
                create_evaluation(temp_dir)

    def test_llm_generation_failure(self):
        """Test handling when LLM generation fails"""
        config_dir = "tests/configs/test_configs"

        with patch("llm.generate_answer") as mock_generate:
            mock_generate.side_effect = Exception("API Error: Rate limit exceeded")

            with pytest.raises(Exception, match="API Error: Rate limit exceeded"):
                create_evaluation(config_dir)

    def test_code_execution_errors_in_pipeline(self):
        """Test pipeline behavior when generated code has execution errors"""
        config_dir = "tests/configs/test_configs"

        with patch("llm.generate_answer") as mock_generate:
            # Mock responses with syntax errors
            mock_generate.side_effect = [
                "result = 5 +",  # Syntax error
                "reversed_str = 'hello'[::-1]",  # Valid
            ]

            # Should raise SyntaxError when trying to execute the code
            with pytest.raises(SyntaxError):
                create_evaluation(config_dir)


class TestEvaluationPipelineWithExistingConfigs:
    """Test pipeline using the existing numpy demo configs"""

    def test_pipeline_with_numpy_configs(self):
        """Test pipeline using actual numpy demo config files"""
        config_dir = "eval_configs/numpy_demo_configs"

        # Skip if the numpy configs don't exist
        if not os.path.exists(config_dir):
            pytest.skip("NumPy demo configs not available")

        with patch("llm.generate_answer") as mock_generate:
            # Mock responses for numpy tasks (we don't know how many there are)
            mock_generate.return_value = (
                "import numpy as np\nresult = np.array([1, 2, 3])"
            )

            try:
                evaluation = create_evaluation(config_dir)

                # Verify basic structure
                assert isinstance(evaluation, Evaluation)
                assert evaluation.language.name == "Python"  # Assuming Python
                assert evaluation.taskset.size > 0
                assert evaluation.resultset.size == evaluation.taskset.size

                # Verify all components are properly linked
                assert len(evaluation.answerset.answers) == evaluation.taskset.size
                assert len(evaluation.resultset.results) == evaluation.taskset.size

            except FileNotFoundError as e:
                pytest.skip(f"Required config files not found: {e}")

    def test_pipeline_performance_metrics(self):
        """Test that pipeline computes performance metrics correctly"""
        config_dir = "tests/configs/test_configs"

        with patch("llm.generate_answer") as mock_generate:
            # Create a mix of passing and failing responses
            mock_generate.side_effect = [
                "result = 5 + 3",  # Should pass (8 == 8)
                "reversed_str = 'goodbye'[::-1]",  # Should fail ('eybdoog' != 'olleh')
            ]

            evaluation = create_evaluation(config_dir)

            # Verify metrics computation
            resultset = evaluation.resultset
            assert resultset.size == 2
            assert resultset.number_passed == 1
            assert resultset.percentage_passed == 50.0

            # Verify individual results
            results = resultset.results
            assert results[0].passed is True
            assert results[1].passed is False
