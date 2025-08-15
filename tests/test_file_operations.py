"""Smoke tests for file operations in affordance evaluation framework"""

import json
import os
import tempfile

import pytest
from pydantic import ValidationError

from data_models import Language, Library, Task, Taskset
from utils import (
    clean_code,
    deserialize_data_model,
    deserialize_dict,
    find_config_file,
    generate_evaluation_output_path,
    serialize_data_model,
)


class TestFileOperations:
    """Smoke tests for file I/O operations"""

    def test_config_file_finder(self):
        """Test that config files can be found using glob patterns"""
        config_dir = "tests/configs/test_configs"

        # Test finding each config file type
        language_config = find_config_file(config_dir, "language_*.json")
        assert "language_test.json" in language_config
        assert os.path.exists(language_config)

        library_config = find_config_file(config_dir, "library_*.json")
        assert "library_test.json" in library_config
        assert os.path.exists(library_config)

        model_config = find_config_file(config_dir, "model_*.json")
        assert "model_test.json" in model_config
        assert os.path.exists(model_config)

        agent_config = find_config_file(config_dir, "agent_*.json")
        assert "agent_test.json" in agent_config
        assert os.path.exists(agent_config)

        taskset_config = find_config_file(config_dir, "taskset_*.json")
        assert "taskset_test.json" in taskset_config
        assert os.path.exists(taskset_config)

        testset_config = find_config_file(config_dir, "testset_*.json")
        assert "testset_test.json" in testset_config
        assert os.path.exists(testset_config)

    def test_config_file_finder_not_found(self):
        """Test that FileNotFoundError is raised when config file doesn't exist"""
        config_dir = "tests/configs/test_configs"

        with pytest.raises(FileNotFoundError, match="No config file matching pattern"):
            find_config_file(config_dir, "nonexistent_*.json")

    def test_config_file_finder_empty_directory(self):
        """Test behavior when directory is empty"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(
                FileNotFoundError, match="No config file matching pattern"
            ):
                find_config_file(temp_dir, "language_*.json")

    def test_serialization_deserialization_language(self, tmp_path):
        """Test that Language objects can be serialized and deserialized"""
        language = Language(
            name="Python",
            version="3.13",
            description="Python programming language",
        )

        # Test serialization
        test_file = tmp_path / "test_language.json"
        serialize_data_model(str(test_file), language)
        assert test_file.exists()

        # Verify file contains valid JSON
        with open(test_file, "r") as f:
            content = f.read()
            assert '"name": "Python"' in content
            assert '"version": "3.13"' in content

        # Test deserialization
        loaded_language = deserialize_data_model(str(test_file), Language)
        assert loaded_language.name == "Python"
        assert loaded_language.version == "3.13"
        assert loaded_language.description == "Python programming language"
        assert loaded_language == language

    def test_serialization_deserialization_complex_object(self, tmp_path):
        """Test serialization/deserialization of complex nested objects"""
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
            description="First task",
            library=library,
            content="x = 1",
        )
        task2 = Task(
            name="Task2",
            version="1.0.0",
            description="Second task",
            library=library,
            content="y = 2",
        )

        taskset = Taskset(
            name="TestTaskset",
            version="1.0.0",
            description="Test taskset",
            library=library,
            tasks=(task1, task2),
        )

        # Test serialization
        test_file = tmp_path / "test_taskset.json"
        serialize_data_model(str(test_file), taskset)
        assert test_file.exists()

        # Test deserialization
        loaded_taskset = deserialize_data_model(str(test_file), Taskset)
        assert loaded_taskset.name == "TestTaskset"
        assert loaded_taskset.size == 2
        assert loaded_taskset.library.name == "NumPy"
        assert loaded_taskset.library.language.name == "Python"
        assert loaded_taskset.tasks[0].content == "x = 1"
        assert loaded_taskset.tasks[1].content == "y = 2"

    def test_deserialize_dict_functionality(self):
        """Test that deserialize_dict properly loads JSON to dict"""
        config_dir = "tests/configs/test_configs"
        language_config = find_config_file(config_dir, "language_*.json")

        data = deserialize_dict(language_config)
        assert isinstance(data, dict)
        assert data["name"] == "Python"
        assert data["version"] == "3.13"
        assert data["description"] == "Python programming language for testing"

    def test_deserialize_dict_complex_structure(self):
        """Test deserialize_dict with complex nested structure"""
        config_dir = "tests/configs/test_configs"
        taskset_config = find_config_file(config_dir, "taskset_*.json")

        data = deserialize_dict(taskset_config)
        assert isinstance(data, dict)
        assert data["name"] == "TestTaskset"
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) == 2
        assert data["tasks"][0]["name"] == "Simple Addition"
        assert data["tasks"][1]["name"] == "String Reversal"

    def test_file_handling_errors(self, tmp_path):
        """Test file handling error cases"""
        # Test deserializing non-existent file
        non_existent_file = tmp_path / "does_not_exist.json"
        with pytest.raises(FileNotFoundError):
            deserialize_data_model(str(non_existent_file), Language)

        # Test deserializing invalid JSON
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text("{ invalid json }")

        with pytest.raises((json.JSONDecodeError, ValidationError)):
            deserialize_data_model(str(invalid_json_file), Language)

    def test_evaluation_output_path_generation(self):
        """Test generation of evaluation output paths"""
        # Test with default eval_dir
        path1 = generate_evaluation_output_path("Test Evaluation", "gpt-4")
        assert path1.startswith("evals/Test_Evaluation_gpt-4_")
        assert path1.endswith(".json")

        # Test with custom eval_dir
        path2 = generate_evaluation_output_path("My Test", "claude", "custom_evals")
        assert path2.startswith("custom_evals/My_Test_claude_")
        assert path2.endswith(".json")

        # Test that spaces are replaced with underscores
        path3 = generate_evaluation_output_path("Multi Word Name", "model-name")
        assert "Multi_Word_Name" in path3
        assert " " not in path3

    def test_clean_code_functionality(self):
        """Test code cleaning utility function"""
        # Test removing code block markers
        code_with_markers = "```python\nprint('hello')\n```"
        cleaned = clean_code(code_with_markers)
        assert "```" not in cleaned
        assert "print('hello')" in cleaned

        # Test removing language-specific markers
        code_with_lang = "```javascript\nconsole.log('test');\n```"
        cleaned_js = clean_code(code_with_lang)
        assert "```" not in cleaned_js
        assert "console.log('test');" in cleaned_js

        # Test code without markers (should remain unchanged)
        plain_code = "x = 5\nprint(x)"
        cleaned_plain = clean_code(plain_code)
        assert cleaned_plain == plain_code

        # Test multiple code blocks
        multiple_blocks = "Some text\n```python\nx = 1\n```\nMore text\n```\ny = 2\n```"
        cleaned_multiple = clean_code(multiple_blocks)
        assert "```" not in cleaned_multiple
        assert "x = 1" in cleaned_multiple
        assert "y = 2" in cleaned_multiple

        # Test edge cases
        assert clean_code("") == ""
        assert clean_code("```\n```") == "\n"

    def test_file_permissions_and_encoding(self, tmp_path):
        """Test that files are created with proper permissions and encoding"""
        language = Language(
            name="Tëst Languägé",  # Test Unicode handling
            version="1.0.0",
            description="Test with special characters: áéíóú",
        )

        test_file = tmp_path / "unicode_test.json"
        serialize_data_model(str(test_file), language)

        # Test file exists and is readable
        assert test_file.exists()
        assert os.access(test_file, os.R_OK)

        # Test Unicode content is preserved
        loaded_language = deserialize_data_model(str(test_file), Language)
        assert loaded_language.name == "Tëst Languägé"
        assert loaded_language.description == "Test with special characters: áéíóú"

    def test_directory_creation_behavior(self, tmp_path):
        """Test behavior when output directories don't exist"""
        # Create nested directory structure in path
        nested_path = tmp_path / "deep" / "nested" / "path" / "test.json"

        language = Language(name="Test", version="1.0.0", description="Test")

        # This should fail since parent directories don't exist
        with pytest.raises((FileNotFoundError, OSError)):
            serialize_data_model(str(nested_path), language)

        # Create parent directories
        nested_path.parent.mkdir(parents=True)

        # Now it should work
        serialize_data_model(str(nested_path), language)
        assert nested_path.exists()

        # Verify content
        loaded = deserialize_data_model(str(nested_path), Language)
        assert loaded.name == "Test"
