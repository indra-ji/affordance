from pathlib import Path
from typing import Optional, Union

import streamlit as st

from data_models import Evaluation
from utils import deserialize_data_model


def display_entity_info(entity_data: dict, title: str, icon: str = ""):
    st.markdown(
        """
        <style>
        .af-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid #e5e7eb;
            background: #f3f4f6;
            color: #111827;
            font-weight: 600;
        }
        .af-badge small { color: #2563eb; font-weight: 500; }
        @media (prefers-color-scheme: dark) {
            .af-badge {
                border-color: rgba(148, 163, 184, 0.18);
                background: rgba(148, 163, 184, 0.06);
                color: #e5e7eb;
            }
            .af-badge small { color: #93c5fd; }
        }
        .af-overview-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 12px; }
        .af-overview-desc { font-size: 0.95rem; color: #64748b; }
        @media (prefers-color-scheme: dark) { .af-overview-desc { color: #94a3b8; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
    icon_part = f"{icon} " if icon else ""
    st.markdown(
        f"<span class='af-badge'>{icon_part}<strong>{title}:</strong> {entity_data['name']} <small>v{entity_data['version']}</small></span>",
        unsafe_allow_html=True,
    )
    st.write(f"_{entity_data['description']}_")


def render_overview_section(data: dict):
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.header("Evaluation Overview")
    st.caption("High-level details of the evaluation run")

    st.divider()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    display_entity_info(data, "Evaluation", "🔬")
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["language"], "Language", "🔤")
    with col2:
        display_entity_info(data["library"], "Library", "📚")
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["model"], "Model", "🤖")
    with col2:
        display_entity_info(data["agent"], "Agent", "🕵️")
    col1, col2 = st.columns(2)
    with col1:
        display_entity_info(data["taskset"], "Taskset", "🧩")

    with col2:
        display_entity_info(data["testset"], "Testset", "🧪")


def render_metrics_section(data: dict):
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    st.header("Metrics")
    st.caption("At-a-glance performance")

    st.divider()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.subheader("Evaluation performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Overall pass rate",
            f"{data['benchmark']['percentage_passed']:.1f}%",
        )
    with col2:
        st.metric("Total tests", data["benchmark"]["total_size"])
    with col3:
        st.metric("Total passed", data["benchmark"]["number_passed"])

    st.divider()

    st.subheader("Dataset sizes")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Taskset size",
            data["taskset"]["size"],
        )
    with col2:
        st.metric(
            "Testset size",
            data["testset"]["size"],
        )
    with col3:
        st.metric(
            "Answerset size",
            data["answerset"]["size"],
        )
    with col4:
        st.metric(
            "Resultset size",
            data["resultset"]["size"],
        )


def render_detailed_view_section(data: dict):
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.header("Detailed view")
    st.caption("Inspect tasks, answers, tests, and results")

    st.divider()

    results = data["resultset"]["results"]
    left_parts = [
        f"Task {i + 1}: {r['answer']['task']['name']}" for i, r in enumerate(results)
    ]
    max_left_len = max((len(s) for s in left_parts), default=0)

    def status_text(passed: bool) -> str:
        return "🟢 PASSED" if passed else "🔴 FAILED"

    task_names = [
        f"{left.ljust(max_left_len + 2)}{status_text(r['passed'])}"
        for left, r in zip(left_parts, results)
    ]

    selected_task_idx = st.selectbox(
        "Select a task to explore in detail:",
        range(len(task_names)),
        format_func=lambda x: task_names[x],
    )

    st.write("")
    st.write("")

    if selected_task_idx is not None:
        result = results[selected_task_idx]

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{result['answer']['task']['name']}")
        with col2:
            if result["passed"]:
                st.success("🟢 PASSED")
            else:
                st.error("🔴 FAILED")

        st.markdown(
            """
        <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 18px;
            font-weight: 600;
            padding: 8px 16px;
        }
        .stTabs [data-baseweb="tab-list"] button {
            height: 50px;
            padding: 0 24px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        tab1, tab2, tab3 = st.tabs(["Task", "Answer", "Test"])

        with tab1:
            st.markdown(
                """
            <style>
            .stTextArea textarea {
                background-color: black !important;
                color: white !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "Task content:",
                result["answer"]["task"]["content"],
                height=150,
                disabled=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Task name:** {result['answer']['task']['name']}")
                st.write(f"**Description:** {result['answer']['task']['description']}")
                st.write(f"**Library:** {result['answer']['task']['library']['name']}")
            with col2:
                st.write(f"**Version:** {result['answer']['task']['version']}")
                st.write(f"**Task number:** {selected_task_idx + 1}")

        with tab2:
            st.code(result["answer"]["content"])

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Agent:** {result['answer']['agent']['name']}")
                st.write(f"**Model:** {result['answer']['agent']['model']['name']}")
                st.write(f"**Prompt:** {result['answer']['agent']['prompt']}")
                st.write(f"**Scaffolding:** {result['answer']['agent']['scaffolding']}")
            with col2:
                st.write(f"**Version:** {result['answer']['agent']['version']}")
                st.write(
                    f"**Provider:** {result['answer']['agent']['model']['provider']}"
                )
                st.write(
                    f"**Configuration:** {result['answer']['agent']['configuration']}"
                )

        with tab3:
            st.code(result["test"]["content"])

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Test name:** {result['test']['name']}")
                st.write(f"**Test version:** {result['test']['version']}")
            with col2:
                st.write(f"**Test description:** {result['test']['description']}")


@st.cache_data
def load_evaluation_from_file(file_path: str) -> Optional[dict]:
    try:
        evaluation = deserialize_data_model(file_path, Evaluation)
        return evaluation.model_dump()
    except Exception as e:
        st.error(f"Error loading evaluation: {e}")
        return None


def show_dashboard(evaluation_data: Optional[Union[dict, Evaluation]] = None):
    st.set_page_config(
        page_title="Evaluation Dashboard",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if evaluation_data is None:
        st.sidebar.header("File Selection")
        eval_files = list(Path("evals").glob("Evaluation_*.json"))

        if not eval_files:
            st.error(
                "No evaluation files found! Make sure your JSON files are in the current directory."
            )
            return

        st.sidebar.markdown(
            """
            <style>
            [data-baseweb="menu"] { max-width: 90vw; width: 640px; left: 20px !important; }
            [data-baseweb="menu"] [role="option"] { white-space: normal; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        selected_file = st.sidebar.selectbox(
            "",
            eval_files,
            format_func=lambda p: p.name,
            label_visibility="collapsed",
        )

        if selected_file:
            data = load_evaluation_from_file(str(selected_file))
            if not data:
                return
        else:
            return

    elif isinstance(evaluation_data, Evaluation):
        data = evaluation_data.model_dump()

    elif isinstance(evaluation_data, dict):
        data = evaluation_data

    else:
        st.error(
            "Invalid evaluation data type. Expected Evaluation object, dict, or None."
        )
        return

    st.sidebar.header("Navigation")
    sections = [
        "Overview",
        "Metrics",
        "Detailed view",
    ]
    selected_section = st.sidebar.radio("", sections, label_visibility="collapsed")

    if selected_section == "Overview":
        render_overview_section(data)
    elif selected_section == "Metrics":
        render_metrics_section(data)
    elif selected_section == "Detailed view":
        render_detailed_view_section(data)


def main():
    show_dashboard()


if __name__ == "__main__":
    main()
