from pathlib import Path

import streamlit as st

from data_models import Evaluation
from utils import deserialize_data_model


def display_basic_info(entity, title: str):
    """Display basic information using Streamlit components only"""
    st.subheader(title)

    st.write(f"**Name:** {entity.name}")
    st.write(f"**Description:** {entity.description}")
    st.write(f"**Version:** {entity.version}")


def render_overview(evaluation: Evaluation):
    st.header("Evaluation Overview")
    st.caption("High-level details of the evaluation run")

    st.divider()

    display_basic_info(evaluation, "Evaluation")

    col1, col2 = st.columns(2)
    with col1:
        display_basic_info(evaluation.language, "Language")
    with col2:
        display_basic_info(evaluation.library, "Library")

    col1, col2 = st.columns(2)
    with col1:
        display_basic_info(evaluation.model, "Model")
    with col2:
        display_basic_info(evaluation.agent, "Agent")

    col1, col2 = st.columns(2)
    with col1:
        display_basic_info(evaluation.taskset, "Taskset")
    with col2:
        display_basic_info(evaluation.testset, "Testset")


def render_metrics(evaluation: Evaluation):
    st.header("Metrics")
    st.caption("At-a-glance performance")

    st.divider()

    st.subheader("Evaluation performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Overall pass rate",
            f"{evaluation.resultset.percentage_passed:.1f}%",
        )
    with col2:
        st.metric("Total tests", evaluation.resultset.size)
    with col3:
        st.metric("Total passed", evaluation.resultset.number_passed)

    st.divider()

    st.subheader("Dataset sizes")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Taskset size", evaluation.taskset.size)
    with col2:
        st.metric("Testset size", evaluation.testset.size)
    with col3:
        st.metric("Answerset size", evaluation.answerset.size)
    with col4:
        st.metric("Resultset size", evaluation.resultset.size)


def render_detailed_view(evaluation: Evaluation):
    st.header("Detailed view")
    st.caption("Inspect tasks, answers, tests, and results")

    st.divider()

    results = evaluation.resultset.results

    text_parts = [
        f"Task {i + 1}: {result.answer.task.name}" for i, result in enumerate(results)
    ]

    task_names = [
        f"{text} {'🟢 PASSED' if result.passed else '🔴 FAILED'}"
        for text, result in zip(text_parts, results)
    ]

    selected_task_idx = st.selectbox(
        "Select a task to explore in detail:",
        range(evaluation.resultset.taskset.size),
        format_func=lambda x: task_names[x],
    )

    result = results[selected_task_idx]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{result.answer.task.name}")
    with col2:
        match result.passed:
            case True:
                st.markdown("## **PASSED**")
            case False:
                st.markdown("## **:red[FAILED]**")

    tab1, tab2, tab3 = st.tabs(["Task", "Answer", "Test"])

    with tab1:
        st.text_area(
            "Task content:",
            result.answer.task.content,
            height=150,
            disabled=True,
        )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Task name:** {result.answer.task.name}")
            st.write(f"**Description:** {result.answer.task.description}")
            st.write(f"**Library:** {result.answer.task.library.name}")
        with col2:
            st.write(f"**Version:** {result.answer.task.version}")
            st.write(f"**Task number:** {selected_task_idx + 1}")

    with tab2:
        st.code(result.answer.content)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Agent:** {result.answer.agent.name}")
            st.write(f"**Model:** {result.answer.agent.model.name}")
            st.write(f"**Prompt:** {result.answer.agent.prompt}")
            st.write(f"**Scaffolding:** {result.answer.agent.scaffolding}")
        with col2:
            st.write(f"**Version:** {result.answer.agent.version}")
            st.write(f"**Provider:** {result.answer.agent.model.provider}")
            st.write(f"**Configuration:** {result.answer.agent.configuration}")

    with tab3:
        st.code(result.test.content)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Test name:** {result.test.name}")
            st.write(f"**Test version:** {result.test.version}")
        with col2:
            st.write(f"**Test description:** {result.test.description}")


@st.cache_data
def load_evaluation_from_file(file_path: str) -> Evaluation | None:
    try:
        evaluation = deserialize_data_model(file_path, Evaluation)
        return evaluation
    except Exception as e:
        st.error(f"Error loading evaluation: {e}")
        return None


def show_dashboard(evaluation_data: Evaluation | None = None):
    st.set_page_config(
        page_title="Evaluation Dashboard",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.header("File Selection")
    eval_files = list(Path("evals").glob("Evaluation_*.json"))

    if not eval_files:
        st.error(
            "No evaluation files found! Make sure your JSON files are in the evals directory."
        )
        return

    selected_file = st.sidebar.selectbox(
        "Evaluation to be displayed",
        eval_files,
        format_func=lambda p: p.name,
        label_visibility="collapsed",
    )

    evaluation = load_evaluation_from_file(str(selected_file))

    st.sidebar.header("Navigation")
    sections = [
        "Overview",
        "Metrics",
        "Detailed view",
    ]
    selected_section = st.sidebar.radio(
        "Section to be displayed",
        sections,
        label_visibility="collapsed",
    )

    match selected_section:
        case "Overview":
            render_overview(evaluation)
        case "Metrics":
            render_metrics(evaluation)
        case "Detailed view":
            render_detailed_view(evaluation)


def main():
    show_dashboard()


if __name__ == "__main__":
    main()
