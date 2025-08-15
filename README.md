# Affordance

**Understand how well software engineering agents can use your software library.**

Affordance is an evaluation framework that measures how effectively AI coding agents can use specific software libraries.

It provides a complete pipeline for creating coding tasks, running AI agents against them, executing generated code safely, and visualizing results through an interactive dashboard.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- OpenAI API key for AI agent evaluation

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/affordance.git
cd affordance

# Install dependencies with uv
uv sync

# Set up environment variables
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Run Your First Evaluation

```bash
# Run evaluation using the provided numpy configs
uv run python evaluation.py --create eval_configs/numpy_demo_configs

# Launch the dashboard to view results
uv run streamlit run dashboard.py
```

## 📊 Architecture Overview

### Core Components

**Configuration System**: JSON files define languages, libraries, tasks, tests, models, and agents

**Evaluation Pipeline**: Orchestrates AI agents to solve coding tasks and executes/tests the generated code  

**Dashboard**: Interactive Streamlit interface for visualizing evaluation results

### Data Model Hierarchy

```markdown
Evaluation
├── Language (Python, JavaScript, etc.)
├── Library (NumPy, React, etc.)
├── Model (GPT-4, Claude, etc.)
├── Agent (Model + prompt + configuration)
├── Taskset (Collection of coding tasks)
├── Testset (Collection of test cases)
├── Answerset (Collection of AI-generated code solutions)
└── Resultset (Execution results + metrics)
```

## 📁 Project Structure

```markdown
affordance/
├── data_models.py          # Pydantic models for all data structures
├── evaluation.py           # Main evaluation pipeline + CLI interface
├── llm.py                  # AI model integration
├── tester.py               # Safe code execution and testing
├── utils.py                # Utillities for file I/O, serialization, etc.
├── dashboard.py            # Streamlit dashboard application
├── tests/                  # Test suite (currently incomplete)
│   ├── test_data_models.py # Data model creation and validation
│   ├── test_file_operations.py # File I/O and serialization
│   ├── test_code_execution.py # Code execution safety
│   ├── test_api_integration.py # Real OpenAI API testing
│   ├── test_evaluation_pipeline.py # Pipeline integration tests
│   ├── test_dashboard.py   # Dashboard functionality tests
│   ├── test_e2e.py         # End-to-end workflow tests
│   └── configs/            # Test configuration files
└── eval_configs/           # Evaluation configurations
    └── numpy_demo_configs/ # NumPy library evaluation example
```

## 🔧 Configuration System

### Config File Structure

Create six JSON configuration files for each evaluation:

Note: Insert any character/name in place of *, and evaluation will work

#### 1. Language (`language_*.json`)

```json
{
  "name": "Python",
  "version": "3.13",
  "description": "Python programming language"
}
```

#### 2. Library (`library_*.json`)

```json
{
  "name": "NumPy",
  "version": "2.0.0",
  "description": "Numerical computing library for Python"
}
```

#### 3. Model (`model_*.json`)

```json
{
  "name": "gpt-4o-mini",
  "version": "1.0.0",
  "description": "OpenAI GPT-4o Mini model",
  "provider": "openai"
}
```

#### 4. Agent (`agent_*.json`)

```json
{
  "name": "NumpyExpert",
  "version": "1.0.0", 
  "description": "AI agent specialized in NumPy tasks",
  "prompt": "You are an expert Python developer. Write clean, efficient code.",
  "configuration": "temperature=0.1",
  "scaffolding": "python3.13 + numpy"
}
```

#### 5. Taskset (`taskset_*.json`)

```json
{
  "name": "NumPy Basics",
  "version": "1.0.0",
  "description": "Basic NumPy operations",
  "tasks": [
    {
      "name": "Array Creation",
      "version": "1.0.0", 
      "description": "Create and manipulate arrays",
      "content": "Create a NumPy array [1,2,3,4,5] and store its sum in variable 'total'"
    }
  ]
}
```

#### 6. Testset (`testset_*.json`)

```json
{
  "name": "NumPy Tests",
  "version": "1.0.0",
  "description": "Test cases for NumPy tasks", 
  "tests": [
    {
      "name": "Test Array Sum",
      "version": "1.0.0",
      "description": "Verify array sum calculation",
      "content": "assert total == 15"
    }
  ]
}
```

## 🖥️ Command Line Interface

### Create New Evaluation

```bash
uv run python evaluation.py --create <config_directory>
```

### Rerun Existing Evaluation  

```bash
uv run python evaluation.py --rerun <evaluation_file.json>
```

### Load Evaluation (for inspection)

```bash
uv run python evaluation.py --load <evaluation_file.json>
```

## 🎯 How It Works

### 1. Configuration Loading

The pipeline loads configuration files and creates structured data models:

- **Language & Library**: Define the target programming environment
- **Model & Agent**: Configure the AI system and prompts  
- **Taskset & Testset**: Define coding challenges and validation tests

### 2. Answer Generation  

The AI agent processes each task:

- Constructs prompts with task context, library info, and agent instructions
- Calls OpenAI API to generate code solutions
- Cleans responses (removes markdown, formatting)

### 3. Safe Code Execution

Generated code is executed in a secure environment:

- **Import Blocking**: Dangerous modules (`os`, `sys`, `subprocess`) are blocked
- **Sandboxed Execution**: Code runs in isolated namespace
- **Test Validation**: Assertions verify correctness

### 4. Results & Metrics

Currently tracking only the most important metric:

- **Pass Rate**: Percentage of tasks completed successfully  

### 5. Dashboard Visualization

Interactive Streamlit dashboard provides:

- **Overview**: High-level evaluation summary
- **Metrics**: Performance statistics
- **Detailed View**: Task-by-task code and test inspection

## 🔒 Security Features

### Code Execution Safety

- **Import Filtering**: Blocks dangerous system modules
- **Namespace Isolation**: Each test runs in clean environment  

Note: Namespace execution is a placeholder, and will be updated to use Docker
for truly OS-level sandboxing and secure code execution

## 🧪 Testing

The project includes a comprehensive test suite with **98 tests** across multiple categories:

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Test Categories

#### Smoke Tests (47 tests)

```bash
uv run pytest tests/test_data_models.py tests/test_file_operations.py tests/test_code_execution.py -v
```

#### Integration Tests (38 tests)  

```bash
# Requires OPENAI_API_KEY for real API testing
uv run pytest tests/test_api_integration.py tests/test_evaluation_pipeline.py tests/test_dashboard.py -v
```

#### End-to-End Tests (13 tests)

```bash
# Requires OPENAI_API_KEY for real API testing
uv run pytest tests/test_e2e.py -v
```

Note: Test suite is currently a WIP

### Test Types

- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interactions  
- **API Tests**: Real OpenAI API integration (with API key)
- **Security Tests**: Code execution safety validation
- **End-to-End Tests**: Complete workflow validation
- **Error Handling**: Edge cases and failure scenarios

## 📈 Dashboard Features

### Overview Tab

- Evaluation metadata and configuration
- Language, library, model, and agent details
- Taskset and testset summaries

### Metrics Tab  

- Overall pass rate percentage
- Total tests and passed counts
- Dataset size metrics
- Performance visualizations

### Detailed View Tab

- Task-by-task breakdown
- Generated code inspection
- Test case analysis  
- Pass/fail indicators with details

### Dashboard Navigation

```bash
# Launch dashboard
uv run streamlit run dashboard.py

# Dashboard will be available at http://localhost:8501
# Select evaluation files from the sidebar
# Navigate between Overview, Metrics, and Detailed View tabs
```

## 🤝 Contributing

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/affordance.git
cd affordance
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check
uv run ruff format
```

## 🆘 Support

- **Documentation**: See code comments and type hints
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions

---

## Built with ❤️ for the AI evaluation community
