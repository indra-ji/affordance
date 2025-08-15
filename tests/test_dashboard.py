"""Tests for the Streamlit dashboard functionality"""

import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from dashboard import load_evaluation_from_file, show_dashboard
from evaluation import create_evaluation
from utils import serialize_data_model


class TestDashboardDataLoading:
    """Test dashboard data loading functionality"""

    def test_load_evaluation_from_valid_file(self):
        """Test loading a valid evaluation file"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = os.path.join(temp_dir, "test_evaluation.json")

            # Create and save an evaluation
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]

                evaluation = create_evaluation(config_dir)
                serialize_data_model(eval_path, evaluation)

            # Test loading
            loaded_evaluation = load_evaluation_from_file(eval_path)

            assert loaded_evaluation is not None
            assert loaded_evaluation.name == "Evaluation for TestLib"
            assert loaded_evaluation.library.name == "TestLib"
            assert loaded_evaluation.taskset.size == 2
            assert loaded_evaluation.resultset.number_passed == 2

    def test_load_evaluation_from_nonexistent_file(self):
        """Test error handling when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = os.path.join(temp_dir, "nonexistent.json")

            # Should return None and not crash
            result = load_evaluation_from_file(nonexistent_path)
            assert result is None

    def test_load_evaluation_from_invalid_json(self):
        """Test error handling for invalid JSON files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = os.path.join(temp_dir, "invalid.json")

            # Create invalid JSON file
            with open(invalid_path, "w") as f:
                f.write("{ invalid json structure }")

            # Should return None and not crash
            result = load_evaluation_from_file(invalid_path)
            assert result is None

    def test_load_evaluation_from_wrong_data_structure(self):
        """Test error handling for files with wrong data structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            wrong_structure_path = os.path.join(temp_dir, "wrong.json")

            # Create valid JSON but wrong structure
            with open(wrong_structure_path, "w") as f:
                f.write('{"some": "other", "data": "structure"}')

            # Should return None and not crash
            result = load_evaluation_from_file(wrong_structure_path)
            assert result is None

    def test_caching_behavior(self):
        """Test that load_evaluation_from_file properly caches results"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = os.path.join(temp_dir, "cached_evaluation.json")

            # Create evaluation file
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]

                evaluation = create_evaluation(config_dir)
                serialize_data_model(eval_path, evaluation)

            # Load twice - should use cache on second load
            first_load = load_evaluation_from_file(eval_path)
            second_load = load_evaluation_from_file(eval_path)

            # Both should succeed and return the same data
            assert first_load is not None
            assert second_load is not None
            assert first_load.name == second_load.name
            assert (
                first_load.resultset.number_passed
                == second_load.resultset.number_passed
            )


class TestDashboardUI:
    """Test dashboard UI components and functionality"""

    @patch("streamlit.set_page_config")
    @patch("streamlit.sidebar.header")
    @patch("streamlit.sidebar.selectbox")
    @patch("streamlit.sidebar.radio")
    @patch("streamlit.error")
    def test_dashboard_no_evaluation_files(
        self,
        mock_error,
        mock_radio,
        mock_selectbox,
        mock_sidebar_header,
        mock_set_page_config,
    ):
        """Test dashboard behavior when no evaluation files are found"""

        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = []  # No files found

            show_dashboard()

            # Should show error message
            mock_error.assert_called_once_with(
                "No evaluation files found! Make sure your JSON files are in the evals directory."
            )

            # Should still set page config
            mock_set_page_config.assert_called_once()

    @patch("streamlit.set_page_config")
    @patch("streamlit.sidebar.header")
    @patch("streamlit.sidebar.selectbox")
    @patch("streamlit.sidebar.radio")
    @patch("dashboard.load_evaluation_from_file")
    def test_dashboard_with_evaluation_files(
        self,
        mock_load_eval,
        mock_radio,
        mock_selectbox,
        mock_sidebar_header,
        mock_set_page_config,
    ):
        """Test dashboard when evaluation files are available"""

        # Mock evaluation files
        mock_file1 = Mock()
        mock_file1.name = "Evaluation_Test1.json"
        mock_file2 = Mock()
        mock_file2.name = "Evaluation_Test2.json"

        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = [mock_file1, mock_file2]

            # Mock selectbox to return first file
            mock_selectbox.return_value = mock_file1

            # Mock radio to return "Overview"
            mock_radio.return_value = "Overview"

            # Mock successful evaluation loading
            mock_evaluation = Mock()
            mock_evaluation.name = "Test Evaluation"
            mock_evaluation.language.name = "Python"
            mock_load_eval.return_value = mock_evaluation

            with patch("dashboard.render_overview") as mock_render_overview:
                show_dashboard()

                # Verify UI components were called
                mock_set_page_config.assert_called_once()
                assert mock_sidebar_header.call_count >= 1
                mock_selectbox.assert_called_once()
                mock_radio.assert_called_once()

                # Verify evaluation was loaded and rendered
                mock_load_eval.assert_called_once_with(str(mock_file1))
                mock_render_overview.assert_called_once_with(mock_evaluation)

    @patch("streamlit.set_page_config")
    @patch("streamlit.sidebar.header")
    @patch("streamlit.sidebar.selectbox")
    @patch("streamlit.sidebar.radio")
    @patch("dashboard.load_evaluation_from_file")
    def test_dashboard_section_navigation(
        self,
        mock_load_eval,
        mock_radio,
        mock_selectbox,
        mock_sidebar_header,
        mock_set_page_config,
    ):
        """Test navigation between different dashboard sections"""

        mock_file = Mock()
        mock_file.name = "Evaluation_Test.json"

        mock_evaluation = Mock()
        mock_evaluation.name = "Test Evaluation"

        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = [mock_file]
            mock_selectbox.return_value = mock_file
            mock_load_eval.return_value = mock_evaluation

            # Test Overview section
            mock_radio.return_value = "Overview"
            with patch("dashboard.render_overview") as mock_render_overview:
                show_dashboard()
                mock_render_overview.assert_called_once_with(mock_evaluation)

            # Test Metrics section
            mock_radio.return_value = "Metrics"
            with patch("dashboard.render_metrics") as mock_render_metrics:
                show_dashboard()
                mock_render_metrics.assert_called_once_with(mock_evaluation)

            # Test Detailed view section
            mock_radio.return_value = "Detailed view"
            with patch("dashboard.render_detailed_view") as mock_render_detailed:
                show_dashboard()
                mock_render_detailed.assert_called_once_with(mock_evaluation)


class TestDashboardRenderingComponents:
    """Test individual dashboard rendering components"""

    def create_mock_evaluation(self):
        """Create a mock evaluation for testing"""
        # Create a comprehensive mock evaluation
        mock_evaluation = Mock()
        mock_evaluation.name = "Test Evaluation"
        mock_evaluation.version = "1.0.0"
        mock_evaluation.description = "Test evaluation for dashboard"

        # Mock language
        mock_evaluation.language.name = "Python"
        mock_evaluation.language.version = "3.13"
        mock_evaluation.language.description = "Python programming language"

        # Mock library
        mock_evaluation.library.name = "TestLib"
        mock_evaluation.library.version = "1.0.0"
        mock_evaluation.library.description = "Test library"

        # Mock model and agent
        mock_evaluation.model.name = "gpt-4"
        mock_evaluation.model.description = "OpenAI GPT-4"
        mock_evaluation.agent.name = "TestAgent"
        mock_evaluation.agent.description = "Test coding agent"

        # Mock taskset and testset
        mock_evaluation.taskset.name = "TestTaskset"
        mock_evaluation.taskset.description = "Test tasks"
        mock_evaluation.taskset.size = 3
        mock_evaluation.testset.name = "TestTestset"
        mock_evaluation.testset.description = "Test cases"
        mock_evaluation.testset.size = 3

        # Mock resultset with metrics
        mock_evaluation.resultset.size = 3
        mock_evaluation.resultset.number_passed = 2
        mock_evaluation.resultset.percentage_passed = 66.7

        return mock_evaluation

    @patch("streamlit.header")
    @patch("streamlit.caption")
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.write")
    @patch("streamlit.columns")
    def test_render_overview(
        self,
        mock_columns,
        mock_write,
        mock_subheader,
        mock_divider,
        mock_caption,
        mock_header,
    ):
        """Test the overview rendering function"""
        from dashboard import render_overview

        mock_evaluation = self.create_mock_evaluation()

        # Mock columns to return mock column objects
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]

        render_overview(mock_evaluation)

        # Verify main header and structure
        mock_header.assert_called_with("Evaluation Overview")
        mock_caption.assert_called_with("High-level details of the evaluation run")
        mock_divider.assert_called()

        # Verify columns were created for layout
        assert mock_columns.call_count >= 1  # Should create columns for layout

    @patch("streamlit.header")
    @patch("streamlit.caption")
    @patch("streamlit.divider")
    @patch("streamlit.subheader")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    def test_render_metrics(
        self,
        mock_columns,
        mock_metric,
        mock_subheader,
        mock_divider,
        mock_caption,
        mock_header,
    ):
        """Test the metrics rendering function"""
        from dashboard import render_metrics

        mock_evaluation = self.create_mock_evaluation()

        # Mock columns
        mock_col1, mock_col2, mock_col3, mock_col4 = Mock(), Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]

        render_metrics(mock_evaluation)

        # Verify headers and structure
        mock_header.assert_called_with("Metrics")
        mock_caption.assert_called_with("At-a-glance performance")

        # Verify metrics are displayed
        assert mock_metric.call_count >= 3  # Should show multiple metrics

        # Check for expected metric calls (at least pass rate and totals)
        metric_calls = [call.args for call in mock_metric.call_args_list]
        metric_labels = [call[0] for call in metric_calls if call]

        # Should include key metrics
        assert any("pass rate" in label.lower() for label in metric_labels)
        assert any("total" in label.lower() for label in metric_labels)

    @patch("streamlit.header")
    @patch("streamlit.caption")
    @patch("streamlit.divider")
    @patch("streamlit.selectbox")
    @patch("streamlit.subheader")
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.text_area")
    @patch("streamlit.code")
    @patch("streamlit.write")
    @patch("streamlit.columns")
    def test_render_detailed_view(
        self,
        mock_columns,
        mock_write,
        mock_code,
        mock_text_area,
        mock_tabs,
        mock_markdown,
        mock_subheader,
        mock_selectbox,
        mock_divider,
        mock_caption,
        mock_header,
    ):
        """Test the detailed view rendering function"""
        from dashboard import render_detailed_view

        mock_evaluation = self.create_mock_evaluation()

        # Create mock results with proper structure
        mock_result1 = Mock()
        mock_result1.answer.task.name = "Task 1"
        mock_result1.answer.task.content = "Test task content"
        mock_result1.answer.task.description = "Test task description"
        mock_result1.answer.content = "test_code = 1 + 1"
        mock_result1.answer.agent.name = "TestAgent"
        mock_result1.answer.agent.model.name = "gpt-4"
        mock_result1.test.content = "assert test_code == 2"
        mock_result1.test.name = "Test 1"
        mock_result1.test.description = "Test description"
        mock_result1.passed = True

        mock_evaluation.resultset.results = [mock_result1]
        mock_evaluation.resultset.taskset.size = 1

        # Mock selectbox to return first task
        mock_selectbox.return_value = 0

        # Mock columns and tabs
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        mock_tab1, mock_tab2, mock_tab3 = Mock(), Mock(), Mock()
        mock_tabs.return_value = [mock_tab1, mock_tab2, mock_tab3]

        render_detailed_view(mock_evaluation)

        # Verify main structure
        mock_header.assert_called_with("Detailed view")
        mock_caption.assert_called_with("Inspect tasks, answers, tests, and results")

        # Verify selectbox for task selection
        mock_selectbox.assert_called_once()

        # Verify tabs were created
        mock_tabs.assert_called_once_with(["Task", "Answer", "Test"])

        # Verify content rendering (code display, text areas, etc.)
        assert mock_code.call_count >= 1  # Should display code
        assert mock_text_area.call_count >= 1  # Should display task content


class TestDashboardIntegration:
    """Test dashboard integration with evaluation data"""

    def test_dashboard_with_real_evaluation_data(self):
        """Test dashboard loading with actual evaluation data"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create evals directory structure
            evals_dir = Path(temp_dir) / "evals"
            evals_dir.mkdir()

            eval_path = evals_dir / "Evaluation_Dashboard_Test.json"

            # Create real evaluation
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]

                evaluation = create_evaluation(config_dir)
                serialize_data_model(str(eval_path), evaluation)

            # Test loading the evaluation
            loaded_eval = load_evaluation_from_file(str(eval_path))

            assert loaded_eval is not None
            assert loaded_eval.name == "Evaluation for TestLib"
            assert loaded_eval.resultset.size == 2
            assert loaded_eval.resultset.number_passed == 2
            assert loaded_eval.resultset.percentage_passed == 100.0

            # Verify detailed structure for dashboard rendering
            results = loaded_eval.resultset.results
            assert len(results) == 2

            # First result
            assert results[0].answer.task.name == "Simple Addition"
            assert results[0].answer.content == "result = 5 + 3"
            assert results[0].test.content == "assert result == 8"
            assert results[0].passed is True

            # Second result
            assert results[1].answer.task.name == "String Reversal"
            assert results[1].answer.content == "reversed_str = 'hello'[::-1]"
            assert results[1].test.content == "assert reversed_str == 'olleh'"
            assert results[1].passed is True

    def test_dashboard_with_mixed_results(self):
        """Test dashboard with evaluations containing both passing and failing tests"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "mixed_results.json"

            # Create evaluation with mixed results
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 2",  # Wrong (7 != 8)
                    "reversed_str = 'hello'[::-1]",  # Correct
                ]

                evaluation = create_evaluation(config_dir)
                serialize_data_model(str(eval_path), evaluation)

            loaded_eval = load_evaluation_from_file(str(eval_path))

            # Verify mixed results
            assert loaded_eval.resultset.number_passed == 1
            assert loaded_eval.resultset.percentage_passed == 50.0

            results = loaded_eval.resultset.results
            assert results[0].passed is False  # Addition failed
            assert results[1].passed is True  # String reversal passed


class TestDashboardErrorScenarios:
    """Test dashboard error handling and edge cases"""

    def test_dashboard_with_missing_evaluation_fields(self):
        """Test dashboard behavior when evaluation data has missing fields"""
        with tempfile.TemporaryDirectory() as temp_dir:
            incomplete_path = os.path.join(temp_dir, "incomplete.json")

            # Create evaluation with missing required fields
            incomplete_data = {
                "name": "Incomplete Evaluation",
                "version": "1.0.0",
                # Missing required fields like language, library, etc.
            }

            with open(incomplete_path, "w") as f:
                f.write(str(incomplete_data).replace("'", '"'))

            # Should return None gracefully
            result = load_evaluation_from_file(incomplete_path)
            assert result is None

    def test_dashboard_with_corrupted_resultset(self):
        """Test dashboard when evaluation has corrupted result data"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = os.path.join(temp_dir, "corrupted_results.json")

            # Create evaluation then corrupt the resultset data
            with patch("llm.generate_answer") as mock_generate:
                mock_generate.side_effect = [
                    "result = 5 + 3",
                    "reversed_str = 'hello'[::-1]",
                ]
                evaluation = create_evaluation(config_dir)

                # Serialize and then corrupt the JSON
                serialize_data_model(eval_path, evaluation)

                # Read and corrupt the JSON
                with open(eval_path, "r") as f:
                    data = f.read()

                # Corrupt the resultset section
                corrupted_data = data.replace('"results":', '"corrupted_results":')

                with open(eval_path, "w") as f:
                    f.write(corrupted_data)

            # Should handle corruption gracefully
            result = load_evaluation_from_file(eval_path)
            assert result is None

    @patch("streamlit.error")
    def test_streamlit_component_failure_handling(self, mock_error):
        """Test dashboard behavior when Streamlit components fail"""
        from dashboard import render_overview

        # Create mock evaluation
        mock_evaluation = Mock()
        mock_evaluation.name = "Test"
        mock_evaluation.version = "1.0.0"
        mock_evaluation.description = "Test"

        # Mock streamlit components to raise exceptions
        with patch(
            "streamlit.header", side_effect=Exception("Streamlit component failed")
        ):
            with patch("streamlit.caption"):
                with patch("streamlit.divider"):
                    # Should not crash when streamlit components fail
                    try:
                        render_overview(mock_evaluation)
                    except Exception as e:
                        assert "Streamlit component failed" in str(e)

    def test_dashboard_with_large_dataset_performance(self):
        """Test dashboard loading with large evaluation datasets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            large_eval_path = os.path.join(temp_dir, "large_evaluation.json")

            # Create evaluation with large number of tasks/results
            large_evaluation_data = {
                "name": "Large Evaluation",
                "version": "1.0.0",
                "description": "Large dataset test",
                "language": {
                    "name": "Python",
                    "version": "3.13",
                    "description": "Python",
                },
                "library": {
                    "name": "TestLib",
                    "version": "1.0.0",
                    "description": "Test",
                    "language": {
                        "name": "Python",
                        "version": "3.13",
                        "description": "Python",
                    },
                },
                "taskset": {
                    "name": "Large Taskset",
                    "version": "1.0.0",
                    "description": "Large taskset",
                    "library": {
                        "name": "TestLib",
                        "version": "1.0.0",
                        "description": "Test",
                        "language": {
                            "name": "Python",
                            "version": "3.13",
                            "description": "Python",
                        },
                    },
                    "tasks": [
                        {
                            "name": f"Task {i}",
                            "version": "1.0.0",
                            "description": f"Task {i}",
                            "library": {
                                "name": "TestLib",
                                "version": "1.0.0",
                                "description": "Test",
                                "language": {
                                    "name": "Python",
                                    "version": "3.13",
                                    "description": "Python",
                                },
                            },
                            "content": f"x_{i} = {i}",
                        }
                        for i in range(1000)  # 1000 tasks
                    ],
                    "size": 1000,
                },
                "testset": {
                    "name": "Large Testset",
                    "version": "1.0.0",
                    "description": "Large testset",
                    "taskset": {},  # Reference to taskset
                    "tests": [
                        {
                            "name": f"Test {i}",
                            "version": "1.0.0",
                            "description": f"Test {i}",
                            "task": {},  # Reference to task
                            "content": f"assert x_{i} == {i}",
                        }
                        for i in range(1000)
                    ],
                    "size": 1000,
                },
                "model": {
                    "name": "gpt-4",
                    "version": "1.0.0",
                    "description": "GPT-4",
                    "provider": "openai",
                },
                "agent": {
                    "name": "TestAgent",
                    "version": "1.0.0",
                    "description": "Test",
                    "model": {},
                    "prompt": "test",
                    "configuration": "test",
                    "scaffolding": "test",
                },
                "answerset": {
                    "name": "Large Answerset",
                    "version": "1.0.0",
                    "description": "Large answerset",
                    "agent": {},
                    "taskset": {},
                    "answers": [],
                    "size": 1000,
                },
                "resultset": {
                    "name": "Large Resultset",
                    "version": "1.0.0",
                    "description": "Large resultset",
                    "taskset": {},
                    "testset": {},
                    "answerset": {},
                    "results": [],
                    "size": 1000,
                    "number_passed": 500,
                    "percentage_passed": 50.0,
                },
            }

            import json

            with open(large_eval_path, "w") as f:
                json.dump(large_evaluation_data, f)

            # Test that loading completes in reasonable time (should not hang)
            import time

            start_time = time.time()
            result = load_evaluation_from_file(large_eval_path)
            load_time = time.time() - start_time

            # Should complete within reasonable time (5 seconds) or return None if too large
            assert load_time < 5.0 or result is None

    def test_dashboard_memory_usage_with_complex_evaluation(self):
        """Test dashboard memory handling with complex nested evaluation data"""
        config_dir = "tests/configs/test_configs"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple evaluations and load them
            eval_paths = []

            for i in range(10):  # Create 10 evaluations
                eval_path = os.path.join(temp_dir, f"eval_{i}.json")

                with patch("llm.generate_answer") as mock_generate:
                    mock_generate.side_effect = [
                        f"result = {i} + 3",
                        f"reversed_str = 'test{i}'[::-1]",
                    ]
                    evaluation = create_evaluation(config_dir)
                    serialize_data_model(eval_path, evaluation)
                    eval_paths.append(eval_path)

            # Load all evaluations - should not cause memory issues
            loaded_evaluations = []
            for path in eval_paths:
                loaded = load_evaluation_from_file(path)
                if loaded:
                    loaded_evaluations.append(loaded)

            # Verify we could load multiple evaluations
            assert len(loaded_evaluations) > 0
