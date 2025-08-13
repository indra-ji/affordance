from pathlib import Path
from typing import Optional, Union

import streamlit as st

from data_models import Evaluation
from json_utils import deserialize_data_model


def display_entity_info(entity_data: dict, title: str, icon: str = "📋"):
    """Display entity information in minimal text format"""
    st.write(f"**{icon} {title}:** {entity_data['name']} (v{entity_data['version']})")
    st.write(f"_{entity_data['description']}_")


def create_progress_bar(value: float, max_value: float, label: str):
    """Create a visual progress bar using Streamlit's progress component"""
    percentage = value / max_value if max_value > 0 else 0
    st.write(f"**{label}:** {value}/{max_value} ({percentage:.1%})")
    st.progress(percentage)


def render_overview_section(data: dict):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("📊 Evaluation Overview")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        display_entity_info(data, "Evaluation", "🔬")

    # Language and Library
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["language"], "Language", "🔤")
    with col2:
        display_entity_info(data["library"], "Library", "📚")

    # Model and Agent
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["model"], "Model", "🤖")
    with col2:
        display_entity_info(data["agent"], "Agent", "🕵️")


def render_performance_section(data: dict):
    """Render the performance metrics section"""
    st.header("🎯 Performance Metrics & Computed Fields")

    # Core size metrics
    st.subheader("📏 Size Metrics (Computed Fields)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Taskset Size",
            data["taskset"]["size"],
            help="Number of tasks in the taskset",
        )
    with col2:
        st.metric(
            "Testset Size",
            data["testset"]["size"],
            help="Number of tests in the testset",
        )
    with col3:
        st.metric(
            "Answerset Size",
            data["answerset"]["size"],
            help="Number of answers generated",
        )
    with col4:
        st.metric(
            "Resultset Size",
            data["resultset"]["size"],
            help="Number of test results",
        )

    st.divider()

    # Resultset performance
    st.subheader("🎯 Resultset Performance (Computed Fields)")

    col1, col2 = st.columns(2)
    with col1:
        passed = data["resultset"]["number_passed"]
        total = data["resultset"]["size"]
        percentage = data["resultset"]["percentage_passed"]

        st.metric("Tests Passed", f"{passed}/{total}")
        st.metric("Pass Rate", f"{percentage:.1f}%")

        # Visual progress bar
        create_progress_bar(passed, total, "Progress")

    with col2:
        failed = total - passed
        fail_rate = 100 - percentage

        st.metric("Tests Failed", failed)
        st.metric("Fail Rate", f"{fail_rate:.1f}%")

        # Status indicator
        if percentage >= 80:
            st.success("🎉 Excellent performance!")
        elif percentage >= 60:
            st.warning("⚠️ Good performance")
        else:
            st.error("❌ Needs improvement")

    st.divider()

    # Benchmark performance
    st.subheader("🏆 Benchmark Performance (Computed Fields)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Benchmark Size", data["benchmark"]["size"])
    with col2:
        st.metric("Total Tests", data["benchmark"]["total_size"])
    with col3:
        st.metric("Total Passed", data["benchmark"]["number_passed"])
    with col4:
        st.metric(
            "Overall Pass Rate",
            f"{data['benchmark']['percentage_passed']:.1f}%",
        )

    # Overall progress
    st.subheader("📊 Overall Progress")
    create_progress_bar(
        data["benchmark"]["number_passed"],
        data["benchmark"]["total_size"],
        "Overall Completion",
    )


def render_task_results_section(data: dict):
    """Render the task results section"""
    st.header("📋 Detailed Task Results")

    # Results summary
    results = data["resultset"]["results"]
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", len(results))
    with col2:
        st.metric("✅ Passed", passed_count)
    with col3:
        st.metric("❌ Failed", failed_count)

    st.divider()

    # Filters
    st.subheader("🔍 Filter Results")
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status:", ["All", "Passed", "Failed"])
    with col2:
        search_term = st.text_input("Search task names:")

    # Display results
    st.subheader("📊 Task Results")

    for i, result in enumerate(results):
        # Apply filters
        if status_filter == "Passed" and not result["passed"]:
            continue
        if status_filter == "Failed" and result["passed"]:
            continue
        if (
            search_term
            and search_term.lower() not in result["answer"]["task"]["name"].lower()
        ):
            continue

        # Display task
        status_icon = "✅" if result["passed"] else "❌"

        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**Task {i + 1}**")
                if result["passed"]:
                    st.success(f"{status_icon} Passed")
                else:
                    st.error(f"{status_icon} Failed")

            with col2:
                st.markdown(f"**{result['answer']['task']['name']}**")
                st.caption(result["answer"]["task"]["description"][:100] + "...")

                with st.expander(f"View Details - Task {i + 1}"):
                    st.markdown("**Task Content:**")
                    st.text(result["answer"]["task"]["content"])

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Generated Answer:**")
                        st.code(result["answer"]["content"], language="python")
                    with col_b:
                        st.markdown("**Test Code:**")
                        st.code(result["test"]["content"], language="python")

        st.divider()


def render_task_explorer_section(data: dict):
    """Render the task explorer section"""
    st.header("🔍 Task Deep Dive Explorer")

    results = data["resultset"]["results"]
    task_names = [
        f"Task {i + 1}: {r['answer']['task']['name']}" for i, r in enumerate(results)
    ]

    selected_task_idx = st.selectbox(
        "Select a task to explore in detail:",
        range(len(task_names)),
        format_func=lambda x: task_names[x],
    )

    if selected_task_idx is not None:
        result = results[selected_task_idx]

        # Task header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📝 {result['answer']['task']['name']}")
        with col2:
            if result["passed"]:
                st.success("✅ PASSED")
            else:
                st.error("❌ FAILED")

        # Task details tabs
        tab1, tab2, tab3 = st.tabs(["📋 Task Info", "🤖 Answer", "🧪 Test"])

        with tab1:
            st.markdown("**Task Description:**")
            st.info(result["answer"]["task"]["description"])

            st.markdown("**Task Content:**")
            st.text_area(
                "",
                result["answer"]["task"]["content"],
                height=200,
                disabled=True,
            )

            # Task metadata
            st.markdown("**Metadata:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Version:** {result['answer']['task']['version']}")
                st.write(f"**Library:** {result['answer']['task']['library']['name']}")
            with col2:
                st.write(f"**Task Number:** {selected_task_idx + 1}")
                st.write(f"**Status:** {'Passed' if result['passed'] else 'Failed'}")

        with tab2:
            st.markdown("**Generated Answer:**")
            st.code(result["answer"]["content"], language="python")

            st.markdown("**Answer Metadata:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Agent:** {result['answer']['agent']['name']}")
                st.write(f"**Model:** {result['answer']['agent']['model']['name']}")
            with col2:
                st.write(f"**Answer Version:** {result['answer']['version']}")
                st.write(
                    f"**Provider:** {result['answer']['agent']['model']['provider']}"
                )

        with tab3:
            st.markdown("**Test Code:**")
            st.code(result["test"]["content"], language="python")

            st.markdown("**Test Metadata:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Test Name:** {result['test']['name']}")
                st.write(f"**Test Version:** {result['test']['version']}")
            with col2:
                st.write(
                    f"**Result:** {'✅ Passed' if result['passed'] else '❌ Failed'}"
                )
                st.write(f"**Test Description:** {result['test']['description']}")


def render_summary_section(data: dict):
    """Render the summary section"""
    st.header("📈 Evaluation Summary")

    # Key statistics
    st.subheader("🔢 Key Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Size Metrics**")
        st.write(f"• Taskset Size: {data['taskset']['size']}")
        st.write(f"• Testset Size: {data['testset']['size']}")
        st.write(f"• Answerset Size: {data['answerset']['size']}")
        st.write(f"• Resultset Size: {data['resultset']['size']}")

    with col2:
        st.markdown("**🎯 Performance Metrics**")
        st.write(f"• Tests Passed: {data['resultset']['number_passed']}")
        st.write(f"• Pass Rate: {data['resultset']['percentage_passed']:.1f}%")
        st.write(f"• Benchmark Size: {data['benchmark']['size']}")
        st.write(f"• Overall Pass Rate: {data['benchmark']['percentage_passed']:.1f}%")

    with col3:
        st.markdown("**📋 Entity Info**")
        st.write(
            f"• Language: {data['language']['name']} {data['language']['version']}"
        )
        st.write(f"• Library: {data['library']['name']} {data['library']['version']}")
        st.write(f"• Model: {data['model']['name']}")
        st.write(f"• Agent: {data['agent']['name']}")

    st.divider()

    # All computed fields summary
    st.subheader("🧮 All Computed Fields")

    computed_fields = {
        "Taskset.size": data["taskset"]["size"],
        "Testset.size": data["testset"]["size"],
        "Answerset.size": data["answerset"]["size"],
        "Resultset.size": data["resultset"]["size"],
        "Resultset.number_passed": data["resultset"]["number_passed"],
        "Resultset.percentage_passed": f"{data['resultset']['percentage_passed']:.2f}%",
        "Benchmark.size": data["benchmark"]["size"],
        "Benchmark.total_size": data["benchmark"]["total_size"],
        "Benchmark.number_passed": data["benchmark"]["number_passed"],
        "Benchmark.percentage_passed": f"{data['benchmark']['percentage_passed']:.2f}%",
    }

    for field, value in computed_fields.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{field}**")
        with col2:
            st.code(str(value))

    st.divider()

    # Final assessment
    st.subheader("🎯 Final Assessment")
    overall_rate = data["benchmark"]["percentage_passed"]

    if overall_rate >= 90:
        st.success(
            "🏆 **Excellent Performance!** The model performed exceptionally well on this evaluation."
        )
    elif overall_rate >= 75:
        st.success(
            "🎉 **Good Performance!** The model showed strong capabilities with room for minor improvements."
        )
    elif overall_rate >= 50:
        st.warning(
            "⚠️ **Moderate Performance.** The model shows promise but needs significant improvement."
        )
    else:
        st.error(
            "❌ **Poor Performance.** The model struggled significantly with these tasks."
        )

    # Recommendations
    st.markdown("**📝 Recommendations:**")
    failed_tasks = [r for r in data["resultset"]["results"] if not r["passed"]]
    if failed_tasks:
        st.write(
            f"• Focus on improving performance on {len(failed_tasks)} failed tasks"
        )
        st.write("• Review failed task patterns for common issues")
        st.write("• Consider adjusting model parameters or prompts")
    else:
        st.write(
            "• Excellent performance! Consider testing with more challenging tasks"
        )


@st.cache_data
def load_evaluation_from_file(file_path: str) -> Optional[dict]:
    """Load evaluation data from JSON file"""
    try:
        evaluation = deserialize_data_model(file_path, Evaluation)
        return evaluation.model_dump()
    except Exception as e:
        st.error(f"Error loading evaluation: {e}")
        return None


def show_dashboard(evaluation_data: Optional[Union[dict, Evaluation]] = None):
    """
    Main dashboard function that can be called from evaluation.py

    Args:
        evaluation_data: Either an Evaluation object or dict, or None to load from file
    """
    st.set_page_config(
        page_title="Evaluation Dashboard",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🔬 Evaluation Dashboard")
    st.markdown(
        "**Comprehensive visualization of evaluation results with all computed fields**"
    )

    # Handle different input types
    if evaluation_data is None:
        # File selection mode (original behavior)
        st.sidebar.header("📁 File Selection")
        eval_files = list(Path(".").glob("Evaluation_*.json"))

        if not eval_files:
            st.error(
                "❌ No evaluation files found! Make sure your JSON files are in the current directory."
            )
            return

        selected_file = st.sidebar.selectbox("Select Evaluation File:", eval_files)

        if selected_file:
            data = load_evaluation_from_file(str(selected_file))
            if not data:
                return
        else:
            return

    elif isinstance(evaluation_data, Evaluation):
        # Pydantic model input
        data = evaluation_data.model_dump()

    elif isinstance(evaluation_data, dict):
        # Dictionary input
        data = evaluation_data

    else:
        st.error(
            "Invalid evaluation data type. Expected Evaluation object, dict, or None."
        )
        return

    # Sidebar navigation
    st.sidebar.header("📍 Navigation")
    sections = [
        "📊 Overview",
        "🎯 Performance Metrics",
        "📋 Task Results",
        "🔍 Task Explorer",
        "📈 Summary",
    ]
    selected_section = st.sidebar.radio("Go to section:", sections)

    # Render selected section
    if selected_section == "📊 Overview":
        render_overview_section(data)
    elif selected_section == "🎯 Performance Metrics":
        render_performance_section(data)
    elif selected_section == "📋 Task Results":
        render_task_results_section(data)
    elif selected_section == "🔍 Task Explorer":
        render_task_explorer_section(data)
    elif selected_section == "📈 Summary":
        render_summary_section(data)


def main():
    """Main function for standalone usage"""
    show_dashboard()


if __name__ == "__main__":
    main()
